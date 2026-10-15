"""SVG charts for the Session 01 deck, drawn from the UCI concrete dataset.

Data: Concrete Compressive Strength, UCI Machine Learning Repository (Yeh, 1998), 1,030 mixes.
Colour roles (validated all-pairs with the dataviz validator, light surface):
  blue   #2a78d6  observations / inputs X
  orange #eb6834  target y, highlighted subset
  green  #1baf7a  model output: fitted curve, decision boundary, clusters
"""
import csv
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, AXIS = "#0E1A2B", "#334155", "#64748B", "#E6EBF1", "#94A3B8"
FONT = "Archivo, sans-serif"

rows = list(csv.reader(open(HERE / "data/concrete.csv")))[1:]
R = np.array([[float(x) for x in r] for r in rows])
cem, slag, ash, wat, sp, cagg, fagg, age, fc = R.T
wc = wat / cem
binder = cem + slag + ash
m28 = age == 28

# Abrams-type fit on 28-day mixes: fc = A / B**(w/c)
_b, _a = np.polyfit(wc[m28], np.log(fc[m28]), 1)
ABR_A, ABR_B = math.exp(_a), math.exp(-_b)
_pred = ABR_A / ABR_B ** wc[m28]
ABR_R2 = 1 - ((fc[m28] - _pred) ** 2).sum() / ((fc[m28] - fc[m28].mean()) ** 2).sum()

BAND = (0.49, 0.54)
band_sel = m28 & (wc > BAND[0]) & (wc < BAND[1])

STATS = {
    "n": len(R), "n28": int(m28.sum()),
    "abr_a": ABR_A, "abr_b": ABR_B, "abr_r2": ABR_R2,
    "band_n": int(band_sel.sum()), "band_min": float(fc[band_sel].min()), "band_max": float(fc[band_sel].max()),
}


class Plot:
    """Tiny SVG plotting helper: linear or log x, linear y, recessive grid, text-token labels."""

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

    def text(self, x, y, s, size=20, fill=MUTED, anchor="start", weight=500, extra="", halo=True):
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                        f'fill="{fill}" text-anchor="{anchor}" paint-order="stroke" stroke="#fff" stroke-width="{6 if halo else 0}" stroke-linejoin="round" {extra}>{s}</text>')

    def axes(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str):
        x0, x1 = self.l, self.w - self.r
        y0, y1 = self.h - self.b, self.t
        for v in yticks:
            y = self.Y(v)
            self.out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1.5"/>')
            self.text(x0 - 14, y + 7, yfmt(v), size=19, anchor="end")
        for v in xticks:
            x = self.X(v)
            self.out.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + 8}" stroke="{AXIS}" stroke-width="1.5"/>')
            self.text(x, y0 + 32, xfmt(v), size=19, anchor="middle")
        self.out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{AXIS}" stroke-width="2"/>')
        self.text((x0 + x1) / 2, self.h - 10, xlabel, size=20, fill=INK2, anchor="middle", weight=600)
        self.text(24, (y0 + y1) / 2, ylabel, size=20, fill=INK2, anchor="middle", weight=600,
                  extra=f'transform="rotate(-90 24 {(y0 + y1) / 2:.1f})"')

    def dots(self, xs, ys, color, r=6, opacity=0.78, shape="circle"):
        for x, y in zip(xs, ys):
            cx, cy = self.X(x), self.Y(y)
            if shape == "circle":
                self.out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}" fill-opacity="{opacity}" stroke="#fff" stroke-width="1.2"/>')
            else:  # triangle: secondary encoding for the second class
                s = r * 1.25
                self.out.append(f'<path d="M{cx:.1f} {cy - s:.1f} L{cx + s:.1f} {cy + s * .8:.1f} L{cx - s:.1f} {cy + s * .8:.1f}Z" '
                                f'fill="{color}" fill-opacity="{opacity}" stroke="#fff" stroke-width="1.2"/>')

    def path(self, pts, color, width=4, dash=""):
        d = "M" + " L".join(f"{self.X(x):.1f} {self.Y(y):.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{da}/>')

    def svg(self, label):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}" '
                f'xmlns="http://www.w3.org/2000/svg">' + "".join(self.out) + "</svg>")


def subsample(mask, k, seed=1):
    idx = np.flatnonzero(mask)
    if len(idx) <= k:
        return idx
    return np.random.default_rng(seed).choice(idx, k, replace=False)


def chart_age():
    from collections import defaultdict
    groups = defaultdict(dict)
    for row in R:
        groups[tuple(row[:7])][int(row[7])] = row[8]
    curves = [[(d, v) for d, v in sorted(g.items()) if d >= 3] for g in groups.values() if len(g) >= 4]
    curves = [c for c in curves if len(c) >= 3]
    STATS["age_curves"] = len(curves)
    p = Plot(820, 520, (2.4, 420), (0, 85), xlog=True)
    p.axes([3, 7, 28, 90, 365], [0, 20, 40, 60, 80], "Age at testing (days, log scale)", "Strength (MPa)")
    hero = max(curves, key=lambda c: c[-1][1] - c[0][1] if c[0][0] <= 3 and c[-1][0] >= 360 else -1)
    for c in curves:
        if c is hero:
            continue
        p.path(c, BLUE, width=2)
        p.out[-1] = p.out[-1].replace('stroke-width="2"', 'stroke-width="2" stroke-opacity=".32"')
    p.path(hero, ORANGE, width=5)
    p.dots([a for a, _ in hero], [v for _, v in hero], ORANGE, r=7, opacity=1)
    (a_s, v_s), (a_e, v_e) = hero[0], hero[-1]
    STATS["age_hero"] = (a_s, v_s, a_e, v_e)
    p.text(p.X(a_e) - 10, p.Y(v_e) - 50, f"One mix: {v_s:.0f} MPa at {a_s} days", size=19, fill=INK, anchor="end", weight=700)
    p.text(p.X(a_e) - 10, p.Y(v_e) - 26, f"→ {v_e:.0f} MPa at {a_e} days", size=19, fill=INK, anchor="end", weight=700)
    p.out.append(f'<line x1="{p.X(28):.1f}" y1="{p.t}" x2="{p.X(28):.1f}" y2="{p.h - p.b}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 6"/>')
    p.text(p.X(28) + 10, p.t + 18, "28-day test", size=18, fill=INK2, weight=600)
    return p.svg(f"Strength-gain curves for {len(curves)} concrete mixes each tested at four or more ages")


def chart_abrams(highlight=False, w=820, h=520):
    p = Plot(w, h, (0.25, 1.25), (0, 85))
    p.axes([0.3, 0.5, 0.7, 0.9, 1.1], [0, 20, 40, 60, 80], "Water–cement ratio, w/c", "28-day strength (MPa)",
           xfmt=lambda v: f"{v:.1f}")
    keep = m28 & (wc <= 1.25)
    if highlight:
        lo, hi = BAND
        p.out.append(f'<rect x="{p.X(lo):.1f}" y="{p.t}" width="{p.X(hi) - p.X(lo):.1f}" height="{p.h - p.b - p.t}" fill="{ORANGE}" fill-opacity=".10"/>')
        p.dots(wc[keep & ~band_sel], fc[keep & ~band_sel], BLUE, r=5, opacity=0.28)
    else:
        p.dots(wc[keep], fc[keep], BLUE, r=5, opacity=0.6)
    xs = np.linspace(0.27, 1.22, 60)
    p.path([(x, ABR_A / ABR_B ** x) for x in xs], GREEN, width=5)
    if highlight:
        p.dots(wc[band_sel], fc[band_sel], ORANGE, r=8, opacity=0.95)
        xm = sum(BAND) / 2
        p.text(p.X(xm) + 30, p.Y(80), f"{STATS['band_n']} mixes at w/c ≈ 0.51", size=20, fill=INK, weight=700)
        p.text(p.X(xm) + 30, p.Y(80) + 26, f"{STATS['band_min']:.0f} to {STATS['band_max']:.0f} MPa", size=20, fill=INK2, weight=500)
    else:
        p.text(p.X(0.82), p.Y(ABR_A / ABR_B ** 0.82) - 30, "Abrams-type fit", size=20, fill=INK, weight=700)
        p.text(p.X(0.82), p.Y(ABR_A / ABR_B ** 0.82) - 6, f"R² = {ABR_R2:.2f}", size=19, fill=INK2)
    return p.svg("28-day compressive strength against water-cement ratio with an Abrams-type curve")


def _logit(X, y, it=20000, lr=0.1):
    mu, sd = X.mean(0), X.std(0)
    Z = np.c_[np.ones(len(X)), (X - mu) / sd]
    w = np.zeros(Z.shape[1])
    for _ in range(it):
        pr = 1 / (1 + np.exp(-Z @ w))
        w -= lr * Z.T @ (pr - y) / len(y)
    return w, mu, sd, float(((Z @ w > 0) == y).mean())


def chart_classify():
    X = np.c_[binder[m28], wat[m28]]
    y = (fc[m28] >= 40).astype(float)
    w, mu, sd, acc = _logit(X, y)
    STATS["cls_acc"], STATS["cls_base"] = acc, float(1 - y.mean())
    p = Plot(820, 520, (180, 660), (115, 255), pad=(80, 64, 30, 76))
    p.axes([200, 300, 400, 500, 600], [120, 150, 180, 210, 240], "x₁  ·  feature 1: binder content (kg/m³)", "x₂  ·  feature 2: water (kg/m³)")
    lo = y == 0
    p.dots(X[lo, 0], X[lo, 1], BLUE, r=6, opacity=0.6)
    p.dots(X[~lo, 0], X[~lo, 1], ORANGE, r=6, opacity=0.8, shape="tri")
    # boundary: w0 + w1*(x-mu0)/sd0 + w2*(v-mu1)/sd1 = 0
    xs = np.linspace(190, 610, 20)
    vs = mu[1] - sd[1] * (w[0] + w[1] * (xs - mu[0]) / sd[0]) / w[2]
    pts = [(a, b) for a, b in zip(xs, vs) if 115 <= b <= 255]
    p.path(pts, GREEN, width=5, dash="16 10")
    # legend: identity is never colour alone
    lx, ly = p.l, 26
    p.out.append(f'<path d="M{lx + 9} {ly - 9} L{lx + 18} {ly + 6} L{lx} {ly + 6}Z" fill="{ORANGE}"/>')
    p.text(lx + 28, ly + 6, "≥ 40 MPa", size=19, fill=INK2, weight=600, halo=False)
    p.out.append(f'<circle cx="{lx + 160}" cy="{ly}" r="8" fill="{BLUE}"/>')
    p.text(lx + 176, ly + 6, "< 40 MPa", size=19, fill=INK2, weight=600, halo=False)
    p.out.append(f'<line x1="{lx + 300}" y1="{ly}" x2="{lx + 342}" y2="{ly}" stroke="{GREEN}" stroke-width="5" stroke-dasharray="12 8"/>')
    p.text(lx + 352, ly + 6, "decision boundary", size=19, fill=INK2, weight=600, halo=False)
    return p.svg("28-day mixes classified as at least 40 MPa or below, by binder and water content, with a decision boundary")


def chart_regress():
    p = Plot(820, 520, (0.25, 1.25), (0, 85))
    p.axes([0.3, 0.5, 0.7, 0.9, 1.1], [0, 20, 40, 60, 80], "x  ·  feature: water–cement ratio", "y  ·  response: 28-day strength (MPa)",
           xfmt=lambda v: f"{v:.1f}")
    keep = m28 & (wc <= 1.25)
    p.dots(wc[keep], fc[keep], BLUE, r=6, opacity=0.6)
    xs = np.linspace(0.27, 1.22, 60)
    p.path([(x, ABR_A / ABR_B ** x) for x in xs], GREEN, width=5)
    p.text(p.X(0.78), p.Y(ABR_A / ABR_B ** 0.78) - 22, "ŷ = f(x)", size=22, fill=INK, weight=700)
    return p.svg("Regression: 28-day strength against water-cement ratio with a fitted curve")


def chart_kmeans():
    F = np.c_[slag / binder, ash / binder]
    rng = np.random.default_rng(0)
    best = None
    for _ in range(12):
        C = F[rng.choice(len(F), 3, replace=False)]
        for _ in range(100):
            L = ((F[:, None] - C[None]) ** 2).sum(2).argmin(1)
            C = np.array([F[L == k].mean(0) if (L == k).any() else C[k] for k in range(3)])
        inertia = ((F - C[L]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, C.copy(), L.copy())
    _, C, L = best
    # name clusters by their centroid
    names = {}
    for k, (s, a) in enumerate(C):
        names[k] = "Slag blends" if s > 0.2 else ("Fly-ash blends" if a > 0.2 else "Mostly cement")
    order = sorted(range(3), key=lambda k: ["Mostly cement", "Slag blends", "Fly-ash blends"].index(names[k]))
    colors = {order[0]: BLUE, order[1]: ORANGE, order[2]: GREEN}
    p = Plot(860, 560, (-0.03, 0.82), (-0.03, 0.6), pad=(100, 30, 30, 76))
    p.axes([0, 0.2, 0.4, 0.6, 0.8], [0, 0.2, 0.4, 0.6], "Slag share of binder", "Fly-ash share of binder",
           xfmt=lambda v: f"{v * 100:.0f}%", yfmt=lambda v: f"{v * 100:.0f}%")
    jit = np.random.default_rng(5).normal(0, 0.006, F.shape)
    for k in order:
        sel = L == k
        p.dots(F[sel, 0] + jit[sel, 0], F[sel, 1] + jit[sel, 1], colors[k], r=6, opacity=0.6)
    STATS["clusters"] = {names[k]: int((L == k).sum()) for k in order}
    for k in order:
        cx, cy = p.X(C[k, 0]), p.Y(C[k, 1])
        p.out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="15" fill="#fff" stroke="{INK}" stroke-width="3"/>'
                     f'<path d="M{cx - 6:.1f} {cy - 6:.1f} l12 12 m0 -12 l-12 12" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        dx, anchor = (24, "start") if C[k, 0] < 0.5 else (-24, "end")
        dy = -22 if names[k] != "Mostly cement" else -26
        p.text(cx + dx, cy + dy, names[k], size=21, fill=INK, anchor=anchor, weight=700)
        p.text(cx + dx, cy + dy + 24, f"{int((L == k).sum())} mixes", size=18, fill=INK2, anchor=anchor)
    return p.svg("k-means groups 1,030 concrete mixes into three binder families without using strength labels")


def build():
    return {
        "age": chart_age(),
        "abrams": chart_abrams(),
        "band": chart_abrams(highlight=True, w=980, h=560),
        "classify": chart_classify(),
        "regress": chart_regress(),
        "kmeans": chart_kmeans(),
    }


if __name__ == "__main__":
    charts = build()
    for k, v in STATS.items():
        print(k, v)
    html = "".join(f'<div style="display:inline-block;margin:10px;background:#fff">{s}</div>' for s in charts.values())
    (HERE / "charts-preview.html").write_text(
        '<html><head><link rel="stylesheet" href="../poster/assets/fonts.css"></head><body style="background:#ddd">' + html + "</body></html>")
