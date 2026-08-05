"""
fetch_contributions.py — scrape the public GitHub contributions
calendar fragment (no auth / token needed) and write a normalized
JSON file with raw days + derived stats.

Usage:
    python scripts/fetch_contributions.py

Writes:
    data/contributions.json
"""
import json
import re
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup

# --- EDIT THIS -----------------------------------------------------------
USERNAME = "prajvxl"
# -------------------------------------------------------------------------

URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_PATH = "data/contributions.json"


def fetch_html() -> str:
    resp = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme bot)"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub's markup has shifted between <td> and <rect> over time;
    # handle whichever the fragment currently returns.
    cells = soup.select("td.ContributionCalendar-day") or soup.select("rect[data-date]")

    for cell in cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue
        level_attr = cell.get("data-level")
        if level_attr is not None:
            level = int(level_attr)
        else:
            # fall back to parsing the class, e.g. "ContributionCalendar-day"
            # with a level encoded via fill-level classes in older markup
            m = re.search(r"level-(\d)", " ".join(cell.get("class", [])))
            level = int(m.group(1)) if m else 0

# The count lives in a separate <tool-tip> element elsewhere in the
        # page, linked to this cell via for="<cell id>".
        count = 0
        cell_id = cell.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": cell_id}) if cell_id else None
        text_source = tooltip.get_text() if tooltip else cell.get("aria-label", "")
        m = re.search(r"(\d+)\s+contribution", text_source or "")
        if m:
            count = int(m.group(1))
        days.append({"date": date_str, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # current streak: consecutive days with count > 0, ending today (or yesterday)
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


if __name__ == "__main__":
    html = fetch_html()
    days = parse_days(html)
    if not days:
        raise SystemExit(
            "No contribution cells found — GitHub may have changed its markup, "
            "or the username is wrong / has no public activity."
        )
    stats = derive_stats(days)
    out = {"username": USERNAME, "days": days, "stats": stats}

    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUTPUT_PATH}: {len(days)} days, {stats['total_last_year']} total contributions")
