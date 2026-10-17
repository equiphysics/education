# Horse Artery Lab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/equiphysics/education/blob/main/labs/Horse-Artery-Lab/Horse_Artery_Lab.ipynb)

A 75-minute computer lab on blood pressure and pressure waves in a horse, built around a Python version of a published model of the horse's arteries (Vera et al., 2019, *PLoS ONE*). Everything runs in Google Colab in a browser. There is nothing to install: **[open the notebook in Colab](https://colab.research.google.com/github/equiphysics/education/blob/main/labs/Horse-Artery-Lab/Horse_Artery_Lab.ipynb)**.

Students run a model of 117 arteries, from the heart to the head, the four legs, and the gut, with a beating heart at one end and 62 tissue beds at the other. They stand the horse up and watch gravity drain pressure from the head and pile it into the legs, check the model with ρgh, follow the pulse down the aorta at about 5 m/s, stiffen the arteries the way age does, speed up the heart, and finally hold the model up against measurements made in real horses.

**Audience and level:** college courses in math biology, biomechanics, physiology, biomedical engineering, or physics; advanced high school with support. Students need ρgh, unit conversion, and reading graphs. No coding: students move sliders and run cells.

## Files

| File | What it is |
|---|---|
| `Horse_Artery_Lab.ipynb` | The Colab notebook: the full model plus sliders for standing, heart rate, and artery stiffness |
| `Horse_Artery_Lab_Worksheet.docx` | Student worksheet (parts A to F), with a QR code that opens the notebook in Colab |
| `Horse_Artery_Lab_Teacher_Guide.docx` | Facilitator guide: timing, background primer, part-by-part notes, extensions, references, and the answer key |
| `Horse_Artery_Model_Overview.pdf` | Four-page summary of the model: equations, boundary conditions, numerical method, every parameter, and how it compares with the study |
| `figures/` | The figures in the worksheet and the guide, made by the notebook's own plotting code |
| `horse1d/` | The model as a Python package (the notebook's setup cell writes these same files) |
| `scripts/` | `quick_demo.py` (one run with plots), `compare_with_paper.py` (the validation runs), and grid and damping checks |
| `results/` | The validation against the study: `comparison.md`, `summary.json`, and figures |
| `MODEL.md` | Technical notes: how the model compares with the study, and every choice the article left to us |
| `build/` | Scripts that rebuild the answer numbers, figures, documents, and notebook, plus the overview's LaTeX source |

## The model

In every artery the model solves the one-dimensional equations for conservation of mass and momentum, with a wall that stiffens as pressure rises, Womersley friction at the wall, and gravity along each vessel. A time-varying elastance left ventricle drives the tree, and three-element Windkessels close its 62 ends. The anatomy (Table 1) and tissue-bed values (S1 Table) are the study's own data. The study's code is not public, so the numerical method is ours: an explicit MacCormack scheme with characteristic boundary conditions. Every choice the article leaves open is listed in the overview PDF and in `MODEL.md`.

One heart setting is calibrated: the diastolic elastance is 0.0127 mmHg/ml instead of the printed 0.01, so the heart fills to the volume implied by the study's stroke volume and ejection fraction. With that one change the model reproduces the study's resting horse:

| | Study, lying | Ours, lying | Study, standing | Ours, standing |
|---|---|---|---|---|
| Cardiac output (L/min) | 33 | 32.5 | 30 | 29.6 |
| Stroke volume (ml) | 820 | 812 | 740 | 740 |
| Aortic pressure (mmHg) | 114/70 | 114/72 | 131/88 | 131/90 |
| Aortic pulse wave speed (m/s) | 5.3 | 5.1 | 5.2 | 5.1 |

Like the study's model, ours overestimates pulse pressure compared with measurements in real horses, and some peak blood speeds differ from the study's by up to 30%. The teacher guide, the overview, and `results/comparison.md` give the details.

## Settings and limits

- **standing:** gravity on (a standing horse) or off (as if lying flat).
- **heart rate:** 35 to 80 beats per minute. Systole shortens with the square root of the heart period.
- **stiffness:** 0.7 to 1.5. Every artery's distensibility is divided by this number.

The model has no reflexes or autoregulation, so faster heart rates and stiffer arteries show the mechanics only. In a standing horse with a slow heart and stiff arteries (for example 35 beats per minute and stiffness 1.5), pressure in the head falls close to zero before the next beat, the head arteries go soft, the blood outruns the pressure wave, and the 1D equations fail. The notebook prints a plain explanation instead of an error. Each new horse takes about a minute in Colab; a horse that has already run comes back instantly.

## Running it

**In a browser:** click **Open in Colab** above, or scan the QR code on the worksheet, and run the Setup cell first. Colab warns that the notebook was not written by Google; click *Run anyway*. Running cells needs a Google account, and *File → Save a copy in Drive* keeps your own copy. The setup cell writes the model's Python files, so the notebook needs nothing else.

**On your own computer:** `pip install -r requirements.txt`, then `python scripts/quick_demo.py --gravity` for a standing horse, or open the notebook in Jupyter. One run of eight heartbeats takes about 30 seconds on a laptop.

## Rebuilding the kit

From this folder (the build scripts also need `python-docx`, `nbformat`, and `qrcode`):

```
python build/make_numbers_and_figures.py
python build/make_docs.py
python build/make_notebook.py
```

The first script runs the five cases the worksheet uses and saves `build/answer_numbers.json` and the figures. The second writes the worksheet and teacher guide from those numbers, so the answer key always matches the notebook. The third copies `horse1d/` into the notebook's setup cell; rerun it after any change to the model. To rebuild the overview, run `pdflatex Horse_Artery_Model_Overview.tex` twice inside `build/` and move the PDF up to this folder. (In EquiPhysics' working copy the lab sits in a `lesson/` folder next to `horse1d/`; the build scripts find the package either way.)

## Credit

Model and data: Vera L, Campos Arias D, Muylle S, Stergiopulos N, Segers P, van Loon G (2019). A 1D computer model of the arterial circulation in horses: an important resource for studying global interactions between heart and vessels under normal and pathological conditions. *PLoS ONE* 14(8): e0221425. https://doi.org/10.1371/journal.pone.0221425. The article and its supplementary data are open access under CC BY 4.0; please keep this credit if you adapt the lab.

Python version and lesson: EquiPhysics, a 501(c)(3) nonprofit in Sonoita, Arizona. Released under the MIT License; please credit EquiPhysics if you adapt it.

Used this lab with a class? Please tell us how it went: https://www.equiphysics.org/for-teachers#tell-us

## Help keep these lessons free

This lesson is free. If one helps you, you can [donate to EquiPhysics](https://www.equiphysics.org/donate). Can't give right now? You can still help a lot: share a lesson with another teacher, star this repository, and follow us on [GitHub](https://github.com/equiphysics), [Instagram](https://www.instagram.com/equiphysics_institute/), [Facebook](https://www.facebook.com/profile.php?id=61579151426160), and [LinkedIn](https://www.linkedin.com/company/equiphysics-institute/). Follows and shares help us show grant funders that people use and value this work. For news a few times a year, [sign up here](https://www.equiphysics.org/#news).
