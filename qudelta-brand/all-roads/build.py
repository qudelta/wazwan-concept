"""Builds the 'All roads lead back to sales' Instagram posts (square, 1080x1080) in dark and light themes.

Concept A draws real perspective roads: each road is a strip that narrows to a single vanishing point
where the word SALES sits on the horizon. Centre-line dashes shrink with distance so the depth reads.
"""
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
LOGOS = {"light": "assets/qudelta-logo-dark.png", "dark": "assets/qudelta-logo-light.png"}

VX, VY = 540, 492          # vanishing point: where every road ends, just under the word SALES
ROADS = [                  # (end point on/beyond the frame, half-width at that end, label)
    ((-150, 640), 62, "BRANDING"),
    ((-120, 905), 88, "WEBSITE"),
    ((150, 1190), 108, "ADS"),
    ((540, 1220), 118, "PRODUCT"),
    ((930, 1190), 108, "CONTENT"),
    ((1200, 905), 88, "APPS"),
    ((1230, 640), 62, "AUTOMATION"),
]
HERO = "PRODUCT"           # the road straight at the viewer carries brand-green dashes


def roads_svg() -> str:
    parts = []
    for (ex, ey), hw, label in ROADS:
        dx, dy = ex - VX, ey - VY
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length          # unit vector from V towards the viewer
        px, py = -uy, ux                           # perpendicular
        a = (ex + px * hw, ey + py * hw)
        b = (ex - px * hw, ey - py * hw)
        parts.append(f'<path class="road" d="M{VX} {VY} L{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} Z"/>')
        parts.append(f'<path class="edge" d="M{VX} {VY} L{a[0]:.1f} {a[1]:.1f} M{VX} {VY} L{b[0]:.1f} {b[1]:.1f}"/>')
        # perspective dashes: dash and gap lengths scale with distance from the vanishing point
        t, dashes = 1.0, []
        while t > 0.06:
            d_len, gap = 0.085 * t, 0.07 * t
            t0, t1 = t, max(t - d_len, 0)
            w = 2 + 5 * t
            dashes.append(f'<line x1="{VX + dx * t0:.1f}" y1="{VY + dy * t0:.1f}" x2="{VX + dx * t1:.1f}" y2="{VY + dy * t1:.1f}" stroke-width="{w:.1f}"/>')
            t = t1 - gap
        parts.append(f'<g class="dash{" hero" if label == HERO else ""}">{"".join(dashes)}</g>')
        # road name, laid along the road near the viewer
        lt = 0.62 if ey < 1100 else 0.40  # roads aimed at the bottom edge: keep the name clear of the caption fade
        lx, ly = VX + dx * lt + px * (hw * lt + 26), VY + dy * lt + py * (hw * lt + 26)
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90:
            ang -= 180
        elif ang < -90:
            ang += 180
        if abs(dx) < 5:  # the straight road: label sits upright beside it
            ang, lx = 0, VX - hw * lt - 52  # left of the road, clear of CONTENT on the right
        parts.append(f'<text class="rl" x="{lx:.1f}" y="{ly:.1f}" transform="rotate({ang:.1f} {lx:.1f} {ly:.1f})" '
                     f'text-anchor="middle" dominant-baseline="middle">{label}</text>')
    return "".join(parts)


src = (HERE / "post.src.html").read_text()
src = src.replace("{{roads}}", roads_svg()).replace("{{vx}}", str(VX)).replace("{{vy}}", str(VY))
for theme, logo in LOGOS.items():
    html = src.replace("{{theme}}", theme).replace("{{logo}}", f'<img src="{logo}" alt="Qudelta Studios">')
    leftover = re.findall(r"\{\{[^}]*\}\}", html)
    assert not leftover, leftover
    (HERE / f"post-{theme}.html").write_text(html)
    print(f"built post-{theme}.html")
