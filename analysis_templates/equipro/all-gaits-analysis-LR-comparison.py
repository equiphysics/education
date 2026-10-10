import os
import sys
import glob
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel, linregress
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ==== CONFIGURATION ====
# RESULTS_DIR: folder of EquiPro "*-results.csv" files for one horse (one file per session).
# Default: labs/Gait-1/data in this repo (Duque, 2024 to 2025). Override on the command line:
#     python all-gaits-analysis-LR-comparison.py path/to/results [path/to/output]
# OUTPUT_DIR: where the tables and plots go. Default: an "equipro_output" folder in the current directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "..", "..", "labs", "Gait-1", "data")
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "equipro_output")
data_folder = RESULTS_DIR
output_base_folder = OUTPUT_DIR
gaits = {
    "walk": 20,
    "trot": 20,
    "canter": 5
}

metrics_to_average = {
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

pretty_labels = {
    "DAP_L": "Diagonal Advance Placement (Left) [s]",
    "DAP_R": "Diagonal Advance Placement (Right) [s]",
    "SI_Head": "Symmetry Index (Head) [unitless]",
    "SI_Withers": "Symmetry Index (Withers) [unitless]",
    "SI_Sacrum": "Symmetry Index (Sacrum) [unitless]",
    "DF_LF": "Duty Factor Left Front [%]",
    "DF_RF": "Duty Factor Right Front [%]",
    "DF_LH": "Duty Factor Left Hind [%]",
    "DF_RH": "Duty Factor Right Hind [%]",
    "ROM_LF": "Range of Motion Left Front [deg]",
    "ROM_RF": "Range of Motion Right Front [deg]",
    "ROM_LH": "Range of Motion Left Hind [deg]",
    "ROM_RH": "Range of Motion Right Hind [deg]"
}


def analyze_gait(gait_name, min_strides):
    # Create output directory
    out_dir = os.path.join(output_base_folder, gait_name)
    os.makedirs(out_dir, exist_ok=True)

    # Load all data
    csv_files = glob.glob(os.path.join(data_folder, "*-results.csv"))
    all_data = []
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            df['source_file'] = os.path.basename(file_path)
            all_data.append(df)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
    if not all_data:
        print(f"No CSV files found for {gait_name}.")
        return
    combined_df = pd.concat(all_data, ignore_index=True)

    # Filter gait
    gait_df = combined_df[combined_df['gait'].str.lower() == gait_name]
    if gait_df.empty:
        print(f"No data found for {gait_name}")
        return

    # Filter by stride count
    stride_counts = gait_df.groupby(['source_file', 'direction', 'segment']).size().reset_index(name='n_strides')
    valid_groups = stride_counts[stride_counts['n_strides'] >= min_strides]
    filtered_df = pd.merge(gait_df, valid_groups, on=['source_file', 'direction', 'segment'])

    if filtered_df.empty:
        print(f"No valid segments with >={min_strides} strides for {gait_name}")
        return

    # Aggregate segment level data
    agg_funcs = {col: ['mean', 'std'] for col in metrics_to_average}
    summary = (
        filtered_df.groupby(['source_file', 'direction', 'segment'])
        .agg(agg_funcs)
        .reset_index()
    )
    summary.columns = ['_'.join(filter(None, col)).strip() for col in summary.columns]
    rename_dict = {f"{k}_mean": f"{v}_Mean" for k, v in metrics_to_average.items()}
    rename_dict.update({f"{k}_std": f"{v}_SD" for k, v in metrics_to_average.items()})
    summary.rename(columns=rename_dict, inplace=True)
    summary['trial_date'] = pd.to_datetime(summary['source_file'].str.extract(r'(\d{8})T')[0], format="%Y%m%d")

    # Trial summary
    trial_summary = (
        summary.groupby(['trial_date', 'direction'])
        .mean(numeric_only=True)
        .reset_index()
        .sort_values('trial_date')
    )
    if trial_summary.empty:
        print(f"No trial summary data for {gait_name}")
        return
    trial_summary['day'] = (trial_summary['trial_date'] - trial_summary['trial_date'].min()).dt.days

    # --- Plotting with regression lines and correlation stats ---
    regression_stats = []
    sns.set(style='whitegrid')
    for metric in [c for c in trial_summary.columns if c.endswith("_Mean")]:
        sd_metric = metric.replace("_Mean", "_SD")
        base_label = metric.replace("_Mean", "")
        label_text = pretty_labels.get(base_label, base_label)
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        for direction, color in zip(['left', 'right'], ['blue', 'red']):
            data = trial_summary[trial_summary['direction'] == direction]
            if metric in data.columns and sd_metric in data.columns and not data.empty:
                plt.errorbar(
                    data['day'], data[metric], yerr=data[sd_metric],
                    label=direction.capitalize(), fmt='o-', capsize=4,
                    color=color, linewidth=2
                )
                if len(data['day']) > 1:
                    x = data['day']
                    y = data[metric]
                    slope, intercept, r_value, p_value, std_err = linregress(x, y)
                    reg_line = slope * x + intercept
                    plt.plot(x, reg_line, '--', color=color, alpha=0.7)
                    # Annotate regression equation, R², and correlation stats
                    eqn = (
                        f"$y = {slope:.2f}x + {intercept:.2f}$\n"
                        f"$R^2 = {r_value**2:.2f}$\n"
                        f"$r = {r_value:.2f}, p = {p_value:.3g}$"
                    )
                    y_max = max(y)
                    x_annot = min(x)
                    y_annot = y_max + 0.03 * (max(y) - min(y)) if max(y) != min(y) else y_max
                    plt.text(
                        x_annot, y_annot,
                        eqn,
                        color=color, fontsize=12,
                        verticalalignment='bottom',
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.6, edgecolor=color)
                    )
                    # Save regression/correlation results for summary export
                    regression_stats.append({
                        "Metric": base_label,
                        "Direction": direction,
                        "Regression Slope": slope,
                        "Regression Intercept": intercept,
                        "R": r_value,
                        "R^2": r_value**2,
                        "P-value (corr)": p_value,
                        "Significant Correlation (p<0.05)": p_value < 0.05
                    })
        plt.xlabel("Time (days since first measurement)", fontsize=14)
        plt.ylabel(label_text, fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(fontsize=12)
        plt.tight_layout()
        # Export as both PNG and PDF
        for ext in ['png', 'pdf']:
            plt.savefig(os.path.join(out_dir, f"{base_label}_plot.{ext}"), dpi=300 if ext=='png' else None)
        plt.close()
    # --- End Plotting ---

    # Stats comparison
    pivoted = trial_summary.pivot(index='trial_date', columns='direction')
    pivoted.columns = ['_'.join(col).strip() for col in pivoted.columns.values]

    comparison_results = []
    for base_metric in metrics_to_average.values():
        left_col = f"{base_metric}_Mean_left"
        right_col = f"{base_metric}_Mean_right"
        if left_col in pivoted.columns and right_col in pivoted.columns:
            valid = pivoted[[left_col, right_col]].dropna()
            if not valid.empty:
                left = valid[left_col]
                right = valid[right_col]
                t_stat, p_val = ttest_rel(left, right)
                effect_size = (left - right).mean() / (left - right).std(ddof=1)
            else:
                t_stat = p_val = effect_size = np.nan
            comparison_results.append({
                "Metric": base_metric,
                "Mean (Left)": pivoted[left_col].mean() if left_col in pivoted else np.nan,
                "Mean (Right)": pivoted[right_col].mean() if right_col in pivoted else np.nan,
                "T-Statistic": t_stat,
                "P-Value": p_val,
                "Effect Size (d)": effect_size,
                "Significant (p < 0.05)": p_val < 0.05 if not np.isnan(p_val) else False
            })

    comparison_df = pd.DataFrame(comparison_results)
    regression_df = pd.DataFrame(regression_stats)

    # Save outputs
    summary.to_csv(os.path.join(out_dir, "segment_metrics.csv"), index=False)
    trial_summary.to_csv(os.path.join(out_dir, "trial_summary.csv"), index=False)
    pivoted.to_csv(os.path.join(out_dir, "pivoted_comparison.csv"))
    comparison_df.to_csv(os.path.join(out_dir, "left_vs_right_stats.csv"), index=False)
    regression_df.to_csv(os.path.join(out_dir, "regression_correlation_stats.csv"), index=False)

    print(f"Completed {gait_name.upper()} — saved to {out_dir}")


# Run for each gait
for gait, min_strides in gaits.items():
    analyze_gait(gait_name=gait, min_strides=min_strides)
