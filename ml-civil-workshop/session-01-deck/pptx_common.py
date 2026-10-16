"""Shared by both PowerPoint builds: speaker notes, slide transition and click-animation timing."""
from lxml import etree

import charts

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
STAGGER_MS = 120


def _notes() -> dict[int, str]:
    charts.build()
    S = charts.STATS
    a_s, v_s, a_e, v_e = S["age_hero"]
    original = {  # new slide number: Dr. Waris's own speaker notes from the original deck
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
    added = {
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
        37: "[Added, real data] Session 01 covers pandas: load the whole lab record in one line. df.shape gives (1030, 9): one "
            "row per mix, eight inputs and the strength. The table shows the real first five rows. Column names follow a "
            "common CSV release of the UCI dataset; match them to the workshop notebook.",
        38: "[Added, real data] First plot with Matplotlib. Ask the cohort what they notice: tests happen at fixed ages "
            "(3, 7, 28, 56, 90 days ...), strength rises with age, and at every age the spread is wide. Age alone cannot "
            "predict strength.",
        39: (f"[Added, real data] After the first cell. {S['band_n']} mixes at 28 days have a w/c between 0.49 and 0.54; their "
             f"strengths range from {S['band_min']:.0f} to {S['band_max']:.0f} MPa. The ratio alone does not fix the "
             f"strength: slag, fly ash, superplasticizer and aggregates matter too. That is why we bring all the inputs "
             f"together with ML."),
        40: "Replace 'Link shared in the session chat' with the real notebook link if you want it on the slide.",
        42: "[Added] Optional practice before session 02.",
    }
    return {**added, **original}


NOTES = _notes()


def note_for(slide_no: int, clicks: int) -> str:
    note = NOTES.get(slide_no, "")
    if clicks:
        note = (note + "\n\n" if note else "") + f"[Clicks on this slide: {clicks}]"
    return note


def transition() -> etree._Element:
    return etree.fromstring(f'<p:transition xmlns:p="{P}" spd="med"><p:fade/></p:transition>')


def _effect(ids, spid: int, kind: str, node_type: str, delay: int) -> str:
    """One entrance effect. 'float' = PowerPoint's Float In (fade while rising slightly), 'fade', 'wipe' (from left)."""
    eff, setv = next(ids), next(ids)
    show = (f'<p:set><p:cBhvr><p:cTn id="{setv}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>')
    if kind == "float":
        preset, sub, dur = 42, 0, 600
        body = (f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
                + "".join(
                    f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}" fill="hold"/>'
                    f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst>'
                    f'</p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="{v0}"/></p:val></p:tav>'
                    f'<p:tav tm="100000"><p:val><p:strVal val="{v1}"/></p:val></p:tav></p:tavLst></p:anim>'
                    for attr, v0, v1 in (("ppt_x", "#ppt_x", "#ppt_x"), ("ppt_y", "#ppt_y+.04", "#ppt_y"))))
    elif kind == "wipe":
        preset, sub, dur = 22, 8, 500
        body = (f'<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
    else:
        preset, sub, dur = 10, 0, 500
        body = (f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
    return (f'<p:par><p:cTn id="{eff}" presetID="{preset}" presetClass="entr" presetSubtype="{sub}" fill="hold" grpId="0" '
            f'nodeType="{node_type}"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>{show}{body}'
            f'</p:childTnLst></p:cTn></p:par>')


def timing(clicks: list[list[tuple[int, str]]], text_shape_ids: set[int] = frozenset()) -> etree._Element:
    """Main sequence: one entry per click; each click lists (shape id, effect) pairs.
    The first shape of a click starts on the click; the rest start 'with previous', each a little later (a stagger)."""
    ids = iter(range(3, 100_000))
    pars = []
    for shapes in clicks:
        outer, inner = next(ids), next(ids)
        effects = "".join(_effect(ids, spid, kind, "clickEffect" if j == 0 else "withEffect", j * STAGGER_MS)
                          for j, (spid, kind) in enumerate(shapes))
        pars.append(f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                    f'<p:childTnLst><p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                    f'<p:childTnLst>{effects}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    bld = "".join(f'<p:bldP spid="{s}" grpId="0" animBg="1"/>' for s in sorted(text_shape_ids))
    xml = (f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
           f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
           f'<p:childTnLst>{"".join(pars)}</p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           f'</p:childTnLst></p:cTn></p:par></p:tnLst>{f"<p:bldLst>{bld}</p:bldLst>" if bld else ""}</p:timing>')
    return etree.fromstring(xml)
