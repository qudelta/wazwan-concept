"""Draws the illustrations used by the carousel and the stories (deterministic, plain SVG).

night-road.svg  a lit Kashmiri shop on an empty mountain road at night (the website nobody visits)
kani.svg        a Kani-shawl swatch: boteh (paisley) rows on ivory, for the export-storefront mockup
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent / "assets"


def night_road(w=936, h=620) -> str:
    rnd = random.Random(7)
    hz = 352  # horizon
    vx = 520  # vanishing point x
    stars = "".join(
        f'<circle cx="{rnd.uniform(0, w):.1f}" cy="{rnd.uniform(0, hz - 120) ** 1.0:.1f}" r="{rnd.choice([0.8, 1, 1.2, 1.6]):.1f}" '
        f'fill="#E6F2EB" opacity="{rnd.uniform(.25, .85):.2f}"/>' for _ in range(70))

    def ridge(y0, amp, n, seed, jag=0.5):
        r = random.Random(seed)
        pts, x = [], -20
        while x < w + 40:
            pts.append((x, y0 - r.uniform(0, amp)))
            x += r.uniform(40, 40 + 90 * jag)
        return pts

    far = ridge(hz - 40, 120, 0, 3, 1.0)
    far_d = "M-20," + str(hz) + " " + " ".join(f"L{x:.0f},{y:.0f}" for x, y in far) + f" L{w + 40},{hz} Z"
    # snow caps on the highest far peaks
    caps = []
    for i in range(1, len(far) - 1):
        x, y = far[i]
        if y < hz - 115 and far[i - 1][1] > y and far[i + 1][1] > y:
            lx = x + (far[i - 1][0] - x) * .28; ly = y + (far[i - 1][1] - y) * .28
            rx = x + (far[i + 1][0] - x) * .28; ry = y + (far[i + 1][1] - y) * .28
            caps.append(f'<path d="M{lx:.0f},{ly:.0f} L{x:.0f},{y:.0f} L{rx:.0f},{ry:.0f} L{(x + rx) / 2:.0f},{ry - 4:.0f} '
                        f'L{x:.0f},{(y + ly) / 2 + 6:.0f} L{(x + lx) / 2:.0f},{ly - 3:.0f} Z" fill="#D9E8E0" opacity=".42"/>')
    mid = ridge(hz - 6, 52, 0, 11, 0.6)
    mid_d = "M-20," + str(hz + 4) + " " + " ".join(f"L{x:.0f},{y:.0f}" for x, y in mid) + f" L{w + 40},{hz + 4} Z"

    # road: wide at the bottom, meets the horizon at the vanishing point
    road = f'M300,{h} L{w - 80},{h} L{vx + 8},{hz} L{vx - 8},{hz} Z'
    dashes = []
    for k in range(9):
        t0 = (k / 9) ** 1.9; t1 = ((k + .45) / 9) ** 1.9
        def at(t):
            y = hz + (h - hz) * t
            cx = vx + ((300 + w - 80) / 2 - vx) * t
            return cx, y, 1 + 9 * t
        x0, y0, s0 = at(t0); x1, y1, s1 = at(t1)
        dashes.append(f'<path d="M{x0 - s0 / 2:.1f},{y0:.1f} L{x0 + s0 / 2:.1f},{y0:.1f} L{x1 + s1 / 2:.1f},{y1:.1f} L{x1 - s1 / 2:.1f},{y1:.1f} Z" fill="#3A433E"/>')

    def chinar(cx, base, s, fill):
        r = random.Random(int(cx))
        blobs = "".join(f'<circle cx="{cx + r.uniform(-1, 1) * 60 * s:.0f}" cy="{base - 120 * s - r.uniform(0, 90) * s:.0f}" '
                        f'r="{r.uniform(28, 46) * s:.0f}"/>' for _ in range(16))
        trunk = (f'<path d="M{cx - 7 * s:.0f},{base} C{cx - 5 * s:.0f},{base - 50 * s:.0f} {cx - 12 * s:.0f},{base - 90 * s:.0f} {cx - 30 * s:.0f},{base - 120 * s:.0f} '
                 f'L{cx - 22 * s:.0f},{base - 124 * s:.0f} C{cx - 4 * s:.0f},{base - 100 * s:.0f} {cx:.0f},{base - 90 * s:.0f} {cx + 2 * s:.0f},{base - 112 * s:.0f} '
                 f'L{cx + 12 * s:.0f},{base - 112 * s:.0f} C{cx + 10 * s:.0f},{base - 70 * s:.0f} {cx + 8 * s:.0f},{base - 40 * s:.0f} {cx + 9 * s:.0f},{base} Z"/>')
        return f'<g fill="{fill}">{blobs}{trunk}</g>'

    # lattice (pinjrakari) for the shop window
    wx, wy, ww, wh = 104, 382, 128, 84
    lattice = []
    for i in range(1, 6):
        x = wx + ww * i / 6
        lattice.append(f'<line x1="{x:.1f}" y1="{wy}" x2="{x:.1f}" y2="{wy + wh}"/>')
    for j in range(1, 4):
        y = wy + wh * j / 4
        lattice.append(f'<line x1="{wx}" y1="{y:.1f}" x2="{wx + ww}" y2="{y:.1f}"/>')
    for i in range(6):
        for j in range(4):
            cx = wx + ww * (i + .5) / 6; cy = wy + wh * (j + .5) / 4
            lattice.append(f'<path d="M{cx:.1f},{cy - 6:.1f} L{cx + 6:.1f},{cy:.1f} L{cx:.1f},{cy + 6:.1f} L{cx - 6:.1f},{cy:.1f} Z" fill="none"/>')

    planks = "".join(f'<line x1="{x}" y1="352" x2="{x}" y2="500"/>' for x in range(78, 336, 14))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0C2620"/><stop offset=".55" stop-color="#08140F"/><stop offset="1" stop-color="#060907"/></linearGradient>
  <radialGradient id="moonglow"><stop offset="0" stop-color="#CFF3DF" stop-opacity=".22"/><stop offset="1" stop-color="#CFF3DF" stop-opacity="0"/></radialGradient>
  <radialGradient id="spill" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#F2A93B" stop-opacity=".42"/><stop offset=".6" stop-color="#F2A93B" stop-opacity=".1"/><stop offset="1" stop-color="#F2A93B" stop-opacity="0"/></radialGradient>
  <linearGradient id="win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE0A3"/><stop offset=".55" stop-color="#F6B04A"/><stop offset="1" stop-color="#C7741D"/></linearGradient>
  <linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121915"/><stop offset="1" stop-color="#0C110E"/></linearGradient>
  <linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E3D36"/><stop offset="1" stop-color="#1A2420"/></linearGradient>
  <radialGradient id="lamp" cx=".5" cy="0" r="1"><stop offset="0" stop-color="#FFE6B0" stop-opacity=".28"/><stop offset="1" stop-color="#FFE6B0" stop-opacity="0"/></radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".6" stop-color="#060907" stop-opacity="0"/><stop offset="1" stop-color="#060907" stop-opacity=".85"/></linearGradient>
</defs>
<rect width="{w}" height="{h}" fill="url(#sky)"/>
{stars}
<circle cx="790" cy="104" r="130" fill="url(#moonglow)"/>
<circle cx="790" cy="104" r="30" fill="#EAF4EE"/><circle cx="803" cy="95" r="27" fill="#0C231D"/>
<path d="{far_d}" fill="#10231C"/>
{"".join(caps)}
<path d="{mid_d}" fill="#0B1813"/>
{chinar(40, hz + 6, .55, "#0A1612")}{chinar(700, hz + 4, .45, "#0A1612")}{chinar(640, hz + 6, .35, "#0A1612")}
<rect y="{hz}" width="{w}" height="{h - hz}" fill="#070C0A"/>
<path d="{road}" fill="url(#road)"/>
<path d="M300,{h} L{vx - 8},{hz}" stroke="#2A322E" stroke-width="2"/><path d="M{w - 80},{h} L{vx + 8},{hz}" stroke="#2A322E" stroke-width="2"/>
{"".join(dashes)}
<ellipse cx="190" cy="506" rx="260" ry="54" fill="url(#spill)"/>
<!-- the shop -->
<g>
  <rect x="70" y="352" width="268" height="148" fill="#2A1F17"/>
  <g stroke="#201710" stroke-width="2">{planks}</g>
  <path d="M46,356 L362,356 L316,284 L92,284 Z" fill="url(#roof)"/>
  <g stroke="#3B4C44" stroke-width="2" opacity=".8">{"".join(f'<line x1="{92 + i * 22.4:.0f}" y1="284" x2="{46 + i * 31.6:.0f}" y2="356"/>' for i in range(1, 10))}</g>
  <path d="M92,284 L316,284" stroke="#4A5C53" stroke-width="3"/>
  <path d="M176,284 L204,262 L232,284 Z" fill="#24302A"/>
  <rect x="{wx - 6}" y="{wy - 6}" width="{ww + 12}" height="{wh + 12}" rx="3" fill="#1B130D"/>
  <rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="url(#win)"/>
  <g stroke="#7A4614" stroke-width="2" opacity=".75">{"".join(lattice)}</g>
  <rect x="{wx + 10}" y="{wy + wh - 30}" width="50" height="20" rx="5" fill="#0B1310" stroke="#22D47C" stroke-width="1.5"/>
  <text x="{wx + 35}" y="{wy + wh - 15.5}" text-anchor="middle" font-family="Archivo" font-weight="800" font-size="11.5" letter-spacing="1.2" fill="#22D47C">OPEN</text>
  <rect x="254" y="386" width="54" height="114" fill="#160F0A"/>
  <rect x="258" y="390" width="46" height="110" fill="#22180F"/>
  <rect x="280" y="392" width="2" height="106" fill="#F2A93B" opacity=".55"/>
  <rect x="88" y="320" width="232" height="30" rx="8" fill="#0D1310" stroke="rgba(255,255,255,.18)"/>
  <circle cx="102" cy="335" r="3.5" fill="#E26D5C"/><circle cx="114" cy="335" r="3.5" fill="#F2A93B"/><circle cx="126" cy="335" r="3.5" fill="#22D47C"/>
  <text x="140" y="340" font-family="JetBrains Mono" font-size="13" fill="#B7C3BC">yourbusiness.com</text>
  <rect x="62" y="498" width="284" height="6" fill="#1A130E"/>
</g>
<!-- street lamp -->
<path d="M410,506 L410,318 Q410,304 424,304 L446,304" stroke="#2C3531" stroke-width="5" fill="none"/>
<path d="M434,306 L462,306 L456,316 L440,316 Z" fill="#3A453F"/>
<path d="M440,316 L456,316 L520,506 L376,506 Z" fill="url(#lamp)"/>
<circle cx="448" cy="317" r="4" fill="#FFE6B0"/>
<rect width="{w}" height="{h}" fill="url(#fade)"/>
</svg>'''


def boteh(x, y, s, fill, accent):
    """One paisley: a teardrop whose tip curls over."""
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<path d="M0,30 C-18,30 -26,10 -18,-6 C-10,-22 8,-30 16,-44 C20,-34 18,-22 12,-14 C24,-6 22,30 0,30 Z" fill="{fill}"/>'
            f'<path d="M0,22 C-10,22 -15,10 -10,0 C-6,-8 2,-12 6,-18 C8,-10 6,-6 4,-2 C12,4 10,22 0,22 Z" fill="none" stroke="{accent}" stroke-width="2.2"/>'
            f'<circle cx="0" cy="10" r="3.4" fill="{accent}"/></g>')


def kani(w=520, h=380) -> str:
    rows = []
    for j, y in enumerate(range(50, h - 60, 66)):
        for i, x in enumerate(range(-20 + (j % 2) * 38, w + 40, 76)):
            fill = "#8E2A30" if (i + j) % 3 else "#1F5F5A"
            acc = "#E0B35A"
            rows.append(boteh(x, y, .78, fill, acc))
    vines = "".join(f'<path d="M0,{y + 34} C{w * .25},{y + 22} {w * .5},{y + 46} {w * .75},{y + 34} S{w},{y + 22} {w + 10},{y + 34}" '
                    f'stroke="#B98F45" stroke-width="1.4" fill="none" opacity=".55"/>' for y in range(50, h - 60, 66))
    border = (f'<rect y="{h - 64}" width="{w}" height="64" fill="#6E1F25"/>'
              + "".join(boteh(x, h - 30, .5, "#E9DDC7", "#E0B35A") for x in range(18, w + 30, 44))
              + f'<rect y="{h - 66}" width="{w}" height="3" fill="#E0B35A"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice">'
            f'<rect width="{w}" height="{h}" fill="#EDE2CC"/>{vines}{"".join(rows)}{border}</svg>')


if __name__ == "__main__":
    (OUT / "night-road.svg").write_text(night_road())
    (OUT / "kani.svg").write_text(kani())
    print("art written")
