import math
import re
import sys
from pathlib import Path

import charts

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/@phosphor-icons/core/assets/duotone"
SHARED = "../session-01-deck/assets"   # logos and the Amiri font live with Session 01
LOGO_LIGHT = "../poster/assets/qudelta-logo-light.png"  # light text, for dark slides
NOTEBOOK_LINK = "Link shared in the session chat"
ORANGE, GREEN, INK, MUTED = charts.ORANGE, charts.GREEN, charts.INK, charts.MUTED

SECTIONS = {
    "0": "Course overview",
    "r": "Recap · concrete strength",
    "1": "Part 01 · ANN intuition",
    "2": "Part 02 · Build & train",
    "3": "Part 03 · Results & judgement",
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
    R = charts.R
    T, rng = R["test"], R["ranges"]
    rf, ann, lin = T["Random forest"], T["ANN (32, 16)"], T["Linear regression"]
    y, p = (charts.np.array(R["lin_test"][k]) for k in ("y", "p"))
    rng_txt = lambda c, d=0: f"{rng[c][0]:,.{d}f}–{rng[c][1]:,.{d}f}"  # noqa: E731
    arch = {a["name"]: a["rmse"] for a in R["arch"]}
    v = {
        "n": f"{R['n']:,}", "nf": f"{R['n_features']}", "miss": f"{R['missing']}",
        "n_train": f"{R['n_train']}", "n_test": f"{R['n_test']}",
        "s_lo": f"{rng['strength'][0]:.1f}", "s_hi": f"{rng['strength'][1]:.1f}",
        "sp_hi": f"{rng['superplastic'][1]:.1f}", "ca_lo": f"{rng['coarseagg'][0]:.0f}", "ca_hi": f"{rng['coarseagg'][1]:,.0f}",
        "a_best": f"{arch['Larger']:.3f}", "a_deep": f"{arch['Deeper']:.3f}",
        "rf_r2": f"{rf['r2']:.3f}", "ann_r2": f"{ann['r2']:.3f}", "lin_r2": f"{lin['r2']:.3f}",
        "r_lo": f"{-(y - p)[y < 20].mean():.1f}", "r_hi": f"{(y - p)[y >= 60].mean():.1f}",
        "d_cement": rng_txt("cement"), "d_water": rng_txt("water"), "d_sp": rng_txt("superplastic", 1),
        "d_age": rng_txt("age"), "d_str": rng_txt("strength", 1),
    }
    for tag, m in (("rf", rf), ("ann", ann), ("lin", lin)):
        v[f"{tag}_mae"], v[f"{tag}_rmse"] = f"{m['mae']:.2f}", f"{m['rmse']:.2f}"
    return v


def stack(layers: list) -> str:
    """Charts that build click by click: every layer is its own absolutely positioned SVG (class L0, L1, ...)."""
    return "".join(f'<svg class="L{k}"' + svg[4:] for k, svg in enumerate(layers))


# ------------------------------------------------------------------ network diagrams (HTML neurons + SVG arrows)
def fat(w: int) -> str:
    """A bold block arrow filling a w × h viewBox (h = 40 for wide arrows, 28 for short ones)."""
    h = 40 if w >= 120 else 28
    t, hw = h * 0.3, h * 0.55
    return (f'<path d="M0 {h / 2 - t / 2:.1f} H{w - hw:.1f} V2 L{w} {h / 2:.1f} L{w - hw:.1f} {h - 2} V{h / 2 + t / 2:.1f} H0 Z" fill="{INK}"/>')


def to_circle(x1, y1, cx, cy, r):
    """End point of an arrow from (x1, y1) that stops just short of a circle of radius r at (cx, cy)."""
    d = math.hypot(cx - x1, cy - y1)
    return cx - (cx - x1) * (r + 6) / d, cy - (cy - y1) * (r + 6) / d


INPUTS = [("Price", 100), ("Shipping cost", 220), ("Marketing", 340), ("Material", 460)]
HIDDEN = [("Affordability", 110, 50, 945), ("Awareness", 290, 232, 912), ("Perceived quality", 470, 500, 1000)]  # name, y, label top, check x
HX, OX, OY, NR = 700, 1240, 290, 36
SPARSE = {3: [(0, 0), (1, 0)], 5: [(2, 1)], 7: [(0, 2), (3, 2)]}       # click: (input, hidden neuron) pairs, as in the draft


def arrows_svg(cls, pairs, color=ORANGE):
    body = ""
    for i, h in pairs:
        y1, cy = INPUTS[i][1], HIDDEN[h][1]
        x2, y2 = to_circle(292, y1, HX, cy, NR)
        body += charts.arrow(292, y1, x2, y2, color, 4, 15)
    return f'<svg class="ar {cls}" viewBox="0 0 1680 640">{body}</svg>'


def dp(mode: str) -> str:
    """The demand-prediction network. mode 'build': every part carries its click class k1…k19 (the draft's order);
    'full': everything shown, sparse arrows class 'sparse'; 'dense': every input feeds every neuron, one class d1…d4 per input."""
    k = (lambda n: f" k{n}") if mode == "build" else (lambda n: "")  # noqa: E731
    out = []
    if mode == "dense":
        out += [arrows_svg(f"d{i + 1}", [(i, h) for h in range(3)]) for i in range(4)]
    else:
        out += [arrows_svg(("sparse" if mode == "full" else "") + k(c), pairs) for c, pairs in SPARSE.items()]
    act = "".join(charts.arrow(HX + NR + 4, y, *to_circle(HX + NR + 4, y, OX, OY + (y - OY) * 0.12, NR), GREEN, 4, 15) for _, y, _, _ in HIDDEN)
    out.append(f'<svg class="ar{k(9)}" viewBox="0 0 1680 640">{act}</svg>')
    out.append(f'<svg class="ar{k(11)}" viewBox="0 0 1680 640">{charts.arrow(OX + NR + 6, OY, 1390, OY, INK, 4, 15)}</svg>')
    ptr_o = f'<path d="M1338 168 Q1300 170 1292 228" fill="none" stroke="{MUTED}" stroke-width="3"/>' + charts.arrow(1293, 214, 1292, 232, MUTED, 3, 12)
    ptr_i = f'<path d="M200 38 Q262 40 268 70" fill="none" stroke="{MUTED}" stroke-width="3"/>' + charts.arrow(268, 58, 268, 76, MUTED, 3, 12)
    out.append(f'<svg class="ar{k(18)}" viewBox="0 0 1680 640">{ptr_o}</svg>')
    out.append(f'<svg class="ar{k(19)}" viewBox="0 0 1680 640">{ptr_i}</svg>')
    out += [f'<span class="in" style="left:30px;top:{y - 20}px">{n}</span>' for n, y in INPUTS]
    out.append(f'<span class="box{k(12)}" style="left:{HX - 54}px;top:56px;width:108px;height:468px"></span>')
    out.append(f'<span class="box{k(14)}" style="left:{OX - 54}px;top:{OY - 54}px;width:108px;height:108px"></span>')
    for c, (_, y, _, _) in zip((2, 4, 6), HIDDEN):
        out.append(f'<span class="nr{k(c)}" style="left:{HX - NR}px;top:{y - NR}px"></span>')
    out.append(f'<span class="nr o{k(8)}" style="left:{OX - NR}px;top:{OY - NR}px"></span>')
    for name, _, top, _ in HIDDEN:
        out.append(f'<span class="act{k(1)}" style="left:760px;top:{top}px">{name}</span>')
    out.append(f'<span class="pr{k(1)}" style="left:1404px;top:{OY - 36}px">Probability of being a top seller</span>')
    for name, _, top, cx in HIDDEN:
        out.append(f'<span class="ck{k(16)}" style="left:{cx}px;top:{top - 2}px">{icon("check-fat")}</span>')
    out.append(f'<span class="acts{k(16)}" style="left:790px;top:12px">“Activations”</span>')
    out.append(f'<span class="lay{k(13)}" style="left:{HX - 100}px;top:14px">Layer</span>')
    out.append(f'<span class="lay{k(15)}" style="left:{OX - 100}px;top:{OY - 94}px">Layer</span>')
    out.append(f'<span class="av{k(17)}" style="left:870px;top:440px">activation value</span>')
    for txt, cx in (("4 numbers", 155), ("3 numbers", HX), ("1 number", OX)):
        out.append(f'<span class="num{k(10)}" style="left:{cx - 110}px;top:584px">{txt}</span>')
    out.append(f'<span class="ptr{k(18)}" style="left:1344px;top:150px">output layer</span>')
    out.append(f'<span class="ptr{k(19)}" style="left:40px;top:20px">input layer</span>')
    return f'<div class="dp">{"".join(out)}</div>'


def mlp(spec: str) -> str:
    """A small multilayer perceptron: x → hidden layers (dashed boxes) → output, with vector a on each arrow."""
    sizes = [int(v) for v in spec.split(",")]
    arr = lambda lab: f'<span class="ar"><span class="v">{lab}</span><svg viewBox="0 0 74 28">{fat(74)}</svg></span>'  # noqa: E731
    names = ["1st hidden<br>layer", "2nd hidden<br>layer"]
    parts = ['<span class="x">x</span>', arr("&nbsp;")]
    for n, name in zip(sizes, names):
        parts.append(f'<div class="col"><div class="dash">{"<i></i>" * n}</div><span class="k">{name}</span></div>')
        parts.append(arr("a"))
    parts.append('<div class="col"><div class="dash o"><i></i></div><span class="k">Output<br>layer</span></div>')
    parts.append(arr("&nbsp;"))
    return f'<div class="net">{"".join(parts)}</div>'


def rows(kind: str) -> str:
    if kind == "epoch":
        return "<i></i>" * 30
    return "".join(f'<i class="b{(j // 4) % 3 + 1}"></i>' for j in range(30))


svgs = charts.build()
values = stats()
src = (HERE / "deck.src.html").read_text()
total = src.count('<section class="slide')
src = re.sub(r"\{\{dp:([a-z]+)\}\}", lambda m: dp(m.group(1)), src)
src = re.sub(r"\{\{mlp:([0-9,]+)\}\}", lambda m: mlp(m.group(1)), src)
src = re.sub(r"\{\{fat:([0-9]+)\}\}", lambda m: fat(int(m.group(1))), src)
src = re.sub(r"\{\{rows:([a-z]+)\}\}", lambda m: rows(m.group(1)), src)
src = src.replace("{{arrows:bio}}", charts.arrow(110, 175, 240, 175, charts.BLUE, 5, 18) + charts.arrow(382, 175, 568, 175, INK, 5, 18))
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
        return (f'<header class="top"><div class="hc">AI &amp; ML for Civil Engineers<span>Session 06</span></div>'
                f'<div class="hr">{pill}<span class="n"><b>{n:02d}</b> / {total}</span></div></header>')
    out.append(re.sub(r"\{\{top:([0-3bdr])\}\}", header, part, count=1))
html = '<section class="slide'.join(out)
leftover = re.findall(r"\{\{[^}]*\}\}", html)
assert not leftover, leftover
(HERE / "deck.html").write_text(html)
print("built deck.html with", total, "slides")
