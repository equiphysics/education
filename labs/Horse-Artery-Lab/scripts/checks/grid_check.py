"""Grid check: the calibrated model at three grid spacings should give the same answers."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from horse1d.model import HorseArteryModel
from horse1d.params import Params
from horse1d import analysis as an

for dx in [0.02, 0.01, 0.005]:
    t0 = time.time()
    m = HorseArteryModel(Params(E_min=0.0127, dx_target=dx, n_cycles=9)); m.run(verbose=False)
    g = an.global_metrics(m)
    s = (f"dx {dx*1000:4.0f} mm, {m.n_nodes:5d} nodes, dt {m.dt*1e3:.3f} ms, {time.time()-t0:3.0f} s: "
         f"CO {g['CO_L_min']:.2f} L/min, root BP {g['SBP']:.1f}/{g['DBP']:.1f} |")
    for name, seg in [('DistAo', '87'), ('CCA', '49'), ('MA', '26'), ('EIA', '93')]:
        L = an.location_metrics(m, seg)
        s += f" {name} U {L['peak_U']:.2f} SBP {L['SBP']:.0f}"
    pwv, _ = an.aortic_pwv(m)
    print(s, f"| PWV {pwv:.2f}", flush=True)
