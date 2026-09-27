#!/usr/bin/env python3
"""Embed fonts/*.woff2 into theme.css as base64, between the FONTS:GENERATED markers.

The community installer only fetches theme.css and manifest.json, and Obsidian's
theme policy bans network requests, so the fonts have to live inside the stylesheet.
Usage: python3 scripts/embed-fonts.py
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+2000-206F,U+2074,U+20AC,U+20BD,"
         "U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
CYRILLIC = "U+0400-045F,U+0490-0491,U+2116"
FACES = [  # family, file, weight, style, unicode-range
    ("EB Garamond", "ebgaramond-latin-400.woff2", "400", "normal", LATIN),
    ("EB Garamond", "ebgaramond-cyrillic-400.woff2", "400", "normal", CYRILLIC),
]

blocks = []
for family, name, weight, style, urange in FACES:
    data = base64.b64encode((ROOT / "fonts" / name).read_bytes()).decode()
    quoted = f'"{family}"' if " " in family else family  # stylelint: quotes only when needed
    blocks.append(
        f'@font-face {{\n  font-family: {quoted};\n'
        f'  src: url("data:font/woff2;base64,{data}") format("woff2");\n'
        f"  font-weight: {weight};\n  font-style: {style};\n  font-display: swap;\n"
        f"  unicode-range: {urange};\n}}\n")

css = (ROOT / "theme.css").read_text()
start = "/* FONTS:GENERATED:START — produced by scripts/embed-fonts.py, do not hand-edit */"
end = "/* FONTS:GENERATED:END */"
css = re.sub(re.escape(start) + r".*?" + re.escape(end),
             lambda _: start + "\n" + "\n".join(blocks) + "\n" + end, css, flags=re.S)
(ROOT / "theme.css").write_text(css)
print(f"embedded {len(FACES)} faces")
