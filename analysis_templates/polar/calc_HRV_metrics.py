"""Compute simple HRV metrics from a raw Polar Equine ECG export.

Usage:
    python calc_HRV_metrics.py ECG_11.14.25_2.40.36_PM.txt [start_ms] [end_ms]

The Polar Equine app exports the ECG as a .txt file. The file starts with "#"
comment lines (device, collection time, column list), then a header row
"ECG, MS", then one row per sample: ECG voltage in millivolts and a timestamp
in milliseconds. Sampling is about 130 Hz.

Default window: the first 60 seconds. Change it on the command line or edit the
PARAMETERS block below.
"""
import io
import sys

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks

# === PARAMETERS ===
ECG_FILE = sys.argv[1] if len(sys.argv) > 1 else "ECG_11.14.25_2.40.36_PM.txt"
start_ms = int(sys.argv[2]) if len(sys.argv) > 2 else 0
end_ms = int(sys.argv[3]) if len(sys.argv) > 3 else 60000  # 60 seconds

# Minimum spacing between R-peaks, in seconds. 0.27 s allows heart rates up to
# about 220 bpm, so peaks are still found during hard exercise. (A resting horse
# is near 30 to 40 bpm. The old cap of 0.6 s missed beats above 100 bpm.)
MIN_RR_SEC = 0.27
PEAK_PROMINENCE_MV = 0.3


def read_polar_ecg(path):
    """Read a raw Polar Equine ECG .txt file into a DataFrame with ecg_mV and time_ms.

    Lines starting with "#" are skipped. Null bytes, which some exports contain,
    are stripped first.
    """
    raw = open(path, "rb").read().replace(b"\x00", b"")
    text = raw.decode("utf-8", errors="replace")
    df = pd.read_csv(io.StringIO(text), comment="#", skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"ECG": "ecg_mV", "MS": "time_ms"})
    df = df[["ecg_mV", "time_ms"]].apply(pd.to_numeric, errors="coerce").dropna()
    return df.reset_index(drop=True)


# === Load ECG Data ===
ecg_df = read_polar_ecg(ECG_FILE)

# === Filter by Time Window ===
ecg_segment = ecg_df[(ecg_df["time_ms"] >= start_ms) & (ecg_df["time_ms"] <= end_ms)].copy()
if len(ecg_segment) < 10:
    raise SystemExit(
        f"Only {len(ecg_segment)} samples between {start_ms} and {end_ms} ms. "
        f"The file runs from {ecg_df['time_ms'].min():.0f} to {ecg_df['time_ms'].max():.0f} ms."
    )

# === Estimate Sampling Frequency ===
time_diffs = np.diff(ecg_segment["time_ms"].values)
fs = 1000 / np.median(time_diffs)  # in Hz


# === Bandpass Filter Definition ===
def bandpass_filter(signal, fs, lowcut=0.5, highcut=40.0, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
    return filtfilt(b, a, signal)


# === Apply Bandpass Filter ===
filtered_ecg = bandpass_filter(ecg_segment["ecg_mV"].values, fs)

# === Detect R-peaks ===
peaks, _ = find_peaks(filtered_ecg, distance=fs * MIN_RR_SEC, prominence=PEAK_PROMINENCE_MV)
peak_times = ecg_segment["time_ms"].values[peaks]

# === Compute RR Intervals (in ms) ===
rr_intervals = np.diff(peak_times)

# === Compute HRV Metrics ===
mean_rr = np.mean(rr_intervals)
sdnn = np.std(rr_intervals)
rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))
nn50 = np.sum(np.abs(np.diff(rr_intervals)) > 50)
pnn50 = 100.0 * nn50 / len(rr_intervals) if len(rr_intervals) > 0 else float("nan")

# === Print Results ===
print(f"\nHRV Metrics for {ECG_FILE}, time window {start_ms} to {end_ms} ms:")
print(f"Sampling Frequency: {fs:.2f} Hz")
print(f"Number of R-peaks: {len(peaks)}")
print(f"Number of RR Intervals: {len(rr_intervals)}")
print(f"Mean RR (ms): {mean_rr:.2f}")
print(f"Mean heart rate (bpm): {60000.0 / mean_rr:.1f}")
print(f"SDNN (ms): {sdnn:.2f}")
print(f"RMSSD (ms): {rmssd:.2f}")
print(f"pNN50 (%): {pnn50:.2f}")
