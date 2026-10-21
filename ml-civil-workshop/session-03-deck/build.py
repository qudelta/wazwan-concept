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
    "1": "Part 01 · Build the model",
    "2": "Part 02 · Evaluation",
    "3": "Part 03 · Validation",
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


def num(v: float, d: int = 1, sign: bool = False) -> str:
    """Typographic minus; optional explicit plus."""
    t = f"{abs(v):,.{d}f}"
    return ("−" if v < 0 else "+" if sign else "") + t


def stats() -> dict:
    s = charts.STATS
    c, ex, A = s["coef"], s["example"], s["alpha"]
    v = {
        "n_raw": f"{s['n_raw']:,}", "n": f"{s['n']:,}", "dups": f"{s['dups']}",
        "n_train": f"{s['n_train']}", "n_test": f"{s['n_test']}", "base": num(s["base"]),
        "mae_gain": f"{100 * (1 - s['lr_test']['mae'] / s['base_test']['mae']):.0f}",
        "b0": num(s["b0"], 2), "coef_list": ", ".join(num(x, 3) for x in c.values()),
        "ex_cement": num(ex["row"]["cement"]), "ex_slag": num(ex["row"]["slag"]), "ex_ash": num(ex["row"]["ash"]),
        "ex_water": num(ex["row"]["water"]), "ex_sp": num(ex["row"]["superplastic"]),
        "ex_agg": f"{ex['row']['coarseagg']:.0f} · {ex['row']['fineagg']:.0f}", "ex_age": f"{ex['row']['age']:.0f}",
        "ex_pred": num(ex["pred"]), "ex_actual": num(ex["actual"]), "ex_err": num(ex["pred"] - ex["actual"], 1, True),
        "gd_steps": f"{s['gd_steps']}", "gd_start": f"{s['gd_start']:,.0f}", "gd_end": f"{s['gd_end']:.0f}",
        "a_small": f"{A['small']['alpha']}", "n_small": f"{A['small']['n']}",
        "pct_small": f"{100 * (1 - A['small']['end'] / A['small']['start']):.0f}",
        "a_good": f"{A['good']['alpha']}", "n_good": f"{A['good']['n']}", "a_large": f"{A['large']['alpha']}",
        "it_raw": f"{s['scale_iters']['raw']:,}", "it_std": f"{s['scale_iters']['scaled']}",
        "s42": f"{s['seed'][42]:.2f}", "s7": f"{s['seed'][7]:.2f}", "s21": f"{s['seed'][21]:.2f}",
        "seed_min": f"{s['seed_min']:.2f}", "seed_max": f"{s['seed_max']:.2f}",
        "cv_mean": f"{s['cv_mean']:.2f}", "cv_sd": f"{s['cv_sd']:.2f}",
    }
    for k, name in (("cement", "cement"), ("slag", "slag"), ("ash", "ash"), ("water", "water"), ("sp", "superplastic"),
                    ("coarse", "coarseagg"), ("fine", "fineagg"), ("age", "age")):
        v[f"c_{k}"] = num(c[name], 3)
    for tag, key in (("bt", "base_test"), ("t", "lr_test"), ("tr", "lr_train")):
        v[f"{tag}_mae"], v[f"{tag}_rmse"] = num(s[key]["mae"]), num(s[key]["rmse"])
        v[f"{tag}_r2"] = num(s[key]["r2"], 2) if abs(s[key]["r2"]) >= 0.005 else "0.00"
    ra = dict(s["resid_age"])
    v["ra_3"], v["ra_56"], v["ra_360"] = num(ra[3.0], 1, True), num(ra[56.0], 1, True), num(ra[360.0], 1, True)
    return v


def stack(layers: list) -> str:
    """Charts that build click by click: every layer is its own absolutely positioned SVG (class L0, L1, ...)."""
    return "".join(f'<svg class="L{k}"' + svg[4:] for k, svg in enumerate(layers))


svgs = charts.build()
values = stats()
src = (HERE / "deck.src.html").read_text()
total = src.count('<section class="slide')
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
src = re.sub(r"\{\{chart:([A-Za-z0-9]+)\}\}", lambda m: svgs[m.group(1)], src)
src = re.sub(r"\{\{stack:([A-Za-z0-9]+)\}\}", lambda m: stack(svgs[m.group(1)]), src)
src = re.sub(r"\{\{stat:([a-z0-9_]+)\}\}", lambda m: values[m.group(1)], src)
src = re.sub(r"\{\{logo:([a-z]+)\}\}", lambda m: f'<img class="lg-{m.group(1)}" src="{SHARED}/logos/{m.group(1)}.svg" alt="{m.group(1)} logo">', src)
src = src.replace("{{logo-light}}", f'<img src="{LOGO_LIGHT}" alt="Qudelta Studios">')
src = src.replace("{{notebook_link}}", NOTEBOOK_LINK)
src = src.replace("{{truss}}", truss())

parts = src.split('<section class="slide')
out = [parts[0]]
for n, part in enumerate(parts[1:], 1):
    def header(m):
        kind = m.group(1)
        pill = f'<span class="sp"><i></i>{SECTIONS[kind]}</span>' if kind in SECTIONS else ""
        return (f'<header class="top"><div class="hc">AI &amp; ML for Civil Engineers<span>Session 03</span></div>'
                f'<div class="hr">{pill}<span class="n"><b>{n:02d}</b> / {total}</span></div></header>')
    out.append(re.sub(r"\{\{top:([0-3bd])\}\}", header, part, count=1))
html = '<section class="slide'.join(out)
leftover = re.findall(r"\{\{[^}]*\}\}", html)
assert not leftover, leftover
(HERE / "deck.html").write_text(html)
print("built deck.html with", total, "slides")
