"""Build Horse_Artery_Lab.ipynb. The model code is copied into the setup cell, so the
notebook runs on its own in Google Colab or Jupyter. Rerun this after changing horse1d/."""
from pathlib import Path

import nbformat as nbf

KIT = Path(__file__).resolve().parents[1]  # the lab folder
PKG_ROOT = KIT if (KIT / "horse1d").is_dir() else KIT.parent  # horse1d/ is inside the lab folder or next to it
PKG = PKG_ROOT / "horse1d"
OUT = KIT / "Horse_Artery_Lab.ipynb"
FILES = ["__init__.py", "network.py", "s1_table.py", "params.py", "womersley.py",
         "model.py", "analysis.py", "paper.py", "lab.py"]


def setup_cell():
    lines = ['#@title Setup: run this cell first (it builds the horse model) { display-mode: "form" }',
             "# The model code (package horse1d) is written to files here, then imported.",
             "import os",
             "os.makedirs('horse1d', exist_ok=True)",
             "FILES = {}"]
    for f in FILES:
        src = (PKG / f).read_text(encoding="utf-8")
        assert "'''" not in src and not src.endswith("\\"), f
        lines.append(f"FILES['horse1d/{f}'] = r'''{src}'''")
    lines += ["for path, text in FILES.items():",
              "    with open(path, 'w', encoding='utf-8') as fh:",
              "        fh.write(text)",
              "import importlib, sys",
              "for name in [m for m in sys.modules if m.startswith('horse1d')]:",
              "    del sys.modules[name]",
              "import matplotlib.pyplot as plt",
              "from horse1d import lab",
              "plt.rcParams.update({'figure.dpi': 100, 'font.size': 11})",
              "print('Ready: 117 arteries, 62 tissue beds, one beating heart.')"]
    return "\n".join(lines)


md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell

cells = [
    md("""[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/equiphysics/education/blob/main/labs/Horse-Artery-Lab/Horse_Artery_Lab.ipynb)

# Horse Artery Lab
### Blood pressure from heart to hoof, in a computer horse

This notebook runs a computer model of a horse's arteries: 117 arteries from the heart to the head, the four legs, and the gut, with a beating heart at one end and 62 tissue beds at the other. The anatomy and settings come from a study by veterinarians and engineers at Ghent University and EPFL (Vera et al., 2019, *PLoS ONE*). EquiPhysics rewrote their model in Python so you can run it here.

**How to use it.** Run the cells in order: click a cell and press Shift+Enter, or use *Runtime → Run all*. The first cell builds the model. Each new horse takes about half a minute to a minute to run. A horse you have already run comes back instantly. If Colab warns that the notebook was not written by Google, click *Run anyway*. To keep your changes, use *File → Save a copy in Drive*."""),
    code(setup_cell()),
    md("""## 1. Meet the arteries

Each line is one artery, drawn with the lengths and angles measured in the study. Thick lines are big arteries. The horse faces left: the head is up and to the left, the tail to the right, and the legs hang down. Left and right arteries sit on top of each other in this side view. The red dots are the five places we will measure."""),
    code("lab.plot_tree()\nplt.show()"),
    md("""## 2. Run one horse

Pick the settings, then run the cell.

* **standing**: tick it for a standing horse, where gravity pulls on the blood. Untick it for a horse lying flat, where gravity does not matter.
* **heart_rate**: beats per minute. A horse at rest is near 40.
* **stiffness**: 1 is normal arteries. 1.5 means every artery is 1.5 times stiffer, as in an older horse.

The cell prints the key numbers, draws blood speed and blood pressure through one heartbeat at the five sites, and colors every artery by its average pressure."""),
    code("""#@title Choose a horse, then run this cell
standing = False  #@param {type:"boolean"}
heart_rate = 40  #@param {type:"slider", min:35, max:80, step:1}
stiffness = 1.0  #@param {type:"slider", min:0.7, max:1.5, step:0.05}

horse = lab.run_horse(standing, heart_rate, stiffness)
if horse:
    lab.summary(horse)
    lab.plot_sites(horse)
    lab.plot_map(horse, "mean")
    plt.show()"""),
    md("""## 3. Compare two horses

Set up horse A and horse B, for example the same horse lying down (A) and standing up (B). The two maps share one color scale, so you can compare colors directly. Choose what the maps show:

* **mean**: the average pressure over a heartbeat,
* **systolic**: the peak pressure of each beat,
* **pulse**: systolic minus diastolic, how much the pressure swings with each beat.

The last figure follows the pressure pulse down the aorta, from 26 cm to 86 cm from the heart."""),
    code("""#@title Horse A and horse B
A_standing = False  #@param {type:"boolean"}
A_heart_rate = 40  #@param {type:"slider", min:35, max:80, step:1}
A_stiffness = 1.0  #@param {type:"slider", min:0.7, max:1.5, step:0.05}
B_standing = True  #@param {type:"boolean"}
B_heart_rate = 40  #@param {type:"slider", min:35, max:80, step:1}
B_stiffness = 1.0  #@param {type:"slider", min:0.7, max:1.5, step:0.05}
map_shows = "mean"  #@param ["mean", "systolic", "pulse"]

A = lab.run_horse(A_standing, A_heart_rate, A_stiffness)
B = lab.run_horse(B_standing, B_heart_rate, B_stiffness)
lab.summary(A, B)
lab.plot_sites(A, B)
lab.plot_maps(A, B, quantity=map_shows)
lab.plot_aorta(A, B)
plt.show()"""),
    md("""## 4. Check gravity by hand

A column of blood *h* meters tall presses down with a pressure of ρ*gh*, where ρ = 1050 kg/m³ is the density of blood and *g* = 9.81 m/s². One mmHg is 133.3 Pa. The cell lists how high each site sits above the heart. Change `h` to the height difference you want to check."""),
    code("""xy = lab.tree_coordinates()
for name, seg in lab.SITES.items():
    (x0, y0), (x1, y1) = xy[seg]
    print(f"{name:24s} {0.5 * (y0 + y1):+.2f} m above the heart")

rho, g = 1050, 9.81
h = 1.0   # meters: change this
print(f"\\nrho * g * h = {rho * g * h:.0f} Pa = {rho * g * h / 133.3:.0f} mmHg")"""),
    md("""## 5. The Womersley number

In a pulsing flow, the Womersley number α = *R* √(2π*f*ρ/μ) compares how fast the flow changes with each heartbeat to how fast friction can slow the blood near the wall. *R* is the artery's radius, *f* the heart rate in beats per second, ρ the blood's density and μ its viscosity (0.004 Pa·s). When α is large, the middle of the artery moves like a plug and friction acts only in a thin layer by the wall. The study needed the Womersley theory of friction because a horse's arteries are so big."""),
    code("""import numpy as np
rho, mu = 1050, 0.004

def womersley(radius_m, beats_per_min):
    return radius_m * np.sqrt(2 * np.pi * (beats_per_min / 60) * rho / mu)

print("horse aorta, radius 3.4 cm, 40 beats/min:   ", round(womersley(0.034, 40), 1))
print("human aorta, radius 1.25 cm, 70 beats/min:  ", round(womersley(0.0125, 70), 1))
print("horse median artery, radius 3.5 mm, 40 bpm: ", round(womersley(0.0035, 40), 1))"""),
    md("""## 6. Check the model against the study (optional)

The study reports these numbers for its own model of a resting horse (40 beats a minute), lying and standing. Ours are next to them. The study also measured some of them in real horses, listed at the bottom."""),
    code("lab.compare_with_paper()"),
    md("""## How the model works, in brief

* In every artery the model solves two equations along its length: one for **mass** (blood that flows in must flow out or stretch the wall) and one for **momentum** (pressure differences push the blood; friction at the wall and gravity hold it back).
* The artery walls are **elastic**, and they get stiffer as the pressure rises, following a formula the study took from measurements of human arteries.
* At the start of the aorta, a **beating left ventricle** squeezes and relaxes on a timed curve (a "time-varying elastance" heart).
* Where an artery branches, the **pressure is the same** in all branches and **no blood is lost**.
* At the 62 ends, each **tissue bed** is a resistor and a balloon (a 3-element Windkessel) with values from the study.

For the equations and every parameter, see *Horse_Artery_Model_Overview.pdf*. The model has no reflexes, so faster heart rates and stiffer arteries show what the mechanics alone would do."""),
    md("""## Credits

**Model and data:** Vera L, Campos Arias D, Muylle S, Stergiopulos N, Segers P, van Loon G (2019). A 1D computer model of the arterial circulation in horses: an important resource for studying global interactions between heart and vessels under normal and pathological conditions. *PLoS ONE* 14(8): e0221425. https://doi.org/10.1371/journal.pone.0221425 (CC BY 4.0).

**Python version and lesson:** EquiPhysics, a nonprofit in Sonoita, Arizona (equiphysics.org), 2026. Free under the MIT License: https://github.com/equiphysics/education/tree/main/labs/Horse-Artery-Lab

Did you use this lab with a class? Please tell us how it went: https://www.equiphysics.org/for-teachers#tell-us"""),
]

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"},
               "colab": {"name": "Horse_Artery_Lab.ipynb", "provenance": []}}
nbf.write(nb, OUT)
print("wrote", OUT, f"({OUT.stat().st_size // 1024} KB)")
