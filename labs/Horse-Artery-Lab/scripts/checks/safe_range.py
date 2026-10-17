"""Which slider settings run cleanly? Standing horses at slow heart rates or with very stiff arteries
push head pressure toward zero, where the 1D model breaks down."""
import sys, warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def one(args):
    warnings.filterwarnings("ignore")
    st, hr, k = args
    from horse1d import lab
    try:
        r = lab.run_horse(st, hr, k, verbose=False)
        low = min(v[2] for v in r["seg_P"].values())
        return args, f"ok   lowest P {low:5.1f} mmHg  BP {r['glob']['SBP']:.0f}/{r['glob']['DBP']:.0f}"
    except Exception as e:
        return args, "FAIL " + str(e)[:60]

if __name__ == "__main__":
    jobs = [(True, hr, k) for hr in (32, 35, 38, 40, 45, 50, 60, 80) for k in (0.7, 1.0, 1.25, 1.5, 1.75, 2.0)]
    jobs += [(False, hr, k) for hr in (30, 80) for k in (0.7, 2.0)]
    with ProcessPoolExecutor(max_workers=20) as ex:
        for args, res in sorted(ex.map(one, jobs)):
            print(f"{'standing' if args[0] else 'lying':8s} {args[1]:3.0f} bpm stiffness {args[2]:4.2f}: {res}", flush=True)
