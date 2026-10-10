import glob
import shutil
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy.stats import ttest_rel, pearsonr   # <--- Fix: add ttest_rel here!
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
import sys


# ==== CONFIGURATION ====
# RESULTS_DIR: folder of EquiPro "*-results.csv" files for one horse (one file per session).
# Default: labs/Gait-1/data in this repo (Duque, 2024 to 2025). Override on the command line:
#     python all_gaits_combined_analysis-averaged.py path/to/results [path/to/output]
# OUTPUT_DIR: where the tables and plots go. Default: an "equipro_output" folder in the current directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "..", "..", "labs", "Gait-1", "data")
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "equipro_output")
data_folder = RESULTS_DIR
output_base_folder = OUTPUT_DIR
stride_thresholds = {'walk': 20, 'trot': 20, 'canter': 5}

# ==== SETUP OUTPUT FOLDERS ====
gait_folders = {
    "walk": "walk-ave",
    "trot": "trot-ave",
    "canter": "canter-ave"
}

output_paths = {}
for gait, folder_name in gait_folders.items():
    full_path = os.path.join(output_base_folder, folder_name)

    if folder_name.endswith("-ave"):
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
    os.makedirs(full_path, exist_ok=True)
    output_paths[gait] = full_path

metric_labels = {
    'DAP_R': 'Diagonal Advance Placement Right (s)',
    'DAP_L': 'Diagonal Advance Placement Left (s)',
    'SI_Head': 'Symmetry Index Head (mm)',
    'SI_Withers': 'Symmetry Index Withers (mm)',
    'SI_Sacrum': 'Symmetry Index Sacrum (mm)',
    'DF_LF': 'Duty Factor LF (%)',
    'DF_RF': 'Duty Factor RF (%)',
    'DF_LH': 'Duty Factor LH (%)',
    'DF_RH': 'Duty Factor RH (%)',
    'ROM_LF': 'Range of Motion LF (deg)',
    'ROM_RF': 'Range of Motion RF (deg)',
    'ROM_LH': 'Range of Motion LH (deg)',
    'ROM_RH': 'Range of Motion RH (deg)'
}

metrics_raw = {
    'dap_R_sec': 'DAP_R',
    'dap_L_sec': 'DAP_L',
    'si_up_head': 'SI_Head',
    'si_up_wth': 'SI_Withers',
    'si_up_sac': 'SI_Sacrum',
    'duty_factor_LF': 'DF_LF',
    'duty_factor_RF': 'DF_RF',
    'duty_factor_LH': 'DF_LH',
    'duty_factor_RH': 'DF_RH',
    'rom_sagittal_LF': 'ROM_LF',
    'rom_sagittal_RF': 'ROM_RF',
    'rom_sagittal_LH': 'ROM_LH',
    'rom_sagittal_RH': 'ROM_RH'
}

for gait in ["walk", "trot", "canter"]:
    stride_thresh = stride_thresholds[gait]
    csv_files = glob.glob(os.path.join(data_folder, "*-results.csv"))
    all_data = []

    for file in csv_files:
        df = pd.read_csv(file)
        df = df[df['gait'].str.lower() == gait]
        df['source_file'] = os.path.basename(file)
        all_data.append(df)

    if not all_data:
        continue

    df = pd.concat(all_data, ignore_index=True)

    stride_counts = df.groupby(['source_file', 'direction', 'segment']).size().reset_index(name='n_strides')
    valid = stride_counts[stride_counts['n_strides'] >= stride_thresh]
    df = pd.merge(df, valid, on=['source_file', 'direction', 'segment'])

    agg_funcs = {col: ['mean', 'std'] for col in metrics_raw.keys()}
    summary = df.groupby(['source_file', 'direction', 'segment']).agg(agg_funcs).reset_index()
    summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in summary.columns.values]

    rename = {f"{k}_mean": f"{v}_Mean" for k, v in metrics_raw.items()}
    rename.update({f"{k}_std": f"{v}_SD" for k, v in metrics_raw.items()})
    summary.rename(columns=rename, inplace=True)

    summary['trial_date'] = pd.to_datetime(summary['source_file'].str.extract(r"(\d{8})T")[0], format="%Y%m%d")

    # === AVERAGE DIRECTION WITHIN TRIAL ===
    trial_avg = summary.groupby(['trial_date', 'direction']).mean(numeric_only=True).reset_index()
    trial_avg.sort_values(by='trial_date', inplace=True)
    pivot = trial_avg.pivot(index='trial_date', columns='direction')
    pivot.columns = ['_'.join(col).strip() for col in pivot.columns.values]
    pivot.dropna(how='all', inplace=True)

    # === COMBINE LEFT/RIGHT ===
    combined = pd.DataFrame(index=pivot.index)
    for metric in metrics_raw.values():
        left = f"{metric}_Mean_left"
        right = f"{metric}_Mean_right"
        if left in pivot and right in pivot:
            n = min(len(pivot[left]), len(pivot[right]))
            combined[metric + "_Mean"] = ((pivot[left][:n] + pivot[right][:n]) / 2).values
            combined[metric + "_SD"] = (np.std([pivot[left][:n], pivot[right][:n]], axis=0)).flatten()

    combined["Days"] = (combined.index - combined.index.min()).days

    # ========== FILTER TO ONLY DATES WITH BOTH LEFT AND RIGHT DATA ========== 
    left_dates = set(trial_avg[trial_avg['direction'] == 'left']['trial_date'])
    right_dates = set(trial_avg[trial_avg['direction'] == 'right']['trial_date'])
    both_dates = sorted(left_dates & right_dates)
    paired_pivot = pivot.loc[both_dates]

    # === STATISTICAL TESTS ===
    results = []
    regression_results = []
    for metric in ['SI_Head', 'SI_Withers', 'SI_Sacrum', 'DAP_R', 'DAP_L']:
        col = metric + "_Mean"
        if col in combined.columns:
            t, p = ttest_rel(combined[col], np.zeros(len(combined)))
            results.append({
                "Metric": metric,
                "Comparison": f"{metric} vs 0",
                "T-stat": t,
                "P-value": p,
                "Significant": p < 0.05
            })

    # Add RH vs LH and RF vs LF comparisons (paired)
    for mtype in ['DF', 'ROM']:
        for side1, side2 in [('RH', 'LH'), ('RF', 'LF')]:
            m1 = f"{mtype}_{side1}_Mean_right"
            m2 = f"{mtype}_{side2}_Mean_left"
            if m1 in paired_pivot.columns and m2 in paired_pivot.columns:
                t, p = ttest_rel(paired_pivot[m1], paired_pivot[m2])
                results.append({
                    "Metric": f"{mtype}_{side1} vs {side2}",
                    "Comparison": f"{side1} vs {side2}",
                    "T-stat": t,
                    "P-value": p,
                    "Significant": p < 0.05
                })

    # === REGRESSION, CORRELATION, AND PLOTTING ===
    sns.set(style="whitegrid", font_scale=1.2)
    for metric in combined.columns:
        if not metric.endswith("_Mean"):
            continue
        label = metric.replace("_Mean", "")
        yerr_col = label + "_SD"
        if label not in metric_labels:
            continue

        # Prepare X, y for regression/correlation
        X_full = combined["Days"].values
        y_full = combined[metric].values
        yerr = combined[yerr_col].values

        # Drop NaNs for regression/correlation and plotting
        mask = ~np.isnan(y_full)
        X = X_full[mask].reshape(-1, 1)
        y = y_full[mask]
        yerr_clean = yerr[mask]

        eqn = ""
        r2 = np.nan
        y_pred = np.full_like(y, np.nan)
        corr_r = np.nan
        corr_p = np.nan

        # Only fit regression/correlation if at least 2 points
        if len(y) > 1:
            reg = LinearRegression().fit(X, y)
            y_pred = reg.predict(X)
            r2 = r2_score(y, y_pred)
            eqn = f"y = {reg.coef_[0]:.3f}x + {reg.intercept_:.3f}"
            # Pearson correlation
            corr_r, corr_p = pearsonr(X.flatten(), y)
            regression_results.append({
                "Metric": label,
                "Regression Slope": reg.coef_[0],
                "Intercept": reg.intercept_,
                "R2": r2,
                "Correlation_r": corr_r,
                "Correlation_p": corr_p
            })

        # === PLOT ===
        plt.figure(figsize=(10, 5))
        plt.errorbar(X.flatten(), y, yerr=yerr_clean,
                     fmt='o-', capsize=4, label=gait.capitalize(), color="blue", linewidth=2)
        # Plot regression line and stats annotation
        if len(y) > 1:
            plt.plot(X.flatten(), y_pred, color="red", linestyle="--", label="Regression line")
            plt.text(
                0.01, 0.97, f"{eqn}\n$R^2$ = {r2:.3f}\nr = {corr_r:.3f}, p = {corr_p:.3g}",
                ha='left', va='top', transform=plt.gca().transAxes, fontsize=11,
                bbox=dict(facecolor='white', edgecolor='gray', alpha=0.7))
        plt.xlabel("Time (days)")
        plt.ylabel(metric_labels[label])
        plt.xticks(rotation=45)
        plt.tight_layout()
        outname_pdf = os.path.join(output_paths[gait], f"{label}.pdf")
        outname_png = os.path.join(output_paths[gait], f"{label}.png")
        plt.savefig(outname_pdf)
        plt.savefig(outname_png)
        plt.close()

    # === EXPORT ===
    combined.reset_index(inplace=True)
    combined.to_excel(os.path.join(output_paths[gait], "combined_summary.xlsx"), index=False)
    summary.to_excel(os.path.join(output_paths[gait], "directional_summary.xlsx"), index=False)
    stats_df = pd.DataFrame(results)
    reg_df = pd.DataFrame(regression_results)
    if not reg_df.empty:
        # Use outer join so all regression results are present, even if not in t-test results
        stats_df = pd.merge(stats_df, reg_df, how="outer", left_on="Metric", right_on="Metric")
    stats_df.to_excel(os.path.join(output_paths[gait], "statistical_tests.xlsx"), index=False)

    print(f"{gait.upper()} complete. Results in: {output_paths[gait]}")