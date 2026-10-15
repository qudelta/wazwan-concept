import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/lucide-static/icons"
LOGO_LIGHT = "../poster/assets/qudelta-logo-light.png"  # light text, for dark slides
NOTEBOOK_LINK = "Link shared in the session chat"


def icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


src = (HERE / "deck.src.html").read_text()
total = src.count('<section class="slide')
src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
src = src.replace("{{logo-light}}", f'<img src="{LOGO_LIGHT}" alt="Qudelta Studios">')
src = src.replace("{{logo-light-big}}", f'<img src="{LOGO_LIGHT}" alt="Qudelta Studios">')
src = src.replace("{{notebook_link}}", NOTEBOOK_LINK)

# number every slide; content slides get the running header
parts = src.split('<section class="slide')
out = [parts[0]]
for n, part in enumerate(parts[1:], 1):
    head = (f'<header class="top"><div class="c">AI &amp; ML for Civil Engineers<span>Session 01</span></div>'
            f'<div class="n"><b>{n:02d}</b> / {total}</div></header>')
    out.append(part.replace("{{top}}", head, 1))
html = '<section class="slide'.join(out)
assert "{{" not in html, re.findall(r"\{\{[^}]*\}\}", html)
(HERE / "deck.html").write_text(html)
print("built deck.html with", total, "slides")
