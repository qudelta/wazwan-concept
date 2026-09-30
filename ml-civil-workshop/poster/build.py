import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "node_modules/lucide-static/icons"

TOTAL_SLIDES = 11
LOGOS = {
    "light": "assets/qudelta-logo-dark.png",
    "dark": "assets/qudelta-logo-light.png",
}


def icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class)="[^"]*"', "", m.group(0)), svg, count=1)
    return re.sub(r"\s+", " ", svg).strip()


def footer(n: int, theme: str) -> str:
    bars = "".join(f'<i class="{"on" if k <= n else ""}"></i>' for k in range(1, TOTAL_SLIDES + 1))
    last = n == TOTAL_SLIDES
    # the final slide sits on the green band, so it always uses the dark-text logo
    logo = LOGOS["light"] if last else LOGOS[theme]
    left = (f'<span class="partner">Technology partner<img src="{logo}" alt="Qudelta Studios"></span>'
            if last else f'<img src="{logo}" alt="Qudelta Studios">')
    arrow = "" if last else icon("arrow-right")
    return (f'<footer class="sf">{left}<div class="prog"><span class="pn"><b>{n:02d}</b> / {TOTAL_SLIDES}</span>'
            f'<span class="bars">{bars}</span>{arrow}</div></footer>')


def render(src_name: str, out_prefix: str) -> None:
    src = (HERE / src_name).read_text()
    src = re.sub(r"\{\{i:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), src)
    for theme, logo in LOGOS.items():
        html = src.replace("{{theme}}", theme).replace("{{logo}}", f'<img src="{logo}" alt="Qudelta Studios">')
        html = re.sub(r"\{\{foot:(\d+)\}\}", lambda m: footer(int(m.group(1)), theme), html)
        (HERE / f"{out_prefix}-{theme}.html").write_text(html)
        print(f"built {out_prefix}-{theme}.html")


render("poster.src.html", "poster")
render("poster-minimal.src.html", "poster-minimal")
render("web-landscape.src.html", "web-landscape")
render("web-portrait.src.html", "web-portrait")
render("carousel.src.html", "carousel")
