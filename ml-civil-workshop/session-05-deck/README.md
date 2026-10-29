# Session 05 · From Prediction to Engineering Decision: Classification

Built from Dr. Waris's 43-slide draft and his three notebooks, in the design system and pipeline of Sessions 01–03
(logos, Amiri font and PowerPoint fonts are shared from `../session-01-deck`).

**Files in `export/`**
- `…_EDITABLE.pptx`: editable PowerPoint (real text and shapes, fonts embedded, 120 click animations, notes on every slide)
- `….pptx`: image-based PowerPoint with the same clicks and notes
- `…_handout.pdf` (one page per slide) · `…_presenter-builds.pdf` (one page per click)
- `Fonts_for_editable_PowerPoint.zip`: install on a Mac if PowerPoint substitutes fonts while editing

## Structure (the requested pedagogy)
1. **Part 01 · Classification basics** (slides 5–18): regression vs classification, vocabulary, why not linear regression,
   logistic regression in four steps (score, sigmoid, log-odds, threshold), a worked prediction with the fitted model,
   linear vs logistic table, confusion matrix, recall / precision / F1 / balanced accuracy, why accuracy misleads.
2. **Part 02 · Slope stability** (19–29): the question, the 616-case grid, the FOS label, imbalance, the two thresholds,
   the φ = 25° slice, the three models' boundaries, handling imbalance, stratified split and CV, tuning grids.
3. **Part 03 · Results & decision** (30–38): CV and test results, confusion matrices, threshold trade-off, model choice,
   limits, exercises. Then takeaways, the multiclass extension and homework (Appendix B), and Appendix A reference slides.

## Data and reproducibility
- `results.py` runs the notebook's modelling steps and writes `data/results.json`; charts and slides read only that file.
  **Use scikit-learn 1.5 or 1.6**: they reproduce the notebook's saved outputs exactly. scikit-learn 1.9 chooses different
  Random Forest settings on this grid (test precision 0.607 instead of 0.680), so participants on a newer Colab image may
  see slightly different Random Forest numbers. Logistic regression and the decision tree are identical across versions.
- The instructor's dataset `Simplified_static_dataset_616.xlsx` is **not committed** (public repository). Put it in
  `data/` to re-run `results.py`.
- Steel Plates Faults: UCI Machine Learning Repository, CC BY 4.0.

## Rebuild
```
python3 results.py                                            # needs the xlsx and scikit-learn 1.6
python3 build.py <phosphor-icons>/assets/duotone              # deck.src.html -> deck.html
node render.mjs export 1 && node render_builds.mjs export
python3 make_pptx.py export
node native/extract.mjs /tmp/native && python3 native/build_pptx.py /tmp/native export/Session-05_From-Prediction-to-Engineering-Decision_Classification_EDITABLE.pptx
```
