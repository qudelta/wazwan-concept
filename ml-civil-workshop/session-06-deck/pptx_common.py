"""Shared by both PowerPoint builds (Session 06): speaker notes, per-click effects, slide transition and click-animation timing."""
import json
from pathlib import Path

from lxml import etree

import charts

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
STAGGER_MS = 120
BUILDS = json.loads((Path(__file__).parent / "builds.json").read_text())

CHART_SLIDES = {26, 27}   # slides whose builds are charts: fade instead of float


def effect_for(slide_no: int, step: int) -> str:
    """The entrance (or exit) effect of one click: as set in builds.json, else fade on chart slides and float elsewhere."""
    st = BUILDS.get(str(slide_no), [])[step - 1]
    if isinstance(st, dict) and st.get("fx"):
        return st["fx"]
    return "fade" if slide_no in CHART_SLIDES else "float"


def _notes() -> dict[int, str]:
    """Presenter notes, one per slide. Numbers come from data/results.json so they always match the slides.
    Dr. Waris's own notes from the draft deck are kept where they belong."""
    R = charts.R
    T, rng = R["test"], R["ranges"]
    lin, rf, ann = T["Linear regression"], T["Random forest"], T["ANN (32, 16)"]
    arch = {a["name"]: a["rmse"] for a in R["arch"]}
    return {
        1: "Welcome to Session 06: artificial neural networks for engineering prediction. Today we go from a single neuron to a "
           "trained network, and then ask the engineering question: is the extra flexibility worth it on our concrete data?",
        2: "Bridge from Sessions 03 to 05. We predicted concrete strength with linear regression and trees, and last time "
           "classified slopes. Today: the same concrete regression problem with an ANN of 8 inputs, hidden layers of 32 and 16 "
           "neurons, and one output. It is one more candidate model and must earn its place on the same test set.",
        3: "Session 06 of 8, in Part 2: from prediction to decision.",
        4: "Three parts: the intuition behind neural networks, then building and training one for concrete strength, then reading "
           "the results honestly. On the right, the five things participants should leave understanding: explain, train, "
           "validate, compare, judge.",
        5: "Recap. Eight mix and age variables in, one continuous strength out: a regression problem.",
        6: (f"Recap of the data: {R['n']:,} mixes, 8 features, no missing values in the original UCI file. One fixed 80/20 split "
            f"gives {R['n_train']} training and {R['n_test']} test mixes. Strength ranges from {rng['strength'][0]:.1f} to "
            f"{rng['strength'][1]:.1f} MPa, mean {R['strength_mean']:.1f}. The data support a prediction exercise; they are not "
            f"a physical model of concrete."),
        7: "Three candidates: linear regression as the baseline, random forest as the nonlinear ensemble from Session 04, and the "
           "ANN. All are compared on the same held-out test set. The baselines are not exhaustively tuned.",
        8: (f"The baseline: an additive linear form. Simple and interpretable, but restricted without interactions or nonlinear "
            f"terms. On today's test mixes it reaches R² = {lin['r2']:.3f}, RMSE {lin['rmse']:.2f} MPa. That is the bar to beat."),
        9: "Done with the recap. Here comes the ANN. Part 01 builds the intuition.",
        10: "Click through the history. Origin: algorithms that try to mimic the brain. Used in the 1980s and early 1990s, out of "
            "favour in the late 1990s. Resurgence from around 2005. Applications came in waves: speech recognition, then image "
            "recognition (computer vision), then text (natural language processing). Today: everything from climate change to "
            "medical imaging, advertising and product recommendations. Last click: today's networks have almost nothing to do "
            "with how the brain learns; the brain was only the early motivation.",
        11: "All of human thought comes from neurons like this, sending electrical impulses and sometimes forming new connections "
            "with other neurons. Dendrites receive the inputs, the cell body combines them, the axon carries the signal, and the "
            "axon terminals pass it on. Click 2: the simplified mathematical model takes a number in, here 2, and outputs a "
            "number, here 0.7. With such extremely simplified models we build powerful algorithms. Don't take the biology too "
            "seriously.",
        12: "Demand prediction, after Andrew Ng: will this T-shirt be a top seller? 19 clicks, in the draft's order. Click 1: the "
            "three intermediate quantities, affordability, awareness, perceived quality, and the output. Clicks 2 to 7: each "
            "neuron and the inputs that feed it: price and shipping cost give affordability; marketing gives awareness; price and "
            "material give perceived quality. Clicks 8 to 9: the output neuron and its inputs. Click 10: 4 numbers, 3 numbers, "
            "1 number. Clicks 11 to 15: output arrow, the hidden layer, the output layer. Click 16: these are the activations. "
            "Click 17: each arrow carries an activation value. Clicks 18 and 19: output layer and input layer.",
        13: "So far we decided by hand which inputs feed which neuron. Click: those hand-picked connections go away.",
        14: "In practice every neuron in a layer receives every input from the previous layer, and learns which ones matter "
            "through its weights. Four clicks, one input at a time: price, shipping cost, marketing, material.",
        15: "The middle layer is called the hidden layer because the training set shows us x and y, the correct inputs and "
            "outputs, but not the correct values of affordability, awareness or perceived quality. We never see them in the "
            "data. One way to see this network: logistic regression, but a version that learns its own features, which makes it "
            "easier to predict accurately. Click: instead of engineering features by hand, the network learns them.",
        16: "Click: when building our own network we choose how many hidden layers and how many neurons per layer: the "
            "architecture. Two examples. Networks with several layers like these are called multilayer perceptrons in some "
            "literature.",
        17: "Hidden layers transform the inputs nonlinearly; the number of layers and neurons are key hyperparameters. Each "
            "neuron j in layer 1 has its own weight vector and bias, and applies an activation g: a_j = g(w_j · x + b_j). The "
            "vector of activations a[1] is the input of layer 2. Forward propagation computes the prediction; the loss "
            "compares it with the label; backpropagation computes gradients, and an optimiser such as stochastic gradient "
            "descent or Adam adjusts weights and biases. For our concrete regressor the loss is squared error, not cross-entropy.",
        18: "Epoch: one complete pass through the training data, like reading the whole book once. We train for many epochs. "
            "Note: within an epoch the weights are updated once per batch, not once per epoch.",
        19: "Batch size: how many samples the model processes before one weight update. 800 rows with batch size 32 means 25 "
            "updates per epoch. Small batches: more, noisier updates; large batches: smoother updates, more memory. "
            "scikit-learn's default is min(200, number of rows).",
        20: "Learning rate: the step size. Too high overshoots and may not converge; too low is slow and may get stuck. The three "
            "small panels show the same bowl with three step sizes. Like your pace on a hike.",
        21: "Summary, with the matching scikit-learn MLPRegressor settings: max_iter is the maximum number of epochs for the adam "
            "and sgd solvers; batch_size 'auto' means min(200, n); learning_rate_init defaults to 0.001. These are "
            "hyperparameters: we choose them, on validation data.",
        22: "Part 02: building and training an ANN for concrete strength.",
        23: "An ANN is a parameterised function made of connected units: inputs, hidden layers of weighted sums and nonlinear "
            "activations, one output. It learns weights and biases from examples; nobody hands it a mix-design equation.",
        24: "Inside one neuron: z is a weighted sum plus a bias, then the activation g. Weights scale each input, the bias shifts z, "
            "and g bends the response. Training adjusts all of them. The same z was the logistic-regression score in Session 05.",
        25: "Our selected network is (32, 16): 32 neurons in the first hidden layer, 16 in the second. The notation counts neurons, "
            "not parameters. Clicks: 8 x 32 + 32 = 288, 32 x 16 + 16 = 528, 16 x 1 + 1 = 17, total 833 weights and biases, "
            f"learned from {R['n_train']} training mixes.",
        26: "Without nonlinear activations, two linear layers collapse into one linear map, so depth adds nothing. Our network uses "
            "ReLU in both hidden layers; the output is linear so it can predict any strength. Clicks show sigmoid and tanh for "
            "comparison only.",
        27: (f"The features live on very different scales: superplasticizer up to {rng['superplastic'][1]:.1f} kg/m³, coarse "
             f"aggregate {rng['coarseagg'][0]:.0f}-{rng['coarseagg'][1]:,.0f} kg/m³, age 1-365 days. Gradient-based training is "
             f"better behaved after StandardScaler. The scaler is inside the Pipeline, so it learns means and standard deviations "
             f"from the training data only."),
        28: "One training step: forward pass, loss (squared error for regression), backpropagation of gradients, an update by the "
            "optimiser (Adam is scikit-learn's default) with the learning rate as the step size. Repeat for every batch and "
            "epoch. This is optimisation, as in Session 03, not the discovery of a physical law.",
        29: "The notebook plots the fitted ANN's optimisation history. Training loss tracks the objective on training batches; it is "
            "not test RMSE. The internal validation R² is computed on a held-out part of the training data and drives early "
            "stopping. The chart here is a schematic of the typical shapes, not the notebook's run. Check whether training "
            "reached the iteration limit.",
        30: (f"Three roles. Training data ({R['n_train']} mixes) fits the parameters; a validation subset inside it monitors "
             f"training and compares architectures; the test data ({R['n_test']} mixes) is used once at the end. The architecture "
             f"is chosen on validation RMSE, never on the test set."),
        31: (f"Four candidates on the validation subset: (8,) {arch['Small']:.3f}, (16, 8) {arch['Medium']:.3f}, (32, 16) "
             f"{arch['Larger']:.3f}, (32, 16, 8) {arch['Deeper']:.3f} MPa RMSE. (32, 16) is selected. The deeper network did not "
             f"help. Best of four tried, not proof of a global optimum."),
        32: "Part 03: results and judgement. Is the ANN worth its complexity?",
        33: "Three complementary metrics. MAE: average error size in MPa. RMSE: also MPa, but large errors count more. R²: "
            "compared with always predicting the mean, and can be negative. Residual = actual minus predicted: positive means "
            "underprediction, negative means overprediction.",
        34: (f"Test results on the same {R['n_test']} mixes. Linear regression: MAE {lin['mae']:.2f}, RMSE {lin['rmse']:.2f}. "
             f"Random forest: MAE {rf['mae']:.2f}, RMSE {rf['rmse']:.2f}, best in this run. ANN (32, 16): MAE {ann['mae']:.2f}, "
             f"RMSE {ann['rmse']:.2f}, competitive but not best. One split, one run: no general verdict on model families."),
        35: (f"R²: linear {lin['r2']:.3f}, random forest {rf['r2']:.3f}, ANN {ann['r2']:.3f}. Useful, but R² alone does not show "
             f"error patterns, behaviour near critical thresholds, or validity outside the training domain."),
        36: "The actual-versus-predicted plot of the linear baseline, reproduced from the UCI data. Look for scatter around the "
            "1:1 line, systematic bias, and changing spread. Then show the ANN and random-forest plots live in the notebook. "
            "Plots complement metrics; they do not prove physical validity.",
        37: "Residual plot of the linear baseline. Positive: underprediction; negative: overprediction; patterns suggest systematic "
            "error. Click: in this baseline, weak mixes are overpredicted and strong mixes underpredicted, on average. A good "
            "average score can hide weak performance in parts of the range. Compare with the ANN residual plot in the notebook.",
        38: "Does an ANN understand concrete? No: it learns a statistical mapping. Interpolation inside the training domain is "
            "reasonable; extrapolation is risky; a high test score does not establish physical validity; deployment needs "
            "representative validation, plausible behaviour and attention to error consequences. The table shows the training "
            "domain.",
        39: "The same idea transfers to geotechnical engineering, as illustrations, not trained models here: a slope-stability "
            "surrogate for the factor of safety, and surrogates of expensive numerical models, the topic of Session 08. A "
            "surrogate speeds up repeated predictions; it does not validate the numerical model or justify extrapolation.",
        40: "Take-home: understand the mapping; training is optimisation; validate correctly; compare honestly, here the random "
            "forest beat the selected ANN; keep claims proportional.",
        41: "After the session: work through the notebook with these five tasks. Dataset citation at the bottom right.",
        42: "Questions.",
        43: "Thank you. Next session: can we trust our ML model? Feature importance, SHAP and engineering judgement.",
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
    """One effect. Entrances: 'float' = PowerPoint's Float In (fade while rising slightly), 'fade', 'wipe' (from left).
    'exit' = Fade out: the shape is on the slide from the start and leaves on the click."""
    eff, setv = next(ids), next(ids)
    if kind == "exit":
        tgt = f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        body = (f'<p:animEffect transition="out" filter="fade"><p:cBhvr><p:cTn id="{next(ids)}" dur="500"/>{tgt}</p:cBhvr></p:animEffect>'
                f'<p:set><p:cBhvr><p:cTn id="{setv}" dur="1" fill="hold"><p:stCondLst><p:cond delay="499"/></p:stCondLst></p:cTn>{tgt}'
                f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set>')
        return (f'<p:par><p:cTn id="{eff}" presetID="10" presetClass="exit" presetSubtype="0" fill="hold" grpId="1" '
                f'nodeType="{node_type}"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>{body}'
                f'</p:childTnLst></p:cTn></p:par>')
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
