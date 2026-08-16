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

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from series_registry import REGISTRY, SeriesSpec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"
METADATA_PATH = ROOT / "metadata" / "series_metadata.json"

WB_API = "https://api.worldbank.org/v2/country/PK/indicator/{code}?format=json&per_page=2000"
HEADERS = {"User-Agent": "pakistan-macro-data-fetcher/0.1 (+https://github.com)"}


def fetch_indicator(code: str, retries: int = 3) -> pd.DataFrame:
    """Pull one World Bank indicator for Pakistan as a tidy (year, value) frame."""
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(WB_API.format(code=code), headers=HEADERS, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            break
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(2 * attempt)
    else:
        raise RuntimeError(f"failed to fetch indicator {code} after {retries} attempts") from last_exc
    if len(payload) < 2 or not payload[1]:
        raise RuntimeError(f"World Bank API returned no observations for indicator {code}")

    records = [{"year": int(row["date"]), "value": row["value"]} for row in payload[1]]
    df = pd.DataFrame(records).dropna(subset=["value"]).sort_values("year").reset_index(drop=True)
    return df


def fetch_and_clean_series(spec: SeriesSpec) -> tuple[pd.DataFrame, dict]:
    raw = fetch_indicator(spec.indicator_code)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_DIR / f"{spec.slug}.csv", index=False)

    clean = raw.copy()
    clean = clean.drop_duplicates(subset="year").sort_values("year").reset_index(drop=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_DIR / f"{spec.slug}.csv", index=False)

    meta = {
        "slug": spec.slug,
        "description": spec.description,
        "source": "World Bank World Development Indicators (api.worldbank.org)",
        "indicator_code": spec.indicator_code,
        "country": "Pakistan (PK)",
        "frequency": spec.frequency,
        "unit": spec.unit,
        "base_year": spec.base_year,
        "seasonal_adjustment": spec.seasonal_adjustment,
        "transformation": spec.transformation,
        "coverage_start": int(clean["year"].min()),
        "coverage_end": int(clean["year"].max()),
        "n_observations": int(len(clean)),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": spec.notes,
    }
    return clean, meta


def derive_inflation(cpi: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """CPI inflation, year-over-year %, derived from the CPI index -- kept as
    its own file since it's a transformation of a source series, not a
    source series itself (documented explicitly per the project's metadata
    discipline)."""
    df = cpi.copy().sort_values("year")
    df["value"] = df["value"].pct_change() * 100
    df = df.dropna().reset_index(drop=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DIR / "cpi_inflation_yoy.csv", index=False)

    meta = {
        "slug": "cpi_inflation_yoy",
        "description": "CPI inflation, year-over-year percent change",
        "source": "Derived from cpi.csv (World Bank WDI indicator FP.CPI.TOTL)",
        "indicator_code": "derived:FP.CPI.TOTL",
        "country": "Pakistan (PK)",
        "frequency": "annual",
        "unit": "percent, year-over-year",
        "base_year": "n/a",
        "seasonal_adjustment": "not applicable",
        "transformation": "pct_change(cpi.value) * 100, computed after sorting by year",
        "coverage_start": int(df["year"].min()),
        "coverage_end": int(df["year"].max()),
        "n_observations": int(len(df)),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": "",
    }
    return df, meta


def main() -> None:
    all_meta = {}
    cpi_clean = None

    for spec in REGISTRY:
        print(f"Fetching {spec.slug} (World Bank {spec.indicator_code}) ...")
        clean, meta = fetch_and_clean_series(spec)
        all_meta[spec.slug] = meta
        print(f"  {meta['n_observations']} observations, {meta['coverage_start']}-{meta['coverage_end']}")
        if spec.slug == "cpi":
            cpi_clean = clean

    if cpi_clean is not None:
        print("Deriving cpi_inflation_yoy from cpi ...")
        _, infl_meta = derive_inflation(cpi_clean)
        all_meta["cpi_inflation_yoy"] = infl_meta
        print(f"  {infl_meta['n_observations']} observations, {infl_meta['coverage_start']}-{infl_meta['coverage_end']}")

    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_meta, f, indent=2)
    print(f"\nWrote metadata for {len(all_meta)} series to {METADATA_PATH}")
    print(f"Refresh date: {date.today().isoformat()}")


if __name__ == "__main__":
    main()
