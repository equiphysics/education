# Python model vs Vera et al. (2019)

All runs use the paper's anatomy (Table 1) and terminal values (S1 Table). **Printed** = every parameter as printed. **Calibrated** = one unstated detail matched to the paper's own numbers: diastolic elastance 0.0127 instead of 0.01 mmHg/ml, which gives the end-diastolic volume of about 1,260 ml implied by its stroke volume (820 ml) and ejection fraction (65%). Gravity is never tuned, so every with-gravity number is a test.

## Whole-body numbers

| | Paper | Ours, printed | Ours, calibrated | Paper, gravity | Ours, printed, gravity | Ours, calibrated, gravity |
|---|---|---|---|---|---|---|
| Cardiac output (L/min) | 33 | 39.6 | 32.5 | 30 | 36.9 | 29.6 |
| Stroke volume (ml) | 820 | 990 | 812 | 740 | 924 | 740 |
| Ejection fraction (%) | 65 | 65 | 66 | 59 | 60 | 60 |
| Aortic root systolic (mmHg) | 114 | 143 | 114 | 131 | 160 | 131 |
| Aortic root diastolic (mmHg) | 70 | 85 | 72 | 88 | 104 | 90 |
| Mean arterial pressure (mmHg) | 93 | 118 | 96 | 111 | 136 | 114 |
| Pulse pressure (mmHg) | 44 | 57 | 42 | 43 | 56 | 41 |
| Total vascular resistance (mmHg s/ml) | 0.17 | 0.18 | 0.18 | 0.22 | 0.22 | 0.23 |
| Aortic pulse wave velocity (m/s) | 5.3 | 5.52 | 5.12 | 5.2 | 5.47 | 5.12 |

Measured in a horse: aortic pulse wave velocity 5.27 m/s.

## Share of cardiac output (%), Table 2 (calibrated)

The paper does not say which branches it counted in each region; our grouping is in `horse1d/network.py` (brain = internal carotids and vertebrals).

| Region | Paper, no gravity | Ours, no gravity | Paper, gravity | Ours, gravity | Literature |
|---|---|---|---|---|---|
| heart | 4.2 | 4.9 | 5.4 | 6.3 | 5 |
| brain | 15.4 | 13.8 | 10.5 | 9.4 | 10 |
| muscle | 7.7 | 6.8 | 11.3 | 10.1 | 15 |
| kidney | 18.2 | 18.6 | 20.7 | 21.2 | 20 |
| splanchnic | 28.3 | 30.3 | 32.6 | 34.5 | 30 |
| other | 26.2 | 25.5 | 19.5 | 18.5 | 20 |

## Local pressures and peak velocities, Table 4 (without gravity, calibrated)

| | Prox Ao paper | Prox Ao ours | Dist Ao paper | Dist Ao ours | CCA paper | CCA ours | MA paper | MA ours | EIA paper | EIA ours |
|---|---|---|---|---|---|---|---|---|---|---|
| Peak velocity (m/s) | 0.95 | 0.97 | 0.83 | 1.10 | 1.54 | 1.26 | 0.46 | 0.44 | 0.64 | 0.75 |
| Mean pressure (mmHg) | 93 | 96 | 95 | 96 | 89 | 94 | 94 | 96 | 95 | 96 |
| Systolic (mmHg) | 114 | 114 | 161 | 149 | 145 | 131 | 161 | 146 | 175 | 159 |
| Diastolic (mmHg) | 70 | 72 | 67 | 66 | 61 | 67 | 68 | 68 | 66 | 66 |
| Pulse pressure (mmHg) | 44 | 42 | 94 | 83 | 84 | 64 | 93 | 78 | 109 | 93 |

## Local pressures and peak velocities, Table 4 (with gravity, calibrated)

| | Prox Ao paper | Prox Ao ours | Dist Ao paper | Dist Ao ours | CCA paper | CCA ours | MA paper | MA ours | EIA paper | EIA ours |
|---|---|---|---|---|---|---|---|---|---|---|
| Peak velocity (m/s) | 0.73 | 0.77 | 0.77 | 0.95 | 1.25 | 0.94 | 0.40 | 0.32 | 0.56 | 0.64 |
| Mean pressure (mmHg) | 111 | 114 | 96 | 98 | 64 | 77 | 132 | 134 | 106 | 110 |
| Systolic (mmHg) | 131 | 131 | 160 | 148 | 103 | 108 | 190 | 177 | 176 | 164 |
| Diastolic (mmHg) | 88 | 90 | 69 | 70 | 45 | 52 | 104 | 107 | 79 | 81 |
| Pulse pressure (mmHg) | 43 | 41 | 90 | 78 | 59 | 56 | 86 | 69 | 97 | 83 |

## Measured in horses (Table 4, in vivo) vs our model

Velocities and carotid pressures: standing horses (mean of 5). Aortic pressures: one anaesthetized horse lying on its back, so compare with care.

| | Prox Ao | Dist Ao | CCA | MA | EIA |
|---|---|---|---|---|---|
| Peak velocity (m/s), measured | 0.74 | NA | 0.85 | 0.40 | 0.46 |
| Peak velocity (m/s), ours with gravity | 0.77 | 0.95 | 0.94 | 0.32 | 0.64 |
| Mean pressure (mmHg), measured | 104 | 120 | 117 | NA | NA |
| Mean pressure (mmHg), ours with gravity | 114 | 98 | 77 | 134 | 110 |
| Systolic (mmHg), measured | 117 | 134 | 135 | NA | NA |
| Systolic (mmHg), ours with gravity | 131 | 148 | 108 | 177 | 164 |
| Diastolic (mmHg), measured | 92 | 110 | 102 | NA | NA |
| Diastolic (mmHg), ours with gravity | 90 | 70 | 52 | 107 | 81 |
| Pulse pressure (mmHg), measured | 24 | 24 | 33 | NA | NA |
| Pulse pressure (mmHg), ours with gravity | 41 | 78 | 56 | 69 | 83 |

## Womersley number, wall shear, Reynolds number, Table 3 (calibrated)

| | Prox Ao | Dist Ao | CCA | MA | EIA |
|---|---|---|---|---|---|
| Womersley number, paper | 35.47 | 15.05 | 6.02 | 3.78 | 8.02 |
| Womersley number, ours | 35.54 | 15.05 | 6.25 | 4.01 | 8.02 |
| Reynolds number, paper, no gravity | 2660 | 749 | 2312 | 68 | 195 |
| Reynolds number, ours, no gravity | 2531 | 672 | 2219 | 63 | 187 |
| Peak wall shear (Pa), paper, no gravity | 3.05 | 3.11 | 2.09 | 1.79 | 1.70 |
| Peak wall shear (Pa), ours, 30 harmonics, no gravity | 7.03 | 12.16 | 9.95 | 5.84 | 9.30 |
| Peak wall shear (Pa), ours, 5 harmonics, no gravity | 4.91 | 3.87 | 6.26 | 1.92 | 2.76 |
| Reynolds number, paper, gravity | 2404 | 870 | 1160 | 98 | 278 |
| Reynolds number, ours, gravity | 2209 | 818 | 1076 | 90 | 276 |
| Peak wall shear (Pa), paper, gravity | 2.72 | 2.89 | 2.28 | 1.74 | 1.50 |
| Peak wall shear (Pa), ours, 30 harmonics, gravity | 6.24 | 10.39 | 7.58 | 4.12 | 7.74 |
| Peak wall shear (Pa), ours, 5 harmonics, gravity | 4.32 | 3.48 | 5.30 | 1.68 | 2.46 |

Peak wall shear grows with the number of flow harmonics kept (the Womersley boundary layer thins as frequency rises). The paper does not state its count. Pressures and flows change by 5% or less between 5 and 30 harmonics.

## Why the S1 Table matters (no gravity, calibrated heart)

Terminal values estimated by the paper's described method (total parallel resistance 0.14 mmHg s/ml split by region and Murray's law) instead of the S1 Table:

| | Prox Ao | Dist Ao | CCA | MA | EIA | CO (L/min) | Root BP (mmHg) |
|---|---|---|---|---|---|---|---|
| Reynolds number, paper | 2660 | 749 | 2312 | 68 | 195 | 33 | 114/70 |
| Reynolds number, ours with S1 | 2531 | 672 | 2219 | 63 | 187 | 32.5 | 114/72 |
| Reynolds number, ours estimated | 2804 | 1730 | 323 | 16 | 88 | 34.8 | 101/60 |

## Womersley vs Poiseuille wall friction (calibrated, no gravity)

| | Prox Ao | Dist Ao | CCA | MA | EIA |
|---|---|---|---|---|---|
| Peak velocity, Womersley (m/s) | 0.97 | 1.10 | 1.26 | 0.44 | 0.75 |
| Peak velocity, Poiseuille (m/s) | 0.98 | 1.18 | 1.33 | 0.47 | 0.81 |
| Pulse pressure, Womersley (mmHg) | 42 | 83 | 64 | 78 | 93 |
| Pulse pressure, Poiseuille (mmHg) | 42 | 84 | 69 | 79 | 96 |
