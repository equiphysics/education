# Duque EquiPro stride tables, June 2024 to August 2025

28 EquiPro results files from our own horse Duque. Each file is one session. Each row is one stride: hoof-on times for the four limbs, stride duration, duty factor, stance and swing durations, symmetry indices for head, withers, and sacrum, sagittal ranges of motion, and more. Taken together they are stride-by-stride summaries over time, so you can follow one horse across a year: how stride duration, duty factor, and left-right symmetry change with training, season, and footing.

## Files

- `YYYYMMDDThhmmss-Duque-results.csv`: one file per session, named by the session start time (UTC). About 6 MB in all.
- `20240701T082442-Duque-results.csv` is a very short session, only a few strides. Keep it or drop it; the scripts skip segments with too few strides.

The columns match the lesson file in the folder above (`20260119T121135-Duque-results.csv`), so the lesson notebook can read any of these files. `segment`, `gait`, `direction`, and `surface` tell you which block of the session a stride belongs to.

## Scripts

`analysis_templates/equipro/` has two scripts that read a whole folder of these files, average each session, and plot each metric over days with regression lines and paired tests.

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque, recorded with EquiPro sensors. Released under the MIT License; please credit EquiPhysics if you use the data.
