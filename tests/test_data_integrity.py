"""Structural validation of everything in data/clean/ against the metadata.

This is deliberately NOT a live-network test -- it validates whatever is
currently committed in data/clean/, metadata/series_metadata.json, and
metadata/stationarity_diagnostics.json, so it's fast, deterministic, and
safe to run in CI on every push. Re-fetching from the World Bank API is a
separate, explicit step (scripts/fetch_data.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT / "data" / "clean"
METADATA_PATH = ROOT / "metadata" / "series_metadata.json"
DIAGNOSTICS_PATH = ROOT / "metadata" / "stationarity_diagnostics.json"
CROSS_VALIDATION_PATH = ROOT / "metadata" / "cross_validation.json"

sys.path.insert(0, str(ROOT / "scripts"))
from series_registry import REGISTRY  # noqa: E402


@pytest.fixture(scope="module")
def metadata() -> dict:
    with open(METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def diagnostics() -> dict:
    with open(DIAGNOSTICS_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_metadata_file_exists_and_parses(metadata):
    assert len(metadata) > 0


def test_every_registry_series_has_a_clean_csv():
    for spec in REGISTRY:
        path = CLEAN_DIR / f"{spec.slug}.csv"
        assert path.exists(), f"missing data/clean/{spec.slug}.csv for registry entry '{spec.slug}'"


def test_every_registry_series_has_metadata(metadata):
    for spec in REGISTRY:
        assert spec.slug in metadata, f"missing metadata for '{spec.slug}'"


def test_every_registry_series_has_a_figure():
    for spec in REGISTRY:
        path = ROOT / "figures" / f"{spec.slug}.png"
        assert path.exists(), f"missing figures/{spec.slug}.png for registry entry '{spec.slug}'"


def test_derived_inflation_series_present(metadata):
    assert "cpi_inflation_yoy" in metadata
    assert (CLEAN_DIR / "cpi_inflation_yoy.csv").exists()


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_has_expected_schema(csv_path):
    df = pd.read_csv(csv_path)
    assert list(df.columns) == ["date", "value"], f"{csv_path.name} has unexpected columns {list(df.columns)}"
    assert len(df) > 0, f"{csv_path.name} is empty"


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_dates_are_sorted_and_unique(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["date"])
    dates = df["date"].tolist()
    assert dates == sorted(dates), f"{csv_path.name} is not sorted by date"
    assert len(dates) == len(set(dates)), f"{csv_path.name} has duplicate dates"


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_has_no_missing_values(csv_path):
    df = pd.read_csv(csv_path)
    assert not df["value"].isna().any(), f"{csv_path.name} has missing values"


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_matches_its_metadata_coverage(csv_path, metadata):
    slug = csv_path.stem
    if slug not in metadata:
        pytest.skip(f"no metadata entry for {slug}")
    df = pd.read_csv(csv_path, parse_dates=["date"])
    meta = metadata[slug]
    assert df["date"].min().strftime("%Y-%m-%d") == meta["coverage_start"]
    assert df["date"].max().strftime("%Y-%m-%d") == meta["coverage_end"]
    assert len(df) == meta["n_observations"]


def test_metadata_records_have_required_fields(metadata):
    required = {
        "description",
        "source",
        "indicator_code",
        "frequency",
        "unit",
        "base_year",
        "seasonal_adjustment",
        "transformation",
        "coverage_start",
        "coverage_end",
        "n_observations",
        "last_updated",
    }
    for slug, meta in metadata.items():
        missing = required - set(meta)
        assert not missing, f"metadata for '{slug}' is missing fields: {missing}"


def test_monthly_series_have_at_least_100_observations(metadata):
    """A GEM-sourced monthly series with only a handful of observations
    would indicate the date-range query silently failed."""
    for slug, meta in metadata.items():
        if meta["frequency"] == "monthly":
            assert meta["n_observations"] >= 100, f"'{slug}' claims monthly frequency but has only {meta['n_observations']} obs"


def test_cpi_inflation_is_consistent_with_cpi_index():
    import numpy as np

    cpi = pd.read_csv(CLEAN_DIR / "cpi.csv", parse_dates=["date"]).set_index("date")["value"]
    inflation = pd.read_csv(CLEAN_DIR / "cpi_inflation_yoy.csv", parse_dates=["date"]).set_index("date")["value"]
    for dt in inflation.index[:50]:  # spot-check a subset for speed
        lag_dt = dt - pd.DateOffset(months=12)
        if lag_dt not in cpi.index:
            continue
        expected = 100 * (np.log(cpi[dt]) - np.log(cpi[lag_dt]))
        assert inflation[dt] == pytest.approx(expected, rel=1e-6), f"inflation mismatch at {dt}"


def test_diagnostics_cover_every_clean_series(diagnostics):
    clean_slugs = {p.stem for p in CLEAN_DIR.glob("*.csv")}
    assert clean_slugs.issubset(set(diagnostics))


def test_diagnostics_have_valid_p_values(diagnostics):
    for slug, d in diagnostics.items():
        if "error" in d:
            continue
        assert 0.0 <= d["adf"]["p_value"] <= 1.0, f"'{slug}' ADF p-value out of range"
        assert 0.0 <= d["kpss"]["p_value"] <= 1.0, f"'{slug}' KPSS p-value out of range"


def test_differenced_series_are_flagged_stationary(diagnostics):
    """cpi_inflation_yoy is a year-over-year growth rate -- it should read
    as stationary, unlike the price *level* it's derived from."""
    assert diagnostics["cpi_inflation_yoy"]["verdict"] == "stationary (both tests agree)"
    assert diagnostics["cpi"]["verdict"] != "stationary (both tests agree)"


def test_cross_validation_file_if_present():
    if not CROSS_VALIDATION_PATH.exists():
        pytest.skip("cross_validation.json not generated in this checkout")
    with open(CROSS_VALIDATION_PATH, encoding="utf-8") as f:
        cross_val = json.load(f)
    for slug, result in cross_val.items():
        if result.get("comparable_years", 0) == 0:
            continue
        assert -1.0 <= result["correlation_of_annual_growth_rates"] <= 1.0
