# Horses and Music

Does music change a horse's heart rate or heart-rate variability? This folder holds data for that question from our own horse Duque: six standing recordings from one day, in silence, with calm music, and with energetic music. See `data/README.md` for the files and some things to try.

**Audience and level:** high school and college students who have met means and standard deviations. The HRV metrics (SDNN, RMSSD) are one-line formulas.

## Files

- `data/`: six Polar Equine `HR_*.txt` files with RR intervals, and a README that maps each file to its condition.

## How to run

- Read the `RR` column from each file (skip the lines that start with `#`, drop rows without skin contact), then compute mean heart rate, SDNN, and RMSSD for each recording. Compare the conditions.
- `analysis_templates/Standing_Music_HorseName_Year_Month_Day_Time.ipynb` is the full standing-session workflow. It also expects an ACC file and the session video, which are not included here, so use it as a reference for the heart-rate and HRV parts.
- `analysis_templates/polar/` has short scripts that show how to read Polar files and compute HRV metrics from an ECG.

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you use the data.

## Help keep these lessons free

This lesson is free. If one helps you, you can [donate to EquiPhysics](https://www.equiphysics.org/donate). Can't give right now? You can still help a lot: share a lesson with another teacher, star this repository, and follow us on [GitHub](https://github.com/equiphysics), [Instagram](https://www.instagram.com/equiphysics_institute/), [Facebook](https://www.facebook.com/profile.php?id=61579151426160), and [LinkedIn](https://www.linkedin.com/company/equiphysics-institute/). Follows and shares help us show grant funders that people use and value this work. For news a few times a year, [sign up here](https://www.equiphysics.org/#news).
