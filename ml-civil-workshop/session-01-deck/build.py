import re
import sys
from pathlib import Path

import charts

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/@phosphor-icons/core/assets/duotone"
LOGO_LIGHT = "../poster/assets/qudelta-logo-light.png"  # light text, for dark slides
NOTEBOOK_LINK = "Link shared in the session chat"

SECTIONS = {
    "0": "Course overview",
    "1": "Part 01 · Problems to ML",
    "2": "Part 02 · Python &amp; Colab",
    "3": "Part 03 · Hands-on",
}


def icon(name: str) -> str:
    svg = (ICONS / f"{name}-duotone.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


def truss() -> str:
    """Faint Warren-truss bridge, the engineering motif on section dividers."""
    top, bot, x0, x1, n = 120, 300, 40, 1260, 12
    step = (x1 - x0) / n
    zig = " ".join(f"L{x0 + i * step:.0f} {bot if i % 2 == 0 else top}" for i in range(n + 1))
    verts = " ".join(f"M{x0 + i * step:.0f} {top} V{bot}" for i in range(1, n, 2))
    return (f'<svg class="truss" viewBox="0 0 1300 420" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M{x0} {bot} {zig[1:]}"/><path d="M{x0 + step:.0f} {top} H{x1 - step:.0f}"/><path d="M0 {bot} H1300"/>'
            f'<path d="{verts}" stroke-width="3"/><path d="M{x0 + 3 * step:.0f} {bot} V420 M{x1 - 3 * step:.0f} {bot} V420" stroke-width="9"/></svg>')


def stats() -> dict:
    s = charts.STATS
    a_s, v_s, a_e, v_e = s["age_hero"]
    return {
        "n28": f"{s['n28']}",
        "age_curves": f"{s['age_curves']}",
        "age_hero": f"one mix went from {v_s:.0f} MPa at {a_s} days to {v_e:.0f} MPa at {a_e} days",
        "r2pct": f"{s['abr_r2'] * 100:.0f}",
        "abr_a": f"{s['abr_a']:.1f}",
        "abr_b": f"{s['abr_b']:.2f}",
        "cls_pct": f"{s['cls_acc'] * 100:.0f}",
        "base_pct": f"{s['cls_base'] * 100:.0f}",
        "band_n": f"{s['band_n']}",
        "band_min": f"{s['band_min']:.0f}",
        "band_max": f"{s['band_max']:.0f}",
    }


svgs = charts.build()
values = stats()
src = (HERE / "deck.src.html").read_text()
total = src.count('<section class="slide')
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
src = re.sub(r"\{\{chart:([a-z0-9]+)\}\}", lambda m: svgs[m.group(1)], src)
src = re.sub(r"\{\{stat:([a-z0-9_]+)\}\}", lambda m: values[m.group(1)], src)
src = re.sub(r"\{\{logo:([a-z]+)\}\}", lambda m: f'<img class="lg-{m.group(1)}" src="assets/logos/{m.group(1)}.svg" alt="{m.group(1)} logo">', src)
src = src.replace("{{logo-light}}", f'<img src="{LOGO_LIGHT}" alt="Qudelta Studios">')
src = src.replace("{{notebook_link}}", NOTEBOOK_LINK)
src = src.replace("{{truss}}", truss())
src = src.replace("{{headrows}}", charts.head_rows())

parts = src.split('<section class="slide')
out = [parts[0]]
for n, part in enumerate(parts[1:], 1):
    def header(m):
        kind = m.group(1)
        pill = f'<span class="sp"><i></i>{SECTIONS[kind]}</span>' if kind in SECTIONS else ""
        return (f'<header class="top"><div class="hc">AI &amp; ML for Civil Engineers<span>Session 01</span></div>'
                f'<div class="hr">{pill}<span class="n"><b>{n:02d}</b> / {total}</span></div></header>')
    out.append(re.sub(r"\{\{top:([0-3bd])\}\}", header, part, count=1))
html = '<section class="slide'.join(out)
leftover = re.findall(r"\{\{[^}]*\}\}", html)
assert not leftover, leftover
(HERE / "deck.html").write_text(html)
print("built deck.html with", total, "slides")
