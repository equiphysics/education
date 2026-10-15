# Horse Heartbeats Lab (Van der Pol + ECG)

> **New in October 2026:** this notebook now has a hands-on companion, the **Horse Heart Lab** web app and 60-minute classroom activity in [`labs/Horse-Heart-Lab`](../Horse-Heart-Lab). The app uses a more physiological ECG model (a phase clock with P, Q, R, S, and T bumps, after McSharry et al. 2003) and a stochastic differential equation for the heart-rate wander. Start there; come here to go deeper with code and the Van der Pol oscillator.

This folder holds a self-guided Jupyter notebook activity on:
- the Van der Pol oscillator (nullclines, phase plane intuition)
- basic ECG data handling and visualization
- connecting model dynamics to real physiological signals

The ECG comes from Duque, one of our own horses, recorded with a Polar Equine strap during a ride on 14 November 2025. Question 3 of the notebook works on his trot.

Primary notebook:
- `labs/horse_heart_VdP/Horse_Heartbeats_VdP.ipynb`

## Files in this folder

- `Horse_Heartbeats_VdP.ipynb`: the notebook
- `ECG_11.14.25_2.40.36_PM.txt`: raw ECG in millivolts at about 130 Hz, with a timestamp in milliseconds for each sample (about 17 minutes)
- `HR_11.14.25_2.40.36_PM.txt`: the strap's own heart rate and RR intervals from the same ride (one row per beat: HR in bpm, RR in ms, timestamp in ms, skin-contact flag). Use it to check the RR intervals you compute from the ECG in Question 3.
- `Horse_Heart_VdP.pptx`: background slides
- `README.md`: this file

Both data files start with a few comment lines that begin with `#`, then a header row, then the data.

---

## Quick start (recommended): run in Google Colab

1. Open the notebook in **Google Colab** with this link:
   https://colab.research.google.com/github/equiphysics/education/blob/main/labs/horse_heart_VdP/Horse_Heartbeats_VdP.ipynb
2. Run cells with **Shift+Enter**.
3. When the notebook asks for the ECG file, upload `ECG_11.14.25_2.40.36_PM.txt` from this folder.

---

## Data access (student-friendly)

The ECG file sits in this folder, right next to the notebook.

### In Colab: upload the ECG file
The loading cell in Question 3 asks you to upload it. If you prefer, upload it yourself:
- Click the **folder icon** (Files) on the left
- Click **Upload**
- Select `ECG_11.14.25_2.40.36_PM.txt`

Then re-run the cell that loads the ECG file.

### On your own computer
Keep the ECG file in the same folder as the notebook. The notebook finds it on its own.

---

## How to complete the activity

- Work through the notebook in order.
- **Run code cells with Shift+Enter** to generate plots and outputs.
- You **do not** need to write new code, but you may need to **change parameter values (numbers)** in a few places and re-run cells.
- For each exercise, write your answer in the cell directly below the prompt.
  - If it's a written response, start the cell with `#` and answer in plain English.

### Submitting
Transfer your final answers to **your course's submission system** (follow your course instructions).

---

## Running locally (optional)

If you prefer to run on your own computer:

### 1) Install Python packages
Using pip:
```bash
python -m pip install numpy scipy matplotlib pandas ipywidgets jupyterlab
```

### 2) Launch Jupyter
From the folder that holds this repo:
```bash
jupyter lab
```
(`jupyter notebook` works too.) A browser tab opens with the file browser.

### 3) Open the notebook
In the file browser, open `labs/horse_heart_VdP/Horse_Heartbeats_VdP.ipynb` and run the cells from the top with Shift+Enter. The ECG file is already in the same folder, so the loading cell finds it without an upload.

---

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horse Duque. Released under the MIT License; please credit EquiPhysics if you adapt these materials.

## Help keep these lessons free

This lesson is free. If one helps you, you can [donate to EquiPhysics](https://www.equiphysics.org/donate). Can't give right now? You can still help a lot: share a lesson with another teacher, star this repository, and follow us on [GitHub](https://github.com/equiphysics), [Instagram](https://www.instagram.com/equiphysics_institute/), [Facebook](https://www.facebook.com/profile.php?id=61579151426160), and [LinkedIn](https://www.linkedin.com/company/equiphysics-institute/). Follows and shares help us show grant funders that people use and value this work. For news a few times a year, [sign up here](https://www.equiphysics.org/#news).
