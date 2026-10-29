"""Shared by both PowerPoint builds (Session 05): speaker notes, chart slides, slide transition and click-animation timing."""
from lxml import etree

import charts

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
STAGGER_MS = 120


CHART_SLIDES = {8, 11, 22, 25, 26, 33, 35, 40, 45, 48}   # slides whose builds are charts: fade instead of float


def _notes() -> dict[int, str]:
    """Presenter notes, one per slide. Numbers come from data/results.json so they always match the slides.
    Dr. Waris's own explanations from the notebook are kept where they belong."""
    R = charts.R
    T, sp, ex, cw = R["test"], R["split"], R["example"], R["cw"]
    lr, dt, rf = T["Logistic regression"], T["Decision tree"], T["Random forest"]
    n, n_un = R["n"], R["counts"]["1.0"]["below"]
    th = {t["t"]: t for t in R["thr"]}
    return {
        1: "Welcome to Session 05. Today the answer is not a number but a category: is this slope stable or unstable? The first "
           "part builds the vocabulary of classification; then we apply it to 616 Morgenstern-Price slope cases; then we decide "
           "which model to use, from the cost of its errors.",
        2: "Bridge from Sessions 03 and 04: we predicted strength, a number, and judged it with MAE, RMSE and R². Today the target "
           "is a class, often with a probability attached. The workflow stays; the model output and the metrics change.",
        3: "Session 05 of 8: the start of Part 2, from prediction to decision.",
        4: "Three parts. Part 01 is all concepts: terms, logistic vs linear regression, the sigmoid, the confusion matrix and its "
           "metrics. Part 02 applies them to the slope dataset. Part 03 reads the results and makes the engineering decision.",
        5: "Part 01: the language of classification.",
        6: "Same inputs, different question. A factor of safety of 1.37 is a regression target; 'is FOS below 1.0?' is a "
           "classification target. A continuous result becomes a class through an engineering threshold.",
        7: "Six terms we use all session. Stress the positive class: we choose unstable as positive because that is the case we "
           "must not miss, and it defines what recall and precision mean.",
        8: (f"Notebook Part A, cell 6. Same 0/1 labels, two models. Click 1: linear regression runs from "
            f"{min(R['demo']['lin']):.2f} to {max(R['demo']['lin']):.2f}, not valid probabilities. Click 2: logistic regression "
            f"stays between 0 and 1 and follows the S-shape. What we want is the probability of unstable given the inputs."),
        9: "Logistic regression in four steps: inputs, a linear score, a probability, a decision. The word regression stays in the "
           "name because the model is linear on the log-odds scale; the class comes from the threshold.",
        10: "Step 1: the same weighted sum as Session 03, written for our three slope inputs. z is unrestricted. Coefficients are "
            "learned from training cases and depend on units and scaling.",
        11: "Step 2: the sigmoid. Clicks: z = -3 gives p = 0.05, z = 0 gives 0.50, z = 3 gives 0.95. These are model estimates, "
            "not automatically calibrated, and not a physical probability of failure.",
        12: "Step 3: odds and log-odds. p = 0.8 means odds of 4 to 1; the log of the odds is unbounded, which is why a linear model "
            "can describe it. A coefficient is the change in log-odds per unit of an input, holding the others fixed.",
        13: "Step 4: a threshold turns the probability into a class. 0.50 is a software default. Lowering it flags more slopes "
            "(fewer misses, more false alarms); raising it does the opposite. Choose it on validation data.",
        14: (f"A real worked prediction with the tuned model. beta = {ex['beta_deg']:.0f} degrees, c/(gamma H) = {ex['c_by_gammaH']:.2f}, "
             f"phi = {ex['phi_deg']:.0f} degrees gives z = {ex['z']:.2f} and p = {ex['p']:.2f}: predicted unstable. "
             f"Morgenstern-Price gives FOS = {ex['fos']:.2f}, so the prediction is correct. Signs: steeper slopes raise z; "
             f"more cohesion and friction lower it. Class weighting shifts these probabilities, so read them as scores."),
        15: "The essential distinction, from the notebook's table. With a fixed threshold, logistic regression draws a straight "
            "boundary in the input space unless features are transformed.",
        16: "The confusion matrix with unstable as the positive class. Click through TN, FP, FN, TP. A false positive costs an "
            "unnecessary check; a false negative is an unstable slope called stable. For safety screening, read FN first.",
        17: "Definitions before scores. Recall: of all unstable slopes, how many did we catch. Precision: of all slopes we flagged, "
            "how many were really unstable. F1 balances them. Balanced accuracy weights both classes equally.",
        18: (f"Why accuracy misleads: always predicting stable scores {100 * T['Majority baseline']['acc']:.1f}% accuracy on the "
             f"{sp['test']} test slopes and detects none of the {sp['test_unstable']} unstable ones. Balanced accuracy is 0.50."),
        19: "Part 02: from factor of safety to a classification.",
        20: "The engineering question. Inputs: slope angle, c/(gamma H), friction angle. The label comes from the Morgenstern-Price "
            "FOS: unstable when FOS < 1.0. These labels reproduce a numerical analysis; they are not field failures.",
        21: "The dataset: 616 rows forming a complete grid, 11 slope angles x 7 cohesion levels x 8 friction angles. No missing "
            "values, no repeated input combinations. itr is an identifier. The slip-surface columns are outputs of the analysis "
            "and would leak the answer.",
        22: (f"The label is an engineering choice. FOS < 1.0: {n_un} unstable, {n - n_un} stable. FOS < 1.5: "
             f"{R['counts']['1.5']['below']} below, a different design or screening question. No case has FOS exactly 1.0."),
        23: (f"Imbalance: {n - n_un} stable ({100 * (n - n_un) / n:.1f}%) and {n_un} unstable ({100 * n_un / n:.1f}%). Unstable "
             f"cases concentrate at low friction angles: 25 at phi = 10 degrees, 3 at 45 degrees. Imbalance is not a defect; it "
             f"changes which metrics matter."),
        24: "Two thresholds. The FOS threshold defines the target before modelling. The probability threshold defines the decision "
            "after modelling. The example shows how a truly unstable slope becomes a false negative at 0.50.",
        25: "One slice of the grid at phi = 25 degrees, with every FOS value. The boundary depends on slope angle and cohesion "
            "together, and phi shifts it. The real boundary is three-dimensional.",
        26: "The three tuned models on the same slice. Logistic regression: a straight edge, reaching into stable cases (false "
            "alarms). Decision tree: axis-aligned steps. Random forest: a tighter stepped region. All three use class weighting, "
            "so they lean towards caution.",
        27: (f"Handling imbalance, with a real effect: logistic regression without weighting misses {cw['None']['cm'][2]} of the "
             f"{sp['train_unstable']} unstable training cases in CV; with class_weight='balanced' it misses none but raises "
             f"{cw['balanced']['cm'][1]} false alarms. Thresholds are tuned on validation data; resampling only inside CV folds."),
        28: (f"Stratified 80/20 split: {sp['train']} training cases ({sp['train_unstable']} unstable) and {sp['test']} test cases "
             f"({sp['test_unstable']} unstable). Five-fold StratifiedKFold and GridSearchCV on the training data only. On a grid, a "
             f"random split mostly tests interpolation."),
        29: "The search grids from the notebook. Scoring is recall for the unstable class, so watch precision: recall-focused tuning "
            "can produce false alarms.",
        30: "Part 03: from scores to an engineering decision.",
        31: (f"Best mean CV recall: logistic regression {R['cv']['Logistic regression']['recall']:.3f}, decision tree "
             f"{R['cv']['Decision tree']['recall']:.3f}, random forest {R['cv']['Random forest']['recall']:.3f}. All chose "
             f"balanced class weights. CV selects settings; it is not the final score."),
        32: (f"Held-out test results, evaluated once. Logistic regression: recall {lr['rec']:.3f}, precision {lr['prec']:.3f}. "
             f"Tree: recall {dt['rec']:.3f}, precision {dt['prec']:.3f}. Forest: recall {rf['rec']:.3f}, precision "
             f"{rf['prec']:.3f}, highest accuracy {rf['acc']:.3f}. With 19 unstable test slopes, one case moves recall by about 0.05."),
        33: "The safety-relevant metrics side by side. No model wins everywhere: logistic regression and the tree catch every "
            "unstable slope; the forest has better precision and F1 but misses two.",
        34: (f"Confusion matrices on the test set. Logistic regression: {lr['cm'][1]} false alarms, 0 missed. Tree: {dt['cm'][1]} "
             f"false alarms, 0 missed. Forest: {rf['cm'][1]} false alarms, {rf['cm'][2]} missed unstable slopes."),
        35: (f"Threshold trade-off on out-of-fold training probabilities, never the test set. At 0.3: recall {th[0.3]['rec']:.2f}, "
             f"precision {th[0.3]['prec']:.2f}. At 0.5: {th[0.5]['rec']:.2f} and {th[0.5]['prec']:.2f}. At 0.7: "
             f"{th[0.7]['rec']:.2f} and {th[0.7]['prec']:.2f}. At 0.9: {th[0.9]['rec']:.2f} and {th[0.9]['prec']:.2f}. The "
             f"notebook's draft note: the default 0.5 is a software convention, not an engineering law."),
        36: "Which model? It depends on the error we most want to avoid. Our stated priority is not missing unstable slopes, so "
            "logistic regression is the provisional screening candidate: it caught all 19, at the cost of 13 false alarms. "
            "Random forest is the alternative if false alarms are costly. Not a universal winner: one split, a structured grid.",
        37: "What the results do and do not show. They show how classifiers reproduce numerical-analysis labels. They do not "
            "validate field failures or performance in unseen parameter regions. Suggest a region holdout, e.g. all phi = 45 "
            "degree cases.",
        38: "Six exercises from the notebook. Allow about 10 minutes; take answers to 4 and 5 aloud.",
        39: "The decision framework to carry into every classification problem. High test accuracy is not proof of "
            "generalisation or engineering safety.",
        40: "Extension: multiclass with the Steel Plates Faults data from Session 02, seven fault types, the rarest under 3%. Per-"
            "class metrics, macro and weighted averages. This is the Appendix B notebook and the homework.",
        41: "Homework on the steel plates. Deliverables: notebook, confusion-matrix plot, comparison table, short interpretation.",
        42: "Two optional notebooks: Appendix A on how trees and forests learn; Appendix B on multiclass classification. The "
            "reference slides for Appendix A follow the closing slides.",
        43: "Questions.",
        44: "Thank you. Session 06: artificial neural networks.",
        45: (f"Appendix A1. Entropy and Gini both measure node impurity: zero for a pure node, largest at 50:50. For our data "
             f"(15.1% unstable) entropy is about 0.61 bits and Gini about 0.26. Compare reductions, not raw values."),
        46: "Appendix A2. Information gain: parent impurity minus the size-weighted child impurity. Split B gains 0.0486 bits, "
            "split A 0.0144, so B is preferred. Counts are illustrative, from the Appendix A notebook.",
        47: "Appendix A3. scikit-learn's DecisionTreeClassifier uses Gini by default, as in today's notebook. If you teach entropy, "
            "say so or set criterion='entropy'.",
        48: "Appendix A4. Random forest: bootstrap samples plus random feature subsets give different trees; their votes are "
            "aggregated. The example draw shows rows 1 and 5 used several times and rows 0, 3, 4 left out (out-of-bag).",
        49: "Appendix A5. The main settings and what they change. Random forest is not automatically better.",
        50: "Appendix A6. Documentation links and the dataset caveat.",
    }


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
