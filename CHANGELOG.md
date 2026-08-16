# Changelog

## [0.2.0] - 2026-08-17

Major rigor upgrade.

- **Monthly data**: switched from all-annual World Bank WDI series (~66 observations each) to World Bank Global Economic Monitor monthly series (~450 observations, 1987-2026) for 7 of the 9 series. The 2 series with no free monthly source (broad money, policy-rate proxy) stay annual, explicitly flagged rather than silently mixed in.
- Added 2 new series: `exchange_rate_neer` and `exchange_rate_reer` (nominal/real effective exchange rates).
- **Stationarity diagnostics** (`scripts/diagnostics.py`): ADF + KPSS on every series, published in `metadata/stationarity_diagnostics.json` and woven into `DATA.md`.
- **Cross-source validation** (`scripts/validate_against_wdi.py`): checks the monthly GEM series against independently-published annual WDI series for the same concept -- both `cpi` and `exchange_rate` come back at >0.99 correlation.
- **Figures** (`scripts/make_figures.py`): a time-series plot per series plus an overview grid.
- `.zenodo.json` scaffold for DOI archival once the repo is connected to Zenodo.
- `refresh-data.yml` now runs the full pipeline (fetch, diagnostics, cross-validation, figures, DATA.md) monthly, not just fetch.
- 48 tests (up from 34), covering the new date-based schema, diagnostic validity, and derived-series transformation arithmetic.

## [0.1.0] - 2026-08-16

Initial public release: 7 annual series from World Bank WDI.
