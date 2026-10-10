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
