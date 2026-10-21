"""Model results and SVG charts for the Session 03 deck.

Data: UCI Concrete Compressive Strength (Yeh, 1998), 1,030 mixes; the 25 duplicate rows found in Session 02 are dropped,
leaving 1,005. Split and models follow the workshop notebook exactly (scikit-learn, test_size=0.2, random_state=42).

Charts that build click by click are returned as a list of layers (same viewBox); build.py stacks them so every layer
is its own object in PowerPoint and can be revealed on its own click.

Colour roles as in Sessions 01-02:
  blue   #2a78d6  observations / inputs X
  orange #eb6834  target y, errors, the test set, the gradient-descent path
  green  #1baf7a  the model: fitted line, predictions, minimum
"""
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, train_test_split

HERE = Path(__file__).parent
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_T, ORANGE_T, GREEN_T = "#CFE0F5", "#F7D3C3", "#C3EAD9"
INK, INK2, MUTED, GRID, AXIS = "#0E1A2B", "#334155", "#64748B", "#E6EBF1", "#94A3B8"
FONT = "Archivo, sans-serif"
MONO = "JetBrains Mono, monospace"

# ------------------------------------------------------------------ data and the notebook's models
RAW = pd.read_csv(HERE / "data/concrete.csv")
DF = RAW.drop_duplicates().reset_index(drop=True)
X, y = DF.drop(columns="strength"), DF["strength"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
LR = LinearRegression().fit(X_train, y_train)
P_TEST, P_TRAIN = LR.predict(X_test), LR.predict(X_train)
BASE = float(y_train.mean())


def scores(t, p):
    return {"mae": mean_absolute_error(t, p), "rmse": mean_squared_error(t, p) ** 0.5, "r2": r2_score(t, p)}


SEEDS = list(range(50))
SEED_R2 = {s: r2_score(e, LinearRegression().fit(a, c).predict(b))
           for s in SEEDS for a, b, c, e in [train_test_split(X, y, test_size=0.2, random_state=s)]}
CV = []
for tr, va in KFold(5, shuffle=True, random_state=42).split(X_train):
    m = LinearRegression().fit(X_train.iloc[tr], y_train.iloc[tr])
    CV.append(r2_score(y_train.iloc[va], m.predict(X_train.iloc[va])))
_mu, _sd = X_train.mean(), X_train.std(ddof=0)
STD_COEF = dict(zip(X.columns, LinearRegression().fit((X_train - _mu) / _sd, y_train).coef_))

# a real test mix for the "regression in one picture" slide: 28 days, modest error
_cand = [(abs(abs(P_TEST[i] - y_test.iloc[i]) - 2.4), i) for i in range(len(y_test)) if X_test.iloc[i]["age"] == 28]
_ex = min(_cand)[1]
EXAMPLE = {"row": X_test.iloc[_ex].to_dict(), "actual": float(y_test.iloc[_ex]), "pred": float(P_TEST[_ex])}

STATS = {
    "n_raw": len(RAW), "n": len(DF), "dups": len(RAW) - len(DF),
    "n_train": len(X_train), "n_test": len(X_test), "base": BASE,
    "base_test": scores(y_test, np.full(len(y_test), BASE)),
    "lr_test": scores(y_test, P_TEST), "lr_train": scores(y_train, P_TRAIN),
    "coef": dict(zip(X.columns, LR.coef_)), "b0": float(LR.intercept_), "std_coef": STD_COEF,
    "seed_min": min(SEED_R2.values()), "seed_max": max(SEED_R2.values()),
    "seed": {s: SEED_R2[s] for s in (42, 7, 21)},
    "cv": CV, "cv_mean": float(np.mean(CV)), "cv_sd": float(np.std(CV)),
    "example": EXAMPLE,
}


class Plot:
    """Tiny SVG plotting helper (Sessions 01-02) with layers: call layer() to start the next click's layer."""

    def __init__(self, w, h, xd, yd, pad=(70, 30, 30, 76)):
        self.w, self.h, self.xd, self.yd = w, h, xd, yd
        self.l, self.t, self.r, self.b = pad
        self.out, self.layers = [], []

    def X(self, v):
        lo, hi = self.xd
        return self.l + (v - lo) / (hi - lo) * (self.w - self.l - self.r)

    def Y(self, v):
        lo, hi = self.yd
        return self.h - self.b - (v - lo) / (hi - lo) * (self.h - self.t - self.b)

    def text(self, x, y, s, size=20, fill=MUTED, anchor="start", weight=500, extra="", halo=True, family=FONT):
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
                        f'fill="{fill}" text-anchor="{anchor}" paint-order="stroke" stroke="#fff" stroke-width="{6 if halo else 0}" stroke-linejoin="round" {extra}>{s}</text>')

    def line(self, x1, y1, x2, y2, color, width=1.5, extra=""):
        self.out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" {extra}/>')

    def axes(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str, size=19):
        x0, x1 = self.l, self.w - self.r
        y0, y1 = self.h - self.b, self.t
        for v in yticks:
            yy = self.Y(v)
            self.line(x0, yy, x1, yy, GRID)
            self.text(x0 - 12, yy + 7, yfmt(v), size=size, anchor="end")
        for v in xticks:
            xx = self.X(v)
            self.line(xx, y0, xx, y0 + 8, AXIS)
            self.text(xx, y0 + 30, xfmt(v), size=size, anchor="middle")
        self.line(x0, y0, x1, y0, AXIS, 2)
        if xlabel:
            self.text((x0 + x1) / 2, self.h - 8, xlabel, size=size + 1, fill=INK2, anchor="middle", weight=600)
        if ylabel:
            self.text(22, (y0 + y1) / 2, ylabel, size=size + 1, fill=INK2, anchor="middle", weight=600,
                      extra=f'transform="rotate(-90 22 {(y0 + y1) / 2:.1f})"')

    def dots(self, xs, ys, color, r=6, opacity=0.78):
        for a, b in zip(xs, ys):
            self.out.append(f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{color}" fill-opacity="{opacity}" stroke="#fff" stroke-width="1.2"/>')

    def path(self, pts, color, width=4, dash="", raw=False):
        f = (lambda a, b: (a, b)) if raw else (lambda a, b: (self.X(a), self.Y(b)))
        d = "M" + " L".join("{:.1f} {:.1f}".format(*f(a, b)) for a, b in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{da}/>')

    def layer(self):
        self.layers.append(self.out)
        self.out = []

    def _wrap(self, body, label):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}" '
                f'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>")

    def svg(self, label):
        return self._wrap(self.out, label)

    def stack(self, label):
        self.layer()
        return [self._wrap(body, f"{label} (part {k + 1})") for k, body in enumerate(self.layers)]


def ball(p, x, y, r=13, color=ORANGE):
    p.out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="#fff" stroke-width="3"/>')


def arrowhead(p, x, y, ang, color, s=13):
    a, d = math.radians(ang), math.radians(28)
    pts = [(x, y), (x - s * math.cos(a - d), y - s * math.sin(a - d)), (x - s * math.cos(a + d), y - s * math.sin(a + d))]
    p.out.append('<path d="M{:.1f} {:.1f} L{:.1f} {:.1f} L{:.1f} {:.1f}Z" fill="{}"/>'.format(*[c for pt in pts for c in pt], color))


# ------------------------------------------------------------------ Part 01: baseline
def chart_baseline():
    p = Plot(900, 520, (0.8, 420), (0, 88), pad=(70, 24, 24, 70))
    lx = lambda a: math.log10(a)  # noqa: E731
    p.xd = (lx(0.8), lx(420))
    p.axes([lx(v) for v in (1, 3, 7, 28, 90, 365)], [0, 20, 40, 60, 80], "Age at testing (days, log scale)", "Strength (MPa)",
           xfmt=lambda v: f"{10 ** v:.0f}", size=18)
    jit = np.random.default_rng(3).uniform(-0.03, 0.03, len(y_test))
    p.dots([lx(a) + j for a, j in zip(X_test["age"], jit)], y_test, BLUE, r=6, opacity=0.6)
    p.path([(lx(0.9), BASE), (lx(400), BASE)], ORANGE, width=5)
    p.text(p.X(lx(1.0)), p.Y(BASE) - 14, f"baseline {BASE:.1f} MPa", size=21, fill="#B9471B", weight=800)
    return p.svg("Measured strength of the test mixes against age, with the flat mean baseline")


# ------------------------------------------------------------------ Part 01: coefficients
NICE = {"cement": "Cement", "slag": "Slag", "ash": "Fly ash", "water": "Water", "superplastic": "Superplasticizer",
        "coarseagg": "Coarse aggregate", "fineagg": "Fine aggregate", "age": "Age"}


def chart_coefs(which):
    vals = STATS["coef"] if which == "raw" else STATS["std_coef"]
    order = list(NICE)
    lim = max(abs(v) for v in vals.values()) * 1.25
    W, H, L, Rm = 660, 470, 200, 30
    rh = (H - 50) / len(order)
    X0 = lambda v: L + (v + lim) / (2 * lim) * (W - L - Rm)  # noqa: E731
    o = [f'<line x1="{X0(0):.1f}" y1="6" x2="{X0(0):.1f}" y2="{H - 40}" stroke="{AXIS}" stroke-width="2"/>']
    for k, c in enumerate(order):
        v = vals[c]
        yy = 8 + k * rh
        a, b = sorted((X0(0), X0(v)))
        col = BLUE if v > 0 else ORANGE
        hot = c in ("superplastic", "age")
        o.append(f'<text x="{L - 14}" y="{yy + rh / 2 + 7:.1f}" font-family="{FONT}" font-size="20" font-weight="{800 if hot else 600}" fill="{INK}" text-anchor="end">{NICE[c]}</text>')
        o.append(f'<rect x="{a:.1f}" y="{yy + 7:.1f}" width="{max(b - a, 2):.1f}" height="{rh - 14:.1f}" rx="4" fill="{col}"/>')
        tx, an = (X0(v) + 8, "start") if v > 0 else (X0(v) - 8, "end")
        fmt = f"{v:+.3f}" if which == "raw" else f"{v:+.1f}"
        o.append(f'<text x="{tx:.1f}" y="{yy + rh / 2 + 7:.1f}" font-family="{MONO}" font-size="17" font-weight="700" fill="{INK2}" text-anchor="{an}">{fmt}</text>')
    unit = "MPa per kg/m³ (age: MPa per day)" if which == "raw" else "MPa per standard deviation of the input"
    o.append(f'<text x="{(L + W - Rm) / 2:.1f}" y="{H - 8}" font-family="{FONT}" font-size="17" font-weight="600" fill="{INK2}" text-anchor="middle">{unit}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Linear-regression coefficients ({which})" xmlns="http://www.w3.org/2000/svg">'
            + "".join(o) + "</svg>")


# ------------------------------------------------------------------ the maths: one feature, real 28-day mixes
_m28 = DF[DF.age == 28]
_S = _m28.sample(26, random_state=11)
XC, YC = _S["cement"].to_numpy(), _S["strength"].to_numpy()
_w1, _b1 = np.polyfit(XC, YC, 1)
# standardised cement for the cost surface and gradient descent (keeps the bowl round enough to see)
_mx, _sx = XC.mean(), XC.std()
ZC = (XC - _mx) / _sx


def J(w, b):
    return float(((w * ZC + b - YC) ** 2).mean() / 2)


W_OPT, B_OPT = float(((ZC - ZC.mean()) * YC).mean() / (ZC ** 2).mean()), float(YC.mean())
J_MIN = J(W_OPT, B_OPT)


def gd(w, b, alpha, n):
    path = [(w, b)]
    for _ in range(n):
        r = w * ZC + b - YC
        w, b = w - alpha * (r * ZC).mean(), b - alpha * r.mean()
        path.append((w, b))
    return path


def chart_linefit():
    p = Plot(900, 600, (90, 560), (0, 90), pad=(80, 30, 40, 76))
    p.axes([100, 200, 300, 400, 500], [0, 20, 40, 60, 80], "x · feature: cement (kg/m³)", "y · response: 28-day strength (MPa)", size=18)
    p.dots(XC, YC, BLUE, r=8, opacity=0.85)
    p.layer()                                                        # click 1: the fitted line f(x) = wx + b
    p.path([(95, _w1 * 95 + _b1), (555, _w1 * 555 + _b1)], GREEN, width=5)
    p.text(p.X(470), p.Y(_w1 * 470 + _b1) - 20, "f(x) = wx + b", size=24, fill="#0B7A55", weight=800, anchor="end")
    p.layer()                                                        # click 2: errors (vertical offsets)
    for a, b in zip(XC, YC):
        p.line(p.X(a), p.Y(b), p.X(a), p.Y(_w1 * a + _b1), ORANGE, 3)
    p.line(p.l + 14, p.Y(77), p.l + 14, p.Y(71), ORANGE, 4)
    p.text(p.l + 28, p.Y(74) + 7, "error of each mix: ŷ − y (prediction minus measurement)", size=20, fill="#B9471B", weight=800)
    p.layer()                                                        # click 3: slope and intercept
    x1, x2 = 180, 300
    p.path([(x1, _w1 * x1 + _b1), (x2, _w1 * x1 + _b1), (x2, _w1 * x2 + _b1)], INK, width=2.5, dash="6 6")
    p.text(p.X((x1 + x2) / 2), p.Y(_w1 * x1 + _b1) + 26, "Δx", size=20, fill=INK, weight=700, anchor="middle")
    p.text(p.X(x2) + 10, p.Y(_w1 * (x1 + x2) / 2 + _b1) + 6, "Δy", size=20, fill=INK, weight=700)
    p.text(p.X(x1), p.Y(_w1 * x1 + _b1) + 58, f"slope w = Δy/Δx ≈ {_w1:.2f} MPa per kg/m³", size=20, fill=INK, weight=800)
    p.text(p.X(x1), p.Y(_w1 * x1 + _b1) + 84, f"intercept b ≈ {_b1:.1f} MPa (where the line meets x = 0)", size=19, fill=INK2, weight=600)
    return p.stack("Fitting a line to 26 real 28-day mixes: errors, slope and intercept")


def chart_bowl():
    """J(w, b) over a grid, drawn as an isometric wireframe, with the real gradient-descent path."""
    W, H = 900, 640
    ws = np.linspace(W_OPT - 30, W_OPT + 30, 25)
    bs = np.linspace(B_OPT - 40, B_OPT + 40, 25)
    Jg = np.array([[J(w, b) for w in ws] for b in bs])
    zmax = Jg.max()

    def raw(w, b, z):
        u = (w - ws[0]) / (ws[-1] - ws[0]) - 0.5
        v = (b - bs[0]) / (bs[-1] - bs[0]) - 0.5
        return (u - v) * 1.0, (u + v) * 0.38 - z / zmax * 0.95

    corners = [raw(w, b, z) for w in (ws[0], ws[-1]) for b in (bs[0], bs[-1]) for z in (0, zmax)]
    x0, x1 = min(c[0] for c in corners), max(c[0] for c in corners)
    y0, y1 = min(c[1] for c in corners), max(c[1] for c in corners)
    k_ = min((W - 120) / (x1 - x0), (H - 90) / (y1 - y0))

    def proj(w, b, z):
        a_, c_ = raw(w, b, z)
        return 60 + (a_ - x0) * k_, 50 + (c_ - y0) * k_

    o = []
    back = proj(ws[0], bs[0], 0)
    for (wa, ba), lab in (((ws[-1], bs[0]), "w"), ((ws[0], bs[-1]), "b")):
        e = proj(wa, ba, 0)
        o.append(f'<line x1="{back[0]:.1f}" y1="{back[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="{INK2}" stroke-width="2.5"/>')
        o.append(f'<text x="{e[0] + (22 if lab == "w" else -22):.1f}" y="{e[1] + 8:.1f}" font-family="{FONT}" font-size="28" font-style="italic" font-weight="800" fill="{INK}" text-anchor="middle">{lab}</text>')
    top = proj(ws[0], bs[0], zmax)
    o.append(f'<line x1="{back[0]:.1f}" y1="{back[1]:.1f}" x2="{top[0]:.1f}" y2="{top[1]:.1f}" stroke="{INK2}" stroke-width="2.5"/>')
    o.append(f'<text x="{top[0] + 14:.1f}" y="{top[1] + 6:.1f}" font-family="{FONT}" font-size="26" font-style="italic" font-weight="800" fill="{INK}">J(w, b)</text>')
    quads = []
    for k in range(len(bs) - 1):
        for j in range(len(ws) - 1):
            c = [(ws[j], bs[k], Jg[k, j]), (ws[j + 1], bs[k], Jg[k, j + 1]), (ws[j + 1], bs[k + 1], Jg[k + 1, j + 1]), (ws[j], bs[k + 1], Jg[k + 1, j])]
            depth = (j + k)                                            # larger u + v is nearer the viewer
            z = sum(q[2] for q in c) / 4 / zmax
            quads.append((depth, z, [proj(*q) for q in c]))
    for depth, z, pts in sorted(quads, key=lambda q: q[0]):
        t = min(1, z * 1.3)
        col = "#{:02X}{:02X}{:02X}".format(*[round(a_ + (b_ - a_) * t) for a_, b_ in zip((0xE5, 0xF6, 0xEF), (0xEA, 0xF2, 0xFC))])
        o.append('<path d="M' + " L".join(f"{a_:.1f} {c_:.1f}" for a_, c_ in pts) + f'Z" fill="{col}" fill-opacity=".92" stroke="{BLUE}" stroke-opacity=".55" stroke-width="1.2"/>')
    layers = [o]
    path = gd(W_OPT + 27, B_OPT - 37, 0.25, 40)
    STATS["gd_steps"] = len(path) - 1
    STATS["gd_start"], STATS["gd_end"] = J(*path[0]), J(*path[-1])
    for lo, hi in ((0, 3), (3, 9), (9, 40)):
        seg = path[lo:hi + 1]
        pts = [proj(w, b, J(w, b)) for w, b in seg]
        L = ['<path d="M' + " L".join(f"{a:.1f} {c:.1f}" for a, c in pts) + f'" fill="none" stroke="{ORANGE}" stroke-width="4" stroke-linecap="round"/>']
        for k, (a, c) in enumerate(pts):
            if k or lo == 0:
                L.append(f'<circle cx="{a:.1f}" cy="{c:.1f}" r="{9 if lo == 0 and k == 0 else 6}" fill="{ORANGE}" stroke="#fff" stroke-width="2"/>')
        if lo == 0:
            a, c = pts[0]
            L.append(f'<text x="{a + 18:.1f}" y="{c - 8:.1f}" font-family="{FONT}" font-size="21" font-weight="800" fill="#B9471B" paint-order="stroke" stroke="#fff" stroke-width="6">start: some w, b</text>')
        layers.append(L)
    m = proj(W_OPT, B_OPT, J_MIN)
    layers.append([f'<circle cx="{m[0]:.1f}" cy="{m[1]:.1f}" r="13" fill="{GREEN}" stroke="#fff" stroke-width="3"/>',
                   f'<text x="{m[0] + 22:.1f}" y="{m[1] + 34:.1f}" font-family="{FONT}" font-size="22" font-weight="800" fill="#0B7A55" paint-order="stroke" stroke="#fff" stroke-width="6">minimum of J</text>'])
    return [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cost surface J(w,b) with gradient descent (part {k + 1})" xmlns="http://www.w3.org/2000/svg">{"".join(L)}</svg>'
            for k, L in enumerate(layers)]


def _Jw(w):
    return J(w, B_OPT)


def chart_gd1d():
    """J(w) with b at its best value: slopes on both sides, then the descent step by step."""
    lo, hi = W_OPT - 22, W_OPT + 22
    jmax = _Jw(lo)
    p = Plot(820, 560, (lo, hi), (J_MIN - 10, jmax * 1.05), pad=(70, 26, 30, 66))
    x0, x1 = p.X(lo), p.X(hi)
    p.line(x0, p.h - p.b, x1, p.h - p.b, AXIS, 2)
    p.line(x0, p.h - p.b, x0, p.t, AXIS, 2)
    p.text(x1, p.h - p.b + 34, "w", size=26, fill=INK, weight=800, anchor="end", extra='font-style="italic"')
    p.text(x0 + 10, p.t + 18, "J(w)", size=24, fill=INK, weight=800, extra='font-style="italic"')
    p.path([(w, _Jw(w)) for w in np.linspace(lo, hi, 80)], INK, width=4)
    p.text(p.X(W_OPT), p.h - p.b + 34, "best w", size=18, fill="#0B7A55", weight=700, anchor="middle")
    p.line(p.X(W_OPT), p.h - p.b, p.X(W_OPT), p.Y(J_MIN), GREEN, 2, 'stroke-dasharray="5 6"')
    for wl, side in ((W_OPT - 14, "l"), (W_OPT + 14, "r")):
        p.layer()                                                    # clicks 1-2: tangent on each side
        s = wl - W_OPT                                               # dJ/dw at b* (unit-variance x)
        jv = _Jw(wl)
        dx = 6
        p.path([(wl - dx, jv - s * dx), (wl + dx, jv + s * dx)], ORANGE if side == "l" else BLUE, width=5)
        ball(p, p.X(wl), p.Y(jv), 10, ORANGE if side == "l" else BLUE)
        if side == "l":
            p.text(p.l + 24, p.h - p.b - 52, "slope < 0", size=20, fill="#B9471B", weight=800)
            p.text(p.l + 24, p.h - p.b - 24, "→ step right, w increases", size=20, fill="#B9471B", weight=800)
        else:
            p.text(p.X(wl) - 26, p.Y(jv) - 34, "slope > 0  →  step left, w decreases", size=20, fill="#1F5FAF", weight=800, anchor="end")
    path = [p_[0] for p_ in gd(W_OPT - 20, B_OPT, 0.25, 12)]
    for a, b in ((0, 1), (1, 3), (3, 12)):                           # clicks 3-5: the ball walks down
        p.layer()
        seg = path[a:b + 1]
        for u, v in zip(seg, seg[1:]):
            p.path([(u, _Jw(u)), (v, _Jw(v))], ORANGE, width=3, dash="3 7")
        for w in seg[1:] if a else seg:
            ball(p, p.X(w), p.Y(_Jw(w)), 9)
    return p.stack("Gradient descent on J(w): the sign of the slope decides the direction of each step")


def chart_alpha(alpha, n, label):
    lo, hi = W_OPT - 22, W_OPT + 22
    p = Plot(520, 360, (lo, hi), (J_MIN - 10, _Jw(lo) * 1.15), pad=(20, 16, 20, 20))
    p.path([(w, _Jw(w)) for w in np.linspace(lo, hi, 60)], INK, width=3)
    path = [p_[0] for p_ in gd(W_OPT - 19, B_OPT, alpha, n)]
    shown = [w for w in path if lo <= w <= hi]
    for u, v in zip(shown, shown[1:]):
        p.path([(u, _Jw(u)), (v, _Jw(v))], ORANGE, width=2.5)
    for w in shown:
        ball(p, p.X(w), p.Y(_Jw(w)), 6)
    STATS.setdefault("alpha", {})[label] = {"alpha": alpha, "n": n, "end": abs(path[-1] - W_OPT), "start": abs(path[0] - W_OPT)}
    return p.svg(f"Gradient descent with learning rate {alpha}")


def chart_scaling(scaled):
    """Contours of the cost over (w_cement, w_age) and the gradient-descent path, raw (centred) vs standardised inputs."""
    A = DF[["cement", "superplastic"]].to_numpy()
    A = A - A.mean(0)
    if scaled:
        A = A / A.std(0)
    yv = DF["strength"].to_numpy() - DF["strength"].mean()
    H = A.T @ A / len(A)                                          # cost Hessian (J = ½ mean squared error)
    w_opt = np.linalg.solve(H, A.T @ yv / len(A))
    alpha = 0.9 / np.linalg.eigvalsh(H).max()                     # the same safe setting for both cases
    w = np.zeros(2)                                               # start from zero weights
    Jf = lambda v: 0.5 * (v - w_opt) @ H @ (v - w_opt)  # noqa: E731
    j0 = Jf(w)
    path, n = [w.copy()], 0
    while Jf(w) > 1e-3 * j0 and n < 1_000_000:
        w = w - alpha * H @ (w - w_opt)
        n += 1
        if n <= 400:
            path.append(w.copy())
    STATS.setdefault("scale_iters", {})["scaled" if scaled else "raw"] = n
    span = np.abs(np.array(path) - w_opt).max(0) * 1.15
    span = np.array([span.max(), span.max()]) if scaled else span
    S = 470
    def P(v):
        return (40 + (v[0] - w_opt[0] + span[0]) / (2 * span[0]) * (S - 80), 40 + (span[1] - (v[1] - w_opt[1])) / (2 * span[1]) * (S - 80))
    o = [f'<rect x="1" y="1" width="{S - 2}" height="{S - 2}" rx="18" fill="#fff" stroke="{GRID}" stroke-width="2"/>']
    ev, V = np.linalg.eigh(H)
    for lvl in (0.02, 0.08, 0.2, 0.4, 0.7, 1.0):
        c = lvl * j0
        pts = []
        for t in np.linspace(0, 2 * math.pi, 120):
            u = np.array([math.cos(t) * math.sqrt(2 * c / ev[0]), math.sin(t) * math.sqrt(2 * c / ev[1])])
            pts.append(P(w_opt + V @ u))
        o.append('<path d="M' + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts) + f'Z" fill="none" stroke="{BLUE}" stroke-opacity=".7" stroke-width="2"/>')
    base = "".join(o)
    pts = [P(v) for v in path]
    p2 = ['<path d="M' + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts) + f'" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linejoin="round"/>',
          f'<circle cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="8" fill="{ORANGE}" stroke="#fff" stroke-width="2"/>']
    m = P(w_opt)
    p2.append(f'<circle cx="{m[0]:.1f}" cy="{m[1]:.1f}" r="9" fill="{GREEN}" stroke="#fff" stroke-width="2"/>')
    lab = ('<text x="{x}" y="{y}" font-family="{f}" font-size="22" font-style="italic" font-weight="800" fill="{c}" text-anchor="{a}">{t}</text>')
    axes = (lab.format(x=S - 20, y=S - 16, f=FONT, c=INK2, a="end", t="w<tspan font-size='15' baseline-shift='sub'>cement</tspan>")
            + lab.format(x=20, y=30, f=FONT, c=INK2, a="start", t="w<tspan font-size='15' baseline-shift='sub'>superplasticizer</tspan>"))
    svg = lambda body, k: f'<svg viewBox="0 0 {S} {S}" role="img" aria-label="Cost contours and gradient-descent path, {"standardised" if scaled else "raw"} inputs (part {k})" xmlns="http://www.w3.org/2000/svg">{body}</svg>'  # noqa: E731
    return [svg(base + axes, 1), svg("".join(p2), 2)]


# ------------------------------------------------------------------ Part 02: evaluation
def chart_parity():
    p = Plot(760, 640, (0, 90), (0, 90), pad=(80, 24, 30, 74))
    p.axes([0, 20, 40, 60, 80], [0, 20, 40, 60, 80], "Actual strength (MPa)", "Predicted strength (MPa)", size=18)
    p.path([(0, 0), (90, 90)], INK, width=2.5, dash="8 8")
    p.text(p.X(86), p.Y(86) + 26, "perfect: ŷ = y", size=19, fill=INK, weight=700, anchor="end")
    p.dots(y_test, P_TEST, GREEN, r=6.5, opacity=0.7)
    return p.svg("Parity plot: predicted against actual strength for the test mixes")


def chart_resid(kind):
    r = y_test.to_numpy() - P_TEST
    if kind == "pred":
        xs, xd, ticks, lab = P_TEST, (0, 85), [0, 20, 40, 60, 80], "Predicted strength (MPa)"
    else:
        xs, xd, ticks, lab = X_test["age"].to_numpy(), (0, 380), [0, 90, 180, 270, 365], "Age (days)"
    p = Plot(760, 470, xd, (-40, 40), pad=(80, 20, 24, 70))
    p.axes(ticks, [-30, -15, 0, 15, 30], lab, "Residual = actual − predicted (MPa)", size=18)
    p.line(p.X(xd[0]), p.Y(0), p.X(xd[1]), p.Y(0), INK, 2.5)
    p.dots(xs, r, ORANGE, r=6, opacity=0.62)
    STATS.setdefault('resid_range', {})[kind] = (float(r.min()), float(r.max()))
    if kind == "age":
        bins = [(1, 3), (7, 7), (14, 14), (28, 28), (56, 56), (90, 100), (120, 180), (270, 365)]
        med = [(float(np.median(xs[(xs >= a) & (xs <= b)])), float(np.median(r[(xs >= a) & (xs <= b)])))
               for a, b in bins if ((xs >= a) & (xs <= b)).sum() >= 3]
        p.path(med, BLUE, width=5)
        p.dots([a for a, _ in med], [b for _, b in med], BLUE, r=7, opacity=1)
        STATS["resid_age"] = med
    return p.svg(f"Residuals of the test mixes against {lab.lower()}")


def chart_seeds():
    vals = np.array([SEED_R2[s] for s in SEEDS])
    p = Plot(1500, 230, (0.45, 0.75), (0, 1), pad=(40, 20, 40, 66))
    for t in (0.5, 0.55, 0.6, 0.65, 0.7):
        p.line(p.X(t), p.t, p.X(t), p.h - p.b, GRID)
        p.text(p.X(t), p.h - p.b + 30, f"{t:.2f}", size=19, anchor="middle")
    p.line(p.l, p.h - p.b, p.w - p.r, p.h - p.b, AXIS, 2)
    p.text((p.l + p.w - p.r) / 2, p.h - 6, "Test R² of the same linear model, 50 different random splits", size=20, fill=INK2, anchor="middle", weight=600)
    order = np.argsort(vals)
    cnt = {}
    for i in order:
        v = round(vals[i] / 0.006) * 0.006
        k = cnt.get(v, 0)
        cnt[v] = k + 1
        hot = SEEDS[i] in (42, 7, 21)
        p.out.append(f'<circle cx="{p.X(v):.1f}" cy="{p.h - p.b - 14 - k * 22:.1f}" r="9" fill="{ORANGE if hot else BLUE}" fill-opacity="{1 if hot else .55}" stroke="#fff" stroke-width="1.5"/>')
    return p.svg("Distribution of test R² across 50 random splits")


def chart_cv():
    p = Plot(760, 420, (0, 6), (0.4, 0.7), pad=(80, 20, 20, 64))
    p.axes([], [0.4, 0.5, 0.6, 0.7], "", "R² on the validation fold", yfmt=lambda v: f"{v:.1f}", size=18)
    for k, v in enumerate(CV, 1):
        x = p.X(k)
        p.out.append(f'<rect x="{x - 40:.1f}" y="{p.Y(v):.1f}" width="80" height="{p.Y(0.4) - p.Y(v):.1f}" rx="6" fill="{GREEN}"/>')
        p.text(x, p.Y(v) - 12, f"{v:.2f}", size=20, fill=INK, weight=800, anchor="middle", family=MONO)
        p.text(x, p.h - p.b + 30, f"Fold {k}", size=19, anchor="middle", fill=INK2, weight=600)
    m = float(np.mean(CV))
    p.line(p.X(0.35), p.Y(m), p.X(5.65), p.Y(m), ORANGE, 3, 'stroke-dasharray="10 8"')
    p.text(p.X(0.4), p.Y(m) - 12, f"mean {m:.2f}", size=20, fill="#B9471B", weight=800)
    return p.svg("Validation R² of linear regression in each of 5 folds")


def build():
    out = {
        "baseline": chart_baseline(),
        "coefraw": chart_coefs("raw"), "coefstd": chart_coefs("std"),
        "linefit": chart_linefit(), "bowl": chart_bowl(), "gd1d": chart_gd1d(),
        "aslow": chart_alpha(0.03, 14, "small"), "agood": chart_alpha(0.3, 10, "good"), "abig": chart_alpha(2.06, 7, "large"),
        "sraw": chart_scaling(False), "sstd": chart_scaling(True),
        "parity": chart_parity(), "rpred": chart_resid("pred"), "rage": chart_resid("age"),
        "seeds": chart_seeds(), "cv": chart_cv(),
    }
    return out


if __name__ == "__main__":
    charts = build()
    for k, v in STATS.items():
        print(k, v)
    flat = [s for v in charts.values() for s in (v if isinstance(v, list) else [v])]
    html = "".join(f'<div style="display:inline-block;margin:10px;background:#fff;width:640px;vertical-align:top">{s}</div>' for s in flat)
    (HERE / "charts-preview.html").write_text(
        '<html><head><link rel="stylesheet" href="../poster/assets/fonts.css"></head><body style="background:#ddd">' + html + "</body></html>")
