# Session 06 · Artificial Neural Networks for Engineering Prediction

Built from Dr. Waris's 37-slide draft, in the design system and pipeline of Sessions 01–05
(logos, Amiri font and PowerPoint fonts are shared from `../session-01-deck`).

**Files in `export/`**
- `…_EDITABLE.pptx`: editable PowerPoint (real text and shapes, fonts embedded, 110 click animations, notes on every slide)
- `….pptx`: image-based PowerPoint with the same clicks and notes
- `…_handout.pdf` (one page per slide, final state) · `…_presenter-builds.pdf` (one page per click)

## Structure
1. **Recap** (slides 5–8): the concrete question, the UCI dataset, why compare models, the linear baseline.
2. **Part 01 · ANN intuition** (9–21): history, brain neuron to simple model, demand prediction, hidden layers learning
   their own features, multilayer perceptrons, epoch / batch size / learning rate.
3. **Part 02 · Build & train** (22–31): one neuron, the (32, 16) architecture, activations, scaling, training,
   loss vs validation, data roles, architecture choice.
4. **Part 03 · Results & judgement** (32–39): metrics, test results, R², actual vs predicted, residuals, limits,
   geotechnical transfer. Then take-home messages, after-session tasks, questions.

## The draft's animations
Slides 10–16 and 18–20 keep the draft's click order (draft slides 8–18). Slide 12 has the draft's 19 steps of the
demand-prediction build; slide 13 removes the hand-picked connections (an exit click); slide 14 adds the full
connections one input at a time. The draft's slide 15 (MLP equations) has no animation, and neither does slide 17 here.

`builds.json` now accepts `{"fx": "float" | "fade" | "wipe" | "exit", "sel": [...]}` for a click, as well as a plain list
of selectors. `render_builds.mjs`, `render.mjs`, `make_pptx.py`, `native/extract.mjs`, `native/build_pptx.py` and
`pptx_common.py` support the effects and exit clicks.

## Data and numbers
- `data/concrete_uci.csv`: the original UCI file (Concrete_Data.xls, all 1,030 rows), exported to CSV with short column
  names. Yeh, I.-C. (1998). Concrete Compressive Strength. UCI Machine Learning Repository, CC BY 4.0. doi:10.24432/C5PK67.
- `results.py` writes `data/results.json`. The linear-regression baseline is recomputed and reproduces the draft exactly
  (MAE 7.745, RMSE 9.797, R² 0.628 with `train_test_split(test_size=0.2, random_state=42)`).
- Random Forest, ANN (32, 16) and the four candidate architectures come from the instructor's notebook, copied from the
  draft's charts (no notebook file was supplied). The actual-vs-predicted and residual plots are of the linear baseline;
  the ANN and Random Forest plots are shown live from the notebook.
- The training-curve chart (slide 29) is a schematic and says so.
- The neuron on slide 11 is drawn for this deck; the draft's ScienceFacts picture is not reused (public repository).

## Rebuild
```
python3 results.py                                            # optional: needs scikit-learn
python3 build.py <phosphor-icons>/assets/duotone              # deck.src.html -> deck.html
node render.mjs export 1 && node render_builds.mjs export
python3 make_pptx.py export
node native/extract.mjs /tmp/native && python3 native/build_pptx.py /tmp/native export/Session-06_Artificial-Neural-Networks_Engineering-Prediction_EDITABLE.pptx
```
