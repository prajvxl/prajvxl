"""
render_heatmap_svg.py — render data/contributions.json as a
53-week x 7-day grid of animated, colored boxes (GitHub-style).

Usage:
    python scripts/render_heatmap_svg.py

Writes:
    contrib-heatmap.svg
"""
import json
from datetime import datetime

INPUT_PATH = "data/contributions.json"
OUTPUT_SVG = "contrib-heatmap.svg"

CELL = 11          # box size in px
GAP = 3             # spacing between boxes
RADIUS = 2          # rounded corner
LEGEND_H = 24
FOOTER_H = 28
MARGIN = 16

# none -> brightest (level 5 is a neon top end, not real GitHub data)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

STAGGER = 0.015     # seconds between each box's reveal (diagonal cascade)
REVEAL_DUR = 0.4


def load_data():
    with open(INPUT_PATH) as f:
        return json.load(f)


def group_into_weeks(days: list[dict]) -> list[list[dict]]:
    """GitHub's calendar is column-major: each column is one week (Sun-Sat)."""
    weeks = []
    current_week = []
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        weekday = (dt.weekday() + 1) % 7  # convert Mon=0 -> Sun=0
        if weekday == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        current_week.append(d)
    if current_week:
        weeks.append(current_week)
    return weeks[-53:]  # last 53 weeks


def build_svg(data: dict) -> str:
    weeks = group_into_weeks(data["days"])
    stats = data["stats"]

    n_weeks = len(weeks)
    grid_w = n_weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)

    width = grid_w + MARGIN * 2
    height = grid_h + LEGEND_H + FOOTER_H + MARGIN * 2

    boxes = []
    delay_index = 0
    for w, week in enumerate(weeks):
        for d in week:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            weekday = (dt.weekday() + 1) % 7
            x = MARGIN + w * (CELL + GAP)
            y = MARGIN + weekday * (CELL + GAP)
            level = min(d["level"], len(PALETTE) - 1)
            color = PALETTE[level]

            # diagonal stagger: delay grows with (week + weekday)
            delay = (w + weekday) * STAGGER

            boxes.append(f'''
    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RADIUS}"
          fill="{color}" opacity="0"
          style="animation: revealBox {REVEAL_DUR}s ease-out {delay:.3f}s forwards;">
      <title>{d['count']} contributions on {d['date']}</title>
    </rect>''')

    legend_y = MARGIN + grid_h + 20
    legend_items = []
    lx = MARGIN
    legend_items.append(f'<text x="{lx}" y="{legend_y}" font-family="Menlo, Consolas, monospace" font-size="11" fill="#8b949e">Less</text>')
    lx += 32
    for color in PALETTE:
        legend_items.append(f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{color}"/>')
        lx += CELL + GAP
    legend_items.append(f'<text x="{lx + 6}" y="{legend_y}" font-family="Menlo, Consolas, monospace" font-size="11" fill="#8b949e">More</text>')

    footer_y = legend_y + FOOTER_H
    footer_text = f"{stats['total_last_year']:,} contributions in the last year - current streak {stats['current_streak']} - longest streak {stats['longest_streak']}"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <style>
    @keyframes revealBox {{
      from {{ opacity: 0; transform: translateY(-8px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
  <rect width="{width}" height="{height}" fill="#0d1117"/>
  <g>{"".join(boxes)}
  </g>
  {"".join(legend_items)}
  <text x="{MARGIN}" y="{footer_y}" font-family="Menlo, Consolas, monospace" font-size="12" fill="#c9d1d9">{footer_text}</text>
</svg>'''
    return svg


if __name__ == "__main__":
    data = load_data()
    svg_content = build_svg(data)
    with open(OUTPUT_SVG, "w") as f:
        f.write(svg_content)
    print(f"Wrote {OUTPUT_SVG}")
