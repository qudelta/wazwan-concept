"""Shared by both PowerPoint builds (Session 02): speaker notes, chart slides, slide transition and click-animation timing."""
from lxml import etree

import charts

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
STAGGER_MS = 120


CHART_SLIDES = {16, 20, 21, 30, 31}   # slides whose builds are charts: fade instead of float


def _notes() -> dict[int, str]:
    """Presenter notes, one per slide. Numbers come from charts.STATS so they always match the slides."""
    charts.build()
    S = charts.STATS
    return {
        1: "Welcome back. Session 02 is about the step before any model: turning raw engineering records into a dataset we can trust. "
           "Read the question on the slide aloud: can we trust our engineering data before giving it to a model? The four labels are the "
           "arc of today: data quality, exploration, preparation, and setting up a fair evaluation.",
        2: "Two-minute recap. X = the inputs, y = what we predict, and the target decides whether it is regression or classification. "
           "We used one workflow for every problem, and we loaded 1,030 concrete tests with pandas. Last time we assumed the table was "
           "ready. Today we question that assumption.",
        3: "Where we are in the course: session 01 done, session 02 today. Everything in sessions 03 to 08 depends on today: a model can "
           "only be as good as the dataset we prepare now.",
        4: "Three parts. Part 01: know your data (what ML-ready means, three real datasets, the first audit, plausibility). Part 02: "
           "clean and explore (missing values, outliers, distributions, correlation). Part 03: prepare to model (X and y, leakage, "
           "train/test split, class balance, scaling). Read the four outcomes; we come back to them at the end.",
        5: "The six-step workflow from the original deck. Today is step 02, Data. Message: a model is only as meaningful as the problem "
           "formulation and the data behind it. The three orange boxes preview what goes wrong if we skip this step.",
        6: "Part 01: know your data before you trust it.",
        7: "Six questions to ask of any dataset before modelling. The examples at the bottom of each card are from the concrete data. "
           "Stress the last one, Availability: it comes back as leakage in Part 03. ML-ready is not the same as clean.",
        8: "A dataset is more than a table. One row = one mix tested at one age (the same mix appears several times at different ages). "
           "X are the inputs, y the target. The data dictionary on the right is something every project should have: meaning, unit and "
           "role of every column. Ask the cohort to write the full nine-row version as homework.",
        9: (f"Our three real datasets today, all from the UCI Machine Learning Repository. Concrete: 1,030 mixes, clean, used for "
            f"distributions and relationships. Water treatment: {S['wt_n']} daily records of an urban wastewater plant in Spain, "
            f"{S['wt_vars']} variables, {S['wt_na']} values recorded as '?': our missing-values case. Steel plates: {S['sp_n']} plates, "
            f"27 features, 7 fault classes: our target and class-balance case. Different problems, same preparation questions."),
        10: (f"Live in Colab. Run the five lines and reveal each output. Shape (1030, 9). Eight float columns and one integer (age). "
             f"No missing values. But {S['dups']} duplicated rows: {S['dup_groups']} mixes appear two to four times with the same "
             f"inputs, the same age and the same strength. They may be repeated records rather than independent tests; we deal with "
             f"them before the split (slide 28). describe() leads to the plausibility check."),
        11: "Two sides of data quality. Computational checks are what pandas can do for us. Engineering checks need us: units, plausible "
            "ranges, how and where the data were measured. A dataset can pass every computational check and still be physically wrong.",
        12: (f"Plausibility on real numbers. w/c goes from {S['wc_min']:.2f} to {S['wc_max']:.2f}; 198 mixes are above 1.0, which looks "
             f"alarming until you notice they contain slag and fly ash: water-to-total-binder stays between 0.24 and 0.90. The sum of "
             f"ingredients ({S['dens_min']:,.0f} to {S['dens_max']:,.0f} kg/m3) is close to the unit weight of normal concrete. The last "
             f"row is hypothetical: a unit slip that code would never flag."),
        13: "Part 02: clean and explore, with engineering eyes.",
        14: "Missing data in three steps. Detect: where, how many, concentrated where. Investigate: why. Decide: delete, impute or a "
            "domain-informed treatment, and document it. There is no universal rule.",
        15: (f"Live in Colab with the water-treatment file. The file writes missing values as '?'. Without na_values='?', pandas reads "
             f"those columns as text. With it: {S['wt_na']} missing values, and {S['wt_rows_na']} of {S['wt_n']} days "
             f"({S['wt_drop_pct']:.0f}%) have at least one gap. pH and conductivity at the plant inflow have none."),
        16: "The missing-value map: one orange mark per gap, rows grouped by what is measured. Online sensors (pH, conductivity) almost "
            "never miss. Sediments and BOD, laboratory tests (BOD takes five days), carry most gaps. The performance columns are "
            "calculated from those lab values, so they inherit the gaps. Missingness follows the measurement method. Note: the file "
            "stores months out of order; we sorted by date first.",
        17: (f"Ask the cohort: why might a sensor go silent? Four typical reasons. Then the real clue: only {S['wt_sat']} of {S['wt_n']} "
             f"records fall on a Saturday. Whole days are missing because of a sampling schedule. A missing day in the calendar and a '?' "
             f"in a cell are different kinds of missing, and both carry information."),
        18: (f"Every option has a cost. Dropping incomplete rows keeps {S['wt_complete']} of {S['wt_n']} days and loses "
             f"{S['wt_drop_pct']:.0f}% of the record, probably the unusual days we care most about. Median filling invents typical values. "
             f"Domain-informed filling uses process knowledge. A 'was missing' flag keeps the information. Whatever you choose, write it "
             f"down, and learn fill values from the training data only (link to leakage)."),
        19: "The 1.5 x IQR rule on four concrete columns flags 82 values. Look at age: all 59 flags are real 180-, 270-, 360- and 365-day "
            "tests. The four 'strength outliers' are high-strength mixes near 80 MPa. Superplasticizer flags are two mix families. Nothing "
            "here is provably wrong. Flag, investigate, decide.",
        20: "df.hist() on four columns. Cement: wide spread, no typical mix. Water: spikes at 192 kg/m3 (118 mixes) and 228 kg/m3: repeated "
            "designs. Age: a handful of test ages, 425 at 28 days. Strength: roughly bell-shaped around 35 MPa with a tail to 83 MPa. "
            "Ask the cohort what they would note before fitting a model.",
        21: (f"Correlation with strength: cement +{S['corr']['cement']:.2f}, superplasticizer +{S['corr']['superplastic']:.2f}, age "
             f"+{S['corr']['age']:.2f}, water {S['corr']['water']:.2f}. Age looks weak by r, yet strength clearly depends on age: it "
             f"rises fast and then levels off. Pearson r measures straight-line association only. And no correlation proves causation."),
        22: "The road example from the original deck, drawn as a cause diagram. Bigger puddles go with deeper potholes, but the puddle does "
            "not cause the pothole. Traffic, cracked asphalt and poor drainage shape both. Engineering action should target the cause.",
        23: "A memorable coincidence: U.S. mozzarella consumption and civil-engineering doctorates rose together 2000-2009 (r about 0.95, "
            "Tyler Vigen's Spurious Correlations). The chart is a schematic of the shape, not the published values. Use it to remember "
            "the principle, not as evidence.",
        24: "Part 03: prepare the data for an honest model.",
        25: "Formulate the learning problem: 8 features, one target. In code, X = df.drop(columns='strength') and y = df['strength']. "
            "Read the shapes aloud: (1030, 8) is a table; (1030,) is one value per row.",
        26: "Four roles a column can play. Identifiers such as the water-treatment date code label a row; they rarely carry meaning. "
            "Leaked information would not exist when the prediction is made. Three questions before using any column.",
        27: "Data leakage, the silent killer. Information unavailable at prediction time sneaks into training or preprocessing; test "
            "scores look excellent; reality disappoints. Two forms: a leaking column (56-day strength or an acceptance test when "
            "predicting 28-day strength at the design stage) and leaking preprocessing (statistics computed on the full dataset before "
            "the split).",
        28: (f"Split before fitting. test_size=0.2 on 1,030 mixes gives {S['n_train']} for training and {S['n_test']} for testing. Remember "
             f"the {S['dups']} duplicates: if one copy lands in train and its twin in test, the test becomes easier than reality. Remove "
             f"them before splitting."),
        29: "Why a separate test set? The exam analogy: memorising last year's paper gives full marks on that paper and says little "
            "about understanding. In session 03 we fit on train, predict the test rows, and compare with their true y.",
        30: "random_state: without a fixed seed each run puts different rows in the test set, so results move between runs. With "
            "random_state=42 the split is identical every time. 42 has no meaning; any number works if it is recorded.",
        31: (f"Steel plates: 7 fault classes, very unequal. A model that always answers 'Other faults' is right "
             f"{S['sp_major'] * 100:.1f}% of the time without learning anything. Dirtiness has only 55 plates, about 11 in a 20% test set. "
             f"stratify=y keeps the class proportions in train and test. We return to this in session 05."),
        32: "Scaling preview. Aggregates are in the hundreds of kg/m3, superplasticizer in the tens, age in days. Distance- and "
            "gradient-based methods care about this; tree methods much less. The rule: fit the scaler on training data, then apply it "
            "to the test data.",
        33: "The complete journey in eight steps, coloured by today's three parts. Good ML begins before the algorithm.",
        34: "Hands-on: open the notebook, save a copy, work through the four sections. Replace 'Link shared in the session chat' with the "
            "real link if you want it on the slide.",
        35: "The final takeaway. Two questions to ask before choosing any algorithm. Then the order: understand the data, formulate the "
            "problem, protect the evaluation, then model.",
        36: "Bridge to session 03: a linear-regression model for concrete strength, trained on today's training set, judged on the test "
            "set with MAE, RMSE, R-squared, residuals and cross-validation.",
        37: "Optional practice before session 03.",
        38: "Questions.",
        39: "Thank you. See you in session 03.",
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
