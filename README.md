# paper2md

Convert academic-paper PDFs to clean Markdown with extracted PNG figures — ready for LLM / agent ingestion.

```
paper.pdf  →  paper_md/
               ├── paper.md      # full text with ![Figure N](img_N.png) references
               ├── img_1.png
               ├── img_2.png
               └── …
```

## Install

```bash
# Lightweight (PyMuPDF backend only)
pip install paper2md

# With marker-pdf for academic-layout awareness (recommended)
pip install "paper2md[marker]"

# With Reducto cloud API
pip install "paper2md[reducto]"
```

## Quick start

### CLI

```bash
# Auto-selects best available backend (prefers marker)
paper2md paper.pdf

# Explicit backend, custom output dir
paper2md paper.pdf --backend pymupdf --output ./out

# Adjust figure DPI (pymupdf backend only, default 150)
paper2md paper.pdf --backend pymupdf --dpi 200

# Print markdown to stdout
paper2md paper.pdf --print
```

### Python API

```python
from paper2md.converter import convert

result = convert("paper.pdf")

result.markdown      # full markdown string
result.images        # {"img_1.png": Path(...), ...}
result.output_dir    # Path to folder with paper.md + PNGs
result.backend_used  # "marker" or "pymupdf"
```

Choose a specific backend:

```python
result = convert("paper.pdf", backend="pymupdf")
result = convert("paper.pdf", backend="marker")
result = convert("paper.pdf", output_dir="/tmp/my_paper")
```

### Reducto (cloud API)

The Reducto backend is a separate module (not wired into the main `convert()` function):

```bash
pip install "paper2md[reducto]"
export REDUCTO_API_KEY=your_key_here
```

```python
from paper2md.reducto import convert_with_reducto
from pathlib import Path

md, images = convert_with_reducto(Path("paper.pdf"), Path("./out"))
```

## How it works

1. The chosen backend converts the PDF to Markdown text and extracts any embedded images.
2. All extracted figures are renamed to `img_1.png`, `img_2.png`, etc. and saved to the output directory.
3. Image references (`![…](…)`) in the Markdown are rewritten to match the canonical filenames.
4. If the backend produced images that aren't referenced in the text (common with pymupdf), they are appended in an **Extracted Figures** section so no figure is lost.
5. Non-ASCII characters common in academic PDFs (Greek letters, math symbols, special dashes) are transliterated to ASCII equivalents for LaTeX compatibility.
6. The final `paper.md` + all PNGs are written to the output directory.

## Backends

| Backend | Quality | Speed | Cost | Install |
|---------|---------|-------|------|---------|
| **marker** | Best | Slow | Free | `pip install "paper2md[marker]"` |
| **pymupdf** | Good | Fast | Free | bundled |
| **Reducto** | Best | Fast | Paid | `pip install "paper2md[reducto]"` + API key |

**marker-pdf** is recommended for academic papers — it handles multi-column layouts, LaTeX equations, figure captions, and tables well. It is the default backend when installed.

**pymupdf** is bundled and works out of the box. Good for simple layouts.

**Reducto** is a cloud API option for high-volume or high-quality needs.
