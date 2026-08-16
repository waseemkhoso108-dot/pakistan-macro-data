# DATA.md

Every series in `data/clean/` is documented here: source, frequency, unit, base year, seasonal-adjustment status, transformation applied, and last-updated timestamp. This file is generated from `metadata/series_metadata.json` by `scripts/build_data_md.py` -- do not hand-edit it, edit `scripts/series_registry.py` and re-run `scripts/fetch_data.py && scripts/build_data_md.py` instead.

All series currently come from the World Bank's World Development Indicators API for Pakistan (`api.worldbank.org`), which mirrors data originally collected by the State Bank of Pakistan (SBP), the Pakistan Bureau of Statistics (PBS), and the IMF. They are annual. **The eventual goal, per the project's data-collection protocol, is to replace these with monthly series pulled directly from SBP/PBS during MPhil fieldwork** -- these World Bank series are a genuine, real, working starting point, not placeholders, but they are coarser (annual, not monthly) and in the policy-rate case a proxy rather than the true series. Each entry below says explicitly which situation it's in.


## `cpi`

Consumer Price Index, all items

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (api.worldbank.org) |
| Indicator code | `FP.CPI.TOTL` |
| Frequency | annual |
| Unit | Index (2010 = 100) |
| Base year | 2010 |
| Seasonal adjustment | not seasonally adjusted (annual average) |
| Transformation | none (raw index as published by World Bank / source: Pakistan Bureau of Statistics via World Bank WDI) |
| Coverage | 1960-2025 (66 observations) |
| Last updated | 2026-08-16T17:13:26Z |

File: [`data/clean/cpi.csv`](data/clean/cpi.csv)

## `exchange_rate`

Official exchange rate, period average

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (api.worldbank.org) |
| Indicator code | `PA.NUS.FCRF` |
| Frequency | annual |
| Unit | PKR per US$ |
| Base year | n/a |
| Seasonal adjustment | not applicable |
| Transformation | none (annual average of official rate, source: IMF International Financial Statistics via World Bank WDI) |
| Coverage | 1960-2025 (66 observations) |
| Last updated | 2026-08-16T17:13:26Z |

File: [`data/clean/exchange_rate.csv`](data/clean/exchange_rate.csv)

## `broad_money_m2`

Broad money (M2)

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (api.worldbank.org) |
| Indicator code | `FM.LBL.BMNY.CN` |
| Frequency | annual |
| Unit | current PKR (local currency units) |
| Base year | n/a |
| Seasonal adjustment | not seasonally adjusted |
| Transformation | none (nominal level, not deflated) |
| Coverage | 1960-2025 (66 observations) |
| Last updated | 2026-08-16T17:13:27Z |

File: [`data/clean/broad_money_m2.csv`](data/clean/broad_money_m2.csv)

## `reserves`

Total reserves (includes gold, valued at end of period)

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (api.worldbank.org) |
| Indicator code | `FI.RES.TOTL.CD` |
| Frequency | annual |
| Unit | current US$ |
| Base year | n/a |
| Seasonal adjustment | not applicable (end-of-period stock) |
| Transformation | none |
| Coverage | 1960-2025 (66 observations) |
| Last updated | 2026-08-16T17:14:00Z |

File: [`data/clean/reserves.csv`](data/clean/reserves.csv)

## `industrial_activity`

Industry (including construction), value added -- proxy for industrial activity

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (api.worldbank.org) |
| Indicator code | `NV.IND.TOTL.KD` |
| Frequency | annual |
| Unit | constant 2015 US$ |
| Base year | 2015 |
| Seasonal adjustment | not applicable (annual) |
| Transformation | none |
| Coverage | 1960-2025 (66 observations) |
| Last updated | 2026-08-16T17:14:01Z |

File: [`data/clean/industrial_activity.csv`](data/clean/industrial_activity.csv)

## `policy_rate_proxy`

Lending interest rate -- PROXY for SBP's policy (target) rate, which the World Bank does not publish. Replace with the actual SBP policy-rate series once collected during MPhil fieldwork (see DATA.md).

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (api.worldbank.org) |
| Indicator code | `FR.INR.LEND` |
| Frequency | annual |
| Unit | percent per annum |
| Base year | n/a |
| Seasonal adjustment | not applicable |
| Transformation | none |
| Coverage | 2004-2021 (18 observations) |
| Last updated | 2026-08-16T17:14:35Z |
| **Note** | **TEMPORARY PROXY -- not the SBP policy rate. See DATA.md.** |

File: [`data/clean/policy_rate_proxy.csv`](data/clean/policy_rate_proxy.csv)

## `cpi_inflation_yoy`

CPI inflation, year-over-year percent change

| Field | Value |
|---|---|
| Source | Derived from cpi.csv (World Bank WDI indicator FP.CPI.TOTL) |
| Indicator code | `derived:FP.CPI.TOTL` |
| Frequency | annual |
| Unit | percent, year-over-year |
| Base year | n/a |
| Seasonal adjustment | not applicable |
| Transformation | pct_change(cpi.value) * 100, computed after sorting by year |
| Coverage | 1961-2025 (65 observations) |
| Last updated | 2026-08-16T17:14:35Z |

File: [`data/clean/cpi_inflation_yoy.csv`](data/clean/cpi_inflation_yoy.csv)
