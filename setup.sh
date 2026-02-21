#!/bin/bash
# Install dependencies and generate the life calendar wallpaper.
# Run once: bash setup.sh
# Re-run anytime to regenerate (e.g. after a birthday or to refresh).

set -e

echo "Installing Pillow..."
pip3 install --quiet pillow

echo "Generating wallpaper..."
python3 "$(dirname "$0")/generate.py"

echo ""
echo "To auto-refresh weekly, add this to your crontab (crontab -e):"
echo "  0 9 * * 1 python3 $(pwd)/generate.py"
