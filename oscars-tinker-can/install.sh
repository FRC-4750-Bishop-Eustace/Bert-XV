#!/bin/bash
# Installs only local files. Does not start REV, run motors, or download packages.
set -euo pipefail
if [[ "$(uname -s)" != Linux || "$(uname -m)" != aarch64 ]]; then
  echo "Run this on the Raspberry Pi with 64-bit Raspberry Pi OS."
  exit 1
fi
if [[ "$EUID" == 0 ]]; then
  echo "Run as your Pi desktop user without sudo. The launcher belongs to your desktop user."
  exit 1
fi
if [[ "$#" -gt 1 || ( "$#" -eq 1 && "$1" != --autostart ) ]]; then
  echo "Usage: bash install.sh [--autostart]"
  exit 1
fi
command -v python3 >/dev/null || { echo "Python 3 is required."; exit 1; }
command -v chromium >/dev/null || { echo "Chromium is required."; exit 1; }
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.local/share/oscars-tinker-can"
CONFIG="$HOME/.config/oscars-tinker-can"
STATE="$HOME/.local/state/oscars-tinker-can"
mkdir -p "$DEST/web" "$CONFIG" "$STATE" "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/Desktop"
cp "$SOURCE/core.py" "$SOURCE/service.py" "$SOURCE/README.md" "$SOURCE/launcher.json" "$SOURCE/examples.json" "$SOURCE/icon.svg" "$DEST/"
cp "$SOURCE/web/index.html" "$SOURCE/web/styles.css" "$SOURCE/web/app.js" "$DEST/web/"
if [[ ! -f "$CONFIG/launcher.json" ]]; then
  cp "$SOURCE/launcher.json" "$CONFIG/launcher.json"
  chmod 600 "$CONFIG/launcher.json"
fi
python3 "$DEST/service.py" --check
cat > "$HOME/.local/bin/oscar-launcher" <<WRAPPER
#!/bin/bash
exec /usr/bin/python3 "$DEST/service.py" "\$@"
WRAPPER
chmod 700 "$HOME/.local/bin/oscar-launcher"
cat > "$HOME/.local/share/applications/oscars-tinker-can.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Oscar's Tinker Can
Comment=Touchscreen component testing launchpad
Exec=$HOME/.local/bin/oscar-launcher
Icon=$DEST/icon.svg
Terminal=false
Categories=Development;Education;
DESKTOP
cp "$HOME/.local/share/applications/oscars-tinker-can.desktop" "$HOME/Desktop/oscars-tinker-can.desktop"
chmod 755 "$HOME/Desktop/oscars-tinker-can.desktop"
if command -v gio >/dev/null; then
  gio set "$HOME/Desktop/oscars-tinker-can.desktop" metadata::trusted true >/dev/null 2>&1 || true
fi
if [[ "${1:-}" == --autostart ]]; then
  mkdir -p "$HOME/.config/autostart"
  cp "$HOME/.local/share/applications/oscars-tinker-can.desktop" "$HOME/.config/autostart/oscars-tinker-can.desktop"
  echo "The launchpad will open after desktop login. REV waits for your button press."
fi
echo
echo "Installed Oscar's Tinker Can. Double-click its new Pi desktop icon."
echo "Configuration: $CONFIG/launcher.json"
echo "Saved settings and logs: $STATE"
echo "Before the first REV launch, stop any older manually launched REV terminal."
if [[ ! -x "$HOME/.local/share/frc-java25/bin/java" ]]; then
  echo "NOTE: The existing Java 25 runtime was not found at the default path. Update the REV backend command in Configuration."
fi
echo "No packages were downloaded. Existing custom launcher configuration was preserved."
