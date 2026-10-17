# Horse arteries in 1D (Python): technical notes

A Python version of the equine arterial model in:

> Vera L, Campos Arias D, Muylle S, Stergiopulos N, Segers P, van Loon G (2019).
> A 1D computer model of the arterial circulation in horses: an important resource for studying global
> interactions between heart and vessels under normal and pathological conditions. *PLoS ONE* 14(8): e0221425.
> https://doi.org/10.1371/journal.pone.0221425 (CC BY 4.0)

The model follows blood pressure and flow through 117 arteries of a horse, from the
heart to the head, the four legs, and the gut, over each heartbeat. It uses the
paper's anatomy (Table 1), its terminal values (S1 Table), and its physics: a
beating left ventricle, elastic arteries whose stiffness changes with pressure,
Womersley wall friction, gravity, and 62 terminal vascular beds.

## Quick start

```
pip install numpy scipy matplotlib
python scripts/quick_demo.py               # resting horse, no gravity
python scripts/quick_demo.py --gravity     # standing horse
python scripts/compare_with_paper.py       # all comparison runs, about 4 minutes
```

One run of 10 heartbeats takes about 30 seconds on a laptop.

## Files

| File | What it holds |
|---|---|
| `horse1d/network.py` | The 117 segments (Table 1), which segment feeds which (Fig 1), body regions |
| `horse1d/s1_table.py` | Terminal resistance and compliance for the 62 terminal branches (S1 Table) |
| `horse1d/params.py` | Every parameter, marked as the paper's or ours |
| `horse1d/model.py` | The solver |
| `horse1d/womersley.py` | Womersley wall shear |
| `horse1d/analysis.py` | The numbers the paper reports, computed from a run |
| `horse1d/paper.py` | The paper's published numbers |
| `scripts/compare_with_paper.py` | Runs the paper's cases and writes `results/comparison.md` and figures |
| `scripts/quick_demo.py` | One run with plots; options for gravity, heart rate, stiffness |
| `scripts/checks/` | Grid and damping checks |

## How it compares with the paper

Full tables: [results/comparison.md](results/comparison.md). Figures: `results/fig3_waveforms.png`,
`fig5_aorta_pressures.png`, `fig6_wave_power.png`, `heart.png`.

With every parameter as printed, our model pumps too much blood (39.6 L/min instead of 33).
The paper's heart fills to about 1,260 ml, which follows from its stroke volume (820 ml) and
ejection fraction (65%), but its printed diastolic elastance (0.01 mmHg/ml) lets ours fill to
1,530 ml. Matching that one number (diastolic elastance 0.0127 mmHg/ml) gives:

| | Paper | Ours | Paper, gravity | Ours, gravity |
|---|---|---|---|---|
| Cardiac output (L/min) | 33 | 32.5 | 30 | 29.6 |
| Stroke volume (ml) | 820 | 812 | 740 | 740 |
| Aortic root pressure (mmHg) | 114/70 | 114/72 | 131/88 | 131/90 |
| Pulse pressure (mmHg) | 44 | 42 | 43 | 41 |
| Total vascular resistance (mmHg s/ml) | 0.17 | 0.18 | 0.22 | 0.23 |
| Aortic pulse wave velocity (m/s) | 5.3 | 5.1 | 5.2 | 5.1 |

Gravity is never tuned, so the right-hand columns are a real test. Also close to the paper:

* Reynolds numbers (mean flow) in the aorta, carotid, median and external iliac arteries: within 10%.
* Womersley numbers: within 6%.
* How gravity shifts blood flow: brain down, limbs, gut, kidneys and heart up (Table 2).
* Pressure amplification along the aorta: systolic pressure rises from about 120 to 145 mmHg
  between 26 and 86 cm from the heart (paper: 115 to 152) (Fig 5).
* The shape of every pressure and velocity waveform in Fig 3, with and without gravity.

Where we differ:

* Peak velocity is 17 to 32% higher in the distal aorta and external iliac artery, and 19% lower in
  the carotid. Pulse pressure in the limb arteries is 10 to 20% lower than in the paper's model.
* With gravity, our carotid mean pressure is 77 mmHg; the paper's is 64.
* Peak wall shear stress depends on how many flow harmonics you keep: 2 to 6 Pa with 5, and 4 to
  12 Pa with 30, against the paper's 1.5 to 3. The paper does not say how many it used.

Like the paper's model, ours gives larger pulse pressures than were measured in horses (24 to 33
mmHg). The paper discusses why: anaesthesia, posture, and unknown equine wall stiffness.

## What we had to choose

The paper refers to a MATLAB code that is not public, so some details are ours:

* **Branching** (which segment feeds which) is read from Fig 1 and equine anatomy. It gives exactly
  117 segments and 62 terminals, as in the paper.
* **The four added terminal segments** (58b, 69b, 99b, 112b) are 5 cm long, as the paper's
  footnote says; Table 1 prints "5" in its mm column.
* **S1 Table typo:** it lists "79b"; we read it as 69b.
* **Terminal Windkessels:** R1 = Zc as in the paper. In nine small head branches Zc is larger than
  the total resistance in S1, so there we use R1 = total resistance and R2 = 0.
* **Heart:** the paper's time-varying elastance with internal resistance. The normalized elastance
  curve is the double-Hill fit to Senzaki et al., stretched to peak at 478 ms (the paper's systolic
  duration). Diastolic elastance 0.0127 mmHg/ml (see above).
* **Coronary arteries** are plain Windkessels; the paper squeezes them with the heart muscle.
* **Womersley friction** uses the previous beat's flow, as in the paper, plus a correction
  for the change since then, so it settles to exactly the paper's formula. 30 harmonics.
* **Numerics:** explicit MacCormack with characteristic boundary conditions (the paper used an
  implicit scheme), plus a small shock-capturing damping because the pulse front steepens along
  the aorta. Results change by 1 to 2% when the grid spacing is halved.

## Using it for teaching

See [README.md](README.md): the Horse Artery Lab, with a Colab notebook with sliders, a student worksheet, a
teacher guide with the answer key, and a four-page overview of the model.

## License

Code: MIT License, EquiPhysics 2026 (see the repository's [LICENSE](../../LICENSE)). The anatomical and terminal data come from Vera et al. (2019), CC BY 4.0:
credit the paper when you use them.
