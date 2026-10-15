# Gait Lesson 1: walk and trot phase models

Real stride-by-stride data from Duque, recorded with EquiPro inertial sensors on 19 January 2026, next to a reduced coupled phase-oscillator model of quadruped gait. Students turn hoof-on times into a phase between 0 and 1, plot the footfall pattern of one walk segment and one trot segment, and compare the data with the model.

**Audience and level:** college students in a first modeling or data course. Strong high-school students can follow with help. The notebook has complete, runnable code. Students change numbers and interpret plots; they do not write code from scratch.

## Files

- `EquiPro_Gait_Lesson_1_Walk_Trot_Phase_Model.ipynb`: the lesson notebook
- `20260119T121135-Duque-results.csv`: the EquiPro stride table the notebook reads, one row per stride
- `IntroToHorseGaits-1.pptx`: background slides on the walk, the trot, the EquiPro sensor system, stride length and duty factor, and the phase model
- `data/`: 28 more EquiPro stride tables from Duque, June 2024 to August 2025, for student projects (see `data/README.md`)

## How to run

- **Google Colab:** open https://colab.research.google.com/github/equiphysics/education/blob/main/labs/Gait-1/EquiPro_Gait_Lesson_1_Walk_Trot_Phase_Model.ipynb and run the cells from the top. The setup cell looks for the CSV next to the notebook first. In Colab it will ask you to upload `20260119T121135-Duque-results.csv` from this folder.
- **Locally:** keep the CSV in this folder, start `jupyter lab`, open the notebook, and run from the top. Needs numpy, pandas, and matplotlib.

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you adapt these materials.

## Help keep these lessons free

This lesson is free. If one helps you, you can [donate to EquiPhysics](https://www.equiphysics.org/donate). Can't give right now? You can still help a lot: share a lesson with another teacher, star this repository, and follow us on [GitHub](https://github.com/equiphysics), [Instagram](https://www.instagram.com/equiphysics_institute/), [Facebook](https://www.facebook.com/profile.php?id=61579151426160), and [LinkedIn](https://www.linkedin.com/company/equiphysics-institute/). Follows and shares help us show grant funders that people use and value this work. For news a few times a year, [sign up here](https://www.equiphysics.org/#news).
