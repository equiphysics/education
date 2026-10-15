# Duque Exercise: heart rate and HRV during a weekly lunge test

Our horse Duque's weekly lunge test during his 90-day fitness routine: quiet standing, lunge left and right with walk and trot sets, then standing recovery. The notebook loads the Polar Equine exports, plots heart rate and RR intervals, picks out baseline, work, and recovery, computes RMSSD and SDNN on clean standing segments, estimates how fast heart rate comes down after the trot sets, and compares left with right.

**Audience and level:** high school and college students who have met means and standard deviations. The notebook has complete code. Students change a few settings marked `#TODO` and write short interpretations. It is an educational notebook, not veterinary diagnosis.

## Files

- `Duque_Lunge_Test.ipynb`: the notebook
- `Duque_HR_HRV_90-days-intro.pptx`: background slides on heart rate, HRV, and the 90-day routine
- `Duque_exercise-data/`: one test session from 19 January 2026
  - `HR_1.19.26_12.00.11_PM.txt`: resting heart rate and RR intervals, a short recording taken standing before the test
  - `HR_1.19.26_12.11.36_PM.txt`: heart rate and RR intervals during the test
  - `ECG_1.19.26_12.11.36_PM.txt`: raw ECG during the test
  - `ACC_1.19.26_12.11.36_PM.txt`: accelerometer during the test, for movement context
  - `GPS_1.19.26_12.11.36_PM.txt`: GPS summary (the notebook does not use it)

Each file starts with comment lines that begin with `#`, then a header row, then the data.

## How to run

- **Google Colab:** open https://colab.research.google.com/github/equiphysics/education/blob/main/labs/Duque-Exercise/Duque_Lunge_Test.ipynb and run the cells from the top. The setup cell asks you to upload the two HR files, the ECG file, and the ACC file from `Duque_exercise-data/`. Select all four at once.
- **Locally:** start `jupyter lab` in this folder, open the notebook, and run from the top. The setup cell finds the files in `Duque_exercise-data/` and skips the upload. Needs numpy, pandas, matplotlib, and ipywidgets.

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you adapt these materials.

## Help keep these lessons free

This lesson is free. If one helps you, you can [donate to EquiPhysics](https://www.equiphysics.org/donate). Can't give right now? You can still help a lot: share a lesson with another teacher, star this repository, and follow us on [GitHub](https://github.com/equiphysics), [Instagram](https://www.instagram.com/equiphysics_institute/), [Facebook](https://www.facebook.com/profile.php?id=61579151426160), and [LinkedIn](https://www.linkedin.com/company/equiphysics-institute/). Follows and shares help us show grant funders that people use and value this work. For news a few times a year, [sign up here](https://www.equiphysics.org/#news).
