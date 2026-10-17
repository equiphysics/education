import sys, numpy as np
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from horse1d.model import HorseArteryModel
from horse1d.params import Params, MMHG
from horse1d import analysis as an
fig, ax = plt.subplots(2, 3, figsize=(14, 6))
for k2, col in [(0.0, 'r'), (1.0, 'k'), (3.0, 'b')]:
    for dx in ([0.01, 0.005] if k2 == 1.0 else [0.01]):
        m = HorseArteryModel(Params(E_min=0.0127, shock_capturing=k2, dx_target=dx, n_cycles=9)); m.run(verbose=False)
        g = an.global_metrics(m); pwv, _ = an.aortic_pwv(m)
        s = f"k2={k2} dx={dx*1000:.0f}mm: BP {g['SBP']:.1f}/{g['DBP']:.1f} CO {g['CO_L_min']:.2f} PWV {pwv:.2f} |"
        for name, seg in [('DistAo','87'),('CCA','49'),('MA','26'),('EIA','93')]:
            L = an.location_metrics(m, seg); s += f" {name} U{L['peak_U']:.2f} SBP{L['SBP']:.0f} PP{L['PP']:.0f} tau{L['tau_max']:.1f}"
        print(s, flush=True)
        for j, seg in enumerate(['87', '93', '1']):
            i = m.node(seg); P = m.rec['P'][i]; U = m.rec['Q'][i]/an._area_at(m, i, P)
            ls = '-' if dx == 0.01 else ':'
            ax[0, j].plot(m.rec['t'], U, col, ls=ls, lw=1.2, label=f'k2={k2}, dx={dx*1000:.0f}mm'); ax[1, j].plot(m.rec['t'], P/MMHG, col, ls=ls, lw=1.2)
            ax[0, j].set_title(f'segment {seg}')
ax[0, 0].legend(fontsize=8); fig.tight_layout(); fig.savefig(str(Path(__file__).resolve().parents[2] / 'results' / 'damping_check.png'), dpi=110)
