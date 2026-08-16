# pakistan-macro-data

[![CI](https://github.com/waseemkhoso108-dot/pakistan-macro-data/actions/workflows/ci.yml/badge.svg)](https://github.com/waseemkhoso108-dot/pakistan-macro-data/actions/workflows/ci.yml)
[![Code License: MIT](https://img.shields.io/badge/Code_License-MIT-yellow.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data_License-CC_BY_4.0-lightgrey.svg)](DATA_LICENSE)

A reproducible, documented repository of Pakistani macroeconomic time series — 9 series covering CPI, CPI inflation, the exchange rate (bilateral, nominal effective, and real effective), industrial activity, reserves, broad money, and a policy-rate proxy, **monthly where a real monthly source exists** (400+ observations, 1987-2026) and annual only where it doesn't — each with full source/frequency/unit/transformation metadata, an ADF+KPSS stationarity diagnosis, and a cross-source validation check against an independently-published series.

## Why this exists

Pakistan-focused econometric work — including my own MPhil thesis and PhD proposal — needs clean, documented, *monthly* macro series, and most quick analyses default to annual World Bank indicators because that's the obvious API to reach for. This repository doesn't: it uses the World Bank's Global Economic Monitor (a separate, sub-annual data source) wherever a monthly series exists, applies the same data-quality protocol I use for my own research (full metadata, stationarity diagnostics, cross-source validation) to a public dataset, and stays reproducible rather than becoming a static dump. As I collect direct SBP/PBS series during MPhil fieldwork, they'll extend or replace what's here (see [DATA.md](DATA.md) for exactly which series are provisional).

## What's here

| Series | Description | Frequency | Coverage |
|---|---|---|---|
| `cpi` | Consumer Price Index, all items | **monthly** | 1987-2026 |
| `cpi_inflation_yoy` | CPI inflation, year-over-year % (derived) | **monthly** | 1988-2026 |
| `exchange_rate` | Official PKR/US$ rate | **monthly** | 1987-2026 |
| `exchange_rate_neer` | Nominal Effective Exchange Rate | **monthly** | 1987-2024 |
| `exchange_rate_reer` | Real Effective Exchange Rate | **monthly** | 1987-2024 |
| `industrial_activity` | Industrial production (real-activity proxy) | **monthly** | 1991-2026 |
| `reserves` | Total reserves | **monthly** | 1990-2026 |
| `broad_money_m2` | Broad money (M2) | annual | 1960-2025 |
| `policy_rate_proxy` | Lending rate (**proxy** for SBP's policy rate) | annual | 2004-2021 |

7 of 9 series are genuinely monthly. The two annual holdouts are flagged explicitly, with why, in [DATA.md](DATA.md) — not silently mixed in as if they were the same frequency as everything else.

Full documentation for every series — source, unit, transformation, stationarity diagnosis — is in **[DATA.md](DATA.md)**, generated directly from `metadata/*.json`.

```
data/
├── raw/     # unmodified API responses, one CSV per series
└── clean/   # deduplicated, sorted, typed -- what you should actually use
metadata/
├── series_metadata.json           # machine-readable version of DATA.md
├── stationarity_diagnostics.json  # ADF + KPSS results per series
└── cross_validation.json          # GEM-vs-WDI agreement check
figures/     # one time-series plot per series, plus an overview grid
scripts/
├── series_registry.py       # the list of tracked series + their metadata fields
├── fetch_data.py             # re-pulls every series from source and re-cleans it
├── diagnostics.py            # ADF + KPSS stationarity tests
├── validate_against_wdi.py   # cross-checks GEM monthly data against independent WDI annual data
├── make_figures.py           # time-series plots
└── build_data_md.py          # regenerates DATA.md from the metadata + diagnostics
```

## Reproduce it yourself

```bash
git clone https://github.com/waseemkhoso108-dot/pakistan-macro-data.git
cd pakistan-macro-data
pip install -r requirements.txt

python scripts/fetch_data.py           # re-pulls every series from source
python scripts/diagnostics.py          # ADF + KPSS on every series
python scripts/validate_against_wdi.py # cross-source consistency check
python scripts/make_figures.py         # regenerates figures/
python scripts/build_data_md.py        # regenerates DATA.md
pytest                                  # validates schema, coverage, and metadata consistency
```

Not a static dump: every script re-derives its output from source (or from the previous script's output) every time it's run, and the monthly `refresh-data` GitHub Actions workflow runs the whole chain automatically and opens a PR if anything changed.

## Data quality, not just data

- **Stationarity diagnostics** (ADF + KPSS, both directions of null hypothesis) on every series — so a reader can tell at a glance whether a series needs differencing before use, without running the tests themselves.
- **Cross-source validation**: annual-averaging the monthly GEM series and comparing year-over-year growth rates against the *independently published* annual WDI series for the same concept. Both `cpi` and `exchange_rate` come back at >0.99 correlation with <0.5 percentage-point mean absolute difference — real evidence the monthly data isn't corrupted, not just an assumption.
- **48 automated tests** covering schema, date ordering, missing values, metadata-vs-data consistency, diagnostic validity, and the derived-series transformation arithmetic.

## Data source

Two World Bank source families: **Global Economic Monitor** (monthly, 1987-present, source id 15) for 7 of the 9 series, and **World Development Indicators** (annual) for the 2 series with no free monthly source. Both ultimately aggregate data originally collected by the State Bank of Pakistan (SBP), the Pakistan Bureau of Statistics (PBS), and the IMF. See [DATA.md](DATA.md) for the exact indicator code and frequency behind each series.

## License

- **Code** (everything in `scripts/`, `tests/`): [MIT](LICENSE)
- **Data** (everything in `data/`): [CC BY 4.0](DATA_LICENSE) — the same license the World Bank publishes its data under; attribute the World Bank when reusing.
