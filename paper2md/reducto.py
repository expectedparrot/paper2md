"""
paper2md.backends.reducto
~~~~~~~~~~~~~~~~~~~~~~~~~
Optional backend that uses the Reducto API for premium document parsing.

Sign up at https://reducto.ai/ and set the environment variable::

    export REDUCTO_API_KEY=your_key_here

Then use::

    from paper2md import convert
    result = convert("paper.pdf", backend="reducto")

Or install and use directly::

    from paper2md.backends.reducto import convert_with_reducto
"""

from __future__ import annotations

import os
import re
import urllib.request
import urllib.parse
import json
from pathlib import Path


def convert_with_reducto(
    pdf_path: Path,
    output_dir: Path,
    api_key: str | None = None,
) -> tuple[str, list[Path]]:
    """Upload *pdf_path* to Reducto and return (markdown, image_paths).

    Requires the ``reducto`` Python client::

        pip install reducto

    Or the API key set via ``REDUCTO_API_KEY``.
    """
    api_key = api_key or os.environ.get("REDUCTO_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Set REDUCTO_API_KEY or pass api_key= to use the Reducto backend."
        )

    try:
        import reducto  # type: ignore
        return _reducto_sdk(pdf_path, output_dir, api_key, reducto)
    except ImportError:
        return _reducto_http(pdf_path, output_dir, api_key)


# ---------------------------------------------------------------------------
# SDK path (pip install reducto)
# ---------------------------------------------------------------------------

def _reducto_sdk(pdf_path, output_dir, api_key, reducto):
    client = reducto.Reducto(api_key=api_key)
    with open(pdf_path, "rb") as f:
        result = client.parse.parse_file(
            file=f,
            options=reducto.ParseOptions(
                chunking=reducto.ChunkingOptions(chunk_mode="disabled"),
                figure_summary=reducto.FigureSummaryOptions(enabled=True),
                table_summary=reducto.TableSummaryOptions(enabled=True, output_mode="markdown"),
            ),
        )

    # Reconstruct markdown from Reducto's structured chunks
    md_parts: list[str] = []
    images: list[Path] = []
    img_counter = 0

    for chunk in result.result.chunks:
        md_parts.append(chunk.content)

        # Download any figures attached to this chunk
        for fig in getattr(chunk, "figures", []) or []:
            img_counter += 1
            img_path = output_dir / f"_reducto_{img_counter}.png"
            _download(fig.url, img_path)
            images.append(img_path)
            md_parts.append(f"\n![Figure {img_counter}](_reducto_{img_counter}.png)\n")

    return "\n\n".join(md_parts), images


# ---------------------------------------------------------------------------
# Raw HTTP path (no SDK)
# ---------------------------------------------------------------------------

def _reducto_http(pdf_path, output_dir, api_key):
    import urllib.request, urllib.error

    url = "https://v1.api.reductoai.com/parse"
    boundary = "paper2md_boundary"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{pdf_path.name}"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode() + pdf_bytes + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    md = data.get("markdown") or data.get("content") or ""
    return md, []


def _download(url: str, dest: Path) -> None:
    with urllib.request.urlopen(url) as resp:
        dest.write_bytes(resp.read())
