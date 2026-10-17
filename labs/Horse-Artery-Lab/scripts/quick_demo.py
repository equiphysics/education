"""Run the horse arterial model once and plot pressure and flow at five arteries.

Examples:
    python scripts/quick_demo.py                       # resting horse, lying-down physics (no gravity)
    python scripts/quick_demo.py --gravity             # standing horse
    python scripts/quick_demo.py --stiffness 0.7       # arteries 30% less distensible (older horse)
    python scripts/quick_demo.py --hr 60 --gravity     # faster heart rate

The model has no reflexes (no baroreflex, no exercise response), so faster heart
rates and stiffer arteries show what the mechanics alone would do.
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from horse1d import analysis as an, network as net
from horse1d.model import HorseArteryModel
from horse1d.params import Params, MMHG


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gravity", action="store_true", help="standing horse (include gravity)")
    ap.add_argument("--hr", type=float, default=40.0, help="heart rate, beats per minute (paper: 40)")
    ap.add_argument("--stiffness", type=float, default=1.0,
                    help="multiply all distensibilities by this (below 1 = stiffer arteries)")
    ap.add_argument("--cycles", type=int, default=8)
    args = ap.parse_args()

    # Our assumption for other heart rates: systole shortens with the square root of the period.
    T_max = 0.478 * (40.0 / args.hr) ** 0.5
    p = Params(gravity=args.gravity, heart_rate_bpm=args.hr, T_max=T_max, E_min=0.0127,
               distensibility_scale=args.stiffness, n_cycles=args.cycles)
    m = HorseArteryModel(p)
    m.run()
    g = an.global_metrics(m)
    print(f"\nCardiac output {g['CO_L_min']:.1f} L/min, stroke volume {g['SV_ml']:.0f} ml, "
          f"aortic pressure {g['SBP']:.0f}/{g['DBP']:.0f} mmHg")

    fig, ax = plt.subplots(2, 5, figsize=(17, 6), sharex=True)
    for j, (name, seg) in enumerate(net.LOCATIONS.items()):
        i = m.node(seg)
        P = m.rec["P"][i]
        L = an.location_metrics(m, seg)
        ax[0, j].plot(m.rec["t"], m.rec["Q"][i] / an._area_at(m, i, P), "k", lw=2)
        ax[0, j].axhline(0, color="0.5", lw=0.5)
        ax[1, j].plot(m.rec["t"], P / MMHG, "k", lw=2)
        ax[0, j].set_title(f"{name}: {net.SEGMENTS[seg]['name']}", fontsize=9)
        ax[1, j].set_title(f"{L['SBP']:.0f}/{L['DBP']:.0f} mmHg", fontsize=9)
        ax[1, j].set_xlabel("Time (s)")
    ax[0, 0].set_ylabel("Blood velocity (m/s)")
    ax[1, 0].set_ylabel("Pressure (mmHg)")
    fig.suptitle(f"Horse arteries, {args.hr:.0f} bpm, {'standing (gravity)' if args.gravity else 'no gravity'}, "
                 f"stiffness factor {args.stiffness}")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
