"""Regenerate DATA.md from metadata/series_metadata.json.

Keeps the human-readable documentation in sync with the machine-readable
metadata automatically -- run after ``fetch_data.py`` (the CI workflow does
both in sequence).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = ROOT / "metadata" / "series_metadata.json"
DATA_MD_PATH = ROOT / "DATA.md"

HEADER = """# DATA.md

Every series in `data/clean/` is documented here: source, frequency, unit, base year, seasonal-adjustment status, transformation applied, and last-updated timestamp. This file is generated from `metadata/series_metadata.json` by `scripts/build_data_md.py` -- do not hand-edit it, edit `scripts/series_registry.py` and re-run `scripts/fetch_data.py && scripts/build_data_md.py` instead.

All series currently come from the World Bank's World Development Indicators API for Pakistan (`api.worldbank.org`), which mirrors data originally collected by the State Bank of Pakistan (SBP), the Pakistan Bureau of Statistics (PBS), and the IMF. They are annual. **The eventual goal, per the project's data-collection protocol, is to replace these with monthly series pulled directly from SBP/PBS during MPhil fieldwork** -- these World Bank series are a genuine, real, working starting point, not placeholders, but they are coarser (annual, not monthly) and in the policy-rate case a proxy rather than the true series. Each entry below says explicitly which situation it's in.

"""


def format_series(slug: str, meta: dict) -> str:
    lines = [f"## `{slug}`", "", f"{meta['description']}", ""]
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| Source | {meta['source']} |")
    lines.append(f"| Indicator code | `{meta['indicator_code']}` |")
    lines.append(f"| Frequency | {meta['frequency']} |")
    lines.append(f"| Unit | {meta['unit']} |")
    lines.append(f"| Base year | {meta['base_year']} |")
    lines.append(f"| Seasonal adjustment | {meta['seasonal_adjustment']} |")
    lines.append(f"| Transformation | {meta['transformation']} |")
    lines.append(f"| Coverage | {meta['coverage_start']}-{meta['coverage_end']} ({meta['n_observations']} observations) |")
    lines.append(f"| Last updated | {meta['last_updated']} |")
    if meta.get("notes"):
        lines.append(f"| **Note** | **{meta['notes']}** |")
    lines.append("")
    lines.append(f"File: [`data/clean/{slug}.csv`](data/clean/{slug}.csv)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    with open(METADATA_PATH, encoding="utf-8") as f:
        metadata = json.load(f)

    parts = [HEADER]
    for slug, meta in metadata.items():
        parts.append(format_series(slug, meta))

    DATA_MD_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {DATA_MD_PATH} ({len(metadata)} series documented)")


if __name__ == "__main__":
    main()
