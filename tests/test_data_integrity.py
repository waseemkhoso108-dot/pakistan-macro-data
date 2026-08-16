"""Structural validation of everything in data/clean/ against the metadata.

This is deliberately NOT a live-network test -- it validates whatever is
currently committed in data/clean/ and metadata/series_metadata.json, so it's
fast, deterministic, and safe to run in CI on every push. Re-fetching from
the World Bank API is a separate, explicit step (`scripts/fetch_data.py`).
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

sys.path.insert(0, str(ROOT / "scripts"))
from series_registry import REGISTRY  # noqa: E402


@pytest.fixture(scope="module")
def metadata() -> dict:
    with open(METADATA_PATH, encoding="utf-8") as f:
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


def test_derived_inflation_series_present(metadata):
    assert "cpi_inflation_yoy" in metadata
    assert (CLEAN_DIR / "cpi_inflation_yoy.csv").exists()


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_has_expected_schema(csv_path):
    df = pd.read_csv(csv_path)
    assert list(df.columns) == ["year", "value"], f"{csv_path.name} has unexpected columns {list(df.columns)}"
    assert len(df) > 0, f"{csv_path.name} is empty"


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_years_are_sorted_and_unique(csv_path):
    df = pd.read_csv(csv_path)
    years = df["year"].tolist()
    assert years == sorted(years), f"{csv_path.name} is not sorted by year"
    assert len(years) == len(set(years)), f"{csv_path.name} has duplicate years"


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_has_no_missing_values(csv_path):
    df = pd.read_csv(csv_path)
    assert not df["value"].isna().any(), f"{csv_path.name} has missing values"


@pytest.mark.parametrize("csv_path", sorted(CLEAN_DIR.glob("*.csv")))
def test_clean_csv_matches_its_metadata_coverage(csv_path, metadata):
    slug = csv_path.stem
    if slug not in metadata:
        pytest.skip(f"no metadata entry for {slug}")
    df = pd.read_csv(csv_path)
    meta = metadata[slug]
    assert int(df["year"].min()) == meta["coverage_start"]
    assert int(df["year"].max()) == meta["coverage_end"]
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


def test_cpi_inflation_is_consistent_with_cpi_index():
    cpi = pd.read_csv(CLEAN_DIR / "cpi.csv").set_index("year")["value"]
    inflation = pd.read_csv(CLEAN_DIR / "cpi_inflation_yoy.csv").set_index("year")["value"]
    for year in inflation.index:
        if year - 1 not in cpi.index:
            continue
        expected = (cpi[year] / cpi[year - 1] - 1) * 100
        assert inflation[year] == pytest.approx(expected, rel=1e-9), f"inflation mismatch at year {year}"
