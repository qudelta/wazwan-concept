"""Package the rendered slides as a PowerPoint file with speaker notes.

Each slide is a full-resolution render. Slides with builds (builds.json) start from a base image and
reveal the rest click by click: every click floats (or fades) in a transparent overlay, so students see one idea at a time.
Every slide carries speaker notes (pptx_common.py).
"""
import glob
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

from pptx_common import CHART_SLIDES, note_for, timing, transition

EMU_PER_PX = 12192000 // 1920  # 16:9 slide, 1920 px wide renders


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
    slide._element.append(transition())
    if overlay_ids:
        kind = "fade" if i in CHART_SLIDES else "float"
        slide._element.append(timing([[(spid, kind)] for spid in overlay_ids]))
        clicks += len(overlay_ids)
    note = note_for(i, len(steps))
    if note:
        slide.notes_slide.notes_text_frame.text = note
prs.save(f"{out_dir}/Session-03_Your-First-Engineering-Prediction-Model.pptx")
print(f"pptx: {len(files)} slides, {clicks} click animations")
