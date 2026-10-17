"""Numbers the paper reports, computed from a finished model run (the last cycle)."""
import numpy as np

from . import network as net
from .params import MMHG, ML
from .womersley import wall_shear_from_flow


def global_metrics(m):
    r, p = m.rec, m.p
    dt = r["t"][1] - r["t"][0]
    SV = r["Qroot"].sum() * dt / ML
    EDV, ESV = r["V"].max() / ML, r["V"].min() / ML
    P = r["P"][m.node("1", "mid")] / MMHG
    CO = SV * 60.0 / p.T / 1000.0
    return dict(CO_L_min=CO, SV_ml=SV, EF_pct=100 * SV / EDV, EDV_ml=EDV, ESV_ml=ESV,
                SBP=P.max(), DBP=P.min(), MAP=P.mean(), PP=P.max() - P.min(),
                TVR=P.mean() / (CO * 1000 / 60.0))


def co_distribution(m):
    """Share of cardiac output (%) by body region, from mean terminal flows."""
    r = m.rec
    qmean = r["Q"][m.term_node].mean(axis=1)
    total = qmean.sum()
    out = {}
    for region, segs in net.REGIONS.items():
        idx = [m.term_segs.index(s) for s in segs]
        out[region] = 100 * qmean[idx].sum() / total
    return out


def location_metrics(m, seg, where="mid"):
    r, p = m.rec, m.p
    i = m.node(seg, where)
    P = r["P"][i]
    Q = r["Q"][i]
    A = _area_at(m, i, P)
    U = Q / A
    Pm = P / MMHG
    # wall shear stress over the cycle
    R = m.Rref[i]
    if m.wom[i]:
        tau = wall_shear_from_flow(Q, R, p.T, p.rho, p.mu, p.n_harmonics)
    else:
        tau = -4 * p.mu * Q / (np.pi * R ** 3)
    # mean convective acceleration d/dx(delta Q^2/A), central difference
    j0, j1 = max(i - 1, m.start[seg]), min(i + 1, m.end[seg])
    G0 = m.delta[j0] * r["Q"][j0] ** 2 / _area_at(m, j0, r["P"][j0])
    G1 = m.delta[j1] * r["Q"][j1] ** 2 / _area_at(m, j1, r["P"][j1])
    conv = ((G1 - G0) / (m.x[j1] - m.x[j0])).mean()
    D = 2 * np.sqrt(A.mean() / np.pi)
    return dict(alpha=m.alpha[i], peak_U=U.max(), mean_U=U.mean(), SBP=Pm.max(), DBP=Pm.min(),
                MAP=Pm.mean(), PP=Pm.max() - Pm.min(), tau_max=np.abs(tau).max(),
                conv_mean=conv, Re=p.rho * abs(U.mean()) * D / p.mu, height_m=m.z[i])


def _area_at(m, i, P):
    return m.area_at(i, P)


def foot_time(t, P):
    """Foot of the pressure wave: maximum of the second derivative during the upstroke."""
    d1 = np.gradient(P, t)
    d2 = np.gradient(d1, t)
    k_up = np.argmax(d1)                      # steepest upstroke
    lo = max(0, k_up - int(0.15 / (t[1] - t[0])))
    k = lo + np.argmax(d2[lo:k_up + 1])
    return t[k]


def aortic_pwv(m, distances_cm=(26.4, 36.4, 46.4, 56.4, 66.4, 76.4, 86.4)):
    r = m.rec
    times = []
    for dcm in distances_cm:
        i = m.node_at_distance(net.AORTA_PATH, dcm / 100.0)
        P = _smooth(r["P"][i])
        times.append(foot_time(r["t"], P))
    times = np.array(times)
    d = np.array(distances_cm) / 100.0
    slope = np.polyfit(times, d, 1)[0]
    return slope, times


def aorta_pressures(m, distances_cm=(26.4, 36.4, 46.4, 56.4, 66.4, 76.4, 86.4)):
    r = m.rec
    return {dcm: r["P"][m.node_at_distance(net.AORTA_PATH, dcm / 100.0)] / MMHG for dcm in distances_cm}


def wave_power(m, seg, where="mid"):
    """Forward and backward wave power, d(pi)+ and d(pi)- (Mynard & Smolich 2016)."""
    r, p = m.rec, m.p
    i = m.node(seg, where)
    P, Q = _smooth(r["P"][i], 9), _smooth(r["Q"][i], 9)   # ~13 ms smoothing, so steep fronts don't swamp the plot
    A = _area_at(m, i, P)
    C = m.Aref[i] * m.Dmm[i] / MMHG       # reference area compliance
    c = np.sqrt(A.mean() / (p.rho * C))
    Zc = p.rho * c / A.mean()
    dP, dQ = np.diff(P), np.diff(Q)
    fwd = (dP + Zc * dQ) ** 2 / (4 * Zc)
    bwd = -(dP - Zc * dQ) ** 2 / (4 * Zc)
    return r["t"][1:], fwd, bwd


def _smooth(y, k=5):
    ker = np.ones(k) / k
    ypad = np.concatenate([y[-k:], y, y[:k]])
    return np.convolve(ypad, ker, mode="same")[k:-k]
