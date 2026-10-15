"""Builds the 'Andhe ko chashma / Kashmir andha nahi hai' square posts (1080x1080) in dark and light themes."""
from pathlib import Path

HERE = Path(__file__).parent
LOGOS = {"light": "assets/qudelta-logo-dark.png", "dark": "assets/qudelta-logo-light.png"}

src = (HERE / "post.src.html").read_text()
for theme, logo in LOGOS.items():
    html = src.replace("{{theme}}", theme).replace("{{logo}}", f'<img src="{logo}" alt="Qudelta Studios">')
    assert "{{" not in html
    (HERE / f"post-{theme}.html").write_text(html)
    print(f"built post-{theme}.html")
