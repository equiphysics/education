# Horse Heartbeats Lab (Van der Pol + ECG)

This repo contains a self-guided Jupyter notebook activity on:
- the Van der Pol oscillator (nullclines, phase plane intuition)
- basic ECG data handling and visualization
- connecting model dynamics to real physiological signals

Primary notebook:
- `labs/Lab_Horse_Heartbeats_VdP_python.ipynb`

---

## Quick start (recommended): run in Google Colab

1. Open the notebook in **:contentReference[oaicite:0]{index=0}** using a Colab link (see below).
2. Run cells with **Shift+Enter**.
3. When prompted (or if the notebook can’t find the ECG file), upload the data file:
   - `ECG_11.14.25_2.40.36_PM.txt`

### Colab link template (edit to match your repo)
Replace `<USER>` and `<REPO>`:

https://colab.research.google.com/github/<USER>/<REPO>/blob/main/labs/Lab_Horse_Heartbeats_VdP_python.ipynb

---

## Data access (student-friendly)

Students have two easy options:

### Option A: Upload the ECG file (fastest, no setup)
In Colab:
- Click the **folder icon** (Files) on the left
- Click **Upload**
- Select `ECG_11.14.25_2.40.36_PM.txt`

Then re-run the cell that loads the ECG file.

### Option B: If the data is included in this repo
If your instructor includes the data in `data/`, the notebook can read it directly.
For example:
- `data/ECG_11.14.25_2.40.36_PM.txt`

(If the file is not included, use Option A.)

---

## How to complete the activity

- Work through the notebook in order.
- **Run code cells with Shift+Enter** to generate plots and outputs.
- You **do not** need to write new code, but you may need to **change parameter values (numbers)** in a few places and re-run cells.
- For each exercise, write your answer in the cell directly below the prompt.
  - If it’s a written response, start the cell with `#` and answer in plain English.

### Submitting
Transfer your final answers to **:contentReference[oaicite:1]{index=1}** for submission (follow your course instructions).

---

## Running locally (optional)

If you prefer to run on your own computer:

### 1) Install Python packages
Using pip:
```bash
python -m pip install numpy scipy matplotlib pandas ipywidgets jupyterlab_widgets

