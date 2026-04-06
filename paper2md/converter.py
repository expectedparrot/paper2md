"""
paper2md.converter
~~~~~~~~~~~~~~~~~~
Core conversion logic: PDF → Markdown + extracted PNG figures.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Backend = Literal["marker", "pymupdf"]


@dataclass
class ConversionResult:
    """Return value from :func:`convert`."""

    markdown: str
    """Full markdown text with image references like ``![Figure 1](img_1.png)``."""

    images: dict[str, Path]
    """Mapping of normalised name → absolute path, e.g. ``{"img_1.png": Path("/out/img_1.png")}``."""

    output_dir: Path
    """Directory that contains ``paper.md`` and all ``img_*.png`` files."""

    backend_used: str
    """Name of the backend that produced the output."""


def convert(
    pdf_path: str | Path,
    output_dir: str | Path | None = None,
    backend: Backend | Literal["auto"] = "auto",
    dpi: int = 150,
) -> ConversionResult:
    """Convert an academic-paper PDF to Markdown with extracted figures.

    Parameters
    ----------
    pdf_path:
        Path to the source PDF.
    output_dir:
        Directory where ``paper.md`` and ``img_*.png`` files will be written.
        Defaults to a sibling directory named ``<pdf_stem>_md/``.
    backend:
        ``"marker"``  – high-quality, layout-aware (requires ``marker-pdf``).
        ``"pymupdf"`` – fast, lightweight (requires ``pymupdf4llm``).
        ``"auto"``    – try marker first, fall back to pymupdf.
    dpi:
        Resolution used when rasterising figures (pymupdf backend only).

    Returns
    -------
    ConversionResult
    """
    pdf_path = Path(pdf_path).expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_md"
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if backend == "auto":
        backend = _pick_backend()

    if backend == "marker":
        md, raw_images = _run_marker(pdf_path, output_dir)
    else:
        md, raw_images = _run_pymupdf(pdf_path, output_dir, dpi=dpi)

    md, images = _normalise_images(md, raw_images, output_dir)
    md = _sanitise_for_latex(md)

    out_md = output_dir / "paper.md"
    out_md.write_text(md, encoding="utf-8")

    return ConversionResult(
        markdown=md,
        images=images,
        output_dir=output_dir,
        backend_used=backend,
    )


# ---------------------------------------------------------------------------
# LaTeX-safe Unicode replacement
# ---------------------------------------------------------------------------

import unicodedata

# Explicit replacements for common Unicode chars found in academic PDFs.
# Applied first, before the NFKD fallback.
_UNICODE_TO_ASCII: dict[str, str] = {
    "\u2217": "*",       # ∗ ASTERISK OPERATOR
    "\u2018": "'",       # '
    "\u2019": "'",       # '
    "\u201c": "\"",      # "
    "\u201d": "\"",      # "
    "\u2013": "--",      # – EN DASH
    "\u2014": "---",     # — EM DASH
    "\u2026": "...",     # …
    "\u00a0": " ",       # NO-BREAK SPACE
    "\u2002": " ",       # EN SPACE
    "\u2003": " ",       # EM SPACE
    "\u200b": "",        # ZERO WIDTH SPACE
    "\u2009": " ",       # THIN SPACE
    "\u202f": " ",       # NARROW NO-BREAK SPACE
    "\ufeff": "",        # BOM
    "\u2212": "-",       # − MINUS SIGN
    "\u00d7": "x",       # ×
    "\u00b7": ".",       # · MIDDLE DOT
    "\u2022": "-",       # • BULLET
    "\u2032": "'",       # ′ PRIME
    "\u2033": "''",      # ″ DOUBLE PRIME
    "\u2190": "<-",      # ←
    "\u2192": "->",      # →
    "\u2264": "<=",      # ≤
    "\u2265": ">=",      # ≥
    "\u2260": "!=",      # ≠
    "\u2248": "~",       # ≈
    "\u2261": "=",       # ≡
    "\u221e": "inf",     # ∞
    "\u03b1": "alpha",   # α
    "\u03b2": "beta",    # β
    "\u03b3": "gamma",   # γ
    "\u03b4": "delta",   # δ
    "\u03b5": "epsilon", # ε
    "\u03b6": "zeta",    # ζ
    "\u03b7": "eta",     # η
    "\u03b8": "theta",   # θ
    "\u03b9": "iota",    # ι
    "\u03ba": "kappa",   # κ
    "\u03bb": "lambda",  # λ
    "\u03bc": "mu",      # μ
    "\u03bd": "nu",      # ν
    "\u03be": "xi",      # ξ
    "\u03c0": "pi",      # π
    "\u03c1": "rho",     # ρ
    "\u03c3": "sigma",   # σ
    "\u03c4": "tau",     # τ
    "\u03c5": "upsilon", # υ
    "\u03c6": "phi",     # φ
    "\u03d5": "phi",     # ϕ
    "\u03c7": "chi",     # χ
    "\u03c8": "psi",     # ψ
    "\u03c9": "omega",   # ω
    "\u0393": "Gamma",   # Γ
    "\u0394": "Delta",   # Δ
    "\u0398": "Theta",   # Θ
    "\u039b": "Lambda",  # Λ
    "\u039e": "Xi",      # Ξ
    "\u03a0": "Pi",      # Π
    "\u03a3": "Sigma",   # Σ
    "\u03a6": "Phi",     # Φ
    "\u03a8": "Psi",     # Ψ
    "\u03a9": "Omega",   # Ω
}


def _sanitise_for_latex(md: str) -> str:
    """Replace all non-ASCII characters with safe ASCII equivalents.

    Uses an explicit map for common academic-paper symbols, then falls back
    to NFKD decomposition, and finally drops anything unresolvable.
    """
    out: list[str] = []
    for ch in md:
        if ord(ch) < 128:
            out.append(ch)
            continue
        # 1. Explicit map
        mapped = _UNICODE_TO_ASCII.get(ch)
        if mapped is not None:
            out.append(mapped)
            continue
        # 2. NFKD decomposition
        decomposed = unicodedata.normalize("NFKD", ch)
        ascii_chars = decomposed.encode("ascii", "ignore").decode("ascii")
        if ascii_chars:
            out.append(ascii_chars)
        else:
            # 3. Drop
            out.append("")
    return "".join(out)


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------

def _pick_backend() -> Backend:
    try:
        import marker  # noqa: F401
        return "marker"
    except ImportError:
        pass
    try:
        import pymupdf4llm  # noqa: F401
        return "pymupdf"
    except ImportError:
        raise ImportError(
            "No supported backend found. "
            "Install one of:\n"
            "  pip install marker-pdf   (recommended)\n"
            "  pip install pymupdf4llm  (lightweight fallback)"
        )


# ---------------------------------------------------------------------------
# marker backend
# ---------------------------------------------------------------------------

def _run_marker(pdf_path: Path, output_dir: Path) -> tuple[str, list[Path]]:
    """Run marker-pdf and return (markdown_text, list_of_extracted_image_paths)."""
    # marker ≥ 1.0 API
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        models = create_model_dict()
        converter = PdfConverter(artifact_dict=models)
        rendered = converter(str(pdf_path))
        md_text, _, images = text_from_rendered(rendered)

        # images is a dict[str, PIL.Image]. Save them to output_dir.
        saved: list[Path] = []
        for name, img in images.items():
            dest = output_dir / name
            img.save(dest)
            saved.append(dest)

        return md_text, saved

    except (ImportError, AttributeError):
        pass

    # marker < 1.0 API
    from marker.convert import convert_single_pdf
    from marker.models import load_all_models

    models = load_all_models()
    full_text, images, _ = convert_single_pdf(str(pdf_path), models)

    saved: list[Path] = []
    for name, img in (images or {}).items():
        dest = output_dir / name
        img.save(dest)
        saved.append(dest)

    return full_text, saved


# ---------------------------------------------------------------------------
# pymupdf backend
# ---------------------------------------------------------------------------

def _run_pymupdf(pdf_path: Path, output_dir: Path, dpi: int) -> tuple[str, list[Path]]:
    """Use pymupdf4llm for text + PyMuPDF directly for image extraction."""
    import pymupdf4llm
    import fitz  # PyMuPDF

    # -- markdown text -------------------------------------------------------
    md_text: str = pymupdf4llm.to_markdown(str(pdf_path))

    # -- figure extraction ---------------------------------------------------
    doc = fitz.open(str(pdf_path))
    saved: list[Path] = []
    raw_index = 0

    for page_num, page in enumerate(doc):
        img_list = page.get_images(full=True)
        for img_info in img_list:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]  # e.g. "png", "jpeg"

            # Rasterise via fitz for a clean PNG at the requested DPI
            rect = page.get_image_bbox(img_info)
            if rect is None or rect.is_empty:
                # Fallback: save raw bytes, convert extension
                raw_index += 1
                tmp_path = output_dir / f"_raw_{raw_index}.{img_ext}"
                tmp_path.write_bytes(img_bytes)
                # Convert to PNG with fitz
                png_path = output_dir / f"_raw_{raw_index}.png"
                _to_png(tmp_path, png_path)
                tmp_path.unlink(missing_ok=True)
                saved.append(png_path)
            else:
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                clip = page.rect  # full page clip — images without exact bbox
                pix = page.get_pixmap(matrix=mat, clip=rect)
                raw_index += 1
                png_path = output_dir / f"_raw_{raw_index}.png"
                pix.save(str(png_path))
                saved.append(png_path)

    doc.close()

    # pymupdf4llm inserts image placeholders as markdown image links.
    # We'll strip those and re-inject our own after normalisation.
    return md_text, saved


def _to_png(src: Path, dest: Path) -> None:
    """Convert any image file to PNG via Pillow (if available) or fitz."""
    try:
        from PIL import Image
        with Image.open(src) as im:
            im.save(dest, "PNG")
    except ImportError:
        import fitz
        pix = fitz.Pixmap(str(src))
        pix.save(str(dest))


# ---------------------------------------------------------------------------
# Image normalisation: rename to img_1.png, img_2.png, …
# ---------------------------------------------------------------------------

_IMG_REF_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)",
    re.IGNORECASE,
)


def _normalise_images(
    md: str,
    raw_images: list[Path],
    output_dir: Path,
) -> tuple[str, dict[str, Path]]:
    """Rename extracted images to img_N.png and patch all references in markdown."""

    # Build a mapping: original filename → new canonical name
    rename_map: dict[str, str] = {}  # old basename → img_N.png
    images_out: dict[str, Path] = {}

    for i, img_path in enumerate(raw_images, start=1):
        new_name = f"img_{i}.png"
        new_path = output_dir / new_name

        if img_path.resolve() != new_path.resolve():
            if img_path.suffix.lower() == ".png":
                shutil.move(str(img_path), str(new_path))
            else:
                _to_png(img_path, new_path)
                img_path.unlink(missing_ok=True)

        rename_map[img_path.name] = new_name
        images_out[new_name] = new_path

    # Patch markdown references
    def _replace(m: re.Match) -> str:
        old_path = m.group("path")
        old_name = Path(old_path).name
        new_name = rename_map.get(old_name, old_name)
        return f"![{m.group('alt')}]({new_name})"

    md = _IMG_REF_RE.sub(_replace, md)

    # For pymupdf backend the markdown may not contain image refs at all;
    # append a figure gallery at the end so agents can access every image.
    referenced = {Path(m.group("path")).name for m in _IMG_REF_RE.finditer(md)}
    missing = [name for name in images_out if name not in referenced]
    if missing:
        gallery = "\n\n---\n\n## Extracted Figures\n\n"
        for name in missing:
            label = name.replace("_", " ").replace(".png", "").title()
            gallery += f"![{label}]({name})\n\n"
        md += gallery

    return md, images_out
