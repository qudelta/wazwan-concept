"""Builds 'The rest of the menu' carousel (1080x1350) and story set (1080x1920) from *.src.html.

Illustrations are {{svg:name}} (assets/name.svg, drawn by gen_art.py). Icons are written as {{i:name}} (Phosphor duotone) or {{i:name:bold}} and inlined as SVG.
Usage: python3 build.py <path to @phosphor-icons/core/assets>
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1])


def icon(m: re.Match) -> str:
    name, weight = m.group(1), m.group(2) or "duotone"
    svg = (ICONS / weight / f"{name}-{weight}.svg").read_text().strip()
    return svg.replace("<svg ", f'<svg class="ic" aria-hidden="true" ', 1)


def art(m: re.Match) -> str:
    svg = (HERE / "assets" / f"{m.group(1)}.svg").read_text().strip()
    return re.sub(r' width="\d+" height="\d+"', ' class="art"', svg, count=1)


def foot(m: re.Match) -> str:
    """{{foot:N/T}}: logo, page count and progress bars."""
    n, t = int(m.group(1)), int(m.group(2))
    bars = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(t))
    arrow = "{{i:arrow-right:bold}}" if n < t else ""
    return (f'<footer class="sf"><img src="assets/qudelta-logo-light.png" alt="Qudelta Studios">'
            f'<div class="prog"><span class="pn"><b>{n:02d}</b> / {t}</span><div class="bars">{bars}</div>{arrow}</div></footer>')


for src in ("carousel", "story"):
    if not (HERE / f"{src}.src.html").exists():
        continue
    html = (HERE / f"{src}.src.html").read_text()
    html = re.sub(r"\{\{foot:(\d+)/(\d+)\}\}", foot, html)
    html = re.sub(r"\{\{svg:([a-z0-9-]+)\}\}", art, html)
    html = re.sub(r"\{\{i:([a-z0-9-]+)(?::([a-z]+))?\}\}", icon, html)
    assert "{{" not in html, src
    (HERE / f"{src}.html").write_text(html)
    print(f"built {src}.html")
