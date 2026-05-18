#!/bin/bash
# md-quick-convert uninstaller

set -e

INSTALL_DIR="$HOME/.local/share/md-quick-convert"
SERVICE_DIR="$HOME/Library/Services/Markdown Convert.workflow"

echo "==> Removing Quick Action..."
rm -rf "$SERVICE_DIR"

echo "==> Removing script + CSS..."
rm -rf "$INSTALL_DIR"

echo "==> Refreshing Finder services..."
/System/Library/CoreServices/pbs -update >/dev/null 2>&1 || true
killall Finder 2>/dev/null || true

echo "Done. pandoc was not removed (uninstall with: brew uninstall pandoc)."
