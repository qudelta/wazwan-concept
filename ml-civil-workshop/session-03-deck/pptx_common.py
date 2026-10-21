"""Shared by both PowerPoint builds (Session 03): speaker notes, chart slides, slide transition and click-animation timing."""
from lxml import etree

import charts

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
STAGGER_MS = 120


CHART_SLIDES = {9, 14, 15, 16, 17, 18, 19, 27, 28, 30, 32}   # slides whose builds are charts: fade instead of float


def _notes() -> dict[int, str]:
    """Presenter notes, one per slide. Numbers come from charts.STATS so they always match the slides.
    Dr. Waris's own instructor notes from the draft are kept (quoted) where they belong."""
    charts.build()
    S = charts.STATS
    T, B, TR = S["lr_test"], S["base_test"], S["lr_train"]
    ex = S["example"]
    return {
        1: "Instructor note (draft): \"Today we are going to build our first actual prediction model. We have already learned how to "
           "prepare the data. Now we ask: can a machine-learning model learn a useful relationship from this data?\"",
        2: "Recap of sessions 01 and 02 in one minute. Everything on the left is what made the data ready. Today: can we use these "
           "inputs to predict an engineering response, and how would we know if the prediction is any good?",
        3: "Session 03 of 8. After today we have a complete, honest modelling workflow that every later session reuses.",
        4: "Three parts: build the model (including the maths behind it), evaluate it, and check whether we can trust it. Read the "
           "four outcomes; we return to them in the summary.",
        5: "Part 01: from engineering question to a trained model.",
        6: "Instructor prompt (draft): \"If I give you a new concrete mix, could you estimate its compressive strength without "
           "performing the test?\" Eight inputs, one numeric target.",
        7: (f"The file has {S['n_raw']:,} mixes. In Session 02 we found {S['dups']} duplicated rows; from today the notebook drops them, "
            f"leaving {S['n']:,}. Eight inputs, no missing values, one continuous target in MPa: a regression problem. The 42.7 MPa "
            f"marker just illustrates that a prediction can be any value on the line."),
        8: (f"A real test mix from the notebook: the model predicts {ex['pred']:.1f} MPa, the lab measured {ex['actual']:.1f} MPa, so "
            f"the error is {ex['pred'] - ex['actual']:+.1f} MPa. Instructor note (draft): \"Every regression model we build today "
            f"ultimately produces predictions that we need to compare against observations.\""),
        9: (f"The mean baseline: predict the average training strength, {S['base']:.1f} MPa, for every mix. It ignores all eight inputs. "
            f"On the test mixes it is off by {B['mae']:.1f} MPa on average. Instructor note (draft): this is a very important research "
            f"habit. Don't simply report that an ML model gives an R² of 0.75. Ask: compared with what?"),
        10: "Training = learning parameters from examples. For linear regression: one intercept and one coefficient per input. "
            "fit() chooses them so that the predictions are as close as possible to the training measurements. (The draft said "
            "'do not introduce gradient descent here'; it comes on slides 15-19.)",
        11: (f"Why hold data back: the exam analogy. 80% ({S['n_train']} mixes) for fitting, development and cross-validation; 20% "
             f"({S['n_test']} mixes) kept for the final evaluation only."),
        12: "Linear regression: the prediction is a weighted sum of the inputs plus an intercept. Simple, fast, interpretable, and the "
            "baseline for every more complex model later. Simple does not mean useless.",
        13: (f"The real fitted equation. Intercept {S['b0']:.2f} MPa; for example cement {S['coef']['cement']:+.3f} and age "
             f"{S['coef']['age']:+.3f}. Instructor note (draft): \"This is the point where the data starts determining the model "
             f"rather than us writing engineering rules manually.\""),
        14: (f"Reading coefficients. Raw: superplasticizer has the largest weight ({S['coef']['superplastic']:+.3f} per kg/m³) but it "
             f"only varies by a few kg/m³. Per standard deviation, cement ({S['std_coef']['cement']:+.1f}) and slag dominate and "
             f"superplasticizer is small ({S['std_coef']['superplastic']:+.1f}). Units matter; a coefficient is an association in "
             f"the fitted model, not a cause."),
        15: "Some maths behind ML models (1 of 5). One input to keep it visible: 26 real 28-day mixes, strength against cement. "
            "Click 1: the line f(x) = wx + b. Click 2: the vertical errors, and the squared-error cost J(w, b) that adds them up. "
            "Click 3: slope and intercept. Click 4: the goal, find w and b that make J smallest.",
        16: (f"(2 of 5) Plot J for every pair (w, b) and you get a bowl: convex, one minimum. Gradient descent starts somewhere and walks "
             f"downhill. The clicks show the real path in three stages; {S['gd_steps']} steps reduce J from {S['gd_start']:,.0f} to "
             f"{S['gd_end']:.0f} MPa², its minimum."),
        17: "(3 of 5) The update rule: new w = old w minus learning rate times slope. Clicks 1-2: on the left the slope is negative, so "
            "w increases; on the right it is positive, so w decreases. Clicks 4-6: the ball steps down, with steps shrinking as the "
            "slope flattens. w and b are updated together.",
        18: (f"(4 of 5) Learning rate: too small ({S['alpha']['small']['alpha']}) crawls; about right ({S['alpha']['good']['alpha']}) "
             f"converges in about ten steps; too large ({S['alpha']['large']['alpha']}) overshoots and diverges. α is a hyperparameter. "
             f"scikit-learn's LinearRegression solves for the weights directly, so we do not tune α today; it returns with neural "
             f"networks in Session 06."),
        19: (f"(5 of 5) Feature scaling. Cement varies about 17 times more than superplasticizer, so the cost contours are long and "
             f"narrow and gradient descent needs {S['scale_iters']['raw']:,} iterations. After standardising (mean 0, sd 1) the "
             f"contours are nearly round: {S['scale_iters']['scaled']} iterations. Note: standardising gives mean 0 and sd 1; it does "
             f"not force values into -1 to 1 (that is min-max scaling). Fit the scaler on the training data only."),
        20: "Part 02: how good is our model?",
        21: "We need a scorecard. Three metrics, three slightly different questions.",
        22: (f"MAE: the average absolute error, in MPa. Our model: {T['mae']:.1f} MPa on the test set, against {B['mae']:.1f} MPa for "
             f"the mean baseline. 'Our predictions are off by about {T['mae']:.1f} MPa on average.'"),
        23: (f"RMSE squares errors first, so big misses count more. The toy example: same MAE, double the RMSE. Ours: "
             f"{T['rmse']:.1f} MPa (baseline {B['rmse']:.1f}). The gap between RMSE and MAE hints at a few large misses."),
        24: (f"R² compares our squared error with the mean baseline's. 1 is perfect, 0 is no better than the mean, negative is worse. "
             f"Ours: {T['r2']:.2f}. R² is not accuracy: 0.58 does not mean 58% of predictions are correct."),
        25: "The scorecard side by side. A metric is evidence, not engineering judgement: is an average error of about 9 MPa "
            "acceptable for the decision you have to make?",
        26: (f"Train R² {TR['r2']:.2f}, test R² {T['r2']:.2f}: similar. No sign of overfitting, but modest on both: the model is "
             f"probably too simple. Good training performance alone is never enough."),
        27: "Parity plot: perfect predictions lie on the 45-degree line. Here high-strength mixes fall below the line: the model "
            "under-predicts strong concrete. Look for ranges where it behaves differently.",
        28: (f"Residuals = actual minus predicted. Against the prediction they look roughly centred. Against age they curve: median "
             f"residual about {dict(S['resid_age'])[3.0]:+.0f} MPa at 3 days, {dict(S['resid_age'])[56.0]:+.0f} at 56 days and "
             f"{dict(S['resid_age'])[360.0]:+.0f} at a year. Strength gain with age is not a straight line, the same lesson as the "
             f"correlation slide in Session 02. This is the evidence that a linear model is too simple."),
        29: "Part 03: is it consistent, and can we trust it?",
        30: (f"Same model, same data, different random split: test R² from {S['seed_min']:.2f} to {S['seed_max']:.2f} across 50 seeds "
             f"(42: {S['seed'][42]:.2f}, 7: {S['seed'][7]:.2f}, 21: {S['seed'][21]:.2f}). One split is one estimate."),
        31: "5-fold cross-validation on the training data only; the test set stays locked. Each fold takes one turn as validation. "
            "Average the five scores. (This replaces the draft's 4-fold / 10% test diagram from another study, so it matches the "
            "80/20 split and 5-fold CV used in the notebook.)",
        32: (f"Our model: fold R² from {min(S['cv']):.2f} to {max(S['cv']):.2f}, mean {S['cv_mean']:.2f} ± {S['cv_sd']:.2f}: "
             f"consistent. Models A and B are an illustration: same mean, very different spread. Note that the 1.02 in the draft's "
             f"Model B example is impossible for R² (maximum 1); it is kept here, marked, as a talking point about sanity checks. "
             f"Instructor note (draft): large variation may indicate that the model behaves very differently for different subsets."),
        33: "The most important rule from today. Do not use the test set to choose models, features, hyperparameters or "
            "pre-processing. Every peek leaks the test set into development.",
        34: "The workflow: cross-validation for decisions, the test set for the final assessment, once. This matters more in Sessions "
            "04 to 06 when we compare several algorithms.",
        35: "Five questions before trusting any prediction, each answered for today's model at the bottom of its card. Machine "
            "learning gives us a model; engineering judgement tells us whether to trust it.",
        36: "Live exercise in the notebook, about 10 minutes. A: change the seed. B: compare with the baseline (DummyRegressor). C: "
            "inspect the residuals. Close with the engineering question: is there evidence that the linear model is too simple? "
            "(Yes: the residuals curve with age.)",
        37: "The complete first modelling workflow in twelve steps. The central lesson: a prediction is not enough.",
        38: "Bridge to Session 04: our residuals curve, civil engineering relationships are often nonlinear, so next we try decision "
            "trees, Random Forest and boosting on the same data, compared with today's workflow.",
        39: "Optional practice. Exercise 2 (log of age) previews the idea that better features can fix some nonlinearity.",
        40: "Questions.",
        41: "Thank you. See you in Session 04.",
        42: "Appendix for the instructor: recommended timing, updated to this deck's slide numbers. Hide this slide when presenting "
            "if you prefer (right-click, Hide Slide).",
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
