"""Build the Horse Artery Lab worksheet and teacher guide (with answer key).
Numbers come from answer_numbers.json (make_numbers_and_figures.py), so they match the notebook."""
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt, RGBColor

KIT = Path(__file__).resolve().parents[1]  # the lab folder
PKG_ROOT = KIT if (KIT / "horse1d").is_dir() else KIT.parent  # horse1d/ is inside the lab folder or next to it
sys.path.insert(0, str(PKG_ROOT))
from horse1d import paper  # noqa: E402

FIG = KIT / "figures"
LOGO = KIT / "build" / "logo.png"
N = json.load(open(KIT / "build" / "answer_numbers.json"))
INDIGO = RGBColor(0x1c, 0x27, 0x57)
GREY = RGBColor(0x66, 0x66, 0x66)
NB = "Horse_Artery_Lab.ipynb"
COLAB = ("https://colab.research.google.com/github/equiphysics/education/blob/"
         "main/labs/Horse-Artery-Lab/Horse_Artery_Lab.ipynb")

L, S, K, H60 = N["lying"], N["standing"], N["lying_stiff"], N["lying_hr60"]
site = lambda run, name, key: run["sites"][name][key]
AH, AHIP, CCA, MA, EIA = "Aorta by the heart", "Aorta at the hips", "Carotid (neck)", "Median (front leg)", "Ext. iliac (hind leg)"
h_cca, h_ma = N["heights"][CCA], N["heights"][MA]
dh = h_cca - h_ma
rgh = 1050 * 9.81 * dh / 133.3
ft26, ft86 = L["foot_times"]["26.4"] * 1000, L["foot_times"]["86.4"] * 1000
pwv_hand = 0.60 / ((ft86 - ft26) / 1000)
STUDY_U = dict(zip([AH, AHIP, CCA, MA, EIA], paper.TABLE4["peak_U"]["no_gravity"]))
MEAS_PP = dict(zip([AH, AHIP, CCA, MA, EIA], paper.TABLE4["PP"]["in_vivo"]))
G0 = paper.GLOBAL["no_gravity"]


def signed(x, nd=2):
    """A number with an explicit sign and a true minus sign (U+2212), for print."""
    return f"{x:+.{nd}f}".replace("-", "\u2212")


# ---------- docx helpers (same look as the Gait Lab and Heart Lab kits) ----------
def new_doc(margins=0.8):
    d = Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(margins)
        s.top_margin = s.bottom_margin = Inches(0.7)
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    return d


def kicker(d, text):
    p = d.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = INDIGO
    p.paragraph_format.space_after = Pt(0)


def title(d, text, size=24):
    p = d.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = INDIGO
    p.paragraph_format.space_after = Pt(2)


def sub(d, text):
    p = d.add_paragraph()
    r = p.add_run(text); r.italic = True; r.font.size = Pt(10.5); r.font.color.rgb = GREY


def h1(d, text): d.add_heading(text, level=1)
def h2(d, text): d.add_heading(text, level=2)
def h3(d, text): d.add_heading(text, level=3)


def para(d, text, bold_lead=None, size=None, italic=False):
    p = d.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead + " "); r.bold = True
    r = p.add_run(text); r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def bullets(d, items):
    for it in items:
        p = d.add_paragraph(style="List Bullet")
        if isinstance(it, tuple):
            r = p.add_run(it[0] + " "); r.bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)


def table(d, rows, header=True, widths=None, font=10):
    if d.paragraphs:  # keep the question or heading above the table on the same page
        d.paragraphs[-1].paragraph_format.keep_with_next = True
    tb = d.add_table(rows=len(rows), cols=len(rows[0]))
    tb.style = "Table Grid"
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = tb.cell(i, j); c.text = ""
            r = c.paragraphs[0].add_run(str(val)); r.font.size = Pt(font)
            if header and i == 0:
                r.bold = True
            if widths:
                c.width = Inches(widths[j])
            if i < len(rows) - 1:
                c.paragraphs[0].paragraph_format.keep_with_next = True
        tb.rows[i]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    d.add_paragraph()
    return tb


def qr_png(url):
    """A QR code for url, as an in-memory PNG."""
    import io
    import qrcode
    buf = io.BytesIO()
    qrcode.make(url, box_size=10, border=2).save(buf, format="PNG")
    buf.seek(0)
    return buf


def answer_lines(d, n=2):
    for _ in range(n):
        p = d.add_paragraph("_" * 86)
        p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)


# ============================================================ WORKSHEET
d = new_doc(0.75)
hdr = d.add_table(rows=1, cols=2); hdr.style = "Table Grid"
c0, c1 = hdr.cell(0, 0), hdr.cell(0, 1)
c0.width, c1.width = Inches(5.3), Inches(1.7)
p = c0.paragraphs[0]
r = p.add_run("EQUIPHYSICS LESSON · 2026\n"); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = INDIGO
r = p.add_run("Horse Artery Lab\n"); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = INDIGO
r = p.add_run("Blood pressure from heart to hoof, in a computer horse. A worksheet for the Colab notebook."); r.font.size = Pt(10)
p = c1.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(LOGO), width=Inches(1.1))
d.add_paragraph()
table(d, [["Name", "Partner"], ["", ""]], widths=[3.5, 3.5])

h2(d, "BEFORE YOU START")
box = d.add_table(rows=1, cols=2)  # no borders: text on the left, QR code on the right
b0, b1 = box.cell(0, 0), box.cell(0, 1)
b0.width, b1.width = Inches(5.5), Inches(1.5)
b0.paragraphs[0].add_run("Open the notebook in Google Colab: scan the code, use the link your teacher shares, or go "
                         "to github.com/equiphysics/education, open labs/Horse-Artery-Lab, and click Open in Colab. "
                         "Sign in with a Google account. If Colab warns that the notebook was not written by Google, "
                         "click Run anyway. Run the Setup cell, then section 1. The red dots on the map are the five "
                         "places you will measure. Each new horse takes about a minute to run, so start the runs in "
                         "section 3 right away and read ahead while they work.")
p = b1.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(qr_png(COLAB), width=Inches(1.25))
r = p.add_run("\nOpen in Colab"); r.font.size = Pt(8); r.font.color.rgb = GREY
d.add_picture(str(FIG / "fig_arteries_sites.png"), width=Inches(4.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

h2(d, "A · Meet the model (10 min)")
para(d, "A1.  The heart in the model beats 40 times a minute. How many seconds does one heartbeat last?")
answer_lines(d, 1)
para(d, "A2.  Run section 5 and write the three Womersley numbers.")
table(d, [["Artery", "Womersley number α"], ["Horse aorta", ""], ["Human aorta", ""], ["Horse median artery (front leg)", ""]],
      widths=[3.0, 2.0])
para(d, "A3.  Whose aorta has the bigger Womersley number, the horse's or yours? What does a big Womersley number "
        "tell you about how blood moves near the artery wall? (Read the text above the cell.)")
answer_lines(d, 2)

h2(d, "B · Lying down and standing up (15 min)")
para(d, "B1.  Predict before you run. In a standing horse, where do you expect the average blood pressure to be "
        "highest: in the head, at the heart, or in the front leg? Why?")
answer_lines(d, 2)
para(d, "B2.  In section 3, run horse A lying down and horse B standing up, both at 40 beats/min and stiffness 1 "
        "(the starting settings). Fill in the mean pressures from the printed table.")
table(d, [["Site", "Lying: mean (mmHg)", "Standing: mean (mmHg)", "Change (standing − lying)"],
          [AH, "", "", ""], [CCA, "", "", ""], [MA, "", "", ""], [EIA, "", "", ""]], widths=[2.1, 1.6, 1.7, 1.8])
para(d, "B3.  In the standing horse, how much higher is the mean pressure in the median artery than in the carotid? "
        "Now check it with gravity alone. Section 4 lists how high each site sits above the heart. Find the height "
        "difference h between the two sites and work out ρgh in mmHg (ρ = 1050 kg/m³, g = 9.81 m/s², "
        "1 mmHg = 133.3 Pa). How close are the two answers?")
table(d, [["Median − carotid in the model (mmHg)", "Height difference h (m)", "ρgh (mmHg)"], ["", "", ""]],
      widths=[2.6, 2.0, 1.6])
para(d, "B4.  Compare the cardiac output and the share of blood going to the brain, lying and standing. "
        "What changed? Why might standing do that to a horse that has no reflexes?")
answer_lines(d, 2)
para(d, "B5.  Look at the two pressure maps. Describe the color pattern of each in one sentence.")
answer_lines(d, 2)

h2(d, "C · The pulse travels (15 min)")
para(d, "Use the last figure in section 3 and the lying horse (black).").paragraph_format.keep_with_next = True
para(d, "C1.  From the left panel, fill in the table. How can the peak pressure rise along the aorta while the "
        "average pressure stays the same?")
table(d, [["Distance from the heart", "Systolic (mmHg)", "Mean (mmHg)"], ["26 cm", "", ""], ["86 cm", "", ""]],
      widths=[2.2, 1.7, 1.7])
answer_lines(d, 2)
para(d, "C2.  In the right panel, read when the pulse arrives at 26 cm and at 86 cm. Work out the pulse wave speed: "
        "the distance it travels divided by the time it takes. The study measured 5.27 m/s in a real horse. "
        "How close is the model?")
table(d, [["Arrives at 26 cm (ms)", "Arrives at 86 cm (ms)", "Wave speed (m/s)"], ["", "", ""]], widths=[2.1, 2.1, 1.8])
para(d, "C3.  In the blood-speed plots, at which sites does the blood flow backward for a moment (speed below zero)? "
        "What could push blood backward in an artery?")
answer_lines(d, 2)

h2(d, "D · Stiffer arteries (10 min)")
para(d, "D1.  Predict: if every artery were 1.5 times stiffer, what would happen to the pulse pressure in the aorta, "
        "and to the pulse wave speed?")
answer_lines(d, 1)
para(d, "D2.  Run horse A lying, 40 beats/min, stiffness 1, and horse B lying, 40 beats/min, stiffness 1.5.")
table(d, [["Stiffness", "Aortic pressure (sys/dia, mmHg)", "Pulse pressure (mmHg)", "Pulse wave speed (m/s)"],
          ["1", "", "", ""], ["1.5", "", "", ""]], widths=[1.0, 2.3, 1.8, 1.9])
para(d, "D3.  For a simple elastic tube, the wave speed goes as c ≈ √(1/(ρD)), where D measures how easily the wall "
        "stretches. If D falls by a factor of 1.5, by what factor should c rise? Did the model's wave speed rise that "
        "much? (Hint: compare the diastolic pressures. The model's arteries get softer at low pressure.)")
answer_lines(d, 2)
para(d, "D4.  Older horses have stiffer arteries. Why might a bigger pulse pressure matter to an artery wall?")
answer_lines(d, 1)

h2(d, "E · A faster heart (10 min)")
para(d, "E1.  Predict: if the heart beats 60 times a minute instead of 40 (horse lying down), what happens to the "
        "stroke volume (blood per beat), the cardiac output (blood per minute), and the blood pressure?")
answer_lines(d, 1)
para(d, "E2.  Run horse A lying, 40 beats/min, and horse B lying, 60 beats/min, both with stiffness 1.")
table(d, [["Heart rate", "Cardiac output (L/min)", "Stroke volume (ml)", "Aortic pressure (mmHg)"],
          ["40", "", "", ""], ["60", "", "", ""]], widths=[1.2, 2.0, 1.8, 2.0])
para(d, "E3.  Why does the stroke volume fall when the heart beats faster?")
answer_lines(d, 1)
para(d, "E4.  At a gallop a horse's heart rate climbs past 200 and its cardiac output rises about eightfold, "
        "yet its blood pressure rises far less. What does a real horse do that this model cannot?")
answer_lines(d, 2)

h2(d, "F · Models and measurements (10 min)")
para(d, "F1.  Run section 6. Name one number where our model matches the study's model well, and one where they differ.")
answer_lines(d, 2)
para(d, "F2.  In standing horses the study measured a peak blood speed in the carotid of 0.85 m/s and a carotid "
        "pulse pressure of 33 mmHg. Write the standing model's values (horse B in section 3). Give two reasons a model "
        "of an average horse might not match measurements in real horses.")
answer_lines(d, 3)
para(d, "F3.  Name one thing the model leaves out, and one thing today that surprised you.")
answer_lines(d, 2)
d.save(KIT / "Horse_Artery_Lab_Worksheet.docx")


# ============================================================ TEACHER GUIDE
d = new_doc(1.0)
kicker(d, "EQUIPHYSICS LESSON MODULE")
title(d, "Horse Artery Lab")
sub(d, "A 75-minute facilitator guide for college classes and advanced high school")
para(d, f"Developed by Laura Miller / EquiPhysics  ·  equiphysics.org  ·  Notebook: {NB} (Google Colab)", size=10)

h1(d, "What this is")
para(d, "Horse Artery Lab is a hands-on computer lab about blood pressure and pressure waves in a horse. Students run "
        "a published model of a horse's arteries: 117 arteries from the heart to the head, the four legs, and the gut, "
        "with a beating heart at one end and 62 tissue beds at the other. They stand the horse up and watch gravity "
        "drain pressure from the head and pile it into the legs, follow the pulse as it races down the aorta at five "
        "meters a second, stiffen the arteries the way age does, speed up the heart, and finally hold the model up "
        "against measurements made in real horses.")
para(d, "The model comes from Vera et al. (2019, PLoS ONE), a study by veterinarians and engineers at Ghent University "
        "and EPFL. EquiPhysics rewrote it in Python and checked it against the study: for a resting horse it reproduces "
        "the study's cardiac output, blood pressures, and pulse wave speed within a few percent, both lying and standing. "
        "Everything runs in Google Colab in a browser. There is nothing to install.")

h2(d, "Learning goals")
bullets(d, [
    "Read systolic, diastolic, mean, and pulse pressure off a waveform, and say what each one means.",
    "Explain how gravity changes blood pressure in a tall animal, and check the model with ρgh.",
    "Describe the arterial pulse as a wave: measure its speed, and explain why its peak grows on the way to the legs.",
    "Predict and test how artery stiffness and heart rate change pressure, flow, and wave speed.",
    "Compare a model with measurements, and name what a model leaves out.",
])

h2(d, "Audience and prerequisites")
para(d, "College courses in math biology, biomechanics, physiology, biomedical engineering, or physics; advanced high "
        "school with support. Students need ρgh, unit conversion, and reading graphs. No coding is needed: students "
        "move sliders and run cells. Students who know some Python can open the model files and change anything.")

h1(d, "Materials and tech setup")
h3(d, "For 20–30 students working in pairs")
bullets(d, [
    "One laptop or Chromebook per pair, each with a Google account (Colab needs one). A phone works but is cramped.",
    "The notebook. It opens in Colab from the Open in Colab link in the lab's folder at github.com/equiphysics/education "
    "(labs/Horse-Artery-Lab), or from the QR code on the worksheet. Students sign in with a Google account; "
    "File → Save a copy in Drive keeps their own copy.",
    "Printed worksheets (Horse_Artery_Lab_Worksheet.docx), one per student.",
    "A projector for the opening question and the debrief.",
])
h3(d, "Before the session (20 minutes)")
bullets(d, [
    "Open the notebook in Colab and use Runtime → Run all. Colab asks you to confirm a notebook from GitHub: click "
    "Run anyway. It takes two to three minutes. Look at every figure once.",
    "In section 3, run standing at 35 beats/min with stiffness 1.5 once, so you have seen the model's breakdown "
    "message. A student will find it, and it makes a good discussion.",
    "Print the worksheets. The figures in this guide come straight from the notebook.",
])
h3(d, "Run times")
para(d, "Each new horse takes about a minute in Colab (eight heartbeats of a 117-artery model). A horse that has already "
        "run comes back instantly, as long as the Colab session stays open. Have pairs start the section 3 runs as soon "
        "as setup finishes and work on Part A while they run. Restarting the session clears the saved runs.")

h1(d, "75-minute timing")
table(d, [["Time", "Phase", "Who", "What is happening"],
          ["0–5", "Hook", "Facilitator", "A horse's head is about a meter above its heart. What does that do to blood "
                                          "pressure in the head? Show the two pressure maps (figure below)."],
          ["5–10", "Setup", "Pairs", "Open the notebook, run Setup and section 1, start the section 3 runs."],
          ["10–20", "Part A", "Pairs", "Meet the model; Womersley numbers for horse and human."],
          ["20–35", "Part B", "Pairs", "Lying versus standing; the ρgh check; blood to the brain."],
          ["35–50", "Part C", "Pairs", "The pulse travels: amplification along the aorta, wave speed, backflow."],
          ["50–60", "Part D", "Pairs", "Stiffer arteries: pulse pressure and wave speed."],
          ["60–68", "Part E", "Pairs", "A faster heart: stroke volume and cardiac output."],
          ["68–75", "Part F + debrief", "Everyone", "Model versus measurements; what the model leaves out."]],
      widths=[0.6, 1.0, 0.9, 4.0], font=9.5)
para(d, "Short on time? For a 50-minute class, do A, B, C, and F and leave D and E as homework.", italic=True)
d.add_picture(str(FIG / "fig_map_mean_lying_standing.png"), width=Inches(6.5))
para(d, "Mean blood pressure in every artery of a resting horse, lying (left) and standing (right), on one color scale.",
     italic=True, size=9.5)

h1(d, "Background primer for the facilitator")
para(d, "You do not need to teach this directly. It is here so you have an answer when a student asks why.")
h3(d, "A horse's circulation in numbers")
para(d, f"A 650-kg warmblood at rest pumps about 33 liters of blood a minute, five times what a person pumps, with a "
        f"heart rate near 40 and about 800 ml per beat. Its aorta is about 7 cm across where it leaves the heart, and "
        f"its arterial tree is more than 9 meters long in total. Blood pressure is similar to ours, about 115/70 mmHg "
        f"at the heart. In the model the head sits about a meter above the heart and the lower front leg about 0.3 m "
        f"below it. The model's leg arteries end partway down the legs; everything below is lumped into tissue beds.")
h3(d, "Four pressures")
para(d, "Systolic pressure is the peak of each beat; diastolic is the lowest point, just before the next beat; mean "
        "pressure is the average over a beat; pulse pressure is systolic minus diastolic. Mean pressure is set by how "
        "much blood flows and how hard the small vessels resist it. Pulse pressure is set by how much blood each beat "
        "pushes out and how stretchy the big arteries are: stiffer arteries give a bigger pulse pressure.")
h3(d, "Gravity")
para(d, "A column of blood h meters tall presses down with ρgh: about 77 mmHg per meter of height. Lying flat, mean "
        "pressure is nearly the same in every big artery. Standing, it drops with every centimeter of height above the "
        "heart and rises below it. The model has no veins and no reflexes, so standing also sends less blood to the "
        "head: the pressure driving blood into the head beds falls, and their resistance stays fixed. Real horses "
        "keep brain flow steady with reflexes and autoregulation, and the veins draining the head help. The study "
        "chose this simplification on purpose; it is a good topic for the debrief.")
h3(d, "The pulse is a wave")
para(d, "Each heartbeat sends a pressure wave down the arteries at a few meters a second, much faster than the blood "
        "itself moves (under 1 m/s). The wave speed depends on stiffness: c ≈ √(1/(ρD)), where D is the wall's "
        "distensibility. Stiffer or smaller arteries carry faster waves. When the wave meets branches, narrowing, and "
        "stiffer vessels, part of it reflects back toward the heart. Forward and reflected waves add, so the pulse "
        "grows taller on its way to the legs (pressure amplification) while mean pressure hardly changes. Reflected "
        "waves also push blood briefly backward in some arteries after each beat. The model's wall gets stiffer as "
        "pressure rises, so the high-pressure peak of the wave travels faster than its foot, and the front steepens "
        "along the aorta.")
h3(d, "The Womersley number")
para(d, "α = R√(2πfρ/μ) compares the time a heartbeat takes with the time friction needs to reach the middle of the "
        "artery. In the horse's aorta α is about 35; in ours about 17. With a large α the core of the flow moves like a "
        "plug, friction acts only in a thin layer at the wall, and the simple Poiseuille formula for friction no longer "
        "applies to the pulsing part of the flow. The study used Womersley's theory for every artery with α above 3.")
h3(d, "The model, in one paragraph")
para(d, "In every artery the model solves two equations along its length for pressure and flow: conservation of mass "
        "(blood that flows in must flow out or stretch the wall) and momentum (pressure differences push the blood; "
        "friction and gravity hold it back). The wall law, the Womersley friction, gravity, the heart (a time-varying "
        "elastance with an internal resistance), the branching rules (equal pressure, no blood lost), and the 62 tissue "
        "beds (3-element Windkessels) all follow the study. The anatomy and tissue-bed values are the study's own data. "
        "Horse_Artery_Model_Overview.pdf gives the equations and every parameter.")
h3(d, "What the model leaves out, and where it misses")
bullets(d, [
    "Reflexes and autoregulation. Faster heart rates and stiffer arteries show the mechanics only.",
    "Veins, lungs, and breathing. The model ends at the tissue beds.",
    "Any one horse. The anatomy is an average from four warmbloods, and the wall stiffness formula comes from human "
    "data.",
    "A detailed head. In the study's settings the head arteries carry a lot of blood through narrow vessels. This is "
    "why a standing horse with a slow heart and stiff arteries can break the model (see Part B notes).",
    f"Where it misses: like the study's model, ours overestimates pulse pressure, by about 70%. A standing horse "
    f"gets {site(S, AH, 'PP'):.0f} mmHg at the heart and {site(S, CCA, 'PP'):.0f} in the carotid; the study measured "
    f"{MEAS_PP[AH]:.0f} and {MEAS_PP[CCA]:.0f} (the aortic value in one anesthetized horse, and anesthesia lowers "
    f"pulse pressure).",
])

h1(d, "Part-by-part facilitator notes")
h2(d, "Part A · Meet the model")
para(d, "Goal: students get oriented on the map and meet one number that makes horses different.")
bullets(d, [
    ("What success looks like:", "students find the five sites on the map and can say, in their own words, that a big "
                                 "Womersley number means the flow is dominated by the beat, not by friction."),
    ("Facilitator prompt:", "'A mouse's aorta has a Womersley number of about 2. What would its velocity profile look like?'"),
])
h2(d, "Part B · Lying down and standing up")
para(d, "Goal: students see gravity in the numbers and check it with a hand calculation.")
bullets(d, [
    ("What success looks like:", f"the hand calculation (about {rgh:.0f} mmHg) lands within 1 to 2 mmHg of the "
                                 f"model's difference ({site(S, MA, 'MAP') - site(S, CCA, 'MAP'):.0f} mmHg)."),
    ("Common sticking point:", "students subtract heights with the wrong sign. The median artery is below the heart, so "
                               "its height is negative; the difference is 0.48 − (−0.25) = 0.73 m."),
    ("Breakdown message:", "standing at 35 beats/min with stiffness 1.5, pressure in the head falls close to zero before "
                           "the next beat, the head arteries go soft, the blood outruns the pressure wave, and the 1D "
                           "equations fail. The notebook prints an explanation instead of an error. Ask what a real "
                           "horse does instead (reflexes, venous drainage)."),
])
h2(d, "Part C · The pulse travels")
para(d, "Goal: students see the pulse as a wave with a speed and a shape.")
bullets(d, [
    ("What success looks like:", f"students get a wave speed near {pwv_hand:.1f} m/s by hand and explain amplification "
                                 "with reflected waves."),
    ("Common sticking point:", "students confuse the speed of the wave (5 m/s) with the speed of the blood (under 1 m/s). "
                               "Ask: 'Does the blood itself reach the hind leg in 0.1 s?'"),
])
d.add_picture(str(FIG / "fig_aorta_lying_standing.png"), width=Inches(6.5))
para(d, "Left: systolic pressure grows along the aorta while mean pressure stays flat. Right: arrival time of the "
        "pulse; the slope is the wave speed.", italic=True, size=9.5)
h2(d, "Part D · Stiffer arteries")
para(d, "Goal: students connect wall stiffness to pulse pressure and wave speed, and meet a nonlinearity.")
bullets(d, [
    ("What success looks like:", "students predict a bigger pulse pressure and a faster wave, see both, and notice the "
                                 "wave speed rose less than √1.5."),
    ("Facilitator prompt:", "'Pulse wave velocity is used in human clinics as a measure of arterial age. Why would it work?'"),
])
h2(d, "Part E · A faster heart")
para(d, "Goal: students see that a faster heart pumps more per minute but less per beat, and that pressure regulation "
        "needs more than a pump.")
bullets(d, [
    ("Common sticking point:", "students expect stroke volume to stay the same. Point them to the time between beats: "
                               "1.5 s at 40 beats/min, 1.0 s at 60."),
])
h2(d, "Part F · Models and measurements")
para(d, "Goal: students hold a model to account without dismissing it.")
bullets(d, [
    ("Facilitator prompt:", "'The model gets cardiac output and the gravity effect right but overshoots pulse pressure. "
                            "Is it a good model? Good for what?'"),
])

h1(d, "Debrief and where this is used")
bullets(d, [
    "Veterinarians measure blood pressure in horses at the tail, below the heart. Gravity matters for reading it.",
    "Arterial rupture motivated the study. In horses it happens during exercise, during foaling (the uterine artery), "
    "and after some drugs, more often in older horses, and aortic rupture is more common in Friesians. Models like "
    "this one estimate the stresses on artery walls that cannot be measured safely.",
    "The same 1D models are used in human medicine to plan surgery, study aging arteries, and design heart devices.",
])
h1(d, "Extensions")
bullets(d, [
    "Change anything: the model's settings are in horse1d/params.py and the anatomy in horse1d/network.py.",
    "Compare Womersley and Poiseuille friction: set friction='poiseuille' in Params and compare peak blood speeds.",
    "Use a real heart rate: the Horse Heart Lab has Duque's resting and exercise heart rates from his strap. "
    "Remember the model has no exercise response.",
    "Wave power: horse1d/analysis.py separates the forward and reflected waves at any artery (the study's Fig 6).",
])

h1(d, "About the model and the data")
para(d, "Vera L, Campos Arias D, Muylle S, Stergiopulos N, Segers P, van Loon G (2019) built the model from post-mortem "
        "measurements of four warmblood horses (lengths, diameters, and branching angles of 117 arteries), ultrasound "
        "and pressure measurements in five standing horses, and an earlier human model (Reymond et al., 2009). The "
        "article and its supplementary data are open access under CC BY 4.0. EquiPhysics' Python version uses their "
        "anatomy and tissue-bed values. Where the article leaves a detail unstated, the choices are listed in the "
        "overview PDF. One heart setting was matched to the study's own numbers. The Python code and these materials are "
        "free under the MIT License at github.com/equiphysics/education.")

h1(d, "Answer key")
h3(d, "A · Meet the model")
para(d, "A1. 60 ÷ 40 = 1.5 s per beat.")
para(d, "A2. Horse aorta 35.7; human aorta 17.3; horse median artery 3.7.")
para(d, "A3. The horse's, about twice ours. With a big Womersley number the beat changes the flow faster than friction "
        "can reach the middle of the artery: the core moves like a plug, and friction acts in a thin layer at the wall.")
h3(d, "B · Lying down and standing up")
para(d, "B1. Prediction. The front leg: it is below the heart, so the weight of the blood above it adds pressure.")
para(d, f"B2. Mean pressures, lying → standing: aorta by the heart {site(L, AH, 'MAP'):.0f} → {site(S, AH, 'MAP'):.0f} "
        f"({signed(site(S, AH, 'MAP') - site(L, AH, 'MAP'), 0)}); carotid {site(L, CCA, 'MAP'):.0f} → {site(S, CCA, 'MAP'):.0f} "
        f"({signed(site(S, CCA, 'MAP') - site(L, CCA, 'MAP'), 0)}); median {site(L, MA, 'MAP'):.0f} → {site(S, MA, 'MAP'):.0f} "
        f"({signed(site(S, MA, 'MAP') - site(L, MA, 'MAP'), 0)}); external iliac {site(L, EIA, 'MAP'):.0f} → "
        f"{site(S, EIA, 'MAP'):.0f} ({signed(site(S, EIA, 'MAP') - site(L, EIA, 'MAP'), 0)}) mmHg. Pressure at the heart rises "
        "because, in a standing horse, almost all of the tissue beds sit above the heart: the gut and kidneys about "
        "0.2 m up and the head about 0.9 m up. In the model every bed drains to zero pressure whatever its height, so "
        "the heart has to push blood uphill to reach them.")
para(d, f"B3. {site(S, MA, 'MAP'):.0f} − {site(S, CCA, 'MAP'):.0f} = {site(S, MA, 'MAP') - site(S, CCA, 'MAP'):.0f} mmHg. "
        f"Heights: carotid {signed(h_cca)} m, median {signed(h_ma)} m, so h = {dh:.2f} m and ρgh = 1050 × 9.81 × {dh:.2f} = "
        f"{1050 * 9.81 * dh:.0f} Pa = {rgh:.0f} mmHg. Gravity explains almost all of the difference.")
para(d, f"B4. Cardiac output falls from {L['glob']['CO_L_min']:.1f} to {S['glob']['CO_L_min']:.1f} L/min; the brain's "
        f"share falls from {L['co']['brain']:.1f}% to {S['co']['brain']:.1f}%, and the limbs' rises from "
        f"{L['co']['muscle']:.1f}% to {S['co']['muscle']:.1f}%. Standing lowers the pressure that drives blood into the "
        "head and raises it in the legs, and with fixed resistances blood shifts from head to legs. The study found "
        "the same: 33 → 30 L/min, brain 15.4% → 10.5%. Real horses keep brain flow steady with reflexes.")
para(d, "B5. Lying: nearly one color everywhere; mean pressure barely changes along the big arteries. Standing: a smooth "
        "gradient with height, dark (low, about 40 mmHg) at the top of the head and bright (high, about 135–140 mmHg) "
        "at the bottom of the legs.")
h3(d, "C · The pulse travels")
para(d, f"C1. 26 cm: systolic {L['aorta']['26.4']['sys']:.0f}, mean {L['aorta']['26.4']['mean']:.0f} mmHg; 86 cm: "
        f"systolic {L['aorta']['86.4']['sys']:.0f}, mean {L['aorta']['86.4']['mean']:.0f} mmHg. The pulse grows as "
        "waves reflected from branches, narrower arteries, and the legs add to it, and its front steepens. The mean is "
        "set by flow and resistance; friction in the wide aorta is tiny, so the mean hardly drops. The pulse changes "
        "shape, not its average.")
para(d, f"C2. About {ft26:.0f} ms and {ft86:.0f} ms, so 0.60 m ÷ {(ft86 - ft26) / 1000:.3f} s = {pwv_hand:.1f} m/s, "
        f"within about {100 * abs(pwv_hand - 5.27) / 5.27:.0f}% of the 5.27 m/s measured in a horse.")
para(d, f"C3. The aorta at the hips (down to {signed(site(L, AHIP, 'min_U'))} m/s), the external iliac "
        f"({signed(site(L, EIA, 'min_U'))}), the median ({signed(site(L, MA, 'min_U'))}), and the aorta by the heart "
        "for an "
        "instant when the valve closes. The carotid never reverses: the head beds have a low resistance. Reflected "
        "pressure waves arriving from downstream push blood back for a moment.")
h3(d, "D · Stiffer arteries")
para(d, "D1. Prediction: both rise.")
para(d, f"D2. Stiffness 1: {L['glob']['SBP']:.0f}/{L['glob']['DBP']:.0f} mmHg, pulse pressure {L['glob']['PP']:.0f}, "
        f"wave speed {L['pwv']:.1f} m/s. Stiffness 1.5: {K['glob']['SBP']:.0f}/{K['glob']['DBP']:.0f} mmHg, pulse "
        f"pressure {K['glob']['PP']:.0f}, wave speed {K['pwv']:.1f} m/s.")
para(d, f"D3. √1.5 ≈ 1.22, so about {L['pwv'] * 1.2247:.1f} m/s. The model rose only to {K['pwv']:.1f} m/s "
        f"({K['pwv'] / L['pwv']:.2f} times). Diastolic pressure fell from {L['glob']['DBP']:.0f} to "
        f"{K['glob']['DBP']:.0f} mmHg, and the model's arteries are softer at lower pressure, which partly cancels the "
        "stiffening. The simple formula assumes the same pressure.")
para(d, "D4. A bigger swing in pressure means a bigger stretch with every beat, more than 50,000 beats a day, which "
        "wears the wall's elastic fibers. The study was motivated by artery ruptures, which are more common in "
        "older horses.")
h3(d, "E · A faster heart")
para(d, "E1. Prediction.")
para(d, f"E2. 40 beats/min: {L['glob']['CO_L_min']:.1f} L/min, {L['glob']['SV_ml']:.0f} ml, "
        f"{L['glob']['SBP']:.0f}/{L['glob']['DBP']:.0f} mmHg. 60 beats/min: {H60['glob']['CO_L_min']:.1f} L/min, "
        f"{H60['glob']['SV_ml']:.0f} ml, {H60['glob']['SBP']:.0f}/{H60['glob']['DBP']:.0f} mmHg.")
para(d, f"E3. There is less time to fill between beats, so the heart starts each beat with less blood "
        f"({L['glob']['EDV_ml']:.0f} ml at 40 beats/min, {H60['glob']['EDV_ml']:.0f} ml at 60).")
para(d, "E4. The arteries in working muscles open wide, so total resistance falls and cardiac output can rise far more than pressure; reflexes adjust the heart and the "
        "vessels; the heart contracts harder; and the spleen adds red blood cells. The model keeps every resistance "
        "and the heart's strength fixed.")
h3(d, "F · Models and measurements")
para(d, f"F1. Close: cardiac output ({L['glob']['CO_L_min']:.1f} vs {G0['CO_L_min']} L/min), aortic pressure "
        f"({L['glob']['SBP']:.0f}/{L['glob']['DBP']:.0f} vs {G0['SBP']}/{G0['DBP']}), wave speed ({L['pwv']:.1f} vs "
        f"{paper.PWV['no_gravity']} m/s), and the standing values. Different: peak blood speeds in the carotid "
        f"({site(L, CCA, 'peak_U'):.2f} vs {STUDY_U[CCA]:.2f} m/s) and the aorta at the hips "
        f"({site(L, AHIP, 'peak_U'):.2f} vs {STUDY_U[AHIP]:.2f} m/s).")
para(d, f"F2. Standing model: carotid peak speed {site(S, CCA, 'peak_U'):.2f} m/s, carotid pulse pressure "
        f"{site(S, CCA, 'PP'):.0f} mmHg. Good reasons: the anatomy is an average of a few horses; the wall stiffness "
        "comes from human data; no reflexes; the measurement point on the carotid differs from the model's; horses "
        "differ from each other; the model has no veins or breathing.")
para(d, "F3. Open.")

h1(d, "References")
bullets(d, [
    "Vera L, Campos Arias D, Muylle S, Stergiopulos N, Segers P, van Loon G (2019). A 1D computer model of the arterial "
    "circulation in horses: an important resource for studying global interactions between heart and vessels under "
    "normal and pathological conditions. PLoS ONE 14(8): e0221425. https://doi.org/10.1371/journal.pone.0221425",
    "Reymond P, Merenda F, Perren F, Rüfenacht D, Stergiopulos N (2009). Validation of a one-dimensional model of the "
    "systemic arterial tree. Am J Physiol Heart Circ Physiol 297: H208–H222.",
    "Womersley JR (1955). Method for the calculation of velocity, rate of flow and viscous drag in arteries when the "
    "pressure gradient is known. J Physiol 127: 553–563.",
    "Poole DC, Erickson HH (2011). Highly athletic terrestrial mammals: horses and dogs. Compr Physiol 1: 1–37.",
])
d.save(KIT / "Horse_Artery_Lab_Teacher_Guide.docx")
print("wrote worksheet and teacher guide")
