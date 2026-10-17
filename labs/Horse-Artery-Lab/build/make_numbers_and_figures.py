"""Run every scenario the worksheet uses; save the answer-key numbers and the kit's figures."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KIT = Path(__file__).resolve().parents[1]  # the lab folder
PKG_ROOT = KIT if (KIT / "horse1d").is_dir() else KIT.parent  # horse1d/ is inside the lab folder or next to it
sys.path.insert(0, str(PKG_ROOT))
from horse1d import lab  # noqa: E402

FIG = KIT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
CASES = {"lying": (False, 40, 1.0), "standing": (True, 40, 1.0), "lying_stiff": (False, 40, 1.5),
         "lying_hr60": (False, 60, 1.0), "standing_hr60": (True, 60, 1.0)}

runs = {k: lab.run_horse(*v) for k, v in CASES.items()}
xy = lab.tree_coordinates()
out = {}
for k, r in runs.items():
    out[k] = dict(settings=r["settings"], glob=r["glob"], co=r["co"], pwv=r["pwv"],
                  foot_times=r["foot_times"],
                  aorta={str(d): dict(sys=float(P.max()), mean=float(P.mean()), dia=float(P.min()))
                         for d, P in r["aorta"].items()},
                  sites={n: {key: float(s[key]) for key in ("SBP", "DBP", "MAP", "PP", "peak_U", "height_m")} |
                         {"min_U": float(s["U"].min())} for n, s in r["sites"].items()})
out["heights"] = {n: 0.5 * (xy[s][0][1] + xy[s][1][1]) for n, s in lab.SITES.items()}
json.dump(out, open(KIT / "build" / "answer_numbers.json", "w"), indent=1, default=float)

# Figures for the worksheet, teacher guide, and overview
ax = lab.plot_tree()
ax.figure.set_size_inches(7.2, 6.0)
ax.figure.tight_layout()
ax.figure.savefig(FIG / "fig_arteries_sites.png", dpi=170)
plt.close("all")

fig = lab.plot_maps(runs["lying"], runs["standing"], quantity="mean")
fig.savefig(FIG / "fig_map_mean_lying_standing.png", dpi=150)
fig = lab.plot_maps(runs["lying"], runs["standing"], quantity="pulse")
fig.savefig(FIG / "fig_map_pulse_lying_standing.png", dpi=150)
fig = lab.plot_sites(runs["lying"], runs["standing"])
fig.savefig(FIG / "fig_sites_lying_standing.png", dpi=140)
fig = lab.plot_aorta(runs["lying"], runs["standing"])
fig.savefig(FIG / "fig_aorta_lying_standing.png", dpi=140)
fig = lab.plot_sites(runs["lying"], runs["lying_stiff"])
fig.savefig(FIG / "fig_sites_stiffness.png", dpi=140)
plt.close("all")
print("saved numbers and figures")
for k, r in runs.items():
    g = r["glob"]
    print(f"{k:14s} CO {g['CO_L_min']:.1f} SV {g['SV_ml']:.0f} EDV {g['EDV_ml']:.0f} BP {g['SBP']:.0f}/{g['DBP']:.0f} "
          f"PP {g['PP']:.0f} PWV {r['pwv']:.2f} brain {r['co']['brain']:.1f} limbs {r['co']['muscle']:.1f}")
