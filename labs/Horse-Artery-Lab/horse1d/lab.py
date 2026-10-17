"""Helpers for the Horse Artery Lab notebook: run the model with three controls, and plot.

Controls:
  standing    - include gravity (a standing horse) or not (as if lying flat)
  heart_rate  - beats per minute (the paper uses 40, a resting horse)
  stiffness   - 1 = normal arteries; 1.5 = every artery 1.5 times stiffer (an older horse)
"""
import functools
import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from . import analysis as an, network as net
from .model import HorseArteryModel
from .params import Params, MMHG

# The five places the paper reports, with plain names
SITES = {
    "Aorta by the heart": "1",
    "Aorta at the hips": "87",
    "Carotid (neck)": "49",
    "Median (front leg)": "26",
    "Ext. iliac (hind leg)": "93",
}
AORTA_CM = (26.4, 36.4, 46.4, 56.4, 66.4, 76.4, 86.4)


def make_params(standing=False, heart_rate=40.0, stiffness=1.0, cycles=8):
    # Systole shortens with the square root of the heart period (our assumption for other rates).
    return Params(gravity=bool(standing), heart_rate_bpm=float(heart_rate),
                  T_max=0.478 * (40.0 / heart_rate) ** 0.5, E_min=0.0127,
                  distensibility_scale=1.0 / float(stiffness), n_cycles=int(cycles))


BREAKDOWN = """
The model broke down for this setting ({what}).

In a standing horse the head sits about a meter above the heart, so blood pressure
in the head is about 75 mmHg lower than at the heart. With a slow heart (a long
pause between beats) or stiff arteries, pressure in the head falls close to zero
before the next beat. The head arteries then go soft and the pressure wave slows
down until the blood moves faster than the wave. The 1D equations cannot handle
that, and the numbers blow up.

Real horses avoid this: reflexes tighten blood vessels and speed up the heart, and
the veins draining the head help pull blood through. This model has neither.
Try a faster heart rate, softer arteries, or a lying horse.
"""


@functools.lru_cache(maxsize=32)
def run_horse(standing=False, heart_rate=40.0, stiffness=1.0, cycles=8, verbose=True):
    """Run the model and return a small dictionary of results (cached, so repeats are instant).
    Returns None, with an explanation, if the model breaks down."""
    m = HorseArteryModel(make_params(standing, heart_rate, stiffness, cycles))
    t0 = time.time()

    def tick(c, n):
        if verbose:
            print(f"{c}" + (" " if c < n else f"  done in {time.time() - t0:.0f} s\n"), end="", flush=True)

    if verbose:
        print(f"Running {label(dict(settings=dict(standing=standing, heart_rate=heart_rate, stiffness=stiffness)))}: "
              f"heartbeat ", end="", flush=True)
    try:
        with np.errstate(all="ignore"):
            m.run(verbose=False, progress=tick)
    except FloatingPointError:
        what = label(dict(settings=dict(standing=standing, heart_rate=heart_rate, stiffness=stiffness)))
        print(BREAKDOWN.format(what=what))
        return None
    g = an.global_metrics(m)
    sites = {}
    for name, seg in SITES.items():
        i = m.node(seg)
        P = m.rec["P"][i]
        L = an.location_metrics(m, seg)
        sites[name] = dict(seg=seg, P=P / MMHG, U=m.rec["Q"][i] / an._area_at(m, i, P),
                           SBP=L["SBP"], DBP=L["DBP"], MAP=L["MAP"], PP=L["PP"],
                           peak_U=L["peak_U"], height_m=m.z[i])
    pwv, feet = an.aortic_pwv(m, AORTA_CM)
    seg_P = {}
    for s in m.order:
        P = m.rec["P"][m.node(s)] / MMHG
        seg_P[s] = (P.mean(), P.max(), P.min())
    return dict(settings=dict(standing=bool(standing), heart_rate=float(heart_rate), stiffness=float(stiffness)),
                t=m.rec["t"].copy(), glob=g, co=an.co_distribution(m), sites=sites,
                aorta={d: P for d, P in an.aorta_pressures(m, AORTA_CM).items()},
                pwv=pwv, foot_times=dict(zip(AORTA_CM, feet)), seg_P=seg_P,
                Plv=m.rec["Plv"] / MMHG, V=m.rec["V"] * 1e6)


def label(res):
    s = res["settings"]
    txt = f"{'standing' if s['standing'] else 'lying'}, {s['heart_rate']:.0f} bpm"
    if s["stiffness"] != 1.0:
        txt += f", stiffness x{s['stiffness']:g}"
    return txt


# ------------------------------------------------------------------ tables
def summary(*results):
    """Print the key numbers for one or more runs side by side."""
    results = [r for r in results if r is not None]
    if not results:
        return
    cols = [label(r) for r in results]
    w = max(26, max(len(c) for c in cols) + 2)
    rows = [("Cardiac output (L/min)", lambda r: f"{r['glob']['CO_L_min']:.1f}"),
            ("Stroke volume (ml)", lambda r: f"{r['glob']['SV_ml']:.0f}"),
            ("Aortic pressure (mmHg)", lambda r: f"{r['glob']['SBP']:.0f}/{r['glob']['DBP']:.0f}"),
            ("Aortic pulse pressure (mmHg)", lambda r: f"{r['glob']['PP']:.0f}"),
            ("Aortic pulse wave speed (m/s)", lambda r: f"{r['pwv']:.1f}"),
            ("Share of blood to the brain (%)", lambda r: f"{r['co']['brain']:.1f}"),
            ("Share of blood to the limbs (%)", lambda r: f"{r['co']['muscle']:.1f}")]
    for name in SITES:
        rows.append((f"{name}: mean (mmHg)", lambda r, n=name: f"{r['sites'][n]['MAP']:.0f}"))
        rows.append((f"{name}: sys/dia (mmHg)", lambda r, n=name: f"{r['sites'][n]['SBP']:.0f}/{r['sites'][n]['DBP']:.0f}"))
        rows.append((f"{name}: peak speed (m/s)", lambda r, n=name: f"{r['sites'][n]['peak_U']:.2f}"))
    print(" " * 38 + "".join(f"{c:>{w}}" for c in cols))
    for lab, f in rows:
        print(f"{lab:38s}" + "".join(f"{f(r):>{w}}" for r in results))


def compare_with_paper():
    """Our resting horse, lying and standing, next to the numbers Vera et al. (2019) report."""
    from . import paper
    lying, standing = run_horse(False, 40, 1.0), run_horse(True, 40, 1.0)
    if lying is None or standing is None:
        return
    G0, G1 = paper.GLOBAL["no_gravity"], paper.GLOBAL["gravity"]
    rows = [("Cardiac output (L/min)", f"{G0['CO_L_min']}", f"{lying['glob']['CO_L_min']:.1f}",
             f"{G1['CO_L_min']}", f"{standing['glob']['CO_L_min']:.1f}"),
            ("Stroke volume (ml)", f"{G0['SV_ml']}", f"{lying['glob']['SV_ml']:.0f}",
             f"{G1['SV_ml']}", f"{standing['glob']['SV_ml']:.0f}"),
            ("Aortic pressure (mmHg)", f"{G0['SBP']}/{G0['DBP']}", f"{lying['glob']['SBP']:.0f}/{lying['glob']['DBP']:.0f}",
             f"{G1['SBP']}/{G1['DBP']}", f"{standing['glob']['SBP']:.0f}/{standing['glob']['DBP']:.0f}"),
            ("Aortic pulse wave speed (m/s)", f"{paper.PWV['no_gravity']}", f"{lying['pwv']:.1f}",
             f"{paper.PWV['gravity']}", f"{standing['pwv']:.1f}")]
    for n, name in enumerate(SITES):
        for key, lab_txt, nd in (("MAP", "mean pressure (mmHg)", 0), ("peak_U", "peak speed (m/s)", 2)):
            rows.append((f"{name}: {lab_txt}", f"{paper.TABLE4[key]['no_gravity'][n]:.{nd}f}",
                         f"{lying['sites'][name][key]:.{nd}f}", f"{paper.TABLE4[key]['gravity'][n]:.{nd}f}",
                         f"{standing['sites'][name][key]:.{nd}f}"))
    print(f"{'':44s}{'Study, lying':>14s}{'Ours, lying':>13s}{'Study, standing':>17s}{'Ours, standing':>16s}")
    for r in rows:
        print(f"{r[0]:44s}{r[1]:>14s}{r[2]:>13s}{r[3]:>17s}{r[4]:>16s}")
    print("\nMeasured in standing horses: aortic pulse wave speed 5.27 m/s; peak blood speed "
          "0.74 m/s (aorta by the heart), 0.85 (carotid), 0.40 (median), 0.46 (external iliac).")


# ------------------------------------------------------------------ plots
def plot_sites(*results, labels=None):
    """Blood speed and pressure over one heartbeat at the five sites."""
    results = [r for r in results if r is not None]
    if not results:
        return None
    fig, ax = plt.subplots(2, 5, figsize=(17, 6), sharex=True)
    styles = ["k", "tab:red", "tab:blue", "tab:green"]
    for r, col in zip(results, styles):
        for j, name in enumerate(SITES):
            s = r["sites"][name]
            ax[0, j].plot(r["t"], s["U"], color=col, lw=2, label=label(r))
            ax[1, j].plot(r["t"], s["P"], color=col, lw=2, label=label(r))
    for j, name in enumerate(SITES):
        ax[0, j].set_title(name)
        ax[0, j].axhline(0, color="0.6", lw=0.6)
        ax[1, j].set_xlabel("Time (s)")
    ax[0, 0].set_ylabel("Blood speed (m/s)")
    ax[1, 0].set_ylabel("Pressure (mmHg)")
    ax[0, 0].legend(frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def tree_coordinates():
    """(x, y) of the start and end of every segment, in meters; the heart is at (0, 0).
    x points toward the tail, y up; the horse faces left."""
    par = net.parent_of()
    ends = {}

    def end(s):
        if s in ends:
            return ends[s]
        x0, y0 = (0.0, 0.0) if s == net.ROOT else end(par[s])[1]
        a = np.radians(net.SEGMENTS[s]["angle_deg"])
        L = net.SEGMENTS[s]["length_mm"] / 1000.0
        ends[s] = ((x0, y0), (x0 + L * np.cos(a), y0 + L * np.sin(a)))
        return ends[s]

    for s in net.SEGMENTS:
        end(s)
    return ends


def plot_tree(ax=None, show_sites=True):
    """The 117 arteries drawn from the paper's lengths and angles, with the five sites marked."""
    xy = tree_coordinates()
    segs = [[a, b] for a, b in xy.values()]
    widths = [0.8 + 7.0 * ((0.5 * (net.SEGMENTS[s]["d_prox_mm"] + net.SEGMENTS[s]["d_dist_mm"])) / 68.0) ** 0.7
              for s in xy]
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.add_collection(LineCollection(segs, colors="0.35", linewidths=widths, capstyle="round"))
    ax.set_xlim(-0.75, 1.3)
    ax.set_ylim(-0.95, 1.08)
    ax.set_aspect("equal")
    ax.set_xlabel("Toward the tail (m)")
    ax.set_ylabel("Height above the heart (m)")
    if show_sites:
        offsets = {"1": (0.2, -0.17, "left"), "87": (-0.1, 0.12, "center"), "49": (0.14, 0.05, "center"),
                   "26": (-0.05, -0.18, "center"), "93": (0.07, -0.2, "left")}
        for name, seg in SITES.items():
            (x0, y0), (x1, y1) = xy[seg]
            x, y = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
            ax.plot(x, y, "o", color="tab:red", ms=9, zorder=5)
            dx, dy, ha = offsets[seg]
            ax.annotate(name.replace(" (", "\n("), (x, y), (x + dx, y + dy), fontsize=9.5, color="tab:red",
                        arrowprops=dict(arrowstyle="-", color="tab:red", lw=0.8), ha=ha)
    ax.set_title("The horse's arteries in the model (horse facing left)")
    return ax


def plot_map(res, quantity="mean", ax=None, vmin=None, vmax=None, title=None, colorbar=True):
    """The arterial tree drawn from the paper's lengths and angles, colored by pressure.
    quantity: "mean", "systolic", or "pulse" (systolic minus diastolic)."""
    xy = tree_coordinates()
    segs, vals, widths = [], [], []
    for s, (a, b) in xy.items():
        mean, sys, dia = res["seg_P"][s]
        v = {"mean": mean, "systolic": sys, "pulse": sys - dia}[quantity]
        segs.append([a, b])
        vals.append(v)
        d = 0.5 * (net.SEGMENTS[s]["d_prox_mm"] + net.SEGMENTS[s]["d_dist_mm"])
        widths.append(0.8 + 7.0 * (d / 68.0) ** 0.7)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.5, 5.5))
    lc = LineCollection(segs, array=np.array(vals), cmap="viridis", linewidths=widths, capstyle="round")
    lc.set_clim(vmin if vmin is not None else min(vals), vmax if vmax is not None else max(vals))
    ax.add_collection(lc)
    ax.set_xlim(-0.75, 1.3)
    ax.set_ylim(-0.95, 1.08)
    ax.set_aspect("equal")
    ax.set_xlabel("Toward the tail (m)")
    ax.set_ylabel("Height above the heart (m)")
    ax.set_title(title or f"{quantity.capitalize()} pressure, {label(res)}")
    for txt, (x, y), ha in [("head", (-0.6, 0.98), "right"), ("heart", (0.06, -0.1), "left"),
                            ("front leg", (-0.1, -0.36), "right"), ("hind leg", (1.0, -0.5), "right"),
                            ("aorta", (0.5, 0.26), "center"), ("neck", (-0.36, 0.5), "right")]:
        ax.annotate(txt, (x, y), fontsize=9, color="0.25", ha=ha)
    if colorbar:
        plt.colorbar(lc, ax=ax, label={"mean": "Mean", "systolic": "Systolic", "pulse": "Pulse"}[quantity] + " pressure (mmHg)",
                     shrink=0.8)
    return ax


def plot_maps(*results, quantity="mean"):
    """Pressure maps side by side, on one color scale."""
    results = [r for r in results if r is not None]
    if not results:
        return None
    allv = []
    for r in results:
        for mean, sys, dia in r["seg_P"].values():
            allv.append({"mean": mean, "systolic": sys, "pulse": sys - dia}[quantity])
    fig, axs = plt.subplots(1, len(results), figsize=(6.4 * len(results) + 0.8, 5.4))
    axs = np.atleast_1d(axs)
    for r, a in zip(results, axs):
        plot_map(r, quantity, ax=a, vmin=min(allv), vmax=max(allv), colorbar=(a is axs[-1]))
    fig.tight_layout()
    return fig


def plot_aorta(*results):
    """Pressure along the aorta (distances from the heart) and the arrival time of the pulse."""
    results = [r for r in results if r is not None]
    if not results:
        return None
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.2))
    styles = ["k", "tab:red", "tab:blue", "tab:green"]
    for r, col in zip(results, styles):
        d = np.array(AORTA_CM)
        ax[0].plot(d, [r["aorta"][x].max() for x in AORTA_CM], "o-", color=col, label=f"systolic, {label(r)}")
        ax[0].plot(d, [r["aorta"][x].mean() for x in AORTA_CM], "s--", color=col, label=f"mean, {label(r)}")
        ax[1].plot([r["foot_times"][x] * 1000 for x in AORTA_CM], d, "o-", color=col,
                   label=f"{label(r)}: {r['pwv']:.1f} m/s")
    ax[0].set_xlabel("Distance from the heart along the aorta (cm)")
    ax[0].set_ylabel("Pressure (mmHg)")
    ax[0].legend(frameon=False, fontsize=8)
    ax[0].set_title("Pressure along the aorta")
    ax[1].set_xlabel("Time the pulse arrives (ms after the beat starts)")
    ax[1].set_ylabel("Distance from the heart (cm)")
    ax[1].set_title("Pulse wave speed = slope")
    ax[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    return fig
