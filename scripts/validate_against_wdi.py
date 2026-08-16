"""Cross-source validation: does annual-averaging the monthly GEM series
roughly reproduce the independently-published annual WDI series for the
same underlying concept?

This is a real data-quality check, not a formality: GEM and WDI are
different World Bank pipelines drawing on the same national-statistics-
office source data but processed independently, so close agreement is
genuine (if weak) evidence the monthly series isn't corrupted, and a
large discrepancy would be a real red flag worth investigating before
trusting the monthly data.

Usage
-----
    python scripts/validate_against_wdi.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT / "data" / "clean"
OUT_PATH = ROOT / "metadata" / "cross_validation.json"

WB_API_ANNUAL = "https://api.worldbank.org/v2/country/PAK/indicator/{code}?format=json&per_page=2000"
HEADERS = {"User-Agent": "pakistan-macro-data-fetcher/0.2"}

# (GEM series in data/clean/, comparable annual WDI indicator code, note)
COMPARISONS = [
    ("cpi", "FP.CPI.TOTL", "CPI index -- different base years across GEM/WDI, so compare growth rates not levels"),
    ("exchange_rate", "PA.NUS.FCRF", "PKR/US$ official rate, period average"),
]


def _fetch_wdi_annual(code: str, retries: int = 3) -> pd.DataFrame:
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(WB_API_ANNUAL.format(code=code), headers=HEADERS, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            break
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(2 * attempt)
    else:
        raise RuntimeError(f"failed to fetch {code}") from last_exc
    records = [{"year": int(row["date"]), "value": row["value"]} for row in payload[1] if row["value"] is not None]
    return pd.DataFrame(records).sort_values("year").reset_index(drop=True)


def _annual_growth(series_by_year: pd.Series) -> pd.Series:
    return series_by_year.pct_change() * 100


def validate_one(gem_slug: str, wdi_code: str) -> dict:
    gem = pd.read_csv(CLEAN_DIR / f"{gem_slug}.csv", parse_dates=["date"])
    gem_annual = gem.set_index("date")["value"].resample("YS").mean()
    gem_annual.index = gem_annual.index.year

    wdi = _fetch_wdi_annual(wdi_code)
    wdi_annual = wdi.set_index("year")["value"]

    gem_growth = _annual_growth(gem_annual)
    wdi_growth = _annual_growth(wdi_annual)

    common_years = sorted(set(gem_growth.dropna().index) & set(wdi_growth.dropna().index))
    if not common_years:
        return {"comparable_years": 0, "note": "no overlapping years with valid growth rates"}

    g = gem_growth.loc[common_years]
    w = wdi_growth.loc[common_years]
    corr = float(g.corr(w))
    mean_abs_diff_pp = float((g - w).abs().mean())

    return {
        "comparable_years": len(common_years),
        "year_range": [int(min(common_years)), int(max(common_years))],
        "correlation_of_annual_growth_rates": corr,
        "mean_absolute_difference_pp": mean_abs_diff_pp,
        "verdict": "consistent" if corr > 0.9 and mean_abs_diff_pp < 5 else "check manually",
    }


def main() -> None:
    results = {}
    for gem_slug, wdi_code, note in COMPARISONS:
        print(f"Validating {gem_slug} (GEM, annual-averaged growth) against {wdi_code} (WDI annual growth) ...")
        result = validate_one(gem_slug, wdi_code)
        result["note"] = note
        results[gem_slug] = result
        print(f"  {result}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
