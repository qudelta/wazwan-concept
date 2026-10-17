"""SVG charts for the Session 02 deck, drawn from three real engineering datasets (UCI Machine Learning Repository).

  Concrete Compressive Strength (Yeh, 1998)            1,030 laboratory mixes, 8 inputs + strength
  Water Treatment Plant (Poch; Bejar & Cortés, 1993)   527 daily records, 38 sensor and lab variables, '?' = missing
  Steel Plates Faults (Buscema, Terzi & Tastle, 2010)  1,941 plates, 27 features, 7 fault classes

Colour roles follow Session 01 (validated all-pairs with the dataviz validator, light surface):
  blue   #2a78d6  observations / inputs X
  orange #eb6834  target y, and anything flagged for attention (missing values, outliers, test rows)
  green  #1baf7a  model-side: fitted curve, training rows
"""
import csv
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_T, ORANGE_T = "#CFE0F5", "#F7D3C3"
INK, INK2, MUTED, GRID, AXIS = "#0E1A2B", "#334155", "#64748B", "#E6EBF1", "#94A3B8"
FONT = "Archivo, sans-serif"

# ------------------------------------------------------------------ data
rows = list(csv.reader(open(HERE / "data/concrete.csv")))
CCOLS = rows[0]
R = np.array([[float(x) for x in r] for r in rows[1:]])
cem, slag, ash, wat, sp, cagg, fagg, age, fc = R.T

WT_NAMES = ("Q-E ZN-E PH-E DBO-E DQO-E SS-E SSV-E SED-E COND-E PH-P DBO-P SS-P SSV-P SED-P COND-P PH-D DBO-D DQO-D "
            "SS-D SSV-D SED-D COND-D PH-S DBO-S DQO-S SS-S SSV-S SED-S COND-S RD-DBO-P RD-SS-P RD-SED-P RD-DBO-S "
            "RD-DQO-S RD-DBO-G RD-DQO-G RD-SS-G RD-SED-G").split()
_wt = [line.strip().split(",") for line in open(HERE / "data/water-treatment.data") if line.strip()]
_dates = [tuple(int(p) for p in r[0][2:].split("/")) for r in _wt]            # D-day/month/yy
_order = sorted(range(len(_wt)), key=lambda i: (_dates[i][2], _dates[i][1], _dates[i][0]))
WT_DATES = [_dates[i] for i in _order]
WT_NA = np.array([[v == "?" for v in _wt[i][1:]] for i in _order])            # rows sorted by date

_sp_cols = open(HERE / "data/steel-plates-faults.columns").read().split()
_sp = np.loadtxt(HERE / "data/steel-plates-faults.tsv")
SP_CLASSES = {c: int(_sp[:, _sp_cols.index(c)].sum()) for c in _sp_cols[-7:]}


def _weekday(d, m, y):
    import datetime
    return datetime.date(1900 + y, m, d).weekday()


def _iqr(v):
    q1, q3 = np.percentile(v, [25, 75])
    i = q3 - q1
    return q1, q3, q1 - 1.5 * i, q3 + 1.5 * i


_dup = {}
for r in R:
    _dup[tuple(r)] = _dup.get(tuple(r), 0) + 1
wc = wat / cem

STATS = {
    "n": len(R),
    "dups": int(sum(k - 1 for k in _dup.values())),
    "dup_groups": int(sum(1 for k in _dup.values() if k > 1)),
    "wc_min": float(wc.min()), "wc_max": float(wc.max()),
    "dens_min": float(R[:, :7].sum(1).min()), "dens_max": float(R[:, :7].sum(1).max()),
    "wt_n": len(_wt), "wt_vars": WT_NA.shape[1],
    "wt_na": int(WT_NA.sum()), "wt_rows_na": int(WT_NA.any(1).sum()), "wt_complete": int((~WT_NA.any(1)).sum()),
    "wt_sat": sum(1 for d in WT_DATES if _weekday(*d) == 5),
    "wt_na_by_var": {n: int(c) for n, c in zip(WT_NAMES, WT_NA.sum(0))},
    "sp_n": len(_sp), "sp_classes": SP_CLASSES,
    "corr": {c: float(np.corrcoef(R[:, k], fc)[0, 1]) for k, c in enumerate(CCOLS[:-1])},
    "n_train": len(R) - math.ceil(0.2 * len(R)), "n_test": math.ceil(0.2 * len(R)),
}
STATS["wt_drop_pct"] = 100 * STATS["wt_rows_na"] / STATS["wt_n"]
STATS["sp_major"] = max(SP_CLASSES.values()) / STATS["sp_n"]


class Plot:
    """Tiny SVG plotting helper (as in Session 01): linear or log x, linear y, recessive grid, text-token labels."""

    def __init__(self, w, h, xd, yd, pad=(70, 30, 30, 76), xlog=False):
        self.w, self.h, self.xd, self.yd, self.xlog = w, h, xd, yd, xlog
        self.l, self.t, self.r, self.b = pad
        self.out = []

    def X(self, v):
        lo, hi = self.xd
        if self.xlog:
            v, lo, hi = math.log10(v), math.log10(lo), math.log10(hi)
        return self.l + (v - lo) / (hi - lo) * (self.w - self.l - self.r)

    def Y(self, v):
        lo, hi = self.yd
        return self.h - self.b - (v - lo) / (hi - lo) * (self.h - self.t - self.b)

    def text(self, x, y, s, size=20, fill=MUTED, anchor="start", weight=500, extra="", halo=True, family=FONT):
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
                        f'fill="{fill}" text-anchor="{anchor}" paint-order="stroke" stroke="#fff" stroke-width="{6 if halo else 0}" stroke-linejoin="round" {extra}>{s}</text>')

    def rect(self, x, y, w, h, fill, extra=""):
        self.out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" fill="{fill}" {extra}/>')

    def line(self, x1, y1, x2, y2, color, width=1.5, extra=""):
        self.out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" {extra}/>')

    def axes(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str, size=19):
        x0, x1 = self.l, self.w - self.r
        y0, y1 = self.h - self.b, self.t
        for v in yticks:
            y = self.Y(v)
            self.line(x0, y, x1, y, GRID)
            self.text(x0 - 12, y + 7, yfmt(v), size=size, anchor="end")
        for v in xticks:
            x = self.X(v)
            self.line(x, y0, x, y0 + 8, AXIS)
            self.text(x, y0 + 30, xfmt(v), size=size, anchor="middle")
        self.line(x0, y0, x1, y0, AXIS, 2)
        if xlabel:
            self.text((x0 + x1) / 2, self.h - 8, xlabel, size=size + 1, fill=INK2, anchor="middle", weight=600)
        if ylabel:
            self.text(22, (y0 + y1) / 2, ylabel, size=size + 1, fill=INK2, anchor="middle", weight=600,
                      extra=f'transform="rotate(-90 22 {(y0 + y1) / 2:.1f})"')

    def dots(self, xs, ys, color, r=6, opacity=0.78):
        for x, y in zip(xs, ys):
            self.out.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{color}" fill-opacity="{opacity}" stroke="#fff" stroke-width="1.2"/>')

    def path(self, pts, color, width=4, dash=""):
        d = "M" + " L".join(f"{self.X(x):.1f} {self.Y(y):.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{da}/>')

    def svg(self, label):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}" '
                f'xmlns="http://www.w3.org/2000/svg">' + "".join(self.out) + "</svg>")


# ------------------------------------------------------------------ explore: histograms
def chart_hist(v, lo, hi, step, xticks, unit, mark=None):
    """One histogram, the way df.hist() shows it but in course styling. mark = (x0, x1, label) shades a range."""
    edges = np.arange(lo, hi + step, step)
    counts, _ = np.histogram(v, edges)
    top = counts.max() * 1.18
    p = Plot(640, 330, (lo, hi), (0, top), pad=(58, 24, 16, 64))
    step_y = next(s for s in (25, 50, 100, 200) if top / s <= 5)
    p.axes(xticks, list(range(0, int(top), step_y)), unit, "", size=18)
    if mark:
        p.rect(p.X(mark[0]), p.t, p.X(mark[1]) - p.X(mark[0]), p.h - p.b - p.t, ORANGE, 'fill-opacity=".10"')
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        hot = mark and a >= mark[0] - 1e-9 and b <= mark[1] + 1e-9
        p.rect(p.X(a) + 1.5, p.Y(c), p.X(b) - p.X(a) - 3, p.Y(0) - p.Y(c), ORANGE if hot else BLUE, 'rx="3"')
    if mark:
        p.text(p.X(mark[0]) + (8 if mark[3] == "start" else -8), p.t + 20, mark[2], size=18, fill=INK, weight=700,
               anchor=mark[3])
    return p.svg(f"Histogram of {unit}")


# ------------------------------------------------------------------ missing values: map
WT_GROUPS = [  # label, variables (in plot order), how it is measured
    ("pH", ["PH-E", "PH-P", "PH-D", "PH-S"], "online"),
    ("Conductivity", ["COND-E", "COND-P", "COND-D", "COND-S"], "online"),
    ("Suspended solids", ["SS-E", "SS-P", "SS-D", "SS-S"], "lab"),
    ("Flow, zinc", ["Q-E", "ZN-E"], "online"),
    ("Volatile SS", ["SSV-E", "SSV-P", "SSV-D", "SSV-S"], "lab"),
    ("COD", ["DQO-E", "DQO-D", "DQO-S"], "lab"),
    ("Sediments", ["SED-E", "SED-P", "SED-D", "SED-S"], "lab"),
    ("BOD (5-day test)", ["DBO-E", "DBO-P", "DBO-D", "DBO-S"], "lab"),
    ("Performance (derived)", ["RD-SS-P", "RD-SS-G", "RD-DQO-S", "RD-DQO-G", "RD-SED-P", "RD-SED-G", "RD-DBO-S", "RD-DBO-G", "RD-DBO-P"], "derived"),
]


def chart_missmap():
    order = [v for _, vs, _ in WT_GROUPS for v in vs]
    assert sorted(order) == sorted(WT_NAMES)
    n = len(WT_DATES)
    W, H, L, T, Rm, B = 1640, 540, 270, 34, 110, 50
    cw, gap = (W - L - Rm) / n, 9
    rh = (H - T - B - gap * (len(WT_GROUPS) - 1)) / len(order)
    o = []
    y = T
    month_x = {}
    for i, (d, m, yy) in enumerate(WT_DATES):
        month_x.setdefault((yy, m), L + i * cw)
    for gi, (label, vs, kind) in enumerate(WT_GROUPS):
        gh = rh * len(vs)
        o.append(f'<rect x="{L}" y="{y:.1f}" width="{W - L - Rm}" height="{gh:.1f}" rx="4" fill="#F1F5F9"/>')
        cnt = 0
        for k, v in enumerate(vs):
            col = WT_NAMES.index(v)
            for i in np.flatnonzero(WT_NA[:, col]):
                o.append(f'<rect x="{L + i * cw - .4:.1f}" y="{y + k * rh + .6:.1f}" width="{max(cw, 2.6) + .8:.1f}" height="{rh - 1.2:.1f}" fill="{ORANGE}"/>')
            cnt += int(WT_NA[:, col].sum())
        fill = INK
        o.append(f'<text x="{L - 16}" y="{y + gh / 2 + 7:.1f}" font-family="{FONT}" font-size="22" font-weight="700" fill="{fill}" text-anchor="end">{label}</text>')
        o.append(f'<text x="{W - Rm + 16}" y="{y + gh / 2 + 7:.1f}" font-family="JetBrains Mono, monospace" font-size="21" font-weight="700" fill="{ORANGE if cnt else GREEN}">{cnt if cnt else "0"}</text>')
        y += gh + gap
    o.append(f'<text x="{W - Rm + 16}" y="{T - 14}" font-family="{FONT}" font-size="16" font-weight="800" letter-spacing="1.5" fill="{MUTED}">MISSING</text>')
    yb = H - B
    for (yy, m), x in month_x.items():
        if m in (1, 4, 7, 10):
            name = ["Jan", "Apr", "Jul", "Oct"][(m - 1) // 3]
            o.append(f'<line x1="{x:.1f}" y1="{yb}" x2="{x:.1f}" y2="{yb + 8}" stroke="{AXIS}" stroke-width="1.5"/>'
                     f'<text x="{x:.1f}" y="{yb + 32}" font-family="{FONT}" font-size="18" fill="{MUTED}" text-anchor="middle">{name} {1900 + yy}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Missing-value map of the water-treatment dataset: '
            f'{STATS["wt_na"]} missing values over {n} days, concentrated in laboratory measurements" xmlns="http://www.w3.org/2000/svg">' + "".join(o) + "</svg>")


# ------------------------------------------------------------------ outliers: box plots with IQR flags
BOX_ROWS = [  # column, label, unit, axis, ticks, note
    (7, "Age", "days", (0, 380), [0, 90, 180, 270, 365], "All are real long-term tests: 180, 270, 360 and 365 days"),
    (8, "Strength", "MPa", (0, 90), [0, 20, 40, 60, 80], "High-strength mixes above 79.8 MPa: rare, not wrong"),
    (4, "Superplasticizer", "kg/m³", (0, 35), [0, 10, 20, 30], "Two mix families at 28.2 and 32.2 kg/m³"),
    (3, "Water", "kg/m³", (110, 255), [120, 160, 200, 240], "Both tails: very low and very high water contents"),
]


def chart_boxes():
    W, rowh, L, Rm = 1060, 136, 210, 30
    H = rowh * len(BOX_ROWS) + 20
    o = []
    rng = np.random.default_rng(3)
    flagged = {}
    for k, (col, label, unit, (lo, hi), ticks, _) in enumerate(BOX_ROWS):
        v = R[:, col]
        q1, q3, f0, f1 = _iqr(v)
        med = np.median(v)
        X = lambda x: L + (x - lo) / (hi - lo) * (W - L - Rm)  # noqa: E731
        y0 = 20 + k * rowh
        cy = y0 + 44
        out = (v < f0) | (v > f1)
        flagged[label] = int(out.sum())
        wl, wh = v[v >= f0].min(), v[v <= f1].max()
        o.append(f'<text x="0" y="{cy - 4:.1f}" font-family="{FONT}" font-size="25" font-weight="800" fill="{INK}">{label}</text>'
                 f'<text x="0" y="{cy + 22:.1f}" font-family="{FONT}" font-size="18" fill="{MUTED}">{unit}</text>')
        o.append(f'<line x1="{X(wl):.1f}" y1="{cy}" x2="{X(wh):.1f}" y2="{cy}" stroke="{INK2}" stroke-width="2.5"/>')
        for wv in (wl, wh):
            o.append(f'<line x1="{X(wv):.1f}" y1="{cy - 12}" x2="{X(wv):.1f}" y2="{cy + 12}" stroke="{INK2}" stroke-width="2.5"/>')
        o.append(f'<rect x="{X(q1):.1f}" y="{cy - 22}" width="{X(q3) - X(q1):.1f}" height="44" rx="6" fill="{BLUE_T}" stroke="{BLUE}" stroke-width="2.5"/>')
        o.append(f'<line x1="{X(med):.1f}" y1="{cy - 22}" x2="{X(med):.1f}" y2="{cy + 22}" stroke="{BLUE}" stroke-width="4"/>')
        jit = rng.uniform(-14, 14, out.sum())
        for x, j in zip(v[out], jit):
            o.append(f'<circle cx="{X(x):.1f}" cy="{cy + j:.1f}" r="6.5" fill="{ORANGE}" fill-opacity=".85" stroke="#fff" stroke-width="1.2"/>')
        ya = cy + 46
        o.append(f'<line x1="{L}" y1="{ya}" x2="{W - Rm}" y2="{ya}" stroke="{GRID}" stroke-width="1.5"/>')
        for t in ticks:
            o.append(f'<text x="{X(t):.1f}" y="{ya + 24}" font-family="{FONT}" font-size="17" fill="{MUTED}" text-anchor="middle">{t}</text>')
    STATS["box_flagged"] = flagged
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Box plots of four concrete variables; points beyond 1.5 IQR flagged in orange" '
            f'xmlns="http://www.w3.org/2000/svg">' + "".join(o) + "</svg>")


# ------------------------------------------------------------------ correlation
NICE = {"cement": "Cement", "slag": "Slag", "ash": "Fly ash", "water": "Water", "superplastic": "Superplasticizer",
        "coarseagg": "Coarse aggregate", "fineagg": "Fine aggregate", "age": "Age"}


def chart_corr():
    items = sorted(STATS["corr"].items(), key=lambda kv: -kv[1])
    W, H, L, Rm = 760, 540, 230, 40
    rh = (H - 70) / len(items)
    X = lambda r: L + (r + 1) / 2 * (W - L - Rm)  # noqa: E731
    o = []
    for t in (-1, -0.5, 0, 0.5, 1):
        o.append(f'<line x1="{X(t):.1f}" y1="10" x2="{X(t):.1f}" y2="{H - 50}" stroke="{AXIS if t == 0 else GRID}" stroke-width="{2 if t == 0 else 1.5}"/>'
                 f'<text x="{X(t):.1f}" y="{H - 20}" font-family="{FONT}" font-size="18" fill="{MUTED}" text-anchor="middle">{"0" if t == 0 else f"{t:+g}"}</text>')
    for k, (c, r) in enumerate(items):
        y = 14 + k * rh
        col = BLUE if r > 0 else ORANGE
        x0, x1 = sorted((X(0), X(r)))
        hot = c == "age"
        o.append(f'<text x="{L - 16}" y="{y + rh / 2 + 7:.1f}" font-family="{FONT}" font-size="21" font-weight="{800 if hot else 600}" fill="{INK}" text-anchor="end">{NICE[c]}</text>')
        o.append(f'<rect x="{x0:.1f}" y="{y + 8:.1f}" width="{x1 - x0:.1f}" height="{rh - 16:.1f}" rx="5" fill="{col}"/>')
        tx, an = (X(r) + 10, "start") if r > 0 else (X(r) - 10, "end")
        o.append(f'<text x="{tx:.1f}" y="{y + rh / 2 + 7:.1f}" font-family="JetBrains Mono, monospace" font-size="19" font-weight="700" fill="{INK2}" text-anchor="{an}">{r:+.2f}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Correlation of each concrete input with compressive strength" '
            f'xmlns="http://www.w3.org/2000/svg">' + "".join(o) + "</svg>")


def chart_age_scatter():
    p = Plot(700, 540, (0, 380), (0, 88), pad=(70, 20, 20, 70))
    p.axes([0, 90, 180, 270, 365], [0, 20, 40, 60, 80], "Age (days)", "Strength (MPa)", size=18)
    idx = np.random.default_rng(2).choice(len(R), 520, replace=False)
    p.dots(age[idx] + np.random.default_rng(4).uniform(-3, 3, len(idx)), fc[idx], BLUE, r=5, opacity=0.45)
    bins = [(1, 3), (7, 7), (14, 14), (28, 28), (56, 56), (90, 100), (120, 180), (270, 365)]
    med = [(float(np.median(age[(age >= a) & (age <= b)])), float(np.median(fc[(age >= a) & (age <= b)]))) for a, b in bins]
    p.path(med, GREEN, width=5)
    p.dots([a for a, _ in med], [m for _, m in med], GREEN, r=7, opacity=1)
    p.text(p.X(370), p.Y(14), f"r = {STATS['corr']['age']:+.2f}", size=28, fill=INK, weight=800, anchor="end")
    p.text(p.X(370), p.Y(14) + 28, "yet strength clearly depends on age", size=19, fill=INK2, weight=600, anchor="end")
    p.text(p.X(120), p.Y(66), "median strength: rises fast, then levels off", size=19, fill="#0B7A55", weight=700)
    return p.svg("Strength against age: a strong but nonlinear relationship with a modest linear correlation")


# ------------------------------------------------------------------ class balance (steel plates)
SP_NICE = {"Other_Faults": "Other faults", "Bumps": "Bumps", "K_Scatch": "K-scratch", "Z_Scratch": "Z-scratch",
           "Pastry": "Pastry", "Stains": "Stains", "Dirtiness": "Dirtiness"}


def chart_classes():
    items = sorted(SP_CLASSES.items(), key=lambda kv: -kv[1])
    W, H, L, Rm = 1000, 560, 190, 210
    rh = (H - 20) / len(items)
    mx = items[0][1]
    o = []
    for k, (c, n) in enumerate(items):
        y = 10 + k * rh
        w = n / mx * (W - L - Rm)
        rare = n / STATS["sp_n"] < 0.05
        o.append(f'<text x="{L - 16}" y="{y + rh / 2 + 8:.1f}" font-family="{FONT}" font-size="23" font-weight="700" fill="{INK}" text-anchor="end">{SP_NICE[c]}</text>')
        o.append(f'<rect x="{L}" y="{y + 9:.1f}" width="{w:.1f}" height="{rh - 18:.1f}" rx="6" fill="{ORANGE if rare else BLUE}"/>')
        o.append(f'<text x="{L + w + 14:.1f}" y="{y + rh / 2 + 8:.1f}" font-family="JetBrains Mono, monospace" font-size="21" font-weight="700" fill="{INK}">{n}'
                 f'<tspan fill="{MUTED}" font-weight="500"> · {100 * n / STATS["sp_n"]:.1f}%</tspan></text>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Number of steel plates in each of seven fault classes" '
            f'xmlns="http://www.w3.org/2000/svg">' + "".join(o) + "</svg>")


# ------------------------------------------------------------------ random_state: which rows land in the test set
def chart_seeds(seed, n=40, test=8):
    rng = np.random.default_rng(seed)
    pick = set(rng.choice(n, test, replace=False).tolist())
    W, cell, g = 1040, 22, 4
    o = []
    for i in range(n):
        x = i * (cell + g)
        col = ORANGE if i in pick else GREEN
        o.append(f'<rect x="{x}" y="0" width="{cell}" height="44" rx="5" fill="{col}" fill-opacity="{1 if i in pick else .55}"/>')
    return f'<svg viewBox="0 0 {n * (cell + g) - g} 44" role="img" aria-label="Rows assigned to the test set" xmlns="http://www.w3.org/2000/svg">{"".join(o)}</svg>'


# ------------------------------------------------------------------ scaling: very different numerical ranges
def chart_ranges():
    cols = [(0, "Cement"), (6, "Fine aggregate"), (5, "Coarse aggregate"), (3, "Water"), (1, "Slag"), (2, "Fly ash"),
            (7, "Age"), (4, "Superplasticizer")]
    p = Plot(1100, 540, (0, 1200), (0, len(cols)), pad=(230, 10, 190, 60))
    for t in (0, 200, 400, 600, 800, 1000, 1200):
        p.line(p.X(t), p.t, p.X(t), p.h - p.b, GRID)
        p.text(p.X(t), p.h - p.b + 30, str(t), size=18, anchor="middle")
    for k, (col, label) in enumerate(cols):
        v = R[:, col]
        y = p.Y(len(cols) - k - 0.5)
        lo, hi = v.min(), v.max()
        p.text(p.l - 16, y + 7, label, size=21, fill=INK, anchor="end", weight=700)
        p.rect(p.X(lo), y - 13, max(p.X(hi) - p.X(lo), 4), 26, BLUE if hi > 100 else ORANGE, 'rx="13" fill-opacity=".85"')
        unit = "days" if label == "Age" else "kg/m³"
        p.text(p.X(hi) + 12, y + 7, f"{lo:.0f}–{hi:.0f} {unit}", size=17, fill=INK2, weight=600)
    p.line(p.l, p.h - p.b, p.w - p.r, p.h - p.b, AXIS, 2)
    return p.svg("Ranges of the eight concrete inputs on one axis: hundreds of kg/m³ against tens")


# ------------------------------------------------------------------ mozzarella: schematic only
def chart_mozz():
    """Schematic: two upward series moving together. Deliberately unlabelled values (not the published data)."""
    p = Plot(760, 420, (0, 9), (0, 10), pad=(30, 30, 30, 50))
    a = [2.0, 2.6, 2.7, 2.8, 3.4, 4.6, 5.4, 6.6, 7.2, 7.4]
    b = [1.6, 2.4, 3.3, 3.7, 3.6, 5.2, 6.0, 7.1, 7.5, 7.3]
    for t in (2, 4, 6, 8):
        p.line(p.l, p.Y(t), p.w - p.r, p.Y(t), GRID)
    p.line(p.l, p.h - p.b, p.w - p.r, p.h - p.b, AXIS, 2)
    p.path(list(enumerate(a)), ORANGE, width=6)
    p.path(list(enumerate(b)), BLUE, width=6, dash="2 12")
    p.dots(range(10), a, ORANGE, r=7, opacity=1)
    p.text(p.X(0), p.h - 14, "year 1", size=18)
    p.text(p.X(9), p.h - 14, "year 10", size=18, anchor="end")
    p.text(p.X(0), p.Y(8.6), "Mozzarella eaten per person", size=21, fill="#B9471B", weight=800)
    p.text(p.X(9), p.Y(2.0), "Civil-engineering Ph.D.s awarded", size=21, fill="#1F5FAF", weight=800, anchor="end")
    return p.svg("Schematic of two unrelated series rising together over ten years")


def build():
    return {
        "hcement": chart_hist(cem, 100, 550, 25, [100, 200, 300, 400, 500], "Cement (kg/m³)"),
        "hwater": chart_hist(wat, 120, 250, 6.5, [120, 150, 180, 210, 240], "Water (kg/m³)", (191.5, 198, "192 kg/m³: 118 mixes", "end")),
        "hage": chart_hist(age, 0, 375, 15, [0, 90, 180, 270, 365], "Age (days)", (15, 30, "28-day tests", "start")),
        "hstrength": chart_hist(fc, 0, 85, 5, [0, 20, 40, 60, 80], "Strength (MPa)"),
        "missmap": chart_missmap(),
        "boxes": chart_boxes(),
        "corr": chart_corr(),
        "agesc": chart_age_scatter(),
        "classes": chart_classes(),
        "seedA": chart_seeds(7),
        "seedB": chart_seeds(19),
        "seed42": chart_seeds(42),
        "ranges": chart_ranges(),
        "mozz": chart_mozz(),
    }


if __name__ == "__main__":
    charts = build()
    for k, v in STATS.items():
        print(k, v)
    html = "".join(f'<div style="display:inline-block;margin:10px;background:#fff;width:700px">{s}</div>' for s in charts.values())
    (HERE / "charts-preview.html").write_text(
        '<html><head><link rel="stylesheet" href="../poster/assets/fonts.css"></head><body style="background:#ddd">' + html + "</body></html>")
