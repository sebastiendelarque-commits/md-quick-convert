# md-quick-convert

> Right-click any `.md` file in Finder → convert to **DOCX**, **PDF** or **HTML** in one click. No LaTeX, no terminal, no fuss.

[🇫🇷 Lire en français](#français) · [☕ Buy me a coffee](https://buymeacoffee.com/YOUR_HANDLE)

![demo](assets/demo.png)

---

## Why

Existing pandoc-based Quick Actions for macOS are either archived ([dsanson/Pandoc-Droplets-and-Services](https://github.com/dsanson/Pandoc-Droplets-and-Services), 2026) or require a heavy LaTeX install (~80 MB) just to export a PDF.

**md-quick-convert** is different:

- ✅ **One Finder menu entry** with a format chooser popup (DOCX / PDF / HTML)
- ✅ **PDF without LaTeX** — uses Chrome headless under the hood
- ✅ **Editorial CSS** for HTML and PDF output (serif body, A4 margins, sober palette)
- ✅ **Multi-select supported** — convert a whole folder of `.md` at once
- ✅ **Bilingual UI** — auto-detects FR / EN system language
- ✅ **~200 lines of bash** — auditable, hackable, no Electron

## Install (one-liner)

```bash
curl -fsSL https://raw.githubusercontent.com/sebastiendelarque/md-quick-convert/main/install.sh | bash
```

Or clone and run locally:

```bash
git clone https://github.com/sebastiendelarque/md-quick-convert
cd md-quick-convert
./install.sh
```

## Requirements

| Tool | Required for | Install |
|------|--------------|---------|
| [pandoc](https://pandoc.org) | All conversions | `brew install pandoc` |
| [Google Chrome](https://www.google.com/chrome/) | PDF only | Already installed for most users |

The installer checks dependencies and offers to install pandoc via Homebrew.

## Usage

1. Right-click a `.md` file in Finder (or select several)
2. **Services** menu → **Convert Markdown…**
3. Choose **DOCX**, **PDF** or **HTML** in the popup
4. The converted file opens automatically, next to the source

## Customize the styling

The CSS used for HTML and PDF output lives at:

```
~/.local/share/md-quick-convert/style.css
```

Edit it freely — changes apply to the next conversion.

## Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
rm -rf ~/Library/Services/"Markdown Convert.workflow"
rm -rf ~/.local/share/md-quick-convert
killall Finder
```

## How it works

- The Finder Quick Action is an Automator workflow (`.workflow` bundle) registered in `~/Library/Services/`
- It calls `convert.sh`, which runs `pandoc` for DOCX / HTML
- For PDF, `pandoc` produces an intermediate HTML, then **Chrome `--headless --print-to-pdf`** renders it (avoids the LaTeX dependency)
- A native AppleScript `choose from list` provides the format picker

## Support

If this saved you time, consider [buying me a coffee](https://buymeacoffee.com/YOUR_HANDLE) ☕

## License

[MIT](LICENSE) — do whatever you want.

---

## Français

> Clic droit sur un fichier `.md` dans le Finder → conversion **DOCX**, **PDF** ou **HTML** en un clic. Sans LaTeX, sans terminal.

### Pourquoi

Les Quick Actions pandoc existantes pour macOS sont soit archivées, soit imposent un LaTeX de ~80 Mo juste pour exporter un PDF. **md-quick-convert** :

- ✅ **Une seule entrée** dans le menu Finder avec popup de choix (DOCX / PDF / HTML)
- ✅ **PDF sans LaTeX** — via Chrome headless
- ✅ **CSS éditoriale** soignée pour HTML et PDF (serif, A4, palette sobre)
- ✅ **Sélection multiple** — convertit un dossier entier de `.md`
- ✅ **Interface bilingue** — détection auto FR / EN
- ✅ **~200 lignes de bash** — auditable, modifiable, zéro Electron

### Installation

```bash
curl -fsSL https://raw.githubusercontent.com/sebastiendelarque/md-quick-convert/main/install.sh | bash
```

### Utilisation

1. Clic droit sur un `.md` (sélection multiple OK)
2. **Services** → **Convert Markdown…**
3. Choisir le format dans le popup
4. Le fichier converti s'ouvre automatiquement à côté du source

### Personnaliser le style

Édite `~/.local/share/md-quick-convert/style.css` — les changements s'appliquent à la prochaine conversion.

### Désinstaller

```bash
./uninstall.sh
```

### Soutenir

Si l'outil te fait gagner du temps, [offre-moi un café](https://buymeacoffee.com/YOUR_HANDLE) ☕
