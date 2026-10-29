"""SVG charts for the Session 05 deck.

Model results come from data/results.json (written by results.py, which reproduces the instructor notebook with
scikit-learn 1.6). Raw values come from the instructor's 616-case Morgenstern-Price dataset and, for the multiclass
extension, the UCI Steel Plates Faults data used in Session 02.

Colour roles as in Sessions 01-03:
  blue   #2a78d6  stable class / observations
  orange #eb6834  unstable class (the positive class), errors that matter
  green  #1baf7a  model output: fitted curve, probability, decision regions
Charts that build click by click return a list of layers (see build.py).
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
R = json.loads((HERE / "data/results.json").read_text())
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_T, ORANGE_T, GREEN_T = "#CFE0F5", "#F7D3C3", "#C3EAD9"
INK, INK2, MUTED, GRID, AXIS = "#0E1A2B", "#334155", "#64748B", "#E6EBF1", "#94A3B8"
FONT = "Archivo, sans-serif"
MONO = "JetBrains Mono, monospace"
MODELS = ["Logistic regression", "Decision tree", "Random forest"]


class Plot:
    """Tiny SVG plotting helper (Sessions 01-03), with layers for click-by-click builds."""

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


# ------------------------------------------------------------------ Part 01: why not linear regression (notebook demo)
def chart_demo():
    d = R["demo"]
    p = Plot(900, 560, (-3.6, 3.6), (-0.45, 1.3), pad=(80, 24, 30, 70))
    p.axes([-3, -2, -1, 0, 1, 2, 3], [0, 0.5, 1], "Illustrative input feature x", "Label  ·  model output", yfmt=lambda v: f"{v:g}", size=18)
    p.rect(p.l, p.Y(1.3), p.w - p.l - p.r, p.Y(1.0) - p.Y(1.3), ORANGE, 'fill-opacity=".08"')
    p.rect(p.l, p.Y(0), p.w - p.l - p.r, p.Y(-0.45) - p.Y(0), ORANGE, 'fill-opacity=".08"')
    jit = np.random.default_rng(1).uniform(-0.025, 0.025, len(d["y"]))
    p.dots(d["x"], [v + j for v, j in zip(d["y"], jit)], BLUE, r=5, opacity=0.45)
    p.text(p.X(-3.5), p.Y(1.0) - 12, "label 1 · unstable", size=18, fill=INK2, weight=700)
    p.text(p.X(-3.5), p.Y(0.0) + 28, "label 0 · stable", size=18, fill=INK2, weight=700)
    p.layer()                                                        # click 1: linear regression
    p.path(list(zip(d["xx"], d["lin"])), ORANGE, width=5)
    p.text(p.X(3.4), p.Y(d["lin"][-1]) - 14, f"linear regression reaches {max(d['lin']):.2f}", size=19, fill="#B9471B", weight=800, anchor="end")
    p.text(p.X(-3.4), p.Y(d["lin"][0]) + 30, f"… and {min(d['lin']):.2f}", size=19, fill="#B9471B", weight=800)
    p.layer()                                                        # click 2: logistic regression
    p.path(list(zip(d["xx"], d["log"])), GREEN, width=6)
    p.text(p.X(0.35), p.Y(0.3), "logistic: always between 0 and 1", size=20, fill="#0B7A55", weight=800)
    return p.stack("Linear regression against logistic regression on the same 0/1 labels")


def chart_sigmoid():
    p = Plot(900, 520, (-7, 7), (-0.05, 1.08), pad=(80, 24, 30, 70))
    p.axes([-6, -3, 0, 3, 6], [0, 0.5, 1], "Linear score z", "Probability p = σ(z)", yfmt=lambda v: f"{v:g}", size=18)
    p.path([(z, sig(z)) for z in np.linspace(-7, 7, 120)], GREEN, width=6)
    p.layer()                                                        # click 1: z < 0
    p.dots([-3], [sig(-3)], ORANGE, r=10, opacity=1)
    p.text(p.X(-3) + 18, p.Y(sig(-3)) - 14, f"z = −3  →  p = {sig(-3):.2f}", size=20, fill=INK, weight=800)
    p.layer()                                                        # click 2: z = 0
    p.line(p.X(0), p.Y(0), p.X(0), p.Y(0.5), INK, 2, 'stroke-dasharray="6 6"')
    p.line(p.X(-7), p.Y(0.5), p.X(0), p.Y(0.5), INK, 2, 'stroke-dasharray="6 6"')
    p.dots([0], [0.5], ORANGE, r=10, opacity=1)
    p.text(p.X(0) + 18, p.Y(0.5) + 8, "z = 0  →  p = 0.50", size=20, fill=INK, weight=800)
    p.layer()                                                        # click 3: z > 0
    p.dots([3], [sig(3)], ORANGE, r=10, opacity=1)
    p.text(p.X(3) - 18, p.Y(sig(3)) - 18, f"z = 3  →  p = {sig(3):.2f}", size=20, fill=INK, weight=800, anchor="end")
    return p.stack("The sigmoid turns any score into a probability between 0 and 1")


# ------------------------------------------------------------------ Part 02: the slope data
def chart_slope():
    """Schematic of a homogeneous slope with the three inputs."""
    o = ['<svg viewBox="0 0 860 470" role="img" aria-label="Slope geometry and soil parameters" xmlns="http://www.w3.org/2000/svg" font-family="Archivo">',
         '<path d="M30 400 H300 L520 150 H830 V440 H30 Z" fill="#E9DFCF"/>',
         '<path d="M30 400 H300 L520 150 H830" fill="none" stroke="#7A6248" stroke-width="5" stroke-linejoin="round"/>',
         '<g fill="#C9B79C" opacity=".7"><circle cx="420" cy="380" r="5"/><circle cx="600" cy="300" r="6"/><circle cx="700" cy="390" r="4"/><circle cx="560" cy="220" r="4"/><circle cx="760" cy="250" r="5"/><circle cx="480" cy="330" r="3"/></g>',
         '<path d="M262 400 C 330 470, 520 430, 600 150" fill="none" stroke="#eb6834" stroke-width="4" stroke-dasharray="12 9"/>',
         '<text x="830" y="128" font-size="19" font-weight="700" fill="#B9471B" text-anchor="end">critical slip surface (Morgenstern–Price)</text>',
         '<path d="M370 400 A 70 70 0 0 0 346 347" fill="none" stroke="#0E1A2B" stroke-width="3"/>',
         '<text x="384" y="378" font-size="30" font-style="italic" font-weight="800" fill="#0E1A2B">β</text>',
         '<line x1="300" y1="400" x2="380" y2="400" stroke="#0E1A2B" stroke-width="2" stroke-dasharray="5 5"/>',
         '<line x1="250" y1="150" x2="250" y2="400" stroke="#0E1A2B" stroke-width="2.5"/><line x1="236" y1="150" x2="264" y2="150" stroke="#0E1A2B" stroke-width="2.5"/><line x1="236" y1="400" x2="264" y2="400" stroke="#0E1A2B" stroke-width="2.5"/>',
         '<line x1="264" y1="150" x2="520" y2="150" stroke="#0E1A2B" stroke-width="1.5" stroke-dasharray="5 5"/>',
         '<text x="230" y="285" font-size="30" font-style="italic" font-weight="800" fill="#0E1A2B" text-anchor="end">H</text>',
         '<g transform="translate(630 330)"><rect x="-10" y="-46" width="200" height="104" rx="16" fill="#fff" fill-opacity=".9"/>',
         '<text x="8" y="-12" font-size="24" font-weight="800" fill="#0E1A2B"><tspan font-style="italic">c</tspan> · cohesion</text>',
         '<text x="8" y="18" font-size="24" font-weight="800" fill="#0E1A2B"><tspan font-style="italic">φ</tspan> · friction angle</text>',
         '<text x="8" y="48" font-size="24" font-weight="800" fill="#0E1A2B"><tspan font-style="italic">γ</tspan> · unit weight</text></g>',
         '</svg>']
    return "".join(o)


def chart_fos_hist():
    counts, edges = R["fos_hist"], R["fos_edges"]
    p = Plot(900, 470, (0, 7.6), (0, 70), pad=(70, 30, 30, 70))
    p.axes([0, 1, 2, 3, 4, 5, 6, 7], [0, 20, 40, 60], "Factor of safety (Morgenstern–Price)", "Number of cases", size=18)
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        col = ORANGE if b <= 1.0001 else (ORANGE_T if a < 1.0 else BLUE)
        p.rect(p.X(a) + 1.5, p.Y(c), p.X(b) - p.X(a) - 3, p.Y(0) - p.Y(c), col, 'rx="3"')
    for t, lab, col in ((1.0, "FOS = 1.0", INK), (1.5, "FOS = 1.5", MUTED)):
        p.line(p.X(t), p.t, p.X(t), p.h - p.b, col, 2.5, 'stroke-dasharray="8 6"')
        p.text(p.X(t) + 8, p.t + 18 + (0 if t == 1.0 else 50), lab, size=19, fill=col, weight=800)
    p.text(p.X(7.4), p.Y(60), f"{R['n']} cases · FOS {R['fos_min']:.2f} – {R['fos_max']:.2f}", size=19, fill=INK2, weight=600, anchor="end")
    return p.svg("Distribution of the factor of safety for 616 cases, with thresholds at 1.0 and 1.5")


def chart_slice():
    """The phi = 25 degree slice as a table of FOS values; unstable cells highlighted, FOS = 1 boundary drawn."""
    cells = R["slice25"]
    betas = sorted({c[0] for c in cells})
    cs = sorted({c[1] for c in cells})
    fos = {(b, c): f for b, c, f in cells}
    W, H, L, T, cw, ch = 1120, 560, 120, 20, 88, 66
    o = []
    for j, c in enumerate(reversed(cs)):
        y = T + j * ch
        o.append(f'<text x="{L - 16}" y="{y + ch / 2 + 7:.1f}" font-family="{MONO}" font-size="19" font-weight="700" fill="{INK2}" text-anchor="end">{c:.2f}</text>')
        for i, b in enumerate(betas):
            x = L + i * cw
            f = fos[(b, c)]
            uns = f < 1.0
            t = min(1, (f - 0.2) / 4.8)
            fill = ORANGE if uns else "#{:02X}{:02X}{:02X}".format(*[round(a + (z - a) * t) for a, z in zip((0xEA, 0xF2, 0xFC), (0x2a, 0x78, 0xd6))])
            tc = "#fff" if uns or t > 0.55 else INK
            o.append(f'<rect x="{x + 2}" y="{y + 2}" width="{cw - 4}" height="{ch - 4}" rx="8" fill="{fill}"/>')
            o.append(f'<text x="{x + cw / 2:.1f}" y="{y + ch / 2 + 7:.1f}" font-family="{MONO}" font-size="19" font-weight="700" fill="{tc}" text-anchor="middle">{f:.2f}</text>')
    yb = T + len(cs) * ch
    for i, b in enumerate(betas):
        o.append(f'<text x="{L + i * cw + cw / 2:.1f}" y="{yb + 30}" font-family="{MONO}" font-size="19" font-weight="700" fill="{INK2}" text-anchor="middle">{b:.0f}°</text>')
    o.append(f'<text x="{L + len(betas) * cw / 2:.1f}" y="{yb + 64}" font-family="{FONT}" font-size="20" font-weight="600" fill="{INK2}" text-anchor="middle">Slope angle β</text>')
    o.append(f'<text x="24" y="{T + len(cs) * ch / 2:.1f}" font-family="{FONT}" font-size="20" font-weight="600" fill="{INK2}" text-anchor="middle" transform="rotate(-90 24 {T + len(cs) * ch / 2:.1f})">c/(γH)</text>')
    # the FOS = 1 boundary as a staircase along cell edges
    seg = []
    for i, b in enumerate(betas):
        k = sum(1 for c in cs if fos[(b, c)] < 1.0)                  # unstable cells from the bottom
        seg.append((L + i * cw, L + (i + 1) * cw, T + (len(cs) - k) * ch))
    d = f"M{seg[0][0]} {seg[0][2]}"
    for x0, x1, y in seg:
        d += f" L{x0} {y} L{x1} {y}"
    o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Factor of safety on the phi = 25 degree slice; unstable cells highlighted" '
            f'xmlns="http://www.w3.org/2000/svg">' + "".join(o) + "</svg>")


def chart_region(name):
    """Decision regions of a tuned model on the phi = 25 degree slice, with the true grid labels."""
    reg = R["regions"]
    bg, cg, Z = reg["beta"], reg["c"], np.array(reg[name])
    p = Plot(560, 460, (15, 65), (0, 0.30), pad=(70, 16, 16, 62))
    db, dc = bg[1] - bg[0], cg[1] - cg[0]
    for j, c in enumerate(cg):
        run = None
        for i, b in enumerate(bg + [None]):
            v = Z[j, i] if b is not None else None
            if run and (v != run[1]):
                x0, x1 = p.X(max(15, run[0] - db / 2)), p.X(min(65, bg[i - 1] + db / 2))
                p.rect(x0, p.Y(min(0.3, c + dc / 2)), x1 - x0, p.Y(max(0, c - dc / 2)) - p.Y(min(0.3, c + dc / 2)) + 0.6,
                       ORANGE_T if run[1] == 1 else "#EEF4FB")
                run = None
            if b is not None and run is None:
                run = (b, v)
    p.axes([15, 25, 35, 45, 55, 65], [0, 0.1, 0.2, 0.3], "Slope angle β (°)", "c/(γH)", yfmt=lambda v: f"{v:.1f}", size=17)
    for b, c, f in R["slice25"]:
        uns = f < 1.0
        p.dots([b], [c], ORANGE if uns else BLUE, r=7 if uns else 5.5, opacity=1 if uns else 0.7)
    return p.svg(f"{name}: predicted regions on the phi = 25 degree slice")


# ------------------------------------------------------------------ Part 03: results
def chart_metrics():
    T = R["test"]
    keys = [("rec", "Recall (unstable)"), ("prec", "Precision (unstable)"), ("f1", "F1 (unstable)"), ("bal", "Balanced accuracy")]
    cols = {"Logistic regression": GREEN, "Decision tree": "#7FD3B4", "Random forest": BLUE}
    p = Plot(1100, 500, (0, len(keys)), (0, 1.08), pad=(70, 40, 20, 60))
    p.axes([], [0, 0.25, 0.5, 0.75, 1.0], "", "", yfmt=lambda v: f"{v:.2f}", size=17)
    bw = 0.22
    for k, (key, lab) in enumerate(keys):
        p.text(p.X(k + 0.5), p.h - p.b + 32, lab, size=19, fill=INK2, weight=700, anchor="middle")
        for m, name in enumerate(MODELS):
            v = T[name][key]
            x0 = k + 0.5 - 1.5 * bw + m * bw
            p.rect(p.X(x0) + 3, p.Y(v), p.X(x0 + bw) - p.X(x0) - 6, p.Y(0) - p.Y(v), cols[name], 'rx="4"')
            p.text(p.X(x0 + bw / 2), p.Y(v) - 8, f"{v:.2f}", size=15, fill=INK, weight=700, anchor="middle", family=MONO)
    lx = p.l
    for name in MODELS:
        p.rect(lx, 6, 18, 18, cols[name], 'rx="4"')
        p.text(lx + 26, 21, name, size=18, fill=INK2, weight=700, halo=False)
        lx += 240
    return p.svg("Safety-relevant test metrics of the three tuned models")


def chart_threshold():
    """Out-of-fold probabilities of the training cases, one row per class, with candidate thresholds."""
    pr = R["oof_prob"]
    p = Plot(1100, 300, (0, 1), (0, 2), pad=(150, 20, 30, 56))
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        p.line(p.X(t), p.t, p.X(t), p.h - p.b, GRID)
        p.text(p.X(t), p.h - p.b + 28, f"{t:.2f}", size=17, anchor="middle")
    p.text((p.l + p.w - p.r) / 2, p.h - 4, "Predicted probability of unstable (out-of-fold, training data)", size=18, fill=INK2, weight=600, anchor="middle")
    rng = np.random.default_rng(7)
    for row, (key, col, lab) in enumerate((("unstable", ORANGE, "Unstable"), ("stable", BLUE, "Stable"))):
        yc = 1.5 - row
        p.text(p.l - 16, p.Y(yc) + 7, f"{lab} ({len(pr[key])})", size=19, fill=INK, weight=800, anchor="end")
        for v in pr[key]:
            p.out.append(f'<circle cx="{p.X(v):.1f}" cy="{p.Y(yc) + rng.uniform(-30, 30):.1f}" r="4.5" fill="{col}" fill-opacity=".55"/>')
    for t, col in ((0.3, MUTED), (0.5, INK), (0.7, MUTED)):
        p.line(p.X(t), p.t - 4, p.X(t), p.h - p.b, col, 3 if t == 0.5 else 2, 'stroke-dasharray="8 6"')
    return p.svg("Out-of-fold predicted probabilities for stable and unstable training cases")


# ------------------------------------------------------------------ extension and appendix
def chart_steel():
    cols = (HERE / "data/steel-plates-faults.columns").read_text().split()
    A = np.loadtxt(HERE / "data/steel-plates-faults.tsv")
    nice = {"Other_Faults": "Other faults", "Bumps": "Bumps", "K_Scatch": "K-scratch", "Z_Scratch": "Z-scratch",
            "Pastry": "Pastry", "Stains": "Stains", "Dirtiness": "Dirtiness"}
    counts = sorted(((nice[c], int(A[:, cols.index(c)].sum())) for c in cols[-7:]), key=lambda kv: -kv[1])
    n = len(A)
    W, H, L, Rm = 900, 470, 170, 170
    rh = (H - 16) / len(counts)
    o = []
    for k, (lab, c) in enumerate(counts):
        y = 8 + k * rh
        w = c / counts[0][1] * (W - L - Rm)
        rare = c / n < 0.05
        o.append(f'<text x="{L - 14}" y="{y + rh / 2 + 7:.1f}" font-family="{FONT}" font-size="21" font-weight="700" fill="{INK}" text-anchor="end">{lab}</text>')
        o.append(f'<rect x="{L}" y="{y + 8:.1f}" width="{w:.1f}" height="{rh - 16:.1f}" rx="6" fill="{ORANGE if rare else BLUE}"/>')
        o.append(f'<text x="{L + w + 12:.1f}" y="{y + rh / 2 + 7:.1f}" font-family="{MONO}" font-size="19" font-weight="700" fill="{INK}">{c}<tspan fill="{MUTED}" font-weight="500"> · {100 * c / n:.1f}%</tspan></text>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Number of steel plates in each of seven fault classes" xmlns="http://www.w3.org/2000/svg">'
            + "".join(o) + "</svg>")


def H2(p):
    return 0.0 if p in (0, 1) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def chart_impurity():
    p = Plot(820, 470, (0, 1), (0, 1.08), pad=(76, 24, 30, 70))
    p.axes([0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1], "Proportion of unstable cases in a node, p", "Impurity",
           xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", size=18)
    ps = np.linspace(0, 1, 101)
    p.path([(q, H2(q)) for q in ps], ORANGE, width=5)
    p.path([(q, 2 * q * (1 - q)) for q in ps], BLUE, width=5)
    p.text(p.X(0.5), p.Y(1.0) - 12, "entropy (bits), max 1", size=20, fill="#B9471B", weight=800, anchor="middle")
    p.text(p.X(0.5), p.Y(0.5) - 12, "Gini, max 0.5", size=20, fill="#1F5FAF", weight=800, anchor="middle")
    q = R["counts"]["1.0"]["below"] / R["n"]
    p.line(p.X(q), p.Y(0), p.X(q), p.Y(H2(q)), INK, 2, 'stroke-dasharray="5 6"')
    p.dots([q, q], [H2(q), 2 * q * (1 - q)], INK, r=7, opacity=1)
    p.text(p.X(q) + 12, p.Y(H2(q)) + 26, f"our data: p = {q:.3f}", size=18, fill=INK, weight=700)
    return p.svg("Entropy and Gini impurity against the class proportion of a node")


def chart_bootstrap():
    draw = R["bootstrap"]
    cnt = np.bincount(draw, minlength=12)
    p = Plot(820, 300, (-0.6, 11.6), (0, 3.6), pad=(56, 20, 20, 56))
    p.axes(list(range(12)), [0, 1, 2, 3], "Original training-row ID", "", size=17)
    for i, c in enumerate(cnt):
        if c:
            p.rect(p.X(i - 0.35), p.Y(c), p.X(i + 0.35) - p.X(i - 0.35), p.Y(0) - p.Y(c), GREEN, 'rx="4"')
        else:
            p.text(p.X(i), p.Y(0) - 12, "out", size=15, fill="#B9471B", weight=800, anchor="middle")
    return p.svg("One bootstrap sample of 12 rows: some rows repeat, others are left out")


def build():
    return {
        "demo": chart_demo(), "sigmoid": chart_sigmoid(),
        "slope": chart_slope(), "foshist": chart_fos_hist(), "slice": chart_slice(),
        "rlr": chart_region("Logistic regression"), "rdt": chart_region("Decision tree"), "rrf": chart_region("Random forest"),
        "metrics": chart_metrics(), "thr": chart_threshold(),
        "steel": chart_steel(), "impurity": chart_impurity(), "boot": chart_bootstrap(),
    }


if __name__ == "__main__":
    charts = build()
    flat = [s for v in charts.values() for s in (v if isinstance(v, list) else [v])]
    html = "".join(f'<div style="display:inline-block;margin:10px;background:#fff;width:640px;vertical-align:top">{s}</div>' for s in flat)
    (HERE / "charts-preview.html").write_text(
        '<html><head><link rel="stylesheet" href="../poster/assets/fonts.css"></head><body style="background:#ddd">' + html + "</body></html>")
    print("charts:", len(flat))
