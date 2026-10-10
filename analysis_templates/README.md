# Analysis templates

Notebooks and scripts for student projects with our Polar Equine and EquiPro data. Work from a copy and keep the original as it is.

**Audience and level:** college students doing a project. The notebooks run in Google Colab with complete code. The scripts need Python on your own computer.

## Files

- `Standing_Music_HorseName_Year_Month_Day_Time.ipynb`: the standing-and-listening-to-music workflow. It loads a Polar HR file, an ACC file, and the session video; lines the video up with the sensor data; extracts audio features (loudness, spectral flux, spectral centroid); computes instant heart rate, RMSSD, and movement; renders side-by-side and portrait videos with scrolling graphs; and runs correlation and lag analyses between the music, the movement, and the heart. Rename your copy with the horse's name and the session date and time. Needs moviepy 1.0.3 (pinned in the install cell) and ffmpeg, both present in Colab.
- `equipro/`: two scripts for a folder of EquiPro stride tables, one file per session, with plots over time and left-right comparisons. See `equipro/README.md`.
- `polar/`: two scripts for raw Polar ECG files: plot a window, find the R-peaks, compute HRV metrics. See `polar/README.md`.
- `../Final_Project_Reel_Generator.ipynb` (repo root): makes a 9:16 reel of a session video with scrolling heart rate, RMSSD, loudness, and spectral centroid graphs. Needs the video, the Polar HR file, and the time lag between the two.

## How to run

Open a notebook in Colab with the badge at its top and run the cells in order; upload your files when prompted. For the scripts, follow the README in each folder. Sample data to practice on: `labs/Horses-and-Music/data` (standing HR files), `labs/horse_heart_VdP` (an ECG), and `labs/Gait-1/data` (EquiPro stride tables).

## Credit

EquiPhysics, Sonoita, Arizona. Data from our own horses. Released under the MIT License; please credit EquiPhysics if you adapt these materials.
