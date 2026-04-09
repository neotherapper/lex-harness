#!/usr/bin/env python3
"""populate_articles.py — fetch verbatim statute text for all article .md files.

Downloads PDFs from official gov.gr sources (Raptarchis, Hellenic Parliament),
extracts the verbatim article text, computes sha256[:16], and rewrites each
article file replacing <<FETCH-FROM-kodiko.gr>> placeholders.

Usage:
    uv run scripts/populate_articles.py [--dry-run] [--article AK_173]

Sources used:
    AK articles     → archive.raptarchis.gov.gr/wp-content/uploads/2020/11/THEMA812.pdf
    KPolD articles  → archive.raptarchis.gov.gr/wp-content/uploads/2020/11/THEMA11.12.pdf
    Syntagma art.   → hellenicparliament.gr/UserFiles/.../FEK 211-A-24-12-2019 NEO SYNTAGMA.pdf
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# Add repo root to path so 'scripts' package resolves
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.greece.fetchers.raptarchis import (
    _download_pdf,
    _extract_article,
    _extract_article_range,
    _extract_text_from_pdf,
)

# ── PDF sources ───────────────────────────────────────────────────────────────

_PDF_AK = (
    "https://archive.raptarchis.gov.gr/wp-content/uploads/2020/11/THEMA812.pdf"
)
_PDF_KPOLD = (
    "https://archive.raptarchis.gov.gr/wp-content/uploads/2020/11/THEMA11.12.pdf"
)
_PDF_SYNTAGMA = (
    "https://www.hellenicparliament.gr/UserFiles/"
    "f3c70a23-7696-49db-9148-f24dce6a27c8/"
    "FEK%20211-A-24-12-2019%20NEO%20SYNTAGMA.pdf"
)

# ── Article file locations ────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).parent.parent
_CORE_DIR = _REPO_ROOT / "law-packs" / "greece" / "core"
_TENANCY_DIR = _REPO_ROOT / "law-packs" / "greece" / "modules" / "tenancy"


_ARTICLE_ID_RE = re.compile(r"^(AK|KPolD|Syntagma)_\d")


def _article_files() -> list[Path]:
    files = sorted(_CORE_DIR.glob("*.md")) + sorted(_TENANCY_DIR.glob("*.md"))
    return [f for f in files if _ARTICLE_ID_RE.match(f.stem)]


def _article_id_from_path(path: Path) -> str:
    return path.stem  # e.g. "AK_173", "KPolD_338"


def _pdf_url_for(article_id: str) -> str:
    if article_id.startswith("KPolD_"):
        return _PDF_KPOLD
    if article_id.startswith("Syntagma_"):
        return _PDF_SYNTAGMA
    return _PDF_AK  # AK_ and any other prefix


def _parse_nums(article_id: str) -> tuple[int, int]:
    nums_part = re.sub(r"^[A-Za-z]+_", "", article_id)
    parts = nums_part.split("_")
    start = int(parts[0])
    end = int(parts[-1]) if len(parts) > 1 else start
    return start, end


def _clean_text(raw: str) -> str:
    """Normalise extracted PDF text: collapse internal whitespace, keep structure."""
    # Replace multiple spaces/tabs within a line with single space
    lines = []
    for line in raw.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)
    # Collapse more than 2 consecutive blank lines to 1
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return result.strip()


def _update_article_file(
    path: Path,
    verbatim_text: str,
    pdf_url: str,
    dry_run: bool = False,
) -> bool:
    """Rewrite the article .md file with fetched text and computed sha256.

    Returns True if changes were made.
    """
    content = path.read_text(encoding="utf-8")

    # Compute sha256 of the cleaned text
    sha256 = hashlib.sha256(verbatim_text.encode("utf-8")).hexdigest()[:16]

    # Replace sha256 placeholder
    content = re.sub(
        r'sha256:\s*"<<TO-BE-COMPUTED>>"',
        f'sha256: "{sha256}"',
        content,
    )
    content = re.sub(
        r'sha256:\s*"[0-9a-f]{16}"',
        f'sha256: "{sha256}"',
        content,
    )

    # Replace last_verified
    content = re.sub(
        r"last_verified:\s*\S+",
        "last_verified: 2026-04-09",
        content,
    )

    # Update source_primary to Raptarchis URL
    content = re.sub(
        r'source_primary:\s*".*?"',
        f'source_primary: "{pdf_url}"',
        content,
    )

    # Update source_verification to Raptarchis page
    raptarchis_page = "https://archive.raptarchis.gov.gr/thema/astiki-nomothesia/astikos-kodikas/thema-v-astikos-kodikas/"
    if "KPolD" in path.stem:
        raptarchis_page = "https://archive.raptarchis.gov.gr/thema/politiki-dikonomia/politiki-dikonomia/thema-v-kodikas-politikis-dikonomias-neos/"
    elif "Syntagma" in path.stem:
        raptarchis_page = "https://www.hellenicparliament.gr/Vouli-ton-Ellinon/To-Politevma/Syntagma/"
    content = re.sub(
        r'source_verification:\s*".*?"',
        f'source_verification: "{raptarchis_page}"',
        content,
    )

    # Replace the verbatim text block placeholder
    placeholder_pattern = re.compile(
        r"(## Verbatim text \(Greek\)\s*\n)(.*?)(\n## )",
        re.DOTALL,
    )
    quote_block = "\n".join(f"> {line}" if line else ">" for line in verbatim_text.split("\n"))
    replacement = rf"\g<1>\n{quote_block}\n\g<3>"

    if placeholder_pattern.search(content):
        content = placeholder_pattern.sub(replacement, content)
    else:
        # Fallback: replace everything between Verbatim text header and next ##
        content = re.sub(
            r"(## Verbatim text \(Greek\)\s*\n)(.+?)(\n##)",
            rf"\g<1>\n{quote_block}\n\g<3>",
            content,
            flags=re.DOTALL,
        )

    if dry_run:
        print(f"  [DRY-RUN] Would write {path.name}: sha256={sha256}")
        print(f"  Text preview: {verbatim_text[:100].replace(chr(10), ' ')}")
        return True

    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print what would change without writing")
    parser.add_argument("--article", help="Process only this article_id (e.g. AK_173)")
    parser.add_argument("--force-download", action="store_true", help="Re-download PDFs even if cached")
    args = parser.parse_args()

    # Pre-download PDFs (cached)
    print("Downloading PDFs...")
    pdf_cache: dict[str, str] = {}  # url → full text
    for url in [_PDF_AK, _PDF_KPOLD, _PDF_SYNTAGMA]:
        print(f"  {url.split('/')[-1]}...", end=" ", flush=True)
        pdf_bytes = _download_pdf(url, force=args.force_download)
        pdf_cache[url] = _extract_text_from_pdf(pdf_bytes)
        print(f"OK ({len(pdf_cache[url]):,} chars)")

    # Process each article file
    files = _article_files()
    if args.article:
        files = [f for f in files if f.stem == args.article]
        if not files:
            print(f"ERROR: No file found for article_id={args.article!r}")
            sys.exit(1)

    ok = 0
    errors = []
    for path in files:
        article_id = _article_id_from_path(path)
        pdf_url = _pdf_url_for(article_id)
        start_num, end_num = _parse_nums(article_id)
        full_text = pdf_cache[pdf_url]

        print(f"  {article_id}...", end=" ", flush=True)
        try:
            if start_num == end_num:
                raw = _extract_article(full_text, start_num)
            else:
                raw = _extract_article_range(full_text, start_num, end_num)
            verbatim = _clean_text(raw)
            _update_article_file(path, verbatim, pdf_url, dry_run=args.dry_run)
            sha256 = hashlib.sha256(verbatim.encode("utf-8")).hexdigest()[:16]
            print(f"OK  sha256={sha256}  len={len(verbatim)}")
            ok += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append((article_id, str(e)))

    print(f"\nDone: {ok}/{len(files)} OK, {len(errors)} errors")
    if errors:
        for aid, err in errors:
            print(f"  FAILED {aid}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
