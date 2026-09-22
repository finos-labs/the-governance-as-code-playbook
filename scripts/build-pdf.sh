#!/usr/bin/env bash
# Build the print/PDF version of the Governance-as-Code Playbook from its
# markdown source in docs/. Run from the repository root.
set -euo pipefail

DOCS_DIR="${1:-docs}"
OUT="${2:-governance-as-code-playbook.pdf}"
TEMPLATE="${3:-book-template.latex}"
TMP="$(mktemp -d)"

# Directory this script itself lives in -- the cover art and logo PNGs are
# expected alongside it (e.g. scripts/cover-art.png), regardless of what
# directory the script is actually invoked from.
ASSET_DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Concatenate chapters in order, converting the raw <img> tags used in the
#    source (sized for GitHub rendering) into pandoc's markdown image syntax
#    with a width attribute. Image paths are rewritten to be relative to the
#    directory this script is run from (DOCS_DIR/images/...), since the PDF
#    engine resolves \includegraphics paths relative to its own working
#    directory, not pandoc's --resource-path.
: > "$TMP/body.md"
for f in "$DOCS_DIR"/*.md; do
  DOCS_DIR="$DOCS_DIR" python3 - "$f" >> "$TMP/body.md" <<'PY'
import re, sys, os
docs_dir = os.environ["DOCS_DIR"]
text = open(sys.argv[1], encoding="utf-8").read()
def fix(m):
    src, alt, style = m.group(1), m.group(2), m.group(3)
    w = re.search(r'width:\s*([\d.]+)in', style)
    width = f"{float(w.group(1))/6.3*100:.0f}%" if w else "80%"
    return f"![{alt}]({docs_dir}/{src}){{ width={width} }}"
text = re.sub(r'<img src="([^"]+)" alt="([^"]*)" style="([^"]+)"\s*/?>', fix, text)
print(text)
print()
PY
done

# 2. Locate the TeX Gyre Pagella font files by their exact path on this
#    machine, rather than relying on xelatex resolving the font by name.
#    On macOS specifically, xelatex asks the OS's own font database (Font
#    Book/CoreText) to resolve font names -- and fonts installed via tlmgr
#    into the TeX Live tree are never registered there, even though
#    kpsewhich (TeX's own file finder) can see them fine. Loading by exact
#    path sidesteps OS font registration entirely, on every platform.
PAGELLA_REGULAR="$(kpsewhich texgyrepagella-regular.otf 2>/dev/null || true)"
if [ -z "$PAGELLA_REGULAR" ]; then
  echo "ERROR: TeX Gyre Pagella not found. Install it with: sudo tlmgr install tex-gyre" >&2
  exit 1
fi
FONT_DIR="$(dirname "$PAGELLA_REGULAR")"

# 3. Build the PDF with a minimal custom template (avoids relying on the
#    lmodern LaTeX package, which some minimal TeX Live installs omit)
pandoc "$TMP/body.md" \
  --from markdown+smart-implicit_figures \
  --template="$TEMPLATE" \
  --pdf-engine=xelatex \
  --toc --toc-depth=2 \
  --lua-filter="$(dirname "$0")/balance-tables.lua" \
  -M title="The Governance-as-Code Playbook" \
  -M subtitle="Adopting FINOS AIGF for Agentic AI in Financial Services" \
  -M date="First Edition (Draft)" \
  -M fontdir="$FONT_DIR" \
  -M assetdir="$ASSET_DIR" \
  -o "$OUT"

rm -rf "$TMP"
echo "Built $OUT"
