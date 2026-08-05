"""
make_ascii_svg.py — convert scripts/prepped-source.png into a
monochrome, self-typing ASCII-art SVG.

Usage:
    python scripts/make_ascii_svg.py

Writes:
    avi-ascii.svg   (rename the output path / variable to your liking)
"""
from PIL import Image

# --- tunables -----------------------------------------------------------
SOURCE_IMAGE = "scripts/prepped-source.png"
OUTPUT_SVG = "avi-ascii.svg"

GRID_COLS = 100          # characters per row
GRID_ROWS = 53           # rows

FONT_SIZE = 8            # px, monospace
CHAR_W = FONT_SIZE * 0.6 # approx monospace advance width
LINE_H = FONT_SIZE * 1.0

FILL_COLOR = "#c9d1d9"   # single light-gray fill (monochrome on purpose)
BG_COLOR = "transparent"

# bright (sparse) -> dark (dense). Leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"

ROW_STAGGER = 0.05        # seconds between each row starting its wipe
WIPE_DURATION = 0.35       # seconds for a single row's reveal
# -------------------------------------------------------------------------


def brightness_to_char(value: int) -> str:
    """value: 0 (black) .. 255 (white) -> character from RAMP."""
    # invert: bright pixel (255) should map to the *sparse* end of RAMP
    idx = int((255 - value) / 255 * (len(RAMP) - 1))
    return RAMP[idx]


def image_to_ascii_rows(path: str, cols: int, rows: int) -> list[str]:
    img = Image.open(path).convert("L").resize((cols, rows))
    pixels = list(img.getdata())
    ascii_rows = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        ascii_rows.append("".join(brightness_to_char(p) for p in row_pixels))
    return ascii_rows


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(ascii_rows: list[str]) -> str:
    width = GRID_COLS * CHAR_W
    height = GRID_ROWS * LINE_H

    defs = []
    uses = []

    for i, row_text in enumerate(ascii_rows):
        clip_id = f"clip{i}"
        y = (i + 1) * LINE_H - 2

        # clipPath: a rect that grows from width 0 to full width
        defs.append(f'''
    <clipPath id="{clip_id}">
      <rect x="0" y="{i * LINE_H}" height="{LINE_H}" width="0">
        <animate attributeName="width" from="0" to="{width}"
                 begin="{i * ROW_STAGGER:.2f}s" dur="{WIPE_DURATION}s"
                 fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>
      </rect>
    </clipPath>''')

        uses.append(f'''
    <text x="0" y="{y}" clip-path="url(#{clip_id})"
          font-family="Menlo, Consolas, monospace" font-size="{FONT_SIZE}"
          fill="{FILL_COLOR}" xml:space="preserve">{escape_xml(row_text)}</text>''')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}">
  <defs>{"".join(defs)}
  </defs>
  <g>{"".join(uses)}
  </g>
</svg>'''
    return svg


if __name__ == "__main__":
    rows = image_to_ascii_rows(SOURCE_IMAGE, GRID_COLS, GRID_ROWS)
    svg_content = build_svg(rows)
    with open(OUTPUT_SVG, "w") as f:
        f.write(svg_content)
    print(f"Wrote {OUTPUT_SVG} ({GRID_COLS}x{GRID_ROWS} grid)")
