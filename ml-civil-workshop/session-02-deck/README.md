# Session 02 · From Raw Engineering Data to an ML-Ready Dataset

Same design system and pipeline as `../session-01-deck` (logos, Amiri font and PowerPoint fonts are shared from there).

**Files in `export/`**
- `…_EDITABLE.pptx`: editable PowerPoint (real text boxes and shapes, Archivo and JetBrains Mono embedded, 124 click animations, speaker notes on every slide)
- `….pptx`: image-based PowerPoint with the same clicks and notes (looks identical everywhere)
- `…_handout.pdf` / `…_presenter-builds.pdf`: one page per slide / one page per click
- `Fonts_for_editable_PowerPoint.zip`: install these on a Mac if PowerPoint substitutes fonts while editing

**Data** (`data/`, UCI Machine Learning Repository, CC BY 4.0): Concrete Compressive Strength (Yeh, 1998);
Water Treatment Plant (Poch; Bejar, Cortés & Poch, 1993); Steel Plates Faults (Buscema, Terzi & Tastle, 2010).
Every number on the slides is computed from these files in `charts.py`.

**Rebuild**
```
python3 build.py <phosphor-icons>/assets/duotone            # deck.src.html -> deck.html
node render.mjs export 1 && node render_builds.mjs export     # slides, handout, click builds, presenter PDF
python3 make_pptx.py export                                  # image PowerPoint
node native/extract.mjs /tmp/native && python3 native/build_pptx.py /tmp/native export/Session-02_From-Raw-Engineering-Data-to-an-ML-Ready-Dataset_EDITABLE.pptx
```
Click builds: `builds.json`. Speaker notes and chart slides: `pptx_common.py`.
