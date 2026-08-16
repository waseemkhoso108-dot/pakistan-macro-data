"""Regenerate DATA.md from metadata/series_metadata.json (+ stationarity
diagnostics + cross-validation, if present).

Keeps the human-readable documentation in sync with the machine-readable
metadata automatically -- run after fetch_data.py / diagnostics.py /
validate_against_wdi.py (the CI refresh workflow runs all of them in
sequence).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = ROOT / "metadata" / "series_metadata.json"
DIAGNOSTICS_PATH = ROOT / "metadata" / "stationarity_diagnostics.json"
CROSS_VALIDATION_PATH = ROOT / "metadata" / "cross_validation.json"
DATA_MD_PATH = ROOT / "DATA.md"

HEADER = """# DATA.md

Every series in `data/clean/` is documented here: source, frequency, unit, base year, seasonal-adjustment status, transformation applied, last-updated timestamp, and a stationarity diagnosis (ADF + KPSS). This file is generated from `metadata/series_metadata.json` and `metadata/stationarity_diagnostics.json` by `scripts/build_data_md.py` -- do not hand-edit it; edit `scripts/series_registry.py` and re-run `scripts/fetch_data.py && scripts/diagnostics.py && scripts/build_data_md.py` instead.

Two source families, both from the World Bank, both real data (not placeholders): the **Global Economic Monitor (GEM)** for genuinely monthly series (1987-present), and **World Development Indicators (WDI)** for the two variables with no free monthly source (broad money, and a policy-rate proxy). See "Why GEM, not just WDI" below for why this distinction matters.

"""

CROSS_VALIDATION_SECTION_TEMPLATE = """## Cross-source validation

The monthly GEM series were checked against the *independently published* annual WDI series for the same underlying concept (both ultimately trace to Pakistan Bureau of Statistics / SBP data, but via different World Bank processing pipelines) -- annual-averaging the monthly data and comparing year-over-year growth rates to the WDI annual growth rates:

| Series | Years compared | Correlation of growth rates | Mean abs. difference (pp) | Verdict |
|---|---|---|---|---|
{rows}

Regenerate with `python scripts/validate_against_wdi.py`.

"""


def format_series(slug: str, meta: dict, diagnostics: dict | None) -> str:
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
    lines.append(f"| Coverage | {meta['coverage_start']} to {meta['coverage_end']} ({meta['n_observations']} observations) |")
    lines.append(f"| Last updated | {meta['last_updated']} |")
    if diagnostics and "error" not in diagnostics:
        lines.append(
            f"| Stationarity (ADF + KPSS) | **{diagnostics['verdict']}** "
            f"(ADF p={diagnostics['adf']['p_value']:.3f}, KPSS p={diagnostics['kpss']['p_value']:.3f}) |"
        )
    if meta.get("notes"):
        lines.append(f"| **Note** | **{meta['notes']}** |")
    lines.append("")
    lines.append(f"File: [`data/clean/{slug}.csv`](data/clean/{slug}.csv) &nbsp;·&nbsp; Figure: [`figures/{slug}.png`](figures/{slug}.png)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    with open(METADATA_PATH, encoding="utf-8") as f:
        metadata = json.load(f)

    diagnostics = {}
    if DIAGNOSTICS_PATH.exists():
        with open(DIAGNOSTICS_PATH, encoding="utf-8") as f:
            diagnostics = json.load(f)

    parts = [HEADER]

    if CROSS_VALIDATION_PATH.exists():
        with open(CROSS_VALIDATION_PATH, encoding="utf-8") as f:
            cross_val = json.load(f)
        rows = []
        for slug, r in cross_val.items():
            if r.get("comparable_years", 0) == 0:
                continue
            rows.append(
                f"| `{slug}` | {r['year_range'][0]}-{r['year_range'][1]} ({r['comparable_years']} yrs) | "
                f"{r['correlation_of_annual_growth_rates']:.3f} | {r['mean_absolute_difference_pp']:.2f} | {r['verdict']} |"
            )
        parts.append(CROSS_VALIDATION_SECTION_TEMPLATE.format(rows="\n".join(rows)))

    for slug, meta in metadata.items():
        parts.append(format_series(slug, meta, diagnostics.get(slug)))

    parts.append(
        "## Why GEM, not just WDI\n\n"
        "World Bank's default country-indicator API (WDI) is annual only. The **Global Economic "
        "Monitor** (source id 15) carries genuinely monthly data for the same underlying national-"
        "statistics-office series back to 1987 -- 400+ observations instead of ~65. This repository "
        "uses GEM wherever a monthly series exists, and falls back to annual WDI only for the two "
        "variables (`broad_money_m2`, `policy_rate_proxy`) with no free monthly source. The cross-"
        "validation section above checks that the two sources agree where both are available.\n"
    )

    DATA_MD_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {DATA_MD_PATH} ({len(metadata)} series documented)")


if __name__ == "__main__":
    main()
