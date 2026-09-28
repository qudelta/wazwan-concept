import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/lucide-static/icons"

GREEN = "#00D26A"

Q_MARK = f"""<svg class="q" viewBox="98 71 356 356" aria-hidden="true">
<defs><mask id="qd-cut"><rect x="0" y="0" width="600" height="600" fill="#fff"/><polygon points="280,220 580,520 280,520" fill="#000"/></mask></defs>
<circle cx="275" cy="248" r="150" fill="none" stroke="{GREEN}" stroke-width="50" mask="url(#qd-cut)"/>
<polygon points="280,255 448,423 280,423" fill="{GREEN}"/>
</svg>"""

COLON = f"""<svg class="colon" viewBox="0 0 12 26" aria-hidden="true"><circle cx="6.4" cy="8.6" r="4.4" fill="{GREEN}"/><circle cx="5.6" cy="21.2" r="4.4" fill="#C9CFCC"/></svg>"""

LOGO = f'<span class="qd" aria-label="Qudelta Studios">{Q_MARK}UDELTA{COLON}STUDIOS</span>'


def icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


src = (HERE / "poster.src.html").read_text()
src = src.replace("{{logo}}", LOGO)
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
(HERE / "poster.html").write_text(src)
print("built poster.html")
