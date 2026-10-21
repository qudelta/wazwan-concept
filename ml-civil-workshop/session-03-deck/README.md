# Session 03 · Your First Engineering Prediction Model

Built from Dr. Waris's 48-slide draft in the design system and pipeline of Sessions 01–02
(logos, Amiri font and PowerPoint fonts are shared from `../session-01-deck`).

**Files in `export/`**
- `…_EDITABLE.pptx`: editable PowerPoint (real text and shapes, fonts embedded, 125 click animations, notes on every slide)
- `….pptx`: image-based PowerPoint with the same clicks and notes
- `…_handout.pdf` / `…_presenter-builds.pdf`: one page per slide / one page per click
- `Fonts_for_editable_PowerPoint.zip`: install on a Mac if PowerPoint substitutes fonts while editing

**Every number is real.** `charts.py` runs the notebook's own steps (scikit-learn): UCI Concrete data, duplicates dropped
(1,030 → 1,005), `train_test_split(test_size=0.2, random_state=42)`, mean baseline, `LinearRegression`, 5-fold CV.

## Changes from the draft, for review
- **Slides 18–21 (maths) redrawn natively from the real concrete data**, replacing the pasted DYP DPU slides and third-party images:
  line fit with errors, the cost bowl J(w,b) with the real gradient-descent path, gradient descent on J(w), learning rate
  (small / right / too large) and feature scaling (contours and iterations, raw vs standardised). The draft's motion-path
  animations are rebuilt as click-by-click steps that play the same in both PowerPoint files.
- **Slide 36 (4-fold CV, 10% test, from another study)** merged into the K-fold slide as 5-fold CV on the 80% training set, to
  match the notebook; its MAE / MSE / R² formulas now sit on the three metric slides.
- Illustrative numbers replaced with real results (baseline 35.1 MPa; test MAE 8.9, RMSE 11.2, R² 0.58; CV 0.59 ± 0.03;
  50-seed range 0.53–0.66). The Model A / B example on the CV slide stays as an illustration; its "1.02" is flagged as an
  impossible R².
- "Standardise (scaling between −1 and 1)" corrected: standardising gives mean 0, sd 1; −1…1 is min-max scaling.
- Duplicate slides 16/17 merged; the second "Part 3" divider renamed; the residuals-vs-age chart added as evidence that the
  linear model is too simple (it leads into Session 04).
- Speaker notes on slides 18–21 and 36 in the draft were from another talk (slope reliability / RBDO); replaced.
- The timing table is kept as an appendix slide with this deck's slide numbers.

## Rebuild
```
python3 build.py <phosphor-icons>/assets/duotone            # deck.src.html -> deck.html
node render.mjs export 1 && node render_builds.mjs export     # slides, handout, click builds, presenter PDF
python3 make_pptx.py export                                  # image PowerPoint
node native/extract.mjs /tmp/native && python3 native/build_pptx.py /tmp/native export/Session-03_Your-First-Engineering-Prediction-Model_EDITABLE.pptx
```
Needs scikit-learn, pandas, python-pptx, fontTools, Playwright. Click builds: `builds.json`. Notes: `pptx_common.py`.
