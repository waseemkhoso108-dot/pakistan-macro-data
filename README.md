# pakistan-macro-data

[![CI](https://github.com/waseemkhoso108-dot/pakistan-macro-data/actions/workflows/ci.yml/badge.svg)](https://github.com/waseemkhoso108-dot/pakistan-macro-data/actions/workflows/ci.yml)
[![Code License: MIT](https://img.shields.io/badge/Code_License-MIT-yellow.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data_License-CC_BY_4.0-lightgrey.svg)](DATA_LICENSE)

A reproducible, documented repository of Pakistani macroeconomic time series: CPI, CPI inflation, the exchange rate, broad money (M2), reserves, industrial activity, and a policy-rate proxy — each with a metadata record covering source, frequency, unit, base year, seasonal-adjustment status, transformation applied, and last-updated date.

## Why this exists

Pakistan-focused econometric work — including my own MPhil thesis and PhD proposal — needs clean, documented macro series, and most existing sources hand you a raw number with no metadata trail. This repository applies the same data-quality protocol I use for that research to a public dataset, so anyone can pull, verify, and cite exactly what each number means. It's a live resource: as I collect monthly SBP/PBS series during MPhil fieldwork, they'll replace the annual World Bank proxies here (see [DATA.md](DATA.md) for which series are provisional).

## What's here

| Series | Description | Frequency | Coverage |
|---|---|---|---|
| `cpi` | Consumer Price Index, all items (2010=100) | annual | 1960-2025 |
| `cpi_inflation_yoy` | CPI inflation, year-over-year % (derived from `cpi`) | annual | 1961-2025 |
| `exchange_rate` | Official exchange rate, PKR per US$ | annual | 1960-2025 |
| `broad_money_m2` | Broad money (M2), current PKR | annual | 1960-2025 |
| `reserves` | Total reserves, current US$ | annual | 1960-2025 |
| `industrial_activity` | Industry value added (proxy), constant 2015 US$ | annual | 1960-2025 |
| `policy_rate_proxy` | Lending interest rate (**proxy** for SBP's policy rate) | annual | 2004-2021 |

Full documentation for every series — source, unit, transformation, everything — is in **[DATA.md](DATA.md)**, generated directly from [`metadata/series_metadata.json`](metadata/series_metadata.json).

```
data/
├── raw/     # unmodified API responses, one CSV per series
└── clean/   # deduplicated, sorted, typed -- what you should actually use
metadata/
└── series_metadata.json   # machine-readable version of DATA.md
scripts/
├── series_registry.py     # the list of tracked series + their metadata fields
├── fetch_data.py           # re-pulls every series from source and re-cleans it
└── build_data_md.py        # regenerates DATA.md from series_metadata.json
```

## Reproduce it yourself

```bash
git clone https://github.com/waseemkhoso108-dot/pakistan-macro-data.git
cd pakistan-macro-data
pip install -r requirements.txt
python scripts/fetch_data.py       # re-pulls every series from the World Bank API
python scripts/build_data_md.py    # regenerates DATA.md
pytest                              # validates schema, coverage, and metadata consistency
```

This is not a static dump: `fetch_data.py` re-derives everything in `data/` from source every time it's run, so the pipeline stays reproducible as new observations become available each year.

## Data source

All series currently come from the [World Bank World Development Indicators API](https://api.worldbank.org) for Pakistan, which itself aggregates data originally collected by the State Bank of Pakistan (SBP), the Pakistan Bureau of Statistics (PBS), and the IMF. See [DATA.md](DATA.md) for the exact indicator code behind each series.

## License

- **Code** (everything in `scripts/`, `tests/`): [MIT](LICENSE)
- **Data** (everything in `data/`): [CC BY 4.0](DATA_LICENSE) — the same license the World Bank publishes its WDI data under; attribute the World Bank when reusing.
