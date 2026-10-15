"""Builds the 'All roads lead back to sales' Instagram Story (1080x1920) in dark and light themes.

Perspective roads run from the bottom of the screen up to one vanishing point on the horizon, where the
word SALES sits. Key text stays inside Instagram's safe area (clear of the top bar and the reply bar).
"""
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
LOGOS = {"light": "assets/qudelta-logo-dark.png", "dark": "assets/qudelta-logo-light.png"}

VX, VY = 540, 1030          # vanishing point, just under the word SALES
ROADS = [                   # (end point beyond the frame, half-width there, label, where the label sits along the road)
    ((-330, 1150), 72, "BRANDING", 0.58),
    ((-300, 1520), 104, "WEBSITE", 0.56),
    ((40, 2120), 132, "ADS", 0.27),
    ((540, 2180), 144, "PRODUCT", 0.25),
    ((1040, 2120), 132, "CONTENT", 0.27),
    ((1380, 1520), 104, "APPS", 0.56),
    ((1410, 1150), 72, "AUTOMATION", 0.58),
]
HERO = "PRODUCT"            # the road straight at the viewer carries brand-green dashes


def roads_svg() -> str:
    parts = []
    for (ex, ey), hw, label, lt in ROADS:
        dx, dy = ex - VX, ey - VY
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        a, b = (ex + px * hw, ey + py * hw), (ex - px * hw, ey - py * hw)
        parts.append(f'<path class="road" d="M{VX} {VY} L{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} Z"/>')
        parts.append(f'<path class="edge" d="M{VX} {VY} L{a[0]:.1f} {a[1]:.1f} M{VX} {VY} L{b[0]:.1f} {b[1]:.1f}"/>')
        t, dashes = 1.0, []
        while t > 0.05:                       # dashes shrink with distance so the depth reads
            t1 = max(t - 0.07 * t, 0)
            dashes.append(f'<line x1="{VX + dx * t:.1f}" y1="{VY + dy * t:.1f}" x2="{VX + dx * t1:.1f}" '
                          f'y2="{VY + dy * t1:.1f}" stroke-width="{2 + 6 * t:.1f}"/>')
            t = t1 - 0.06 * t
        parts.append(f'<g class="dash{" hero" if label == HERO else ""}">{"".join(dashes)}</g>')
        ang = math.degrees(math.atan2(dy, dx))
        ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
        while True:                           # slide the label towards the horizon until it sits fully on screen
            off = hw * lt + 30
            lx, ly = VX + dx * lt + px * off, VY + dy * lt + py * off
            half = len(label) * 11 + 20
            if 70 + half < lx < 1010 - half or abs(dx) < 5 or lt < 0.2:
                break
            lt -= 0.02
        if abs(dx) < 5:                       # the straight road: label runs along it, on its left side
            ang, lx = 90, VX - hw * lt - 30
        parts.append(f'<text class="rl" x="{lx:.1f}" y="{ly:.1f}" transform="rotate({ang:.1f} {lx:.1f} {ly:.1f})" '
                     f'text-anchor="middle" dominant-baseline="middle">{label}</text>')
    return "".join(parts)


src = (HERE / "story.src.html").read_text()
src = src.replace("{{roads}}", roads_svg()).replace("{{vx}}", str(VX)).replace("{{vy}}", str(VY))
for theme, logo in LOGOS.items():
    html = src.replace("{{theme}}", theme).replace("{{logo}}", f'<img src="{logo}" alt="Qudelta Studios">')
    leftover = re.findall(r"\{\{[^}]*\}\}", html)
    assert not leftover, leftover
    (HERE / f"story-{theme}.html").write_text(html)
    print(f"built story-{theme}.html")
