# EquiPro stride-table scripts

Two Python scripts for a folder of EquiPro `*-results.csv` files from one horse. Each CSV holds one row per stride. The scripts group strides by session, gait, and direction, and follow the horse over time.

**Audience and level:** student projects. You should be comfortable with pandas and a paired t-test.

## Files

- `all-gaits-analysis-LR-comparison.py`: for walk, trot, and canter, average each session's segments, plot each metric over days with the left and right circles kept separate, fit a regression line, and compare left versus right with a paired t-test. Writes CSV tables and PNG/PDF plots into `walk/`, `trot/`, and `canter/`.
- `all_gaits_combined_analysis-averaged.py`: same idea, but averages the left and right circles within each session, tests the symmetry indices against zero, compares hind-limb and forelimb pairs, and writes Excel tables and plots into `walk-ave/`, `trot-ave/`, and `canter-ave/`.

Metrics: diagonal advance placement (left and right), symmetry indices for head, withers, and sacrum, duty factor for each limb, and sagittal range of motion for each limb.

## How to run

Point a script at a folder of results files. The default is `labs/Gait-1/data` in this repo (Duque, June 2024 to August 2025).

```bash
python all-gaits-analysis-LR-comparison.py ../../labs/Gait-1/data
python all_gaits_combined_analysis-averaged.py ../../labs/Gait-1/data
```

Outputs go into an `equipro_output` folder in the current directory. Give a second argument to change that, or edit `RESULTS_DIR` and `OUTPUT_DIR` at the top of each script. Segments with fewer than 20 strides (walk, trot) or 5 strides (canter) are skipped.

Needs pandas, numpy, scipy, matplotlib, and seaborn. The averaged script also needs scikit-learn and openpyxl.

## Credit

EquiPhysics, Sonoita, Arizona. Written by Laura Miller. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you adapt these scripts.
