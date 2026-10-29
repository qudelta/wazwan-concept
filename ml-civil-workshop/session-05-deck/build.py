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

SECTIONS = {
    "0": "Course overview",
    "1": "Part 01 · Classification basics",
    "2": "Part 02 · Slope stability",
    "3": "Part 03 · Results & decision",
    "a": "Appendix A · Trees & forests",
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


def H2(p):
    return 0.0 if p in (0, 1) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def stats() -> dict:
    R = charts.R
    T, cnt, sp, ex, c = R["test"], R["counts"], R["split"], R["example"], R["lr_coef"]
    n, n_un = R["n"], cnt["1.0"]["below"]
    lr, rf = T["Logistic regression"], T["Random forest"]
    bl = T["Majority baseline"]
    v = {
        "n": f"{n}", "n_un": f"{n_un}", "n_st": f"{cnt['1.0']['above']}",
        "n_un15": f"{cnt['1.5']['below']}", "n_st15": f"{cnt['1.5']['above']}",
        "pct_un": f"{100 * n_un / n:.1f}", "pct_st": f"{100 * (n - n_un) / n:.1f}", "w_un": f"{100 * n_un / (n - n_un):.1f}",
        "fos_range": f"{R['fos_min']:.2f}–{R['fos_max']:.2f}",
        "n_train": f"{sp['train']}", "n_test": f"{sp['test']}", "train_un": f"{sp['train_unstable']}",
        "train_st": f"{sp['train'] - sp['train_unstable']}", "test_un": f"{sp['test_unstable']}",
        "test_st": f"{sp['test'] - sp['test_unstable']}",
        "demo_min": num(min(R["demo"]["lin"]), 2), "demo_max": num(max(R["demo"]["lin"]), 2),
        "bl_tn": f"{bl['cm'][0]}", "bl_fn": f"{bl['cm'][2]}", "bl_acc": f"{100 * bl['acc']:.1f}",
        "b0": num(c["b0"], 2), "b_beta": num(c["beta_deg"], 3), "b_c": num(c["c_by_gammaH"], 1, True).replace("+", "+ ").replace("−", "− "),
        "b_phi": num(c["phi_deg"], 3, True).replace("+", "+ ").replace("−", "− "),
        "ex_beta": f"{ex['beta_deg']:.0f}", "ex_c": f"{ex['c_by_gammaH']:.2f}", "ex_phi": f"{ex['phi_deg']:.0f}",
        "ex_z": num(ex["z"], 2), "ex_p": f"{ex['p']:.2f}", "ex_fos": f"{ex['fos']:.2f}",
        "cv_lr": f"{R['cv']['Logistic regression']['recall']:.3f}", "cv_dt": f"{R['cv']['Decision tree']['recall']:.3f}",
        "cv_rf": f"{R['cv']['Random forest']['recall']:.3f}",
        "rf_fn": f"{rf['cm'][2]}", "lr_fp": f"{lr['cm'][1]}",
        "boot": ", ".join(str(i) for i in R["bootstrap"]),
        "h_root": f"{H2(n_un / n):.3f}", "g_root": f"{2 * (n_un / n) * (1 - n_un / n):.3f}",
    }
    for tag, m in (("lr", lr), ("rf", rf)):
        for k in ("rec", "prec", "f1", "bal"):
            v[f"{tag}_{k}"] = f"{m[k]:.3f}"
    for tag, key in (("cw0", "None"), ("cw1", "balanced")):
        cw = R["cw"][key]
        v[f"{tag}_rec"] = f"{cw['rec']:.2f}"
        v[f"{tag}_tn"], v[f"{tag}_fp"], v[f"{tag}_fn"], v[f"{tag}_tp"] = (f"{x}" for x in cw["cm"])
    return v


def tables() -> dict:
    R = charts.R
    T = R["test"]
    rows = []
    for name in ["Majority baseline"] + charts.MODELS:
        m = T[name]
        cls = ' class="bl"' if name == "Majority baseline" else ""
        cells = "".join(f'<td{" class=\"k\"" if k == "rec" else ""}>{m[k]:.3f}</td>' for k in ("acc", "bal", "prec", "rec", "f1", "auc", "ap"))
        rows.append(f"<tr{cls}><td>{name}</td>{cells}</tr>")
    boxes = []
    for name in charts.MODELS:
        tn, fp, fn, tp = T[name]["cm"]
        boxes.append(f'<div class="box"><h3>{name}</h3><div class="cm"><span></span><span class="hd">Pred. stable</span><span class="hd">Pred. unstable</span>'
                     f'<span class="ax rl">Stable</span><div class="c tn"><b>{tn}</b><span>TN</span></div><div class="c fp"><b>{fp}</b><span>FP · false alarm</span></div>'
                     f'<span class="ax rl">Unstable</span><div class="c fn"><b>{fn}</b><span>FN · missed</span></div><div class="c tp"><b>{tp}</b><span>TP</span></div></div>'
                     f'<div class="s">recall {T[name]["rec"]:.3f} · precision {T[name]["prec"]:.3f}</div></div>')
    phirows = "".join(f'<tr><td>{p}°</td><td><span class="b" style="width:{u * 12}px"></span>{u}</td></tr>' for p, u in R["unstable_by_phi"].items())
    thr = R["thr"]
    on = lambda t: ' class="on"' if t["t"] == 0.5 else ""  # noqa: E731
    return {
        "testrows": "".join(rows), "cmboxes": "".join(boxes), "phirows": phirows,
        "thr_head": "".join(f'<th>{t["t"]:.1f}</th>' for t in thr),
        "thr_rec": "".join(f'<td{on(t)}>{t["rec"]:.2f}</td>' for t in thr),
        "thr_prec": "".join(f'<td{on(t)}>{t["prec"]:.2f}</td>' for t in thr),
        "thr_err": "".join(f'<td{on(t)}>{t["cm"][2]} · {t["cm"][1]}</td>' for t in thr),
    }


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
for k, v in tables().items():
    src = src.replace("{{" + k + "}}", v)

parts = src.split('<section class="slide')
out = [parts[0]]
for n, part in enumerate(parts[1:], 1):
    def header(m):
        kind = m.group(1)
        pill = f'<span class="sp"><i></i>{SECTIONS[kind]}</span>' if kind in SECTIONS else ""
        return (f'<header class="top"><div class="hc">AI &amp; ML for Civil Engineers<span>Session 05</span></div>'
                f'<div class="hr">{pill}<span class="n"><b>{n:02d}</b> / {total}</span></div></header>')
    out.append(re.sub(r"\{\{top:([0-3bda])\}\}", header, part, count=1))
html = '<section class="slide'.join(out)
leftover = re.findall(r"\{\{[^}]*\}\}", html)
assert not leftover, leftover
(HERE / "deck.html").write_text(html)
print("built deck.html with", total, "slides")
