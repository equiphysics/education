"""1D model of the equine arterial tree, after Vera et al. (2019), PLoS ONE 14(8): e0221425.

In each of the 117 segments we solve, for pressure P(x,t) and flow Q(x,t),

    mass:      C_A(P) dP/dt + dQ/dx = 0
    momentum:  dQ/dt + d(delta Q^2/A)/dx + (A/rho) dP/dx = 2 pi R tau_w / rho - A g sin(phi)

with the paper's nonlinear wall law A(P), Womersley (or Poiseuille) wall shear
tau_w, and gravity along each segment. Boundary conditions:
  * aortic root: time-varying elastance left ventricle with internal resistance,
  * branch points: equal pressure and conservation of flow,
  * 62 terminal branches: 3-element Windkessels.

Numerics (ours; the paper used an implicit scheme in MATLAB): explicit MacCormack
in the interior, and the method of characteristics at every segment end.
"""
import time
from collections import deque

import numpy as np

from . import network as net
from .params import Params, MMHG, ML
from .womersley import womersley_number, shear_factor

_trapezoid = getattr(np, "trapezoid", None) or np.trapz   # np.trapz is np.trapezoid from NumPy 2.0 on


class HorseArteryModel:
    def __init__(self, params=None, terminal_table=None):
        self.p = params or Params()
        self.terminal_table = terminal_table   # optional {seg: (R1, R2, C)} in mmHg s/ml, ml/mmHg
        self._build_grid()
        self._build_wall_law()
        self._build_terminals()
        self._build_heart()

    # ------------------------------------------------------------------ grid
    def _build_grid(self):
        p = self.p
        order, q = [], deque([net.ROOT])
        while q:
            s = q.popleft()
            order.append(s)
            q.extend(net.CHILDREN.get(s, []))
        self.order = order
        parent = net.parent_of()

        start, end, nodes = {}, {}, 0
        x_list, Ar, Dm, sphi, dxn, zz, vid = [], [], [], [], [], [], []
        z_start = {}
        for k, s in enumerate(order):
            seg = net.SEGMENTS[s]
            L = seg["length_mm"] / 1000.0
            N = max(3, int(round(L / p.dx_target)) + 1)
            x = np.linspace(0.0, L, N)
            r = 0.5e-3 * (seg["d_prox_mm"] + (seg["d_dist_mm"] - seg["d_prox_mm"]) * x / L)
            sin_phi = np.sin(np.radians(seg["angle_deg"]))
            z0 = 0.0 if s == net.ROOT else z_start[parent[s]] + net.SEGMENTS[parent[s]]["length_mm"] / 1000.0 * np.sin(
                np.radians(net.SEGMENTS[parent[s]]["angle_deg"]))
            z_start[s] = z0
            start[s], end[s] = nodes, nodes + N - 1
            nodes += N
            x_list.append(x)
            Ar.append(np.pi * r ** 2)
            Dm.append(np.full(N, seg["distensibility_per_mmHg"] * p.distensibility_scale))
            sphi.append(np.full(N, sin_phi))
            dxn.append(np.full(N, L / (N - 1)))
            zz.append(z0 + x * sin_phi)
            vid.append(np.full(N, k))
        self.n_nodes = nodes
        self.start, self.end = start, end
        self.x = np.concatenate(x_list)
        self.Aref = np.concatenate(Ar)
        self.Rref = np.sqrt(self.Aref / np.pi)
        self.Dmm = np.concatenate(Dm)
        self.sinphi = np.concatenate(sphi)
        self.dx = np.concatenate(dxn)
        self.z = np.concatenate(zz)
        self.vessel = np.concatenate(vid)

        is_first = np.zeros(nodes, bool)
        is_last = np.zeros(nodes, bool)
        is_first[[start[s] for s in order]] = True
        is_last[[end[s] for s in order]] = True
        self.fwd = np.where(~is_last)[0]
        self.bwd = np.where(~is_first)[0]
        self.interior = np.where(~is_first & ~is_last)[0]

        # Womersley number at the heart rate, per node
        f0 = 1.0 / p.T
        self.alpha = womersley_number(self.Rref, f0, p.rho, p.mu)
        self.wom = (self.alpha > p.womersley_alpha_min) & (p.friction == "womersley")
        # Convective profile coefficient: flat (1) where inertia dominates, Poiseuille (4/3) otherwise
        self.delta = np.where(self.alpha > p.womersley_alpha_min, 1.0, 4.0 / 3.0)

        # Branch points
        jp, jd = [], []
        for j, (par, kids) in enumerate((s, net.CHILDREN[s]) for s in order if s in net.CHILDREN):
            jp.append((j, end[par]))
            for kid in kids:
                jd.append((j, start[kid]))
        self.n_junctions = len(jp)
        self.jp_id = np.array([a for a, _ in jp])
        self.jp_node = np.array([b for _, b in jp])
        self.jd_id = np.array([a for a, _ in jd])
        self.jd_node = np.array([b for _, b in jd])
        self.term_segs = [s for s in order if s not in net.CHILDREN]
        self.term_node = np.array([end[s] for s in self.term_segs])
        self.root_node = start[net.ROOT]
        self.ends = np.array([end[s] for s in order])
        self.starts = np.array([start[s] for s in order])

    # ------------------------------------------------------------- wall law
    def _build_wall_law(self):
        p = self.p
        self._Cp_ref = p.a1 + p.b1 / (1.0 + ((p.P_ref_mmHg - p.PmaxC_mmHg) / p.Pwidth_mmHg) ** 2)
        self._F_ref = self._F(p.P_ref_mmHg)

    def _F(self, Pm):
        p = self.p
        return p.a1 * Pm + p.b1 * p.Pwidth_mmHg * np.arctan((Pm - p.PmaxC_mmHg) / p.Pwidth_mmHg)

    # Below this fraction of the reference area the wall law continues as a smooth
    # exponential collapse (our addition). Normal runs never get there; it only matters
    # when pressure in the head falls near or below zero (standing horse, very slow heart).
    _F0 = 0.25

    def _wall(self, P, Aref, Dmm):
        """Area (m^2) and area compliance dA/dP (m^2/Pa) from pressure (Pa).
        Above collapse: A integrates the paper's compliance law, Eq (3)."""
        p = self.p
        Pm = P / MMHG
        f = 1.0 + Dmm * (self._F(Pm) - self._F_ref) / self._Cp_ref
        Cp = p.a1 + p.b1 / (1.0 + ((Pm - p.PmaxC_mmHg) / p.Pwidth_mmHg) ** 2)
        dfdP = Dmm * Cp / self._Cp_ref / MMHG
        F0 = self._F0
        e = np.exp(np.minimum(f - F0, 0.0) / F0)
        A = np.where(f >= F0, Aref * f, Aref * F0 * e)
        C = np.where(f >= F0, Aref * dfdP, Aref * e * dfdP)
        return A, C

    def area(self, P):
        """Lumen area (m^2) at every node from pressure (Pa)."""
        return self._wall(P, self.Aref, self.Dmm)[0]

    def compliance(self, P):
        """Area compliance C_A = dA/dP (m^2/Pa) at every node."""
        return self._wall(P, self.Aref, self.Dmm)[1]

    def area_at(self, i, P):
        """Area at node i for an array of pressures (e.g. over time)."""
        return self._wall(P, self.Aref[i], self.Dmm[i])[0]

    # ------------------------------------------------------------ terminals
    def _build_terminals(self):
        p = self.p
        tn = self.term_node
        c_ref = np.sqrt(1.0 / (p.rho * self.Dmm[tn] / MMHG))
        Zc = p.rho * c_ref / self.Aref[tn]                       # Pa s/m^3
        self.Zc_term = Zc
        R_tot = p.R_total_parallel * MMHG / ML
        self.region_of = {s: r for r, segs in net.REGIONS.items() for s in segs}
        Cnode = self.compliance(np.full(self.n_nodes, p.P_ref_mmHg * MMHG))
        self.C_vessels = self._integrate_segments(Cnode).sum()
        table = self.terminal_table
        if table is None and p.terminals == "s1":
            from .s1_table import load
            table = load()
        if table is not None:
            # Paper's S1 Table: total resistance R_T and compliance per terminal.
            # R1 = Zc (paper); where Zc > R_T (internal carotids, small head branches)
            # we use R1 = R_T, R2 = 0, i.e. a pure resistance.
            RT = np.array([table[s][0] for s in self.term_segs]) * MMHG / ML
            C = np.array([table[s][1] for s in self.term_segs]) * ML / MMHG
            R1 = np.minimum(Zc, RT)
            R2 = RT - R1
        else:
            # Flow share of each terminal: region target, split within the region by Murray's law
            frac = np.zeros(len(tn))
            total_target = sum(p.flow_targets.values())
            for r, segs in net.REGIONS.items():
                idx = [self.term_segs.index(s) for s in segs]
                w = self.Aref[tn[idx]] ** p.murray_exponent
                frac[idx] = p.flow_targets[r] / total_target * w / w.sum()
            RT = R_tot / frac                                    # parallel combination = R_tot
            R1 = np.minimum(Zc, 0.9 * RT)                        # paper: R1 = Zc
            R2 = RT - R1
            # Terminal compliance: a fixed share of total compliance, split by
            # distal area compliance (Eq 8)
            f = p.terminal_compliance_fraction
            C_T = f / (1.0 - f) * self.C_vessels
            C = C_T * Cnode[tn] / Cnode[tn].sum()
        self.R1, self.R2, self.CT = R1, R2, C
        # decay factor for the Windkessel capacitor over one step (set in run)
        self._tauW = self.R2 * self.CT

    def _integrate_segments(self, f):
        """Trapezoid integral of a node field over each segment."""
        out = []
        for s in self.order:
            i0, i1 = self.start[s], self.end[s]
            out.append(_trapezoid(f[i0:i1 + 1], self.x[i0:i1 + 1]))
        return np.array(out)

    # ---------------------------------------------------------------- heart
    def _build_heart(self):
        p = self.p
        t = np.linspace(0, 3, 30001)
        e = self._hill(t, 1.0, 1.0)
        self._t_peak_unit = t[np.argmax(e)]
        self._hill_norm = e.max()

    def _hill(self, t, scale, norm):
        p = self.p
        t1, t2 = p.hill_a1 * scale, p.hill_a2 * scale
        g1 = (t / t1) ** p.hill_n1
        return (g1 / (1 + g1)) / (1 + (t / t2) ** p.hill_n2) / norm

    def elastance(self, t_in_cycle):
        """Isovolumic elastance E*(t), Pa/m^3."""
        p = self.p
        scale = p.T_max / self._t_peak_unit
        e = self._hill(t_in_cycle, scale, self._hill_norm)
        return (p.E_min + (p.E_max - p.E_min) * e) * MMHG / ML

    # ------------------------------------------------------------ physics
    def source(self, P, Q, A, tau_lag=None, Q_lag=None):
        """Friction + gravity per unit length, divided by rho (m^3/s^2 per m)."""
        p = self.p
        S = -8.0 * np.pi * p.mu / p.rho * Q / A                 # Poiseuille
        if tau_lag is not None:
            w = self.wom
            R = self.Rref[w]
            tau = tau_lag[w] - 4.0 * p.mu / (np.pi * R ** 3) * (Q[w] - Q_lag[w])
            S[w] = 2.0 * np.pi * R * tau / p.rho
        if p.gravity:
            S = S - A * p.g * self.sinphi
        return S

    # ---------------------------------------------------------------- run
    def run(self, n_cycles=None, verbose=True, progress=None):
        """Run n_cycles heartbeats. progress(cycle, n_cycles) is called after each beat, if given."""
        p = self.p
        n_cycles = n_cycles or p.n_cycles
        T, rho = p.T, p.rho
        N = self.n_nodes

        # initial state (paper: 100 mmHg, 1 ml/s); with gravity start from hydrostatic balance
        P = np.full(N, p.P_init_mmHg * MMHG)
        if p.gravity:
            P = P - rho * p.g * self.z
        Q = np.full(N, p.Q_init_ml_s * ML)
        Pc = P[self.term_node] - self.R1 * Q[self.term_node]
        V = p.P_fill_mmHg / p.E_min * ML + p.V0_ml * ML
        V0 = p.V0_ml * ML
        P_fill = p.P_fill_mmHg * MMHG
        R_fill = p.R_fill * MMHG / ML
        kappa = p.kappa / ML                                       # s/m^3
        P_out = p.P_out_mmHg * MMHG

        # time step from the fastest wave at high pressure
        Phi = np.full(N, 250 * MMHG)
        c_max = np.sqrt(self.area(Phi) / (rho * self.compliance(Phi)))
        dt = p.cfl * np.min(self.dx / (c_max + 2.0))
        steps_per_cycle = int(np.ceil(T / dt))
        dt = T / steps_per_cycle
        self.dt = dt
        with np.errstate(divide="ignore"):
            decay = np.where(self._tauW > 0, np.exp(-dt / np.maximum(self._tauW, 1e-300)), 0.0)

        M = p.history_samples
        hist_every = steps_per_cycle / M
        Q_hist = np.zeros((N, M))
        tau_lag = Q_lag = None
        tau_tab = Q_tab = None

        n_out = p.output_samples
        out_every = max(1, steps_per_cycle // n_out)
        n_out = steps_per_cycle // out_every
        rec = dict(t=np.zeros(n_out), P=np.zeros((N, n_out)), Q=np.zeros((N, n_out)),
                   Plv=np.zeros(n_out), V=np.zeros(n_out), Qroot=np.zeros(n_out), Pc=np.zeros((len(Pc), n_out)))
        root_cycles = []

        wtab = self.wom.copy()
        Rw = self.Rref[wtab]
        harm = np.arange(M // 2 + 1)
        Fw = shear_factor(womersley_number(Rw[:, None], harm[None, :] / T, rho, p.mu))
        Fw[:, 0] = -4.0
        Fw[:, p.n_harmonics + 1:] = 0.0

        t = 0.0
        t_wall = time.time()
        fwd, bwd, inner = self.fwd, self.bwd, self.interior
        root = self.root_node
        ends, starts = self.ends, self.starts
        for cyc in range(n_cycles):
            root_P = np.zeros(M)
            last = cyc == n_cycles - 1
            for k in range(steps_per_cycle):
                tc = k * dt
                if tau_tab is not None:
                    ph = k / hist_every
                    m0 = int(ph) % M
                    wph = ph - int(ph)
                    m1 = (m0 + 1) % M
                    tau_lag = (1 - wph) * tau_tab[:, m0] + wph * tau_tab[:, m1]
                    Q_lag = (1 - wph) * Q_tab[:, m0] + wph * Q_tab[:, m1]

                A = self.area(P)
                CA = self.compliance(P)
                c = np.sqrt(A / (rho * CA))
                Z = rho * c / A
                S = self.source(P, Q, A, tau_lag, Q_lag)
                G = self.delta * Q * Q / A

                # --- MacCormack in the interior (alternate the sweep direction)
                Ps, Qs = P.copy(), Q.copy()
                if k % 2 == 0:
                    i, j = fwd, fwd + 1
                    Ps[i] = P[i] - dt * (Q[j] - Q[i]) / self.dx[i] / CA[i]
                    Qs[i] = Q[i] - dt * ((G[j] - G[i]) / self.dx[i] + A[i] / rho * (P[j] - P[i]) / self.dx[i]) + dt * S[i]
                    a, b = inner - 1, inner
                else:
                    i, j = bwd - 1, bwd
                    Ps[j] = P[j] - dt * (Q[j] - Q[i]) / self.dx[j] / CA[j]
                    Qs[j] = Q[j] - dt * ((G[j] - G[i]) / self.dx[j] + A[j] / rho * (P[j] - P[i]) / self.dx[j]) + dt * S[j]
                    a, b = inner, inner + 1
                As = self.area(Ps)
                CAs = self.compliance(Ps)
                Ss = self.source(Ps, Qs, As, tau_lag, Q_lag)
                Gs = self.delta * Qs * Qs / As
                Pn, Qn = P.copy(), Q.copy()
                dxi = self.dx[inner]
                Pn[inner] = 0.5 * (P[inner] + Ps[inner] - dt * (Qs[b] - Qs[a]) / dxi / CAs[inner])
                Qn[inner] = 0.5 * (Q[inner] + Qs[inner]
                                   - dt * ((Gs[b] - Gs[a]) / dxi + As[inner] / rho * (Ps[b] - Ps[a]) / dxi)
                                   + dt * Ss[inner])

                # --- characteristics arriving at every segment end (from time level n)
                lam = np.clip((Q[ends] / A[ends] + c[ends]) * dt / self.dx[ends], 0, 1)
                Pf = P[ends] - lam * (P[ends] - P[ends - 1])
                Qf = Q[ends] - lam * (Q[ends] - Q[ends - 1])
                Wp = Pf + Z[ends] * Qf + Z[ends] * S[ends] * dt          # P + Z Q along C+
                lam = np.clip((c[starts] - Q[starts] / A[starts]) * dt / self.dx[starts], 0, 1)
                Pf = P[starts] + lam * (P[starts + 1] - P[starts])
                Qf = Q[starts] + lam * (Q[starts + 1] - Q[starts])
                Wm = Pf - Z[starts] * Qf - Z[starts] * S[starts] * dt    # P - Z Q along C-
                W_end = np.zeros(N); W_end[ends] = Wp
                W_start = np.zeros(N); W_start[starts] = Wm

                # --- branch points: same pressure, flow conserved
                jp, jd = self.jp_node, self.jd_node
                num = np.bincount(self.jp_id, W_end[jp] / Z[jp], self.n_junctions) + \
                    np.bincount(self.jd_id, W_start[jd] / Z[jd], self.n_junctions)
                den = np.bincount(self.jp_id, 1 / Z[jp], self.n_junctions) + \
                    np.bincount(self.jd_id, 1 / Z[jd], self.n_junctions)
                Pj = num / den
                Pn[jp] = Pj[self.jp_id]
                Qn[jp] = (W_end[jp] - Pn[jp]) / Z[jp]
                Pn[jd] = Pj[self.jd_id]
                Qn[jd] = (Pn[jd] - W_start[jd]) / Z[jd]

                # --- terminal Windkessels
                tn = self.term_node
                Qt = (W_end[tn] - Pc) / (Z[tn] + self.R1)
                Pn[tn] = Pc + self.R1 * Qt
                Qn[tn] = Qt
                # capacitor: C dPc/dt = Q - (Pc - P_out)/R2, integrated exactly over dt
                Pinf = P_out + self.R2 * Qt
                Pc = Pinf + (Pc - Pinf) * decay

                # --- left ventricle at the aortic root
                Es = self.elastance(tc)
                Wr = W_start[root]
                Zr = Z[root]
                q = (Es * (V - V0) - Wr) / (Es * (V - V0) * kappa + Zr)
                if q > 0:
                    Qn[root] = q
                    Pn[root] = Wr + Zr * q
                    Plv = Pn[root]
                    V -= q * dt
                else:
                    Qn[root] = 0.0
                    Pn[root] = Wr
                    Plv = Es * (V - V0)
                    if Plv < P_fill:
                        V += (P_fill - Plv) / R_fill * dt

                # --- shock-capturing damping where the pressure has a sharp kink
                if p.shock_capturing > 0:
                    nu = np.zeros(N)
                    num = np.abs(Pn[inner + 1] - 2 * Pn[inner] + Pn[inner - 1])
                    nu[inner] = p.shock_capturing * num / (Pn[inner + 1] + 2 * Pn[inner] + Pn[inner - 1])
                    eR = np.minimum(np.maximum(nu[inner], nu[inner + 1]), 0.25)
                    eL = np.minimum(np.maximum(nu[inner - 1], nu[inner]), 0.25)
                    for U in (Pn, Qn):
                        U[inner] = U[inner] + eR * (U[inner + 1] - U[inner]) - eL * (U[inner] - U[inner - 1])

                P, Q = Pn, Qn
                t += dt

                # --- records
                if k % hist_every < 1.0:
                    m = int(k / hist_every)
                    if m < M:
                        Q_hist[:, m] = Q
                        root_P[m] = P[root]
                if last and k % out_every == 0 and k // out_every < n_out:
                    o = k // out_every
                    rec["t"][o] = tc
                    rec["P"][:, o] = P
                    rec["Q"][:, o] = Q
                    rec["Plv"][o] = Plv
                    rec["V"][o] = V
                    rec["Qroot"][o] = Q[root]
                    rec["Pc"][:, o] = Pc
                if k % 50 == 0 and not np.isfinite(P).all():
                    bad = np.where(~np.isfinite(P))[0]
                    segs = sorted({self.order[self.vessel[b]] for b in bad})
                    raise FloatingPointError(f"solution blew up at t={t:.3f} s in segments {segs[:8]}")

            # end of cycle: Womersley wall shear for the next cycle, from this cycle's flow
            root_cycles.append(root_P / MMHG)
            if p.friction == "womersley":
                Qh = np.fft.rfft(Q_hist[wtab], axis=1) / M
                Th = (p.mu / (np.pi * Rw[:, None] ** 3)) * Fw * Qh
                tau_w = np.fft.irfft(Th * M, n=M, axis=1)
                tau_tab = np.zeros((N, M)); tau_tab[wtab] = tau_w
                Q_tab = Q_hist.copy()
            if progress is not None:
                progress(cyc + 1, n_cycles)
            if verbose:
                d = np.abs(root_cycles[-1] - root_cycles[-2]).max() if len(root_cycles) > 1 else np.nan
                print(f"cycle {cyc + 1}/{n_cycles}: root P {root_P.min() / MMHG:5.1f}-{root_P.max() / MMHG:5.1f} mmHg, "
                      f"change vs last cycle {d:5.2f} mmHg, {time.time() - t_wall:5.1f} s")

        self.rec = rec
        self.root_cycles = root_cycles
        self.final_state = dict(P=P, Q=Q, Pc=Pc, V=V)
        return rec

    # ----------------------------------------------------------- helpers
    def node(self, seg, where="mid"):
        s, e = self.start[seg], self.end[seg]
        return {"start": s, "end": e, "mid": (s + e) // 2}[where]

    def node_at_distance(self, path, dist_m):
        """Node at a given distance from the start of a path of segments."""
        acc = 0.0
        for s in path:
            L = net.SEGMENTS[s]["length_mm"] / 1000.0
            if dist_m <= acc + L:
                i = self.start[s] + int(round((dist_m - acc) / L * (self.end[s] - self.start[s])))
                return i
            acc += L
        return self.end[path[-1]]
