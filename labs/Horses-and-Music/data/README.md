# Duque standing heart-rate recordings, 27 February 2026

Six short recordings of our own horse Duque standing still, wearing a Polar Equine strap, all on one day. Three conditions: silence, calm music, energetic music. Two recordings per condition. Use them to compare heart rate and heart-rate variability (HRV) across the conditions.

| File | Condition | Time of day | Length | RR rows |
|---|---|---|---|---|
| `HR_2.27.26_11.41.15_AM.txt` | Silence, recording 1 | 11:41 AM | 7.9 min | 259 |
| `HR_2.27.26_11.49.34_AM.txt` | Energetic music, recording 1 | 11:49 AM | 5.8 min | 189 |
| `HR_2.27.26_11.55.51_AM.txt` | Energetic music, recording 2 | 11:55 AM | 3.7 min | 134 |
| `HR_2.27.26_2.53.19_PM.txt` | Silence, recording 2 | 2:53 PM | 5.3 min | 126 |
| `HR_2.27.26_3.01.29_PM.txt` | Calm music, recording 1 | 3:01 PM | 5.3 min | 175 |
| `HR_2.27.26_3.12.24_PM.txt` | Calm music, recording 2 | 3:12 PM | 4.8 min | 162 |

Silence was recorded in the morning and again in the afternoon, so each music condition has a silence recording from the same part of the day.

## File format

Each file starts with comment lines that begin with `#` (device, collection time, column list), then a header row, then one row per beat:

```
HR, RR, MS, SC
```

- `HR`: heart rate in beats per minute as the strap reports it
- `RR`: the interval between this beat and the previous one, in milliseconds
- `MS`: timestamp in milliseconds from the start of the recording
- `SC`: skin contact, 1 = good contact, 0 = none

The first rows of each file show `HR = 0` and `SC = 0` while the strap finds the signal. Drop rows with `SC = 0` before computing anything. Some files contain a stray null byte; strip `\x00` before parsing if your reader complains.

## Things to try

- Mean heart rate, SDNN, and RMSSD for each recording. Which condition has the highest HRV?
- Do the two recordings of one condition agree with each other?
- Morning versus afternoon: compare the two silence recordings before you compare music to silence.
- The first minute versus the last minute of a recording: does Duque settle?

The notebook `analysis_templates/Standing_Music_HorseName_Year_Month_Day_Time.ipynb` is the full standing-session analysis. The scripts in `analysis_templates/polar/` show how to read Polar files and compute HRV metrics.

Only the HR files are here. The ECG, accelerometer, and video from the same sessions are not included.

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you use the data.
