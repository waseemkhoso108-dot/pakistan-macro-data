"""Re-pull and re-clean every series in the registry from its public source.

This is the "single script that re-pulls and re-cleans from source" the
repository's own data-quality protocol calls for -- run it any time to
refresh data/raw and data/clean, and to regenerate metadata/series_metadata.json
with a fresh last_updated timestamp.

Usage
-----
    python scripts/fetch_data.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from series_registry import REGISTRY, SeriesSpec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"
METADATA_PATH = ROOT / "metadata" / "series_metadata.json"

WB_API_ANNUAL = "https://api.worldbank.org/v2/country/PAK/indicator/{code}?format=json&per_page=2000"
WB_API_MONTHLY = "https://api.worldbank.org/v2/country/PAK/indicator/{code}?date=1960M01:2026M12&format=json&per_page=2000"
HEADERS = {"User-Agent": "pakistan-macro-data-fetcher/0.2"}


def _parse_wb_date(date_str: str) -> str:
    """GEM dates look like '2021M07' -> ISO '2021-07-01'; WDI annual dates
    look like '2021' -> '2021-01-01'."""
    if "M" in date_str:
        year, month = date_str.split("M")
        return f"{int(year):04d}-{int(month):02d}-01"
    return f"{int(date_str):04d}-01-01"


def _fetch_indicator(spec: SeriesSpec, retries: int = 3) -> pd.DataFrame:
    url_template = WB_API_MONTHLY if spec.source == "GEM" else WB_API_ANNUAL
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url_template.format(code=spec.indicator_code), headers=HEADERS, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            break
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(2 * attempt)
    else:
        raise RuntimeError(f"failed to fetch indicator {spec.indicator_code} after {retries} attempts") from last_exc

    if len(payload) < 2 or not payload[1]:
        raise RuntimeError(f"World Bank API returned no observations for indicator {spec.indicator_code}")

    records = [
        {"date": _parse_wb_date(row["date"]), "value": row["value"]} for row in payload[1] if row["value"] is not None
    ]
    df = pd.DataFrame(records).drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)
    return df


def fetch_and_clean_series(spec: SeriesSpec) -> tuple[pd.DataFrame, dict]:
    raw = _fetch_indicator(spec)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_DIR / f"{spec.slug}.csv", index=False)

    clean = raw.drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_DIR / f"{spec.slug}.csv", index=False)

    meta = {
        "slug": spec.slug,
        "description": spec.description,
        "source": (
            "World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org"
            if spec.source == "GEM"
            else "World Bank World Development Indicators (WDI), api.worldbank.org"
        ),
        "indicator_code": spec.indicator_code,
        "country": "Pakistan (PK)",
        "frequency": spec.frequency,
        "unit": spec.unit,
        "base_year": spec.base_year,
        "seasonal_adjustment": spec.seasonal_adjustment,
        "transformation": spec.transformation,
        "coverage_start": clean["date"].min(),
        "coverage_end": clean["date"].max(),
        "n_observations": int(len(clean)),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": spec.notes,
    }
    return clean, meta


def derive_yoy(base: pd.DataFrame, slug: str, description: str, periods: int, base_slug: str) -> tuple[pd.DataFrame, dict]:
    """Year-over-year % change via a log-difference -- `periods` is 12 for a
    monthly series, 1 for an annual one."""
    df = base.copy().sort_values("date")
    log_val = np.log(df["value"])
    df["value"] = (log_val - log_val.shift(periods)) * 100
    df = df.dropna().reset_index(drop=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DIR / f"{slug}.csv", index=False)

    meta = {
        "slug": slug,
        "description": description,
        "source": f"Derived from {base_slug}.csv",
        "indicator_code": f"derived:{base_slug}",
        "country": "Pakistan (PK)",
        "frequency": "monthly" if periods == 12 else "annual",
        "unit": "percent, year-over-year",
        "base_year": "n/a",
        "seasonal_adjustment": "not applicable",
        "transformation": f"100 * (log(value_t) - log(value_t-{periods})), computed after sorting by date",
        "coverage_start": df["date"].min(),
        "coverage_end": df["date"].max(),
        "n_observations": int(len(df)),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": "",
    }
    return df, meta


def main() -> None:
    all_meta = {}
    cpi_clean = None

    for spec in REGISTRY:
        print(f"Fetching {spec.slug} ({spec.source} {spec.indicator_code}) ...")
        clean, meta = fetch_and_clean_series(spec)
        all_meta[spec.slug] = meta
        print(f"  {meta['n_observations']} observations, {meta['coverage_start']} to {meta['coverage_end']}")
        if spec.slug == "cpi":
            cpi_clean = clean

    if cpi_clean is not None:
        print("Deriving cpi_inflation_yoy from cpi (monthly, 12-month log-difference) ...")
        _, infl_meta = derive_yoy(cpi_clean, "cpi_inflation_yoy", "CPI inflation, year-over-year percent change", 12, "cpi")
        all_meta["cpi_inflation_yoy"] = infl_meta
        print(f"  {infl_meta['n_observations']} observations, {infl_meta['coverage_start']} to {infl_meta['coverage_end']}")

    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_meta, f, indent=2, default=str)
    print(f"\nWrote metadata for {len(all_meta)} series to {METADATA_PATH}")
    print(f"Refresh date: {date.today().isoformat()}")


if __name__ == "__main__":
    main()
