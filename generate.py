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
CELL_SIZE      = 13          # square size in pixels
CELL_GAP       = 2           # gap between squares

OUTPUT_PATH    = os.path.expanduser("~/Desktop/life_calendar.png")
SET_WALLPAPER  = True        # auto-set as wallpaper after generating

# ─────────────────────────────────────────────────────────────────────────────

COLS = 52   # weeks per row
ROWS = LIFESPAN_YEARS


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
    for row in range(ROWS):
        for col in range(COLS):
            idx = row * COLS + col
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
    for year in range(0, ROWS + 1, 10):
        y = oy + year * step
        label = str(year)
        draw.text((ox - 10, y), label, fill=TEXT_COLOR, font=font, anchor="rm")


def main():
    today = date.today()
    total_weeks = ROWS * COLS
    weeks_past = (today - BIRTHDAY).days // 7
    current_week = weeks_past  # current week index

    step = CELL_SIZE + CELL_GAP
    grid_w = COLS * step - CELL_GAP
    grid_h = ROWS * step - CELL_GAP

    canvas_w, canvas_h = RESOLUTION

    # Reserve space: 90px top for title, 60px bottom for stats
    usable_h = canvas_h - 90 - 60
    label_margin = 36   # space to the left for year labels

    # Center the grid horizontally (accounting for left label margin)
    ox = (canvas_w - grid_w + label_margin) // 2
    oy = 90 + (usable_h - grid_h) // 2

    img = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_grid(draw, ox, oy, weeks_past, current_week)

    label_font = load_font(11)
    draw_year_labels(draw, ox, oy, label_font)

    # Title
    title_font = load_font(15)
    draw.text(
        (canvas_w // 2, 48),
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
        script = (
            f'tell application "System Events" to tell every desktop '
            f'to set picture to "{OUTPUT_PATH}"'
        )
        result = subprocess.run(["osascript", "-e", script], capture_output=True)
        if result.returncode == 0:
            print("Wallpaper set.")
        else:
            print(f"Could not auto-set wallpaper — set it manually in System Settings > Wallpaper")
            print(f"File is at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
