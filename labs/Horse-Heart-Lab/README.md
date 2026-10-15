# Horse Heart Lab

A 60-minute, phone-based classroom activity on how a horse's heart beats, built around the free web app at **https://equiphysics.github.io/web-apps/heart/** and real recordings from our own horse Duque.

Students watch a model heart beat, read its ECG (P, QRS, T), measure heart-rate variability (SDNN and RMSSD), see what a stochastic differential equation adds to the rhythm, and then build the beat themselves from a phase clock and five Gaussian bumps. At the end they compare the model with Duque's real standing, walking, and trotting recordings and find the beats the strap missed.

**Audience and level:** high school and early college. Biology, precalculus (angles, sine, square roots), and a little data reading. No horse experience needed.

## Files

| File | What it is |
|---|---|
| `Horse_Heart_Lab_Worksheet.docx` | Student worksheet with the QR code to the app (parts A to D) |
| `Horse_Heart_Lab_Teacher_Guide.docx` | Facilitator guide: timing, background primer, part-by-part notes, extensions, references |
| `Horse_Heart_Lab_Answer_Key.docx` | Expected answers and the numbers the app produces |
| `Horse_Heart_Lab.pptx` | Short slide deck for the hook and the wrap-up |
| `fig_model_vs_duque.png` | Duque's average beat at a walk and a trot next to the model with the app's default numbers |
| `fig_label_me.png` | One model beat with blank boxes for students to label |

## The model

The app uses the dynamical ECG model of McSharry, Clifford, Tarassenko, and Smith (IEEE Trans. Biomed. Eng. 50, 2003): a phase clock, dθ/dt = ω, with one Gaussian bump per wave placed at a fixed angle, ECG(θ) = Σ aᵢ exp(−(θ − θᵢ)²/2bᵢ²). Heart rate sets ω; breathing modulates ω (respiratory sinus arrhythmia); per-beat jitter and an optional dropped-beat switch add variability; and the P and T waves move toward the R wave in proportion to the square root of the RR interval (Bazett's rule) while the QRS keeps its width in milliseconds. The wave sizes and positions were fitted to Duque's own average beat. The heart-rate wander follows an Ornstein–Uhlenbeck stochastic differential equation, dx = −(x/τ)dt + σ dW, with a switch that turns the stochastic term off. The earlier Van der Pol version of this lab lives on in `labs/horse_heart_VdP` as the computational follow-up.

## The data

Duque wore a Polar Equine heart-rate strap (one ECG lead at 125 samples per second plus the strap's beat detector) during a ride on 14 November 2025, a lunging session on 19 January 2026, and quiet standing recordings on 27 February 2026. The raw files are in `labs/horse_heart_VdP`, `labs/Duque-Exercise`, and `labs/Horses-and-Music`. All measurements are noninvasive and made under approved animal-care protocols.

## Running it

Open https://equiphysics.github.io/web-apps/heart/ on any phone or laptop. Nothing to install. The app is a single HTML file in the `web-apps` repository (`heart/index.html`).

## Credit

Built by EquiPhysics, a 501(c)(3) nonprofit in Sonoita, Arizona. Released under the MIT License; please credit EquiPhysics if you adapt it.

## Help keep these lessons free

This lesson is free. If one helps you, you can [donate to EquiPhysics](https://www.equiphysics.org/donate). Can't give right now? You can still help a lot: share a lesson with another teacher, star this repository, and follow us on [GitHub](https://github.com/equiphysics), [Instagram](https://www.instagram.com/equiphysics_institute/), [Facebook](https://www.facebook.com/profile.php?id=61579151426160), and [LinkedIn](https://www.linkedin.com/company/equiphysics-institute/). Follows and shares help us show grant funders that people use and value this work. For news a few times a year, [sign up here](https://www.equiphysics.org/#news).
