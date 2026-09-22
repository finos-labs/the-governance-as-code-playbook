# Building the PDF book (exact match to the original print book)

Regenerates `governance-as-code-playbook.pdf` from the markdown source in `docs/`, matching the original navy cover, colophon, colored tables, and print typography exactly.

## Requirements

- [pandoc](https://pandoc.org/) (tested with 3.1.3)
- A LaTeX distribution with `xelatex` (TeX Live / BasicTeX is fine)
- Python 3
- TeX Gyre fonts (bundled with virtually every TeX Live install, including BasicTeX)

## Usage

Copy all the files in this folder to a `scripts/` directory in the repo root, then run from the repo root (the directory containing `docs/`):

```bash
./scripts/build-pdf.sh docs governance-as-code-playbook.pdf scripts/book-template.latex
```

## Important: where the design lives

Plain markdown has no concept of colors, fonts, or a cover page — GitHub-flavored
tables carry zero styling metadata. All of that design information had to be
re-encoded directly into this build pipeline, matching the original document
exactly:

- **Cover page & colophon** — hardcoded directly in `book-template.latex`
  (title text, subtitle, colophon paragraphs, and the three image assets:
  `cover-art.png`, `logo-aifund.png`, `logo-finos.png`).
- **Per-table row colors** — hardcoded in `balance-tables.lua`, keyed by each
  table's exact row/column-count signature (e.g. `"13x3"` for the components
  table). The colors were extracted directly from the original, verified
  print-book document to guarantee an exact match.
- **Code block shading** — a `CodeBlock` handler in `balance-tables.lua` wraps
  every fenced code block in a cream-colored `shaded` box (via the `framed`
  package), matching the original's Consolas-on-cream styling.
- **Font** — TeX Gyre Pagella (a Palatino-style book serif bundled with every
  standard TeX Live install), replacing the plainer DejaVu Serif used in an
  earlier draft of this pipeline.

**If you add a new table to the guide**, its colors won't carry over
automatically — you'll need to add a new entry to the `ROW_COLORS` table in
`balance-tables.lua`, keyed by its row/column signature, or it will render
uncolored (which is a safe, ugly-but-correct fallback, not a crash).

## Regenerating after content changes

Any edit to existing chapter text picks up automatically. Structural changes
(new tables, a new cover subtitle, etc.) require a matching update to
`balance-tables.lua` or `book-template.latex` as described above.
