"""Plot a time window of a raw Polar Equine ECG export.

Usage:
    python plot_ECG.py ECG_11.14.25_2.40.36_PM.txt [start_ms] [end_ms]

The .txt file starts with "#" comment lines, then a header row "ECG, MS", then
one row per sample: ECG in millivolts and a timestamp in milliseconds.
"""
import io
import sys

import matplotlib.pyplot as plt
import pandas as pd

ECG_FILE = sys.argv[1] if len(sys.argv) > 1 else "ECG_11.14.25_2.40.36_PM.txt"
start_ms = int(sys.argv[2]) if len(sys.argv) > 2 else 0
end_ms = int(sys.argv[3]) if len(sys.argv) > 3 else 60000  # first 60 seconds


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


# Load ECG data
ecg_df = read_polar_ecg(ECG_FILE)

# Trim to the chosen time window
ecg_segment = ecg_df[(ecg_df["time_ms"] >= start_ms) & (ecg_df["time_ms"] <= end_ms)]

# Plot ECG
plt.figure(figsize=(12, 4))
plt.plot(ecg_segment["time_ms"], ecg_segment["ecg_mV"], label="ECG (mV)")
plt.xlabel("Time (ms)")
plt.ylabel("ECG (mV)")
plt.title(f"ECG Signal Over Time: {ECG_FILE}")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
