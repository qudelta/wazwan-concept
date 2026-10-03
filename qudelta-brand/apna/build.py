import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/lucide-static/icons"
TOTAL = 8
LOGOS = {"light": "assets/qudelta-logo-dark.png", "dark": "assets/qudelta-logo-light.png"}


def icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


def footer(n: int, theme: str) -> str:
    bars = "".join(f'<i class="{"on" if k <= n else ""}"></i>' for k in range(1, TOTAL + 1))
    last = n == TOTAL
    # the last slide signs off with its own large logo, so the footer drops it
    left = "<span></span>" if last else f'<img src="{LOGOS[theme]}" alt="Qudelta Studios">'
    arrow = "" if last else icon("arrow-right")
    return (f'<footer class="sf">{left}<div class="prog"><span class="pn"><b>{n:02d}</b> / {TOTAL}</span>'
            f'<span class="bars">{bars}</span>{arrow}</div></footer>')


src = (HERE / "carousel.src.html").read_text()
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
for theme in LOGOS:
    html = src.replace("{{theme}}", theme)
    html = re.sub(r"\{\{foot:(\d+)\}\}", lambda m: footer(int(m.group(1)), theme), html)
    (HERE / f"carousel-{theme}.html").write_text(html)
    print(f"built carousel-{theme}.html")
