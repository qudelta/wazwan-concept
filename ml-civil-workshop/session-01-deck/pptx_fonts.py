"""Static fonts for the editable PowerPoint, cut from the official Google Fonts variable fonts.

PowerPoint cannot use a variable font's width axis, so every weight/width the deck uses becomes its own
static TrueType font. Naming follows Google Fonts' static releases: weights 400/700 form the RIBBI family
("Archivo" Regular + Bold); every other weight is its own family ("Archivo Black", "Archivo SemiCondensed
ExtraBold", ...). The same TTFs are embedded in the .pptx (as EOT, the format PowerPoint embeds) and shipped
for installation.

Usage: python3 pptx_fonts.py <Archivo[wdth,wght].ttf> <JetBrainsMono[wght].ttf> <out_dir>
"""
import struct
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# (family, style, source, axes)
FACES = [
    ("Archivo", "Regular", "archivo", {"wght": 400, "wdth": 100}),
    ("Archivo", "Bold", "archivo", {"wght": 700, "wdth": 100}),
    ("Archivo Medium", "Regular", "archivo", {"wght": 500, "wdth": 100}),
    ("Archivo SemiBold", "Regular", "archivo", {"wght": 600, "wdth": 100}),
    ("Archivo ExtraBold", "Regular", "archivo", {"wght": 800, "wdth": 100}),
    ("Archivo Black", "Regular", "archivo", {"wght": 900, "wdth": 100}),
    ("Archivo SemiCondensed", "Regular", "archivo", {"wght": 400, "wdth": 87.5}),
    ("Archivo SemiCondensed", "Bold", "archivo", {"wght": 700, "wdth": 87.5}),
    ("Archivo SemiCondensed ExtraBold", "Regular", "archivo", {"wght": 800, "wdth": 87.5}),
    ("Archivo SemiCondensed Black", "Regular", "archivo", {"wght": 900, "wdth": 87.5}),
    ("JetBrains Mono", "Regular", "mono", {"wght": 400}),
    ("JetBrains Mono", "Bold", "mono", {"wght": 700}),
    ("JetBrains Mono Medium", "Regular", "mono", {"wght": 500}),
]


def file_name(family: str, style: str) -> str:
    return f"{family.replace(' ', '')}-{style}.ttf"


def set_names(font: TTFont, family: str, style: str) -> None:
    ps = f"{family.replace(' ', '')}-{style}"
    full = family if style == "Regular" else f"{family} {style}"
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            name.removeNames(nameID=rec.nameID)
    for nid, val in ((1, family), (2, style), (3, f"Qudelta-static:{ps}"), (4, full), (6, ps)):
        name.setName(val, nid, 3, 1, 0x409)   # Windows / Unicode BMP / English
        name.setName(val, nid, 1, 0, 0)       # Mac Roman
    bold = style == "Bold"
    os2 = font["OS/2"]
    os2.fsSelection = (os2.fsSelection & ~0b1100001) | (0b100000 if bold else 0b1000000)  # BOLD or REGULAR bit
    font["head"].macStyle = 1 if bold else 0
    os2.fsType = 0  # OFL fonts are installable; PowerPoint checks this before embedding


def eot(ttf_path: Path) -> bytes:
    """Wrap a TrueType font as uncompressed Embedded OpenType (version 0x00020001)."""
    data = ttf_path.read_bytes()
    f = TTFont(str(ttf_path))
    os2, name = f["OS/2"], f["name"]

    def n(nid):
        s = name.getDebugName(nid) or ""
        b = s.encode("utf-16-le")
        return struct.pack("<H", len(b)) + b

    panose = os2.panose
    pan = bytes([panose.bFamilyType, panose.bSerifStyle, panose.bWeight, panose.bProportion, panose.bContrast,
                 panose.bStrokeVariation, panose.bArmStyle, panose.bLetterForm, panose.bMidline, panose.bXHeight])
    italic = 1 if os2.fsSelection & 1 else 0
    body = struct.pack("<I", 0x00020001) + struct.pack("<I", 0)        # Version, Flags (no compression/XOR)
    body += pan + struct.pack("<BB", 1, italic)                       # PANOSE, Charset (DEFAULT), Italic
    body += struct.pack("<I", os2.usWeightClass) + struct.pack("<HH", os2.fsType, 0x504C)
    body += struct.pack("<IIII", os2.ulUnicodeRange1, os2.ulUnicodeRange2, os2.ulUnicodeRange3, os2.ulUnicodeRange4)
    body += struct.pack("<II", os2.ulCodePageRange1, os2.ulCodePageRange2)
    body += struct.pack("<I", f["head"].checkSumAdjustment) + struct.pack("<IIII", 0, 0, 0, 0)
    body += struct.pack("<H", 0) + n(1) + struct.pack("<H", 0) + n(2) + struct.pack("<H", 0) + n(5)
    body += struct.pack("<H", 0) + n(4) + struct.pack("<H", 0) + struct.pack("<H", 0)   # Padding5, RootStringSize 0
    header_len = 8 + len(body)
    return struct.pack("<II", header_len + len(data), len(data)) + body + data


def build(archivo_vf: str, mono_vf: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    src = {"archivo": archivo_vf, "mono": mono_vf}
    for family, style, key, axes in FACES:
        font = instancer.instantiateVariableFont(TTFont(src[key]), axes, updateFontNames=False)
        set_names(font, family, style)
        font.save(out / file_name(family, style))
        print("built", file_name(family, style))


if __name__ == "__main__":
    build(*sys.argv[1:4])
