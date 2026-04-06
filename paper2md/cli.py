"""
paper2md CLI
~~~~~~~~~~~~
Usage:
    paper2md paper.pdf
    paper2md paper.pdf --output ./out --backend pymupdf --dpi 200
    paper2md paper.pdf --backend marker
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="paper2md",
        description="Convert an academic-paper PDF to Markdown + PNG figures.",
    )
    parser.add_argument("pdf", type=Path, help="Path to the PDF file.")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        metavar="DIR",
        help="Output directory (default: <pdf_stem>_md/ next to the PDF).",
    )
    parser.add_argument(
        "--backend", "-b",
        choices=["auto", "marker", "pymupdf"],
        default="auto",
        help="Conversion backend (default: auto).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Figure rasterisation DPI for the pymupdf backend (default: 150).",
    )
    parser.add_argument(
        "--print", "-p",
        dest="print_md",
        action="store_true",
        help="Print the generated Markdown to stdout.",
    )

    args = parser.parse_args()

    from .converter import convert

    try:
        result = convert(
            pdf_path=args.pdf,
            output_dir=args.output,
            backend=args.backend,
            dpi=args.dpi,
        )
    except FileNotFoundError as exc:
        print(f"Error: file not found – {exc}", file=sys.stderr)
        sys.exit(1)
    except ImportError as exc:
        print(f"Error: missing dependency – {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"✓  Backend   : {result.backend_used}")
    print(f"✓  Output    : {result.output_dir}")
    print(f"✓  Markdown  : {result.output_dir / 'paper.md'}")
    print(f"✓  Figures   : {len(result.images)} image(s) extracted")
    for name in sorted(result.images):
        print(f"     {name}")

    if args.print_md:
        print("\n" + "─" * 60 + "\n")
        print(result.markdown)


if __name__ == "__main__":
    main()
