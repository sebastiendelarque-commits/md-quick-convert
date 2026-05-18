#!/bin/bash
# md-quick-convert installer
# https://github.com/sebastiendelarque/md-quick-convert

set -e

REPO_RAW="https://raw.githubusercontent.com/sebastiendelarque/md-quick-convert/main"
INSTALL_DIR="$HOME/.local/share/md-quick-convert"
SERVICE_NAME="Markdown Convert.workflow"
SERVICE_DIR="$HOME/Library/Services/$SERVICE_NAME"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}==>${NC} $1"; }
warn()  { echo -e "${YELLOW}!! ${NC} $1"; }
fail()  { echo -e "${RED}xx ${NC} $1"; exit 1; }

# --- Detect run mode (curl pipe vs local clone) ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" 2>/dev/null && pwd )"
if [ -f "$SCRIPT_DIR/convert.sh" ] && [ -d "$SCRIPT_DIR/$SERVICE_NAME" ]; then
  MODE="local"
  info "Local install mode (from $SCRIPT_DIR)"
else
  MODE="remote"
  info "Remote install mode (downloading from GitHub)"
fi

# --- Dependency check ---
info "Checking dependencies..."

if ! command -v pandoc >/dev/null 2>&1; then
  warn "pandoc not found."
  if command -v brew >/dev/null 2>&1; then
    read -p "Install pandoc via Homebrew? [Y/n] " yn
    case "$yn" in
      [Nn]*) fail "pandoc is required. Install it manually: brew install pandoc" ;;
      *)     brew install pandoc ;;
    esac
  else
    fail "pandoc is required. Install Homebrew first (https://brew.sh) then: brew install pandoc"
  fi
fi

if [ ! -d "/Applications/Google Chrome.app" ]; then
  warn "Google Chrome not detected — required for PDF export (DOCX and HTML will still work)."
fi

# --- Stage files ---
TMP=$(mktemp -d -t mdqc)
trap "rm -rf $TMP" EXIT

if [ "$MODE" = "local" ]; then
  cp "$SCRIPT_DIR/convert.sh" "$TMP/convert.sh"
  cp "$SCRIPT_DIR/style.css" "$TMP/style.css"
  cp -R "$SCRIPT_DIR/$SERVICE_NAME" "$TMP/$SERVICE_NAME"
else
  info "Downloading files..."
  curl -fsSL "$REPO_RAW/convert.sh" -o "$TMP/convert.sh" || fail "Failed to download convert.sh"
  curl -fsSL "$REPO_RAW/style.css"  -o "$TMP/style.css"  || fail "Failed to download style.css"
  mkdir -p "$TMP/$SERVICE_NAME/Contents"
  curl -fsSL "$REPO_RAW/Markdown%20Convert.workflow/Contents/Info.plist"      -o "$TMP/$SERVICE_NAME/Contents/Info.plist"
  curl -fsSL "$REPO_RAW/Markdown%20Convert.workflow/Contents/document.wflow"  -o "$TMP/$SERVICE_NAME/Contents/document.wflow"
fi

# --- Install script + CSS ---
info "Installing script to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$TMP/convert.sh" "$INSTALL_DIR/convert.sh"
cp "$TMP/style.css"  "$INSTALL_DIR/style.css"
chmod +x "$INSTALL_DIR/convert.sh"

# --- Install Quick Action with path substitution ---
info "Installing Finder Quick Action"
rm -rf "$SERVICE_DIR"
mkdir -p "$SERVICE_DIR/Contents"
cp "$TMP/$SERVICE_NAME/Contents/Info.plist" "$SERVICE_DIR/Contents/Info.plist"

# Substitute __INSTALL_PATH__ with actual path (escape for sed)
ESCAPED_PATH=$(echo "$INSTALL_DIR" | sed 's|/|\\/|g')
sed "s|__INSTALL_PATH__|$INSTALL_DIR|g" "$TMP/$SERVICE_NAME/Contents/document.wflow" > "$SERVICE_DIR/Contents/document.wflow"

# --- Register service ---
info "Registering with Finder"
/System/Library/CoreServices/pbs -update >/dev/null 2>&1 || true
killall Finder 2>/dev/null || true

echo ""
info "Done. Right-click a .md file in Finder → Services → Convert Markdown…"
echo ""
echo "If the menu entry doesn't appear:"
echo "  System Settings → Keyboard → Keyboard Shortcuts → Services"
echo "  → Files and Folders → enable 'Convert Markdown…'"
