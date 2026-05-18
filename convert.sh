#!/bin/bash
# md-quick-convert — convert .md files to DOCX / PDF / HTML from Finder
# https://github.com/sebastiendelarque/md-quick-convert

set -u

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

INSTALL_DIR="$HOME/.local/share/md-quick-convert"
CSS="$INSTALL_DIR/style.css"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# --- Language detection (FR vs EN, default EN) ---
SYS_LANG=$(defaults read -g AppleLocale 2>/dev/null || echo "en_US")
case "$SYS_LANG" in
  fr*) LANG_FR=1 ;;
  *)   LANG_FR=0 ;;
esac

t() {
  local key="$1"
  if [ "$LANG_FR" = "1" ]; then
    case "$key" in
      no_file_title)    echo "Aucun fichier" ;;
      no_file_msg)      echo "Sélectionne un fichier .md dans le Finder." ;;
      dialog_title)     echo "Convertir Markdown" ;;
      dialog_prompt)    echo "Format de sortie :" ;;
      btn_ok)           echo "Convertir" ;;
      btn_cancel)       echo "Annuler" ;;
      err_not_found)    echo "fichier introuvable" ;;
      err_not_md)       echo "pas un markdown" ;;
      err_pandoc_miss)  echo "pandoc manquant (brew install pandoc)" ;;
      err_chrome_miss)  echo "Chrome introuvable (requis pour PDF)" ;;
      err_chrome_fail)  echo "Chrome a échoué" ;;
      notif_done)       echo "fichier(s) en" ;;
      notif_errors)     echo "erreurs (voir alerte)" ;;
      alert_errors)     echo "Erreurs de conversion" ;;
      ok)               echo "converti(s)" ;;
    esac
  else
    case "$key" in
      no_file_title)    echo "No file" ;;
      no_file_msg)      echo "Select a .md file in the Finder." ;;
      dialog_title)     echo "Convert Markdown" ;;
      dialog_prompt)    echo "Output format:" ;;
      btn_ok)           echo "Convert" ;;
      btn_cancel)       echo "Cancel" ;;
      err_not_found)    echo "file not found" ;;
      err_not_md)       echo "not a markdown file" ;;
      err_pandoc_miss)  echo "pandoc missing (brew install pandoc)" ;;
      err_chrome_miss)  echo "Chrome not found (required for PDF)" ;;
      err_chrome_fail)  echo "Chrome failed" ;;
      notif_done)       echo "file(s) to" ;;
      notif_errors)     echo "errors (see alert)" ;;
      alert_errors)     echo "Conversion errors" ;;
      ok)               echo "converted" ;;
    esac
  fi
}

# --- Preflight ---
if [ $# -eq 0 ]; then
  osascript -e "display alert \"$(t no_file_title)\" message \"$(t no_file_msg)\" as critical"
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  osascript -e "display alert \"pandoc\" message \"$(t err_pandoc_miss)\" as critical"
  exit 1
fi

# --- Format dialog ---
FORMAT=$(osascript <<EOF
set choix to choose from list {"DOCX", "PDF", "HTML"} ¬
  with title "$(t dialog_title)" ¬
  with prompt "$(t dialog_prompt)" ¬
  default items {"PDF"} ¬
  OK button name "$(t btn_ok)" ¬
  cancel button name "$(t btn_cancel)"
if choix is false then return "CANCEL"
return item 1 of choix
EOF
)

[ "$FORMAT" = "CANCEL" ] && exit 0

case "$FORMAT" in
  DOCX) EXT="docx" ;;
  PDF)  EXT="pdf"  ;;
  HTML) EXT="html" ;;
  *) exit 0 ;;
esac

ERRORS=""
LAST_OUT=""
COUNT=0

for SRC in "$@"; do
  if [ ! -f "$SRC" ]; then
    ERRORS="$ERRORS\n• $(basename "$SRC") : $(t err_not_found)"
    continue
  fi

  case "$SRC" in
    *.md|*.markdown|*.mdown|*.mkd) : ;;
    *) ERRORS="$ERRORS\n• $(basename "$SRC") : $(t err_not_md)"; continue ;;
  esac

  DIR=$(dirname "$SRC")
  BASE=$(basename "$SRC")
  NAME="${BASE%.*}"
  OUT="$DIR/$NAME.$EXT"

  case "$EXT" in
    docx)
      if ! pandoc "$SRC" -o "$OUT" --from gfm 2>/tmp/mdqc.err; then
        ERRORS="$ERRORS\n• $BASE : $(head -1 /tmp/mdqc.err)"
        continue
      fi
      ;;

    html)
      if ! pandoc "$SRC" -s --from gfm --metadata title="$NAME" \
            --css="$CSS" --embed-resources --standalone \
            -o "$OUT" 2>/tmp/mdqc.err; then
        ERRORS="$ERRORS\n• $BASE : $(head -1 /tmp/mdqc.err)"
        continue
      fi
      ;;

    pdf)
      TMP_HTML=$(mktemp -t mdqc).html
      if ! pandoc "$SRC" -s --from gfm --metadata title="$NAME" \
            --css="$CSS" --embed-resources --standalone \
            -o "$TMP_HTML" 2>/tmp/mdqc.err; then
        ERRORS="$ERRORS\n• $BASE : $(head -1 /tmp/mdqc.err)"
        rm -f "$TMP_HTML"
        continue
      fi
      if [ ! -x "$CHROME" ]; then
        ERRORS="$ERRORS\n• $BASE : $(t err_chrome_miss)"
        rm -f "$TMP_HTML"
        continue
      fi
      if ! "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
            --print-to-pdf="$OUT" "file://$TMP_HTML" \
            >/dev/null 2>/tmp/mdqc.err; then
        ERRORS="$ERRORS\n• $BASE : $(t err_chrome_fail)"
        rm -f "$TMP_HTML"
        continue
      fi
      rm -f "$TMP_HTML"
      ;;
  esac

  LAST_OUT="$OUT"
  COUNT=$((COUNT + 1))
done

if [ -n "$LAST_OUT" ]; then
  open -R "$LAST_OUT"
  open "$LAST_OUT"
fi

if [ -n "$ERRORS" ]; then
  osascript -e "display notification \"$COUNT $(t ok), $(t notif_errors)\" with title \"$(t dialog_title)\""
  osascript -e "display alert \"$(t alert_errors)\" message \"$(printf "%b" "$ERRORS")\""
else
  osascript -e "display notification \"$COUNT $(t notif_done) .$EXT\" with title \"$(t dialog_title)\" sound name \"Glass\""
fi
