"""Package the rendered slides as a PowerPoint file with speaker notes.

Each slide is a full-resolution render. Slides with builds (builds.json) start from a base image and
reveal the rest click by click: every click fades in a transparent overlay, so students see one idea at a time.
Dr. Waris's original notes are kept on their slides; slides added for this course carry a note marked [Added].
"""
import glob
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu
from lxml import etree

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
    39: (f"[Added, real data] After the first cell. {S['band_n']} mixes at 28 days have a w/c between 0.49 and 0.54; their "
         f"strengths range from {S['band_min']:.0f} to {S['band_max']:.0f} MPa. The ratio alone does not fix the strength: "
         f"slag, fly ash, superplasticizer and aggregates matter too. That is why we bring all the inputs together with ML."),
    40: "Replace 'Link shared in the session chat' with the real notebook link if you want it on the slide.",
    42: "[Added] Optional practice before session 02.",
    37: "[Added, real data] Session 01 covers pandas: load the whole lab record in one line. df.shape gives (1030, 9): one row per mix, eight inputs and the strength. The table shows the real first five rows. Column names follow a common CSV release of the UCI dataset; match them to the workshop notebook.",
    38: "[Added, real data] First plot with Matplotlib. Ask the cohort what they notice: tests happen at fixed ages (3, 7, 28, 56, 90 days ...), strength rises with age, and at every age the spread is wide. Age alone cannot predict strength.",
}

EMU_PER_PX = 12192000 // 1920  # 16:9 slide, 1920 px wide renders
P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def fade_transition() -> etree._Element:
    return etree.fromstring(f'<p:transition xmlns:p="{P}" spd="med"><p:fade/></p:transition>')


def click_fades(shape_ids: list[int]) -> etree._Element:
    """Main-sequence timing: each shape fades in on its own click (PowerPoint preset 10, 'Fade')."""
    ids = iter(range(3, 10_000))
    clicks = []
    for spid in shape_ids:
        outer, inner, eff, setv, anim = (next(ids) for _ in range(5))
        clicks.append(f"""
      <p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>
        <p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
          <p:par><p:cTn id="{eff}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">
            <p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
              <p:set><p:cBhvr><p:cTn id="{setv}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
                <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>
                <p:to><p:strVal val="visible"/></p:to></p:set>
              <p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{anim}" dur="400"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>
            </p:childTnLst></p:cTn></p:par>
        </p:childTnLst></p:cTn></p:par>
      </p:childTnLst></p:cTn></p:par>""")
    xml = f"""<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>
    <p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{''.join(clicks)}
    </p:childTnLst></p:cTn>
    <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
    <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>
  </p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"""
    return etree.fromstring(xml)


out_dir = sys.argv[1] if len(sys.argv) > 1 else "export"
manifest = json.loads(Path(out_dir, "builds", "manifest.json").read_text())
prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
files = sorted(glob.glob(f"{out_dir}/slides/slide-*.png"), key=lambda f: int(re.search(r"(\d+)\.png$", f).group(1)))
clicks = 0
for i, f in enumerate(files, 1):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    steps = manifest.get(str(i), [])
    base = f"{out_dir}/builds/slide-{i:02d}-0.png" if steps else f
    slide.shapes.add_picture(base, 0, 0, prs.slide_width, prs.slide_height).name = f"Slide {i}"
    overlay_ids = []
    for st in steps:
        pic = slide.shapes.add_picture(f"{out_dir}/builds/{st['file']}", Emu(st["x"] * EMU_PER_PX), Emu(st["y"] * EMU_PER_PX),
                                       Emu(st["w"] * EMU_PER_PX), Emu(st["h"] * EMU_PER_PX))
        pic.name = f"Click {st['step']}"
        overlay_ids.append(pic.shape_id)
    slide._element.append(fade_transition())
    if overlay_ids:
        slide._element.append(click_fades(overlay_ids))
        clicks += len(overlay_ids)
    note = ORIGINAL_NOTES.get(i) or ADDED_NOTES.get(i)
    if steps:
        note = (note + "\n\n" if note else "") + f"[Clicks on this slide: {len(steps)}]"
    if note:
        slide.notes_slide.notes_text_frame.text = note
prs.save(f"{out_dir}/Session-01_From-Engineering-Problems-to-Python.pptx")
print(f"pptx: {len(files)} slides, {clicks} click animations")
