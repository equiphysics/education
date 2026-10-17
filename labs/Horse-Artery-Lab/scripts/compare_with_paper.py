"""Run the horse model and compare it with Vera et al. (2019), PLoS ONE 14(8): e0221425.

Cases (all use the paper's Table 1 anatomy and S1 terminal values):
  printed    - every parameter as printed in the paper
  calibrated - one unstated detail matched to the paper's own numbers: the diastolic
               elastance (0.0127 instead of 0.01 mmHg/ml), which sets the end-diastolic
               volume (about 1,260 ml, implied by the paper's SV 820 ml and EF 65%)
Each runs with and without gravity. Two side checks: terminal values estimated by
the paper's method instead of S1, and Poiseuille instead of Womersley friction.
Writes results/comparison.md, results/summary.json, and figures.
"""
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from horse1d import analysis as an, network as net, paper
from horse1d.model import HorseArteryModel
from horse1d.params import Params, MMHG, ML
from horse1d.womersley import wall_shear_from_flow

OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
CALIB = dict(E_min=0.0127)
LOC = paper.LOCATION_ORDER


def run_case(label, **kw):
    m = HorseArteryModel(Params(n_cycles=10, **kw))
    t0 = time.time()
    m.run(verbose=False)
    print(f"{label}: {time.time() - t0:.0f} s", flush=True)
    return m


def summarize(m):
    loc = {name: an.location_metrics(m, seg) for name, seg in net.LOCATIONS.items()}
    for name, seg in net.LOCATIONS.items():   # peak wall shear with only 5 harmonics, for Table 3
        i = m.node(seg)
        tau5 = wall_shear_from_flow(m.rec["Q"][i], m.Rref[i], m.p.T, m.p.rho, m.p.mu, 5)
        loc[name]["tau_max_5h"] = np.abs(tau5).max() if m.wom[i] else loc[name]["tau_max"]
    pwv, _ = an.aortic_pwv(m)
    return dict(global_=an.global_metrics(m), co=an.co_distribution(m), loc=loc, pwv=pwv)


def fmt(v, nd):
    return "NA" if v is None else f"{v:.{nd}f}"


def main():
    M = {
        ("printed", False): run_case("printed, no gravity"),
        ("printed", True): run_case("printed, gravity", gravity=True),
        ("calibrated", False): run_case("calibrated, no gravity", **CALIB),
        ("calibrated", True): run_case("calibrated, gravity", gravity=True, **CALIB),
    }
    est = run_case("estimated terminals, no gravity", terminals="estimated", **CALIB)
    pois = run_case("Poiseuille friction, no gravity", friction="poiseuille", **CALIB)
    S = {k: summarize(m) for k, m in M.items()}
    Se, Sp = summarize(est), summarize(pois)
    C0, C1 = S[("calibrated", False)], S[("calibrated", True)]

    md = ["# Python model vs Vera et al. (2019)\n",
          "All runs use the paper's anatomy (Table 1) and terminal values (S1 Table). "
          "**Printed** = every parameter as printed. **Calibrated** = one unstated detail matched to the "
          "paper's own numbers: diastolic elastance 0.0127 instead of 0.01 mmHg/ml, which gives the "
          "end-diastolic volume of about 1,260 ml implied by its stroke volume (820 ml) and ejection "
          "fraction (65%). Gravity is never tuned, so every with-gravity number is a test.\n"]

    md.append("## Whole-body numbers\n")
    md.append("| | Paper | Ours, printed | Ours, calibrated | Paper, gravity | Ours, printed, gravity | Ours, calibrated, gravity |")
    md.append("|---|---|---|---|---|---|---|")
    rows = [("Cardiac output (L/min)", "CO_L_min", 1), ("Stroke volume (ml)", "SV_ml", 0),
            ("Ejection fraction (%)", "EF_pct", 0), ("Aortic root systolic (mmHg)", "SBP", 0),
            ("Aortic root diastolic (mmHg)", "DBP", 0), ("Mean arterial pressure (mmHg)", "MAP", 0),
            ("Pulse pressure (mmHg)", "PP", 0), ("Total vascular resistance (mmHg s/ml)", "TVR", 2)]
    for label, key, nd in rows:
        md.append(f"| {label} | {paper.GLOBAL['no_gravity'][key]} | {fmt(S[('printed', False)]['global_'][key], nd)} | "
                  f"{fmt(C0['global_'][key], nd)} | {paper.GLOBAL['gravity'][key]} | "
                  f"{fmt(S[('printed', True)]['global_'][key], nd)} | {fmt(C1['global_'][key], nd)} |")
    md.append(f"| Aortic pulse wave velocity (m/s) | {paper.PWV['no_gravity']} | {S[('printed', False)]['pwv']:.2f} | "
              f"{C0['pwv']:.2f} | {paper.PWV['gravity']} | {S[('printed', True)]['pwv']:.2f} | {C1['pwv']:.2f} |")
    md.append(f"\nMeasured in a horse: aortic pulse wave velocity {paper.PWV['in_vivo']} m/s.\n")

    md.append("## Share of cardiac output (%), Table 2 (calibrated)\n")
    md.append("The paper does not say which branches it counted in each region; our grouping is in "
              "`horse1d/network.py` (brain = internal carotids and vertebrals).\n")
    md.append("| Region | Paper, no gravity | Ours, no gravity | Paper, gravity | Ours, gravity | Literature |")
    md.append("|---|---|---|---|---|---|")
    for r in paper.CO_DISTRIBUTION["no_gravity"]:
        md.append(f"| {r} | {paper.CO_DISTRIBUTION['no_gravity'][r]} | {C0['co'][r]:.1f} | "
                  f"{paper.CO_DISTRIBUTION['gravity'][r]} | {C1['co'][r]:.1f} | {paper.CO_DISTRIBUTION['reference'][r]} |")

    for grav, Sx in ((False, C0), (True, C1)):
        key = "gravity" if grav else "no_gravity"
        md.append(f"\n## Local pressures and peak velocities, Table 4 ({'with' if grav else 'without'} gravity, calibrated)\n")
        md.append("| | " + " | ".join(f"{l} paper | {l} ours" for l in LOC) + " |")
        md.append("|---|" + "---|---|" * len(LOC))
        for label, k, nd in [("Peak velocity (m/s)", "peak_U", 2), ("Mean pressure (mmHg)", "MAP", 0),
                             ("Systolic (mmHg)", "SBP", 0), ("Diastolic (mmHg)", "DBP", 0),
                             ("Pulse pressure (mmHg)", "PP", 0)]:
            cells = [f"{paper.TABLE4[k][key][n]:.{nd}f} | {Sx['loc'][l][k]:.{nd}f}" for n, l in enumerate(LOC)]
            md.append(f"| {label} | " + " | ".join(cells) + " |")
    md.append("\n## Measured in horses (Table 4, in vivo) vs our model\n")
    md.append("Velocities and carotid pressures: standing horses (mean of 5). Aortic pressures: one "
              "anaesthetized horse lying on its back, so compare with care.\n")
    md.append("| | " + " | ".join(LOC) + " |")
    md.append("|---|" + "---|" * len(LOC))
    for label, k, nd in [("Peak velocity (m/s)", "peak_U", 2), ("Mean pressure (mmHg)", "MAP", 0),
                         ("Systolic (mmHg)", "SBP", 0), ("Diastolic (mmHg)", "DBP", 0), ("Pulse pressure (mmHg)", "PP", 0)]:
        md.append(f"| {label}, measured | " + " | ".join(fmt(v, nd) for v in paper.TABLE4[k]["in_vivo"]) + " |")
        md.append(f"| {label}, ours with gravity | " + " | ".join(fmt(C1['loc'][l][k], nd) for l in LOC) + " |")

    md.append("\n## Womersley number, wall shear, Reynolds number, Table 3 (calibrated)\n")
    md.append("| | " + " | ".join(LOC) + " |")
    md.append("|---|" + "---|" * len(LOC))
    md.append("| Womersley number, paper | " + " | ".join(f"{v:.2f}" for v in paper.TABLE3["alpha"]) + " |")
    md.append("| Womersley number, ours | " + " | ".join(f"{C0['loc'][l]['alpha']:.2f}" for l in LOC) + " |")
    for grav, Sx in ((False, C0), (True, C1)):
        key = "gravity" if grav else "no_gravity"
        g = "gravity" if grav else "no gravity"
        md.append(f"| Reynolds number, paper, {g} | " + " | ".join(f"{v:.0f}" for v in paper.TABLE3["Re"][key]) + " |")
        md.append(f"| Reynolds number, ours, {g} | " + " | ".join(f"{Sx['loc'][l]['Re']:.0f}" for l in LOC) + " |")
        md.append(f"| Peak wall shear (Pa), paper, {g} | " + " | ".join(f"{v:.2f}" for v in paper.TABLE3["tau_max"][key]) + " |")
        md.append(f"| Peak wall shear (Pa), ours, 30 harmonics, {g} | " + " | ".join(f"{Sx['loc'][l]['tau_max']:.2f}" for l in LOC) + " |")
        md.append(f"| Peak wall shear (Pa), ours, 5 harmonics, {g} | " + " | ".join(f"{Sx['loc'][l]['tau_max_5h']:.2f}" for l in LOC) + " |")
    md.append("\nPeak wall shear grows with the number of flow harmonics kept (the Womersley boundary layer "
              "thins as frequency rises). The paper does not state its count. Pressures and flows change "
              "by 5% or less between 5 and 30 harmonics.\n")

    md.append("## Why the S1 Table matters (no gravity, calibrated heart)\n")
    md.append("Terminal values estimated by the paper's described method (total parallel resistance 0.14 "
              "mmHg s/ml split by region and Murray's law) instead of the S1 Table:\n")
    md.append("| | " + " | ".join(LOC) + " | CO (L/min) | Root BP (mmHg) |")
    md.append("|---|" + "---|" * (len(LOC) + 2))
    for label, Sx in (("Reynolds number, paper", None), ("Reynolds number, ours with S1", C0), ("Reynolds number, ours estimated", Se)):
        if Sx is None:
            md.append(f"| {label} | " + " | ".join(f"{v:.0f}" for v in paper.TABLE3['Re']['no_gravity']) +
                      f" | {paper.GLOBAL['no_gravity']['CO_L_min']} | {paper.GLOBAL['no_gravity']['SBP']}/{paper.GLOBAL['no_gravity']['DBP']} |")
        else:
            md.append(f"| {label} | " + " | ".join(f"{Sx['loc'][l]['Re']:.0f}" for l in LOC) +
                      f" | {Sx['global_']['CO_L_min']:.1f} | {Sx['global_']['SBP']:.0f}/{Sx['global_']['DBP']:.0f} |")

    md.append("\n## Womersley vs Poiseuille wall friction (calibrated, no gravity)\n")
    md.append("| | " + " | ".join(LOC) + " |")
    md.append("|---|" + "---|" * len(LOC))
    for label, k, nd, src in [("Peak velocity, Womersley (m/s)", "peak_U", 2, C0), ("Peak velocity, Poiseuille (m/s)", "peak_U", 2, Sp),
                              ("Pulse pressure, Womersley (mmHg)", "PP", 0, C0), ("Pulse pressure, Poiseuille (mmHg)", "PP", 0, Sp)]:
        md.append(f"| {label} | " + " | ".join(f"{src['loc'][l][k]:.{nd}f}" for l in LOC) + " |")

    (OUT / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    json.dump({f"{c}_{'gravity' if g else 'no_gravity'}": {"global": S[(c, g)]["global_"], "co": S[(c, g)]["co"],
                                                           "pwv": S[(c, g)]["pwv"], "loc": S[(c, g)]["loc"]}
               for (c, g) in S}, open(OUT / "summary.json", "w"), indent=1, default=float)
    make_figures(M[("calibrated", False)], M[("calibrated", True)])
    print("wrote", OUT / "comparison.md")


def make_figures(m0, m1):
    lines = [(m1, "0.6", "with gravity"), (m0, "k", "without gravity")]
    # Fig 3: pressure and velocity at five sites
    fig, ax = plt.subplots(2, 5, figsize=(17, 6), sharex=True)
    for j, (name, seg) in enumerate(net.LOCATIONS.items()):
        for m, col, lab in lines:
            i = m.node(seg)
            P = m.rec["P"][i]
            ax[0, j].plot(m.rec["t"], m.rec["Q"][i] / an._area_at(m, i, P), color=col, lw=2, label=lab)
            ax[1, j].plot(m.rec["t"], P / MMHG, color=col, lw=2, label=lab)
        ax[0, j].set_title(f"{name} (segment {seg})")
        ax[0, j].axhline(0, color="k", lw=0.5)
        ax[1, j].set_xlabel("Time (s)")
    ax[0, 0].set_ylabel("Flow velocity (m/s)")
    ax[1, 0].set_ylabel("Pressure (mmHg)")
    ax[0, 1].legend(frameon=False)
    fig.suptitle("Python model: compare with Fig 3 of Vera et al. (2019)")
    fig.tight_layout()
    fig.savefig(OUT / "fig3_waveforms.png", dpi=130)

    # Fig 5: pressure along the aorta
    fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    styles = ["-", "--", (0, (5, 1)), "-.", "-", ":", "-"]
    greys = ["k", "k", "k", "0.4", "0.4", "0.4", "0.6"]
    for a, m, title in [(ax[0], m1, "Model with gravity"), (ax[1], m0, "Model without gravity")]:
        for (dcm, P), ls, col in zip(an.aorta_pressures(m).items(), styles, greys):
            a.plot(m.rec["t"], P, ls=ls, color=col, lw=1.8, label=f"{dcm} cm")
        a.set_title(title)
        a.set_xlabel("Time (s)")
        a.set_ylim(70, 160)
    ax[0].set_ylabel("Pressure (mmHg)")
    ax[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Pressure along the aorta (distance from the aortic root): compare with Fig 5")
    fig.tight_layout()
    fig.savefig(OUT / "fig5_aorta_pressures.png", dpi=130)

    # Heart
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for m, col, lab in lines:
        ax[0].plot(m.rec["V"] / ML, m.rec["Plv"] / MMHG, color=col, lw=2, label=lab)
        ax[1].plot(m.rec["t"], m.rec["Qroot"] / ML, color=col, lw=2, label=lab)
    ax[0].set_xlabel("Left ventricle volume (ml)")
    ax[0].set_ylabel("Left ventricle pressure (mmHg)")
    ax[0].set_title("Pressure-volume loop")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Flow into the aorta (ml/s)")
    ax[1].set_title("Ejection")
    ax[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "heart.png", dpi=130)

    # Fig 6: wave power
    fig, ax = plt.subplots(1, 4, figsize=(16, 3.5))
    for j, (name, seg) in enumerate([("Prox Ao", "1"), ("CCA", "49"), ("MA", "26"), ("EIA", "93")]):
        for m, col, lab in lines:
            t, fwd, bwd = an.wave_power(m, seg)
            ax[j].plot(t, fwd, color=col, lw=1.6, label=lab)
            ax[j].plot(t, bwd, color=col, lw=1.6, ls="--")
        ax[j].set_title(name)
        ax[j].set_xlabel("Time (s)")
    ax[0].set_ylabel("Wave power per time step (W)")
    ax[0].legend(frameon=False)
    fig.suptitle("Forward (solid) and backward (dashed) wave power: compare with Fig 6")
    fig.tight_layout()
    fig.savefig(OUT / "fig6_wave_power.png", dpi=130)


if __name__ == "__main__":
    main()
