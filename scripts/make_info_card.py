"""
make_info_card.py — hand-authored neofetch-style SVG panel.
Edit the CONTENT list below with your own info.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame, no animation

Writes:
    info-card.svg
"""
import os

OUTPUT_SVG = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

FONT = "Menlo, Consolas, monospace"
FONT_SIZE = 14
LINE_H = 26
PADDING_TOP = 56          # space for the title bar
LABEL_COLOR = "#39d353"   # green, like a real neofetch key
VALUE_COLOR = "#c9d1d9"
BAR_COLOR = "#161b22"
BG_COLOR = "#0d1117"

# --- EDIT THIS with your own info ---------------------------------------
CONTENT = [
    ("Now",        "3rd-year student, learning full-stack web dev"),
    ("Prev",       "Building a strong foundation in computer science and programming"),
    ("Stack",      "Python, JS/TS, React, Java, C++, JavaScript, Git & GitHub"),
    ("Highlights", "Building projects and strengthening problem-solving skills"),
]
# -------------------------------------------------------------------------

WIDTH = 490
HEIGHT = PADDING_TOP + LINE_H * len(CONTENT) + 24
STAGGER = 0.12  # seconds between each line's fade-in

def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def build_svg() -> str:
    lines_svg = []
    for i, (label, value) in enumerate(CONTENT):
        y = PADDING_TOP + i * LINE_H
        delay = i * STAGGER

        anim_style = "" if STATIC else f'''
        style="animation: fadeSlide 0.5s ease-out {delay:.2f}s both;"'''

        lines_svg.append(f'''
    <text x="24" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE}"{anim_style}>
      <tspan fill="{LABEL_COLOR}">{label}:</tspan>
      <tspan fill="{VALUE_COLOR}" dx="8">{escape_xml(value)}</tspan>
    </text>''')

    keyframes = "" if STATIC else '''
    <style>
      @keyframes fadeSlide {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
      }
    </style>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
  {keyframes}
  <rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{BG_COLOR}"/>
  <rect width="{WIDTH}" height="32" rx="8" fill="{BAR_COLOR}"/>
  <rect y="24" width="{WIDTH}" height="8" fill="{BAR_COLOR}"/>
  <circle cx="20" cy="16" r="6" fill="#ff5f56"/>
  <circle cx="40" cy="16" r="6" fill="#ffbd2e"/>
  <circle cx="60" cy="16" r="6" fill="#27c93f"/>
  {"".join(lines_svg)}
</svg>'''
    return svg


if __name__ == "__main__":
    with open(OUTPUT_SVG, "w") as f:
        f.write(build_svg())
    print(f"Wrote {OUTPUT_SVG}" + (" (static)" if STATIC else ""))
