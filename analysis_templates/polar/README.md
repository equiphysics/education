# Polar Equine scripts

Two small Python scripts for the raw `.txt` files the Polar Equine app exports. They read the files as exported: the `#` comment lines at the top are skipped, and stray null bytes are stripped.

**Audience and level:** students who can run a Python script from the command line. Nothing here needs more than a semester of Python.

## Files

- `plot_ECG.py`: plot a time window of the ECG.
- `calc_HRV_metrics.py`: band-pass filter the ECG, find the R-peaks, and print mean RR, heart rate, SDNN, RMSSD, and pNN50 for a time window.

## How to run

From this folder:

```bash
python plot_ECG.py ../../labs/horse_heart_VdP/ECG_11.14.25_2.40.36_PM.txt 0 60000
python calc_HRV_metrics.py ../../labs/horse_heart_VdP/ECG_11.14.25_2.40.36_PM.txt 122630 229412
```

Times are in milliseconds from the start of the recording. The second example is the trot interval used in the Horse Heartbeats lab. With no arguments, each script looks for `ECG_11.14.25_2.40.36_PM.txt` in the current folder and takes the first 60 seconds.

Needs numpy, pandas, scipy, and matplotlib.

## Notes

- R-peaks must be at least 0.27 s apart (`MIN_RR_SEC`). That allows heart rates up to about 220 bpm, so the script works for exercise, not only rest. If the ECG is noisy, raise `PEAK_PROMINENCE_MV` or pick a cleaner window.
- Look at the peaks on a plot before trusting the numbers. A missed beat doubles one RR interval and inflates SDNN and RMSSD.
- The `HR_*.txt` file from the same session holds the strap's own RR intervals. Compare them with yours.

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you adapt these scripts.
