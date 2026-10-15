"""Package the rendered slides as a PowerPoint file with speaker notes.

Each slide is the full-resolution render; Dr. Waris's original notes are kept on their slides,
and every slide added for this course carries a short presenter note marked [Added].
"""
import glob
import re
import sys

from pptx import Presentation
from pptx.util import Emu

import charts

charts.build()
S = charts.STATS
a_s, v_s, a_e, v_e = S["age_hero"]

ORIGINAL_NOTES = {  # new slide number: original deck's speaker notes
    8: """Slide 2 — Start with an engineering problem

They are not learning an alien computer problem.
They are solving an engineering problem with another tool.""",
    10: """Slide 3 — Civil Engineers already use models

Speaker point
"We already build models. We use equations, correlations, numerical models, experiments and design standards. Machine learning doesn't suddenly replace engineering thinking. It gives us another way to represent relationships when we have sufficient data.\"""",
    11: """Slide — Why are we talking about AI?

What you say
"You will hear these three terms constantly, so let's establish the vocabulary first.
Artificial Intelligence is the broadest term.
Machine Learning is one approach within AI, where algorithms learn patterns from data.
Deep Learning is a family of machine-learning methods based on neural networks with multiple layers."

Then immediately:
"For this workshop, ML is our main focus. We will touch deep learning later when we reach Artificial Neural Networks."
That is enough.""",
    12: "Slide — AI, ML and DL: one engineering example",
    19: """Speaker point
"This little diagram is going to follow us throughout the course. X is the information we give the model. y is what we want it to predict."

Then give the Energy and Steel examples verbally.""",
    21: """Slide 6 — One workflow. Many engineering problems.
This should be one of the signature slides of the course.

The engineering problem changes. The dataset changes. The target changes. But the basic workflow survives.""",
}

ADDED_NOTES = {
    9: (f"[Added] Real data: 1,030 laboratory mixes (UCI Concrete Compressive Strength, Yeh 1998). "
        f"Left: {S['age_curves']} mixes tested at four or more ages; one slag mix went from {v_s:.0f} MPa at {a_s} days "
        f"to {v_e:.0f} MPa at {a_e} days. Right: an Abrams-type curve fitted to {S['n28']} mixes at 28 days explains only "
        f"{S['abr_r2'] * 100:.0f}% of the variation (R² = {S['abr_r2']:.2f}). Message: one input at a time leaves much "
        f"unexplained; ML can use all the inputs together."),
    13: "Arthur Samuel's 1959 definition. Samuel worked at IBM; his checkers program improved by playing against itself.",
    14: "[Layout added] From the original slide 6: 'Machine learning algorithms: Supervised / Unsupervised'. "
        "Supervised: every example has its label y. Unsupervised: only X, no label.",
    15: "Table from the original slide 6. Two civil engineering rows added at the bottom for this course.",
    17: (f"[Real data] Left: regression, 28-day strength against water-cement ratio with the Abrams-type fit. "
         f"Right: the same {S['n28']} mixes with the target changed to 'does the mix reach 40 MPa?'. A logistic regression "
         f"on binder content and water is right {S['cls_acc'] * 100:.0f}% of the time, against {S['cls_base'] * 100:.0f}% "
         f"for always guessing 'below 40'. The boundary roughly follows a constant water-binder ratio: engineering "
         f"knowledge is visible in the model."),
    18: ("[Real data] k-means with three groups on the slag share and fly-ash share of the binder; no strength labels used. "
         "Groups found: " + ", ".join(f"{k} {v} mixes" for k, v in S["clusters"].items()) + ". "
         "Dimensionality reduction compresses data into fewer variables (dimensions)."),
    20: "[Added] Vocabulary for the whole course: X features, y target/label, ŷ prediction, f model, dataset, training.",
    22: "[Added] Give the cohort two minutes and ask them to vote in the chat. Answers on the next slide.",
    23: "[Added] Answers: 1 regression, 2 classification, 3 clustering (unsupervised), 4 anomaly detection (unsupervised), "
        "5 regression, 6 classification.",
    27: "Python supports the workflow; engineering knowledge supplies the meaning.",
    37: (f"[Added, real data] After the first cell. {S['band_n']} mixes at 28 days have a w/c between 0.49 and 0.54; their "
         f"strengths range from {S['band_min']:.0f} to {S['band_max']:.0f} MPa. The ratio alone does not fix the strength: "
         f"slag, fly ash, superplasticizer and aggregates matter too. That is why we bring all the inputs together with ML."),
    38: "Replace 'Link shared in the session chat' with the real notebook link if you want it on the slide.",
    40: "[Added] Optional practice before session 02.",
}

out_dir = sys.argv[1] if len(sys.argv) > 1 else "export"
prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
files = sorted(glob.glob(f"{out_dir}/slides/slide-*.png"), key=lambda f: int(re.search(r"(\d+)\.png$", f).group(1)))
for i, f in enumerate(files, 1):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_picture(f, 0, 0, prs.slide_width, prs.slide_height)
    note = ORIGINAL_NOTES.get(i) or ADDED_NOTES.get(i)
    if note:
        slide.notes_slide.notes_text_frame.text = note
prs.save(f"{out_dir}/Session-01_From-Engineering-Problems-to-Python.pptx")
print(f"pptx: {len(files)} slides, notes on {sorted(set(ORIGINAL_NOTES) | set(ADDED_NOTES))}")
