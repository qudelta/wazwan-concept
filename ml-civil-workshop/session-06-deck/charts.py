"""SVG charts for the Session 06 deck.

Numbers come from data/results.json (results.py): the UCI concrete data and linear-regression baseline, plus the
Random Forest, ANN and architecture results of the instructor's notebook.

Colour roles as in Sessions 01-05:
  blue   #2a78d6  inputs and observations
  green  #1baf7a  the network: activations, the selected ANN
  orange #eb6834  attention: errors, learning-rate overshoot
Charts that build click by click return a list of layers (see build.py).
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
R = json.loads((HERE / "data/results.json").read_text())
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, AXIS = "#0E1A2B", "#334155", "#64748B", "#E6EBF1", "#94A3B8"
FONT = "Archivo, sans-serif"
MONO = "JetBrains Mono, monospace"


class Plot:
    """Tiny SVG plotting helper (Sessions 01-05), with layers for click-by-click builds."""

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

    def rect(self, x, y, w, h, fill, extra=""):
        self.out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" fill="{fill}" {extra}/>')

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

    def path(self, pts, color, width=4, dash=""):
        d = "M" + " L".join(f"{self.X(a):.1f} {self.Y(b):.1f}" for a, b in pts)
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



def sig(z):
    return 1 / (1 + math.exp(-z))


def arrow(x1, y1, x2, y2, color, width=4, head=14, extra=""):
    """A straight arrow as SVG: a shaft that stops short of the tip, plus a filled head."""
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    a1, a2 = ang + 2.6, ang - 2.6
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" {extra}/>'
            f'<path d="M{x2:.1f} {y2:.1f} L{x2 + head * math.cos(a1):.1f} {y2 + head * math.sin(a1):.1f} '
            f'L{x2 + head * math.cos(a2):.1f} {y2 + head * math.sin(a2):.1f} Z" fill="{color}"/>')


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


# ------------------------------------------------------------------ recap: the dataset
def chart_strength():
    hist = R["strength_hist"]
    p = Plot(900, 470, (0, 85), (0, 140), pad=(70, 24, 24, 70))
    p.axes([0, 20, 40, 60, 80], [0, 40, 80, 120], "Compressive strength (MPa)", "Mixes", size=18)
    for k, c in enumerate(hist):
        p.rect(p.X(5 * k) + 2, p.Y(c), p.X(5) - p.X(0) - 4, p.Y(0) - p.Y(c), BLUE, 'rx="3"')
    m = R["strength_mean"]
    p.line(p.X(m), p.Y(0), p.X(m), p.Y(138), INK, 2.5, 'stroke-dasharray="7 7"')
    p.text(p.X(m) + 12, p.Y(128), f"mean {m:.1f} MPa", size=19, fill=INK, weight=800)
    return p.svg("Distribution of compressive strength for the 1,030 mixes")


# ------------------------------------------------------------------ Part 01: the biological neuron (drawn, schematic)
def chart_neuron():
    """A schematic neuron: dendrites (inputs) → cell body → myelinated axon → axon terminals (outputs)."""
    W, H = 860, 500
    o = []
    body = "#F6C76B"
    edge = "#C98A1E"
    dend = [((210, 250), (120, 150), (60, 120)), ((210, 250), (110, 230), (40, 210)), ((210, 250), (120, 330), (50, 360)),
            ((210, 250), (170, 130), (150, 60)), ((210, 250), (190, 380), (150, 440))]
    for (x0, y0), (x1, y1), (x2, y2) in dend:
        o.append(f'<path d="M{x0} {y0} Q{x1} {y1} {x2} {y2}" fill="none" stroke="{body}" stroke-width="14" stroke-linecap="round"/>')
        for t, d in ((0.62, 1), (0.85, -1)):                              # small side branches
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2
            o.append(f'<path d="M{bx:.0f} {by:.0f} l{-28:.0f} {d * 26:.0f}" stroke="{body}" stroke-width="8" stroke-linecap="round"/>')
    o.append(f'<path d="M270 262 C310 280 320 300 352 300 L640 300" fill="none" stroke="{body}" stroke-width="12" stroke-linecap="round"/>')
    for k in range(5):                                                    # myelin sheath
        x = 352 + k * 56
        o.append(f'<rect x="{x}" y="288" width="44" height="24" rx="12" fill="#7FB8E6" stroke="#2a78d6" stroke-width="2"/>')
    for dy in (-60, -20, 25, 65):                                         # axon terminals
        o.append(f'<path d="M640 300 Q690 {300 + dy * 0.4:.0f} 730 {300 + dy}" fill="none" stroke="{body}" stroke-width="9" stroke-linecap="round"/>')
        o.append(f'<circle cx="736" cy="{300 + dy}" r="9" fill="{body}" stroke="{edge}" stroke-width="2"/>')
    o.append(f'<circle cx="215" cy="250" r="62" fill="{body}" stroke="{edge}" stroke-width="3"/>')
    o.append(f'<circle cx="222" cy="248" r="24" fill="#B08CC8" stroke="#7A5A93" stroke-width="2"/>')

    def lab(x, y, t, sub, anchor="start", col=INK):
        o.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="23" font-weight="800" fill="{col}" text-anchor="{anchor}">{t}</text>'
                 f'<text x="{x}" y="{y + 25}" font-family="{FONT}" font-size="18" font-weight="500" fill="{MUTED}" text-anchor="{anchor}">{sub}</text>')
    lab(250, 40, "Dendrites", "receive signals · inputs", col="#1F5FAF")
    lab(300, 150, "Cell body", "combines the signals")
    lab(470, 360, "Axon", "carries the signal on")
    lab(650, 420, "Axon terminals", "pass it on · outputs", col="#B9471B")
    o.append(f'<path d="M248 52 Q200 60 172 92" fill="none" stroke="{MUTED}" stroke-width="2"/>')
    o.append(f'<path d="M300 158 Q262 175 250 205" fill="none" stroke="{MUTED}" stroke-width="2"/>')
    o.append(f'<path d="M500 340 L500 312" stroke="{MUTED}" stroke-width="2"/>')
    o.append(f'<path d="M700 398 L730 372" stroke="{MUTED}" stroke-width="2"/>')
    return svg(W, H, "".join(o), "Schematic of a biological neuron: dendrites, cell body, axon and axon terminals")


# ------------------------------------------------------------------ Part 01: learning rate, three step sizes
def chart_lr3():
    """Gradient descent on one bowl with a step size that is too small, about right, and too large."""
    out = []
    for k, (alpha, n, title, col) in enumerate(((0.06, 6, "Too low", BLUE), (0.38, 5, "About right", GREEN), (2.2, 3, "Too high", ORANGE))):
        ox = k * 300
        f = lambda w: (w / 10) ** 2 * 130  # noqa: E731  bowl J(w), minimum at w = 0
        X = lambda w: ox + 140 + w * 11.5  # noqa: E731
        Y = lambda j: 200 - j  # noqa: E731
        pts = " L".join(f"{X(w):.1f} {Y(f(w)):.1f}" for w in np.linspace(-10.5, 10.5, 50))
        out.append(f'<path d="M{pts}" fill="none" stroke="{INK}" stroke-width="3"/>')
        w = -9.0 if alpha < 2 else -7.0
        path = [w]
        for _ in range(n):
            w = w - alpha * w
            path.append(w)
        for u, v in zip(path, path[1:]):
            out.append(f'<path d="M{X(u):.1f} {Y(f(u)):.1f} L{X(v):.1f} {Y(f(v)):.1f}" stroke="{col}" stroke-width="2.5" fill="none"/>')
        for u in path:
            out.append(f'<circle cx="{X(u):.1f}" cy="{Y(f(u)):.1f}" r="6" fill="{col}" stroke="#fff" stroke-width="1.5"/>')
        out.append(f'<text x="{ox + 140}" y="244" font-family="{FONT}" font-size="22" font-weight="800" fill="{INK}" text-anchor="middle">{title}</text>')
    return svg(880, 256, "".join(out), "Gradient descent with a learning rate that is too low, about right, and too high")


# ------------------------------------------------------------------ Part 02: one neuron, and the (32, 16) network
def chart_unit():
    W, H = 820, 330
    o = []
    cx, cy, r = 520, 165, 72
    ins = [("x₁", "w₁", 60), ("x₂", "w₂", 150), ("xₙ", "wₙ", 280)]
    for x, w, y in ins:
        o.append(arrow(90, y, cx - r - 4, cy + (y - cy) * 0.35, BLUE, 3.5))
        o.append(f'<text x="64" y="{y + 9}" font-family="{FONT}" font-size="28" font-weight="800" font-style="italic" fill="#1F5FAF" text-anchor="end">{x}</text>')
        mx, my = 250, y + (cy + (y - cy) * 0.35 - y) * (160 / 358)
        o.append(f'<text x="{mx}" y="{my - 12:.0f}" font-family="{FONT}" font-size="22" font-weight="800" font-style="italic" fill="#1F5FAF" '
                 f'paint-order="stroke" stroke="#fff" stroke-width="6">{w}</text>')
    o.append(f'<text x="50" y="222" font-family="{FONT}" font-size="30" font-weight="800" fill="{MUTED}" text-anchor="middle">⋮</text>')
    o.append(arrow(cx, 18, cx, cy - r - 4, ORANGE, 3.5))
    o.append(f'<text x="{cx + 14}" y="36" font-family="{FONT}" font-size="24" font-weight="800" font-style="italic" fill="#B9471B">b</text>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}" fill-opacity=".12" stroke="{GREEN}" stroke-width="4"/>')
    o.append(f'<text x="{cx}" y="{cy + 12}" font-family="{FONT}" font-size="34" font-weight="800" fill="#0B7A55" text-anchor="middle">Σ → <tspan font-style="italic">g</tspan></text>')
    o.append(arrow(cx + r + 4, cy, 740, cy, INK, 4))
    o.append(f'<text x="752" y="{cy + 11}" font-family="{FONT}" font-size="32" font-weight="800" font-style="italic" fill="{INK}">a</text>')
    return svg(W, H, "".join(o), "One neuron: weighted inputs plus a bias, passed through an activation function")


def chart_net():
    W, H = 1000, 600
    cols = [(110, 8, 15, BLUE, "8 inputs"), (380, 32, 6.5, GREEN, "32 neurons · ReLU"), (650, 16, 10, GREEN, "16 neurons · ReLU"), (890, 1, 18, INK, "1 output")]
    pos = []
    for x, n, r, col, _ in cols:
        gap = 470 / max(n - 1, 1)
        pos.append([(x, 280 if n == 1 else 45 + k * gap) for k in range(n)])
    o = []
    for a, b in zip(pos, pos[1:]):
        for x1, y1 in a:
            for x2, y2 in b:
                o.append(f'<line x1="{x1}" y1="{y1:.1f}" x2="{x2}" y2="{y2:.1f}" stroke="#AAB6C5" stroke-width="0.6" stroke-opacity=".55"/>')
    for (x, n, r, col, lab), pts in zip(cols, pos):
        for px, py in pts:
            o.append(f'<circle cx="{px}" cy="{py:.1f}" r="{r}" fill="#fff" stroke="{col}" stroke-width="{3 if r > 8 else 2.2}"/>')
        o.append(f'<text x="{x}" y="568" font-family="{FONT}" font-size="22" font-weight="800" fill="{INK}" text-anchor="middle">{lab}</text>')
    o.append(f'<text x="{pos[0][0][0] - 26}" y="{pos[0][0][1] + 7:.0f}" font-family="{FONT}" font-size="19" font-weight="700" fill="#1F5FAF" text-anchor="end">cement</text>')
    o.append(f'<text x="{pos[0][-1][0] - 26}" y="{pos[0][-1][1] + 7:.0f}" font-family="{FONT}" font-size="19" font-weight="700" fill="#1F5FAF" text-anchor="end">age</text>')
    o.append(f'<text x="{pos[3][0][0] + 30}" y="{pos[3][0][1] + 8:.0f}" font-family="{FONT}" font-size="24" font-weight="800" font-style="italic" fill="{INK}">ŷ</text>')
    return svg(W, H, "".join(o), "The selected network: 8 inputs, hidden layers of 32 and 16 neurons, 1 output")


# ------------------------------------------------------------------ Part 02: activations
def chart_act():
    p = Plot(900, 560, (-5, 5), (-1.3, 5.2), pad=(70, 30, 30, 70))
    p.axes([-4, -2, 0, 2, 4], [-1, 0, 1, 2, 3, 4, 5], "Pre-activation z", "Activation g(z)", size=18)
    p.line(p.X(0), p.Y(-1.3), p.X(0), p.Y(5.2), AXIS, 1.5)
    zs = np.linspace(-5, 5, 121)
    p.path([(z, max(0.0, z)) for z in zs], BLUE, width=6)
    p.text(p.X(3.0) - 14, p.Y(3.0) - 16, "ReLU: max(0, z)", size=21, fill="#1F5FAF", weight=800, anchor="end")
    p.layer()
    p.path([(z, sig(z)) for z in zs], ORANGE, width=5)
    p.text(p.X(-4.8), p.Y(1.0) - 14, "sigmoid: 0 to 1", size=20, fill="#B9471B", weight=800)
    p.layer()
    p.path([(z, math.tanh(z)) for z in zs], GREEN, width=5)
    p.text(p.X(-4.8), p.Y(-1.0) + 30, "tanh: −1 to 1", size=20, fill="#0B7A55", weight=800)
    return p.stack("Activation functions: ReLU, sigmoid and tanh")


# ------------------------------------------------------------------ Part 02: why scale
NAMES = {"cement": "Cement", "slag": "Slag", "ash": "Fly ash", "water": "Water", "superplastic": "Superplasticizer",
         "coarseagg": "Coarse agg.", "fineagg": "Fine agg.", "age": "Age (days)"}


def chart_scale(std):
    rng, mu, sd = R["ranges"], R["means"], R["sds"]
    feats = list(NAMES)
    if std:
        p = Plot(760, 470, (-3, 6), (0, len(feats)), pad=(190, 16, 24, 62))
        p.axes([-2, 0, 2, 4, 6], [], "Standardised value (z-score)", "", size=17)
        p.line(p.X(0), p.Y(0), p.X(0), p.Y(len(feats)), INK, 2, 'stroke-dasharray="6 6"')
        val = lambda c, v: (v - mu[c]) / sd[c]  # noqa: E731
        col = GREEN
    else:
        p = Plot(760, 470, (0, 1200), (0, len(feats)), pad=(190, 16, 24, 62))
        p.axes([0, 300, 600, 900, 1200], [], "Raw value (kg/m³, or days for age)", "", size=17)
        val = lambda c, v: v  # noqa: E731
        col = BLUE
    for k, c in enumerate(feats):
        yy = p.Y(len(feats) - k - 0.5)
        lo, hi = val(c, rng[c][0]), val(c, rng[c][1])
        p.text(p.l - 14, yy + 7, NAMES[c], size=18, fill=INK2, weight=700, anchor="end")
        p.line(p.X(lo), yy, p.X(hi), yy, col, 14)
    return p.svg("Ranges of the eight inputs, " + ("after standard scaling" if std else "in their raw units"))


# ------------------------------------------------------------------ Part 02: training curves (schematic)
def chart_curves():
    p = Plot(900, 470, (0, 100), (0, 1.05), pad=(60, 30, 30, 64))
    p.axes([], [], "Iterations (epochs)", "", size=18)
    p.line(p.l, p.Y(0), p.l, p.Y(1.05), AXIS, 2)
    it = np.linspace(1, 100, 100)
    loss = 0.08 + 0.9 * np.exp(-it / 14)
    val = 0.86 - 0.86 * np.exp(-it / 12) - 0.0018 * np.clip(it - 45, 0, None)
    p.path(list(zip(it, loss)), ORANGE, width=5)
    p.text(p.X(70), p.Y(0.15), "training loss keeps falling", size=20, fill="#B9471B", weight=800)
    p.path(list(zip(it, val)), GREEN, width=5)
    best = int(np.argmax(val))
    p.line(p.X(it[best]), p.Y(0), p.X(it[best]), p.Y(1.0), INK, 2, 'stroke-dasharray="6 6"')
    p.dots([it[best]], [val[best]], GREEN, r=9, opacity=1)
    p.text(p.X(it[best]) + 14, p.Y(val[best]) - 16, "validation score peaks: stop here", size=20, fill="#0B7A55", weight=800)
    p.text(p.X(2), p.Y(1.02), "Schematic", size=17, fill=MUTED, weight=700)
    return p.svg("Schematic training loss and validation score against iterations, with early stopping")


# ------------------------------------------------------------------ Part 02: architecture candidates
def chart_arch():
    A = R["arch"]
    p = Plot(1000, 470, (0, 8), (0, len(A)), pad=(260, 20, 40, 64))
    p.axes([0, 2, 4, 6, 8], [], "Validation RMSE (MPa) · lower is better", "", size=18)
    best = min(a["rmse"] for a in A)
    for k, a in enumerate(A):
        yy = p.Y(len(A) - k - 0.5)
        on = a["rmse"] == best
        p.rect(p.X(0), yy - 30, p.X(a["rmse"]) - p.X(0), 60, GREEN if on else "#B9C4D2", 'rx="6"')
        lay = ", ".join(str(v) for v in a["layers"]) + ("," if len(a["layers"]) == 1 else "")
        p.text(p.l - 16, yy - 2, a["name"], size=21, fill=INK, weight=800, anchor="end")
        p.text(p.l - 16, yy + 22, f"({lay})", size=18, fill=MUTED, weight=600, anchor="end", family=MONO)
        p.text(p.X(a["rmse"]) + 12, yy + 8, f'{a["rmse"]:.3f}', size=21, fill="#0B7A55" if on else INK, weight=800, family=MONO)
    return p.svg("Validation RMSE of four candidate ANN architectures")


# ------------------------------------------------------------------ Part 03: results
MODELS = ["Linear regression", "Random forest", "ANN (32, 16)"]
MCOL = {"Linear regression": "#B9C4D2", "Random forest": BLUE, "ANN (32, 16)": GREEN}


def chart_err():
    T = R["test"]
    p = Plot(1000, 520, (0, 2), (0, 11), pad=(70, 46, 20, 60))
    p.axes([], [0, 2, 4, 6, 8, 10], "", "MPa · lower is better", size=17)
    bw = 0.25
    for k, (key, lab) in enumerate((("mae", "MAE"), ("rmse", "RMSE"))):
        p.text(p.X(k + 0.5), p.h - p.b + 34, lab, size=22, fill=INK, weight=800, anchor="middle")
        for m, name in enumerate(MODELS):
            v = T[name][key]
            x0 = k + 0.5 - 1.5 * bw + m * bw
            p.rect(p.X(x0) + 4, p.Y(v), p.X(x0 + bw) - p.X(x0) - 8, p.Y(0) - p.Y(v), MCOL[name], 'rx="5"')
            p.text(p.X(x0 + bw / 2), p.Y(v) - 10, f"{v:.2f}", size=18, fill=INK, weight=700, anchor="middle", family=MONO)
    lx = p.l
    for name in MODELS:
        p.rect(lx, 8, 18, 18, MCOL[name], 'rx="4"')
        p.text(lx + 26, 23, name, size=19, fill=INK2, weight=700, halo=False)
        lx += 250
    return p.svg("Test MAE and RMSE of linear regression, random forest and the ANN")


def chart_r2():
    T = R["test"]
    p = Plot(1000, 470, (0, 1), (0, 3), pad=(230, 20, 40, 64))
    p.axes([0, 0.25, 0.5, 0.75, 1.0], [], "Test R² · higher is better", "", xfmt=lambda v: f"{v:.2f}", size=18)
    for k, name in enumerate(MODELS):
        yy = p.Y(3 - k - 0.5)
        v = T[name]["r2"]
        p.rect(p.X(0), yy - 34, p.X(v) - p.X(0), 68, MCOL[name], 'rx="6"')
        p.text(p.l - 16, yy + 8, name, size=21, fill=INK, weight=800, anchor="end")
        p.text(p.X(v) + 12, yy + 8, f"{v:.3f}", size=22, fill=INK, weight=800, family=MONO)
    return p.svg("Test R² of the three models")


def _lin():
    L = R["lin_test"]
    return np.array(L["y"]), np.array(L["p"])


def chart_parity():
    y, pr = _lin()
    p = Plot(700, 600, (0, 90), (0, 90), pad=(80, 20, 24, 72))
    p.axes([0, 20, 40, 60, 80], [0, 20, 40, 60, 80], "Actual strength (MPa)", "Predicted strength (MPa)", size=18)
    p.path([(0, 0), (90, 90)], INK, width=2.5, dash="8 8")
    p.text(p.X(86), p.Y(86) + 26, "1 : 1 line", size=19, fill=INK, weight=700, anchor="end")
    p.dots(y, pr, "#8A99AD", r=6, opacity=0.75)
    return p.svg("Linear regression: predicted against actual strength for the 206 test mixes")


def chart_resid():
    y, pr = _lin()
    r = y - pr
    p = Plot(760, 560, (0, 80), (-32, 32), pad=(80, 20, 24, 72))
    p.axes([0, 20, 40, 60, 80], [-30, -15, 0, 15, 30], "Predicted strength (MPa)", "Residual = actual − predicted (MPa)", size=18)
    p.line(p.X(0), p.Y(0), p.X(80), p.Y(0), INK, 2.5)
    p.dots(pr, r, "#8A99AD", r=6, opacity=0.7)
    return p.svg("Linear regression residuals against predicted strength for the test mixes")


def build():
    return {
        "strength": chart_strength(), "neuron": chart_neuron(), "lr3": chart_lr3(),
        "unit": chart_unit(), "net": chart_net(), "act": chart_act(), "scraw": chart_scale(False), "scstd": chart_scale(True), "curves": chart_curves(),
        "arch": chart_arch(), "err": chart_err(), "r2": chart_r2(), "parity": chart_parity(), "resid": chart_resid(),
    }


if __name__ == "__main__":
    charts = build()
    flat = [s for v in charts.values() for s in (v if isinstance(v, list) else [v])]
    html = "".join(f'<div style="display:inline-block;margin:10px;background:#fff;width:640px;vertical-align:top">{s}</div>' for s in flat)
    (HERE / "charts-preview.html").write_text(
        '<html><head><link rel="stylesheet" href="../poster/assets/fonts.css"></head><body style="background:#ddd">' + html + "</body></html>")
    print("charts:", len(flat))
