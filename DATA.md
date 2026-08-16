# DATA.md

Every series in `data/clean/` is documented here: source, frequency, unit, base year, seasonal-adjustment status, transformation applied, last-updated timestamp, and a stationarity diagnosis (ADF + KPSS). This file is generated from `metadata/series_metadata.json` and `metadata/stationarity_diagnostics.json` by `scripts/build_data_md.py` -- do not hand-edit it; edit `scripts/series_registry.py` and re-run `scripts/fetch_data.py && scripts/diagnostics.py && scripts/build_data_md.py` instead.

Two source families, both from the World Bank, both real data (not placeholders): the **Global Economic Monitor (GEM)** for genuinely monthly series (1987-present), and **World Development Indicators (WDI)** for the two variables with no free monthly source (broad money, and a policy-rate proxy). See "Why GEM, not just WDI" below for why this distinction matters.


## Cross-source validation

The monthly GEM series were checked against the *independently published* annual WDI series for the same underlying concept (both ultimately trace to Pakistan Bureau of Statistics / SBP data, but via different World Bank processing pipelines) -- annual-averaging the monthly data and comparing year-over-year growth rates to the WDI annual growth rates:

| Series | Years compared | Correlation of growth rates | Mean abs. difference (pp) | Verdict |
|---|---|---|---|---|
| `cpi` | 1988-2025 (38 yrs) | 0.998 | 0.17 | consistent |
| `exchange_rate` | 1988-2025 (38 yrs) | 0.991 | 0.44 | consistent |

Regenerate with `python scripts/validate_against_wdi.py`.


## `cpi`

Consumer Price Index, all items

| Field | Value |
|---|---|
| Source | World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org |
| Indicator code | `CPTOTNSXN` |
| Frequency | monthly |
| Unit | Index |
| Base year | varies by vintage |
| Seasonal adjustment | not seasonally adjusted |
| Transformation | none (raw index, source: Pakistan Bureau of Statistics via World Bank Global Economic Monitor) |
| Coverage | 1987-01-01 to 2026-02-01 (470 observations) |
| Last updated | 2026-08-16T19:02:16Z |
| Stationarity (ADF + KPSS) | **non-stationary (both tests agree)** (ADF p=1.000, KPSS p=0.010) |

File: [`data/clean/cpi.csv`](data/clean/cpi.csv) &nbsp;·&nbsp; Figure: [`figures/cpi.png`](figures/cpi.png)

## `exchange_rate`

Official exchange rate, period average

| Field | Value |
|---|---|
| Source | World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org |
| Indicator code | `DPANUSLCU` |
| Frequency | monthly |
| Unit | PKR per US$ |
| Base year | n/a |
| Seasonal adjustment | not applicable |
| Transformation | none (source: IMF International Financial Statistics via World Bank Global Economic Monitor) |
| Coverage | 1987-01-01 to 2026-03-01 (471 observations) |
| Last updated | 2026-08-16T19:02:17Z |
| Stationarity (ADF + KPSS) | **non-stationary (both tests agree)** (ADF p=0.996, KPSS p=0.010) |

File: [`data/clean/exchange_rate.csv`](data/clean/exchange_rate.csv) &nbsp;·&nbsp; Figure: [`figures/exchange_rate.png`](figures/exchange_rate.png)

## `exchange_rate_neer`

Nominal Effective Exchange Rate (trade-weighted basket)

| Field | Value |
|---|---|
| Source | World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org |
| Indicator code | `NEER` |
| Frequency | monthly |
| Unit | Index |
| Base year | varies by vintage |
| Seasonal adjustment | not applicable |
| Transformation | none |
| Coverage | 1987-01-01 to 2024-10-01 (454 observations) |
| Last updated | 2026-08-16T19:02:19Z |
| Stationarity (ADF + KPSS) | **ambiguous (ADF and KPSS disagree -- common near a trend/level shift)** (ADF p=0.006, KPSS p=0.010) |
| **Note** | **Trade-weighted, so more informative than the bilateral PKR/US$ rate about Pakistan's overall external competitiveness.** |

File: [`data/clean/exchange_rate_neer.csv`](data/clean/exchange_rate_neer.csv) &nbsp;·&nbsp; Figure: [`figures/exchange_rate_neer.png`](figures/exchange_rate_neer.png)

## `exchange_rate_reer`

Real Effective Exchange Rate (NEER adjusted for relative inflation)

| Field | Value |
|---|---|
| Source | World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org |
| Indicator code | `REER` |
| Frequency | monthly |
| Unit | Index |
| Base year | varies by vintage |
| Seasonal adjustment | not applicable |
| Transformation | none |
| Coverage | 1987-01-01 to 2024-10-01 (454 observations) |
| Last updated | 2026-08-16T19:02:21Z |
| Stationarity (ADF + KPSS) | **ambiguous (ADF and KPSS disagree -- common near a trend/level shift)** (ADF p=0.015, KPSS p=0.010) |
| **Note** | **Adjusts NEER for inflation differentials with trading partners -- the standard measure of real external competitiveness.** |

File: [`data/clean/exchange_rate_reer.csv`](data/clean/exchange_rate_reer.csv) &nbsp;·&nbsp; Figure: [`figures/exchange_rate_reer.png`](figures/exchange_rate_reer.png)

## `industrial_activity`

Industrial Production, constant US$ -- proxy for real economic activity

| Field | Value |
|---|---|
| Source | World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org |
| Indicator code | `IPTOTNSKD` |
| Frequency | monthly |
| Unit | constant US$ |
| Base year | varies by vintage |
| Seasonal adjustment | not seasonally adjusted |
| Transformation | none |
| Coverage | 1991-01-01 to 2026-01-01 (421 observations) |
| Last updated | 2026-08-16T19:02:22Z |
| Stationarity (ADF + KPSS) | **non-stationary (both tests agree)** (ADF p=0.867, KPSS p=0.010) |

File: [`data/clean/industrial_activity.csv`](data/clean/industrial_activity.csv) &nbsp;·&nbsp; Figure: [`figures/industrial_activity.png`](figures/industrial_activity.png)

## `reserves`

Total reserves

| Field | Value |
|---|---|
| Source | World Bank Global Economic Monitor (GEM, source id 15), api.worldbank.org |
| Indicator code | `TOTRESV` |
| Frequency | monthly |
| Unit | current US$ |
| Base year | n/a |
| Seasonal adjustment | not applicable (end-of-period stock) |
| Transformation | none |
| Coverage | 1990-01-01 to 2026-02-01 (434 observations) |
| Last updated | 2026-08-16T19:02:23Z |
| Stationarity (ADF + KPSS) | **non-stationary (both tests agree)** (ADF p=0.666, KPSS p=0.010) |

File: [`data/clean/reserves.csv`](data/clean/reserves.csv) &nbsp;·&nbsp; Figure: [`figures/reserves.png`](figures/reserves.png)

## `broad_money_m2`

Broad money (M2)

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (WDI), api.worldbank.org |
| Indicator code | `FM.LBL.BMNY.CN` |
| Frequency | annual |
| Unit | current PKR (local currency units) |
| Base year | n/a |
| Seasonal adjustment | not seasonally adjusted |
| Transformation | none (nominal level, not deflated) |
| Coverage | 1960-01-01 to 2025-01-01 (66 observations) |
| Last updated | 2026-08-16T19:02:25Z |
| Stationarity (ADF + KPSS) | **non-stationary (both tests agree)** (ADF p=1.000, KPSS p=0.010) |
| **Note** | **No free monthly source found; World Bank GEM does not carry broad money. Annual WDI series used instead -- see DATA.md.** |

File: [`data/clean/broad_money_m2.csv`](data/clean/broad_money_m2.csv) &nbsp;·&nbsp; Figure: [`figures/broad_money_m2.png`](figures/broad_money_m2.png)

## `policy_rate_proxy`

Lending interest rate -- PROXY for SBP's policy (target) rate, which the World Bank does not publish. Replace with the actual SBP policy-rate series once collected during MPhil fieldwork (see DATA.md).

| Field | Value |
|---|---|
| Source | World Bank World Development Indicators (WDI), api.worldbank.org |
| Indicator code | `FR.INR.LEND` |
| Frequency | annual |
| Unit | percent per annum |
| Base year | n/a |
| Seasonal adjustment | not applicable |
| Transformation | none |
| Coverage | 2004-01-01 to 2021-01-01 (18 observations) |
| Last updated | 2026-08-16T19:02:27Z |
| Stationarity (ADF + KPSS) | **stationary (both tests agree)** (ADF p=0.000, KPSS p=0.100) |
| **Note** | **TEMPORARY PROXY -- not the SBP policy rate. See DATA.md.** |

File: [`data/clean/policy_rate_proxy.csv`](data/clean/policy_rate_proxy.csv) &nbsp;·&nbsp; Figure: [`figures/policy_rate_proxy.png`](figures/policy_rate_proxy.png)

## `cpi_inflation_yoy`

CPI inflation, year-over-year percent change

| Field | Value |
|---|---|
| Source | Derived from cpi.csv |
| Indicator code | `derived:cpi` |
| Frequency | monthly |
| Unit | percent, year-over-year |
| Base year | n/a |
| Seasonal adjustment | not applicable |
| Transformation | 100 * (log(value_t) - log(value_t-12)), computed after sorting by date |
| Coverage | 1988-01-01 to 2026-02-01 (458 observations) |
| Last updated | 2026-08-16T19:02:27Z |
| Stationarity (ADF + KPSS) | **stationary (both tests agree)** (ADF p=0.041, KPSS p=0.100) |

File: [`data/clean/cpi_inflation_yoy.csv`](data/clean/cpi_inflation_yoy.csv) &nbsp;·&nbsp; Figure: [`figures/cpi_inflation_yoy.png`](figures/cpi_inflation_yoy.png)

## Why GEM, not just WDI

World Bank's default country-indicator API (WDI) is annual only. The **Global Economic Monitor** (source id 15) carries genuinely monthly data for the same underlying national-statistics-office series back to 1987 -- 400+ observations instead of ~65. This repository uses GEM wherever a monthly series exists, and falls back to annual WDI only for the two variables (`broad_money_m2`, `policy_rate_proxy`) with no free monthly source. The cross-validation section above checks that the two sources agree where both are available.
