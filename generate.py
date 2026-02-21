#!/usr/bin/env python3
"""
Life Calendar Wallpaper Generator
Generates a "life in weeks" grid wallpaper for macOS.

Edit the CONFIG section below, then run:
    python3 generate.py
"""

from datetime import date
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import sys

# ── CONFIG ────────────────────────────────────────────────────────────────────

BIRTHDAY       = date(2005, 4, 6)
LIFESPAN_YEARS = 90

# M1 MacBook Air native resolution
RESOLUTION     = (2560, 1664)

# Dark theme colors
BG_COLOR       = "#111111"
PAST_COLOR     = "#DEDEDE"   # weeks already lived
FUTURE_COLOR   = "#252525"   # weeks ahead
CURRENT_COLOR  = "#FF6B35"   # the current week (accent)
TEXT_COLOR     = "#4A4A4A"   # year labels

# Grid layout
CELL_SIZE      = 20          # square size in pixels
CELL_GAP       = 3           # gap between squares

OUTPUT_PATH    = os.path.expanduser("~/Pictures/life_calendar.png")
SET_WALLPAPER  = True        # auto-set as wallpaper after generating

# ─────────────────────────────────────────────────────────────────────────────

COLS = LIFESPAN_YEARS  # years across (horizontal)
ROWS = 52              # weeks down (vertical)


def load_font(size):
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_grid(draw, ox, oy, weeks_past, current_week):
    step = CELL_SIZE + CELL_GAP
    for row in range(ROWS):          # row = week within year (0-51)
        for col in range(COLS):      # col = year of life (0-89)
            idx = col * ROWS + row   # = year * 52 + week_within_year
            x = ox + col * step
            y = oy + row * step
            if idx < weeks_past:
                color = PAST_COLOR
            elif idx == current_week:
                color = CURRENT_COLOR
            else:
                color = FUTURE_COLOR
            draw.rectangle([x, y, x + CELL_SIZE, y + CELL_SIZE], fill=color)


def draw_year_labels(draw, ox, oy, font):
    step = CELL_SIZE + CELL_GAP
    for year in range(0, COLS + 1, 10):
        x = ox + year * step
        label = str(year)
        draw.text((x, oy - 8), label, fill=TEXT_COLOR, font=font, anchor="mb")


def main():
    # Ensure output directory exists and remove any existing wallpaper
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)

    today = date.today()
    total_weeks = ROWS * COLS
    weeks_past = (today - BIRTHDAY).days // 7
    current_week = weeks_past  # current week index

    step = CELL_SIZE + CELL_GAP
    grid_w = COLS * step - CELL_GAP
    grid_h = ROWS * step - CELL_GAP

    canvas_w, canvas_h = RESOLUTION

    # Reserve space: 80px top for title, 50px for year labels above grid, 60px bottom for stats
    label_margin_top = 50   # space above grid for year labels
    usable_h = canvas_h - 80 - label_margin_top - 60

    # Center the grid
    ox = (canvas_w - grid_w) // 2
    oy = 80 + label_margin_top + (usable_h - grid_h) // 2

    img = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_grid(draw, ox, oy, weeks_past, current_week)

    label_font = load_font(15)
    draw_year_labels(draw, ox, oy, label_font)

    # Title
    title_font = load_font(24)
    draw.text(
        (canvas_w // 2, 62),
        "life  in  weeks",
        fill=TEXT_COLOR,
        font=title_font,
        anchor="mm",
    )

    # Stats line
    pct = (weeks_past / total_weeks) * 100
    remaining = total_weeks - weeks_past
    stats = (
        f"{weeks_past:,} weeks lived  ·  {remaining:,} remaining  ·  {pct:.1f}% of a {LIFESPAN_YEARS}-year life"
    )
    stats_font = load_font(11)
    draw.text(
        (canvas_w // 2, oy + grid_h + 32),
        stats,
        fill=TEXT_COLOR,
        font=stats_font,
        anchor="mm",
    )

    img.save(OUTPUT_PATH, "PNG")
    print(f"Saved → {OUTPUT_PATH}")
    print(f"{weeks_past} weeks lived  |  {remaining} remaining  |  {pct:.1f}%")

    if SET_WALLPAPER:
        abs_path = os.path.abspath(OUTPUT_PATH)
        # Finder approach works on macOS Sonoma+ and earlier
        script = f'tell application "Finder" to set desktop picture to POSIX file "{abs_path}"'
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if result.returncode == 0:
            print("Wallpaper set.")
        else:
            # Fallback: System Events approach
            script2 = (
                f'tell application "System Events" to tell every desktop '
                f'to set picture to "{abs_path}"'
            )
            result2 = subprocess.run(["osascript", "-e", script2], capture_output=True, text=True)
            if result2.returncode == 0:
                print("Wallpaper set.")
            else:
                print(f"Could not auto-set wallpaper — set it manually in System Settings > Wallpaper")
                print(f"File is at: {abs_path}")


if __name__ == "__main__":
    main()
