#!/bin/bash
# Install dependencies, generate the life calendar wallpaper,
# and register a LaunchAgent to auto-refresh every Monday at 9 AM.
# Run once: bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST=~/Library/LaunchAgents/com.lifecalendar.refresh.plist

echo "Installing Pillow..."
pip3 install --quiet pillow

echo "Generating wallpaper..."
python3 "$SCRIPT_DIR/generate.py"

echo "Setting up weekly auto-refresh (every Monday at 9 AM)..."
mkdir -p ~/Library/LaunchAgents
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lifecalendar.refresh</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_DIR/generate.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

# Unload first in case it was already registered, then load fresh
launchctl bootout gui/$(id -u) "$PLIST" 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$PLIST"

echo ""
echo "Done. Wallpaper will refresh every Monday at 9 AM."
