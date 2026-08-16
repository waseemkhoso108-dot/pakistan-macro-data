"""Stationarity diagnostics for every series in data/clean/.

Runs the Augmented Dickey-Fuller test (H0: unit root / non-stationary) and
the KPSS test (H0: stationary) on every series -- reporting both matters
because they have opposite nulls, so a series that's "borderline" on one
often resolves cleanly when read against the other. This is exactly the
kind of diagnostic a stranger checking whether this data is analysis-ready
(vs. a raw dump) would want to see already done.

Usage
-----
    python scripts/diagnostics.py
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT / "data" / "clean"
OUT_PATH = ROOT / "metadata" / "stationarity_diagnostics.json"


def _adf(series: pd.Series) -> dict:
    stat, pvalue, n_lags, n_obs, crit, _ = adfuller(series, autolag="AIC")
    return {
        "statistic": float(stat),
        "p_value": float(pvalue),
        "n_lags": int(n_lags),
        "critical_values": {k: float(v) for k, v in crit.items()},
        "rejects_unit_root_at_5pct": bool(pvalue < 0.05),
    }


def _kpss(series: pd.Series) -> dict:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # KPSS warns when p-value is outside its lookup table's range
        stat, pvalue, n_lags, crit = kpss(series, regression="c", nlags="auto")
    return {
        "statistic": float(stat),
        "p_value": float(pvalue),
        "n_lags": int(n_lags),
        "critical_values": {k: float(v) for k, v in crit.items()},
        "rejects_stationarity_at_5pct": bool(pvalue < 0.05),
    }


def diagnose_series(series: pd.Series) -> dict:
    series = series.dropna()
    adf = _adf(series)
    kp = _kpss(series)

    if adf["rejects_unit_root_at_5pct"] and not kp["rejects_stationarity_at_5pct"]:
        verdict = "stationary (both tests agree)"
    elif not adf["rejects_unit_root_at_5pct"] and kp["rejects_stationarity_at_5pct"]:
        verdict = "non-stationary (both tests agree)"
    else:
        verdict = "ambiguous (ADF and KPSS disagree -- common near a trend/level shift)"

    return {"n_observations": int(len(series)), "adf": adf, "kpss": kp, "verdict": verdict}


def main() -> None:
    results = {}
    for csv_path in sorted(CLEAN_DIR.glob("*.csv")):
        df = pd.read_csv(csv_path)
        slug = csv_path.stem
        try:
            results[slug] = diagnose_series(df["value"])
            print(f"{slug:25s} n={results[slug]['n_observations']:4d}  {results[slug]['verdict']}")
        except Exception as exc:  # a too-short or degenerate series shouldn't kill the whole run
            results[slug] = {"error": str(exc)}
            print(f"{slug:25s} ERROR: {exc}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
