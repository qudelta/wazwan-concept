import re
import sys
from pathlib import Path

import charts

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/@phosphor-icons/core/assets/duotone"
SHARED = "../session-01-deck/assets"   # logos and the Amiri font live with Session 01
LOGO_LIGHT = "../poster/assets/qudelta-logo-light.png"  # light text, for dark slides
NOTEBOOK_LINK = "Link shared in the session chat"

SECTIONS = {
    "0": "Course overview",
    "1": "Part 01 · Data quality",
    "2": "Part 02 · Exploration",
    "3": "Part 03 · Preparation",
}


def icon(name: str) -> str:
    svg = (ICONS / f"{name}-duotone.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


def truss() -> str:
    """Faint Warren-truss bridge, the engineering motif on section dividers (as in Session 01)."""
    top, bot, x0, x1, n = 120, 300, 40, 1260, 12
    step = (x1 - x0) / n
    zig = " ".join(f"L{x0 + i * step:.0f} {bot if i % 2 == 0 else top}" for i in range(n + 1))
    verts = " ".join(f"M{x0 + i * step:.0f} {top} V{bot}" for i in range(1, n, 2))
    return (f'<svg class="truss" viewBox="0 0 1300 420" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M{x0} {bot} {zig[1:]}"/><path d="M{x0 + step:.0f} {top} H{x1 - step:.0f}"/><path d="M0 {bot} H1300"/>'
            f'<path d="{verts}" stroke-width="3"/><path d="M{x0 + 3 * step:.0f} {bot} V420 M{x1 - 3 * step:.0f} {bot} V420" stroke-width="9"/></svg>')


def stats() -> dict:
    s = charts.STATS
    return {
        "dups": f"{s['dups']}",
        "dup_groups": f"{s['dup_groups']}",
        "wc_min": f"{s['wc_min']:.2f}", "wc_max": f"{s['wc_max']:.2f}",
        "dens_min": f"{s['dens_min']:,.0f}", "dens_max": f"{s['dens_max']:,.0f}",
        "wt_na": f"{s['wt_na']}",
        "wt_rows_na": f"{s['wt_rows_na']}",
        "wt_complete": f"{s['wt_complete']}",
        "wt_drop_pct": f"{s['wt_drop_pct']:.0f}",
        "wt_sat": f"{s['wt_sat']}",
        "n_train": f"{s['n_train']}", "n_test": f"{s['n_test']}",
    }


def tbl_rows(n=4) -> str:
    """First rows of the concrete file: cement, slag, water, age | strength."""
    out = []
    for i, r in enumerate(charts.R[:n]):
        cls = ' class="r1"' if i == 0 else ""
        out.append(f'<tr{cls}><td class="i">{i}</td><td>{r[0]:.1f}</td><td>{r[1]:.1f}</td><td>{r[3]:.1f}</td>'
                   f'<td>{int(r[7])}</td><td class="y">{r[8]:.2f}</td></tr>')
    return "".join(out)


svgs = charts.build()
values = stats()
src = (HERE / "deck.src.html").read_text()
total = src.count('<section class="slide')
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
src = re.sub(r"\{\{chart:([A-Za-z0-9]+)\}\}", lambda m: svgs[m.group(1)], src)
src = re.sub(r"\{\{stat:([a-z0-9_]+)\}\}", lambda m: values[m.group(1)], src)
src = re.sub(r"\{\{logo:([a-z]+)\}\}", lambda m: f'<img class="lg-{m.group(1)}" src="{SHARED}/logos/{m.group(1)}.svg" alt="{m.group(1)} logo">', src)
src = src.replace("{{logo-light}}", f'<img src="{LOGO_LIGHT}" alt="Qudelta Studios">')
src = src.replace("{{notebook_link}}", NOTEBOOK_LINK)
src = src.replace("{{truss}}", truss())
src = src.replace("{{tblrows}}", tbl_rows())

parts = src.split('<section class="slide')
out = [parts[0]]
for n, part in enumerate(parts[1:], 1):
    def header(m):
        kind = m.group(1)
        pill = f'<span class="sp"><i></i>{SECTIONS[kind]}</span>' if kind in SECTIONS else ""
        return (f'<header class="top"><div class="hc">AI &amp; ML for Civil Engineers<span>Session 02</span></div>'
                f'<div class="hr">{pill}<span class="n"><b>{n:02d}</b> / {total}</span></div></header>')
    out.append(re.sub(r"\{\{top:([0-3bd])\}\}", header, part, count=1))
html = '<section class="slide'.join(out)
leftover = re.findall(r"\{\{[^}]*\}\}", html)
assert not leftover, leftover
(HERE / "deck.html").write_text(html)
print("built deck.html with", total, "slides")
