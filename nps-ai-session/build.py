import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/lucide-static/icons"

DARK_TEXT = "assets/qudelta-logo-dark.png"
LIGHT_TEXT = "assets/qudelta-logo-light.png"
# logo on the page background, and logo on the "Session by" band (dark band in light theme, green band in dark theme)
LOGOS = {
    "light": {"logo": DARK_TEXT, "logo_band": LIGHT_TEXT},
    "dark": {"logo": LIGHT_TEXT, "logo_band": DARK_TEXT},
}
SOURCES = {"poster.src.html": "poster", "poster-b.src.html": "poster-b"}


def icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


for src_name, prefix in SOURCES.items():
    src = (HERE / src_name).read_text()
    src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
    for theme, logos in LOGOS.items():
        html = src.replace("{{theme}}", theme)
        for key, path in logos.items():
            html = html.replace("{{" + key + "}}", f'<img src="{path}" alt="Qudelta Studios">')
        (HERE / f"{prefix}-{theme}.html").write_text(html)
        print(f"built {prefix}-{theme}.html")
