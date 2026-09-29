import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/lucide-static/icons"

LOGOS = {
    "light": "assets/qudelta-logo-dark.png",
    "dark": "assets/qudelta-logo-light.png",
}


def icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


src = (HERE / "poster.src.html").read_text()
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
for theme, logo in LOGOS.items():
    html = src.replace("{{theme}}", theme).replace("{{logo}}", f'<img src="{logo}" alt="Qudelta Studios">')
    (HERE / f"poster-{theme}.html").write_text(html)
    print(f"built poster-{theme}.html")
