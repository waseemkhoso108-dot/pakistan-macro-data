"""The registry of series this repository tracks.

Two source families, both from the World Bank, both real:

- **GEM** (Global Economic Monitor, World Bank source id 15): monthly
  frequency, 1987-present. Used wherever a monthly series exists.
- **WDI** (World Development Indicators, the default World Bank source):
  annual only. Used only for the two variables (broad money, a policy-rate
  proxy) that have no free monthly source.

Each entry carries the metadata fields the project's own data-quality
protocol requires (source, frequency, unit, base year, seasonal-adjustment
status, transformation, last-updated). Adding a series -- e.g. swapping in
an SBP-collected monthly policy rate once that data collection happens --
means adding one entry here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesSpec:
    slug: str
    indicator_code: str
    source: str  # "GEM" (monthly) or "WDI" (annual)
    description: str
    unit: str
    frequency: str
    base_year: str
    seasonal_adjustment: str
    transformation: str
    notes: str = ""


REGISTRY: list[SeriesSpec] = [
    SeriesSpec(
        slug="cpi",
        indicator_code="CPTOTNSXN",
        source="GEM",
        description="Consumer Price Index, all items",
        unit="Index",
        frequency="monthly",
        base_year="varies by vintage",
        seasonal_adjustment="not seasonally adjusted",
        transformation="none (raw index, source: Pakistan Bureau of Statistics via World Bank Global Economic Monitor)",
    ),
    SeriesSpec(
        slug="exchange_rate",
        indicator_code="DPANUSLCU",
        source="GEM",
        description="Official exchange rate, period average",
        unit="PKR per US$",
        frequency="monthly",
        base_year="n/a",
        seasonal_adjustment="not applicable",
        transformation="none (source: IMF International Financial Statistics via World Bank Global Economic Monitor)",
    ),
    SeriesSpec(
        slug="exchange_rate_neer",
        indicator_code="NEER",
        source="GEM",
        description="Nominal Effective Exchange Rate (trade-weighted basket)",
        unit="Index",
        frequency="monthly",
        base_year="varies by vintage",
        seasonal_adjustment="not applicable",
        transformation="none",
        notes="Trade-weighted, so more informative than the bilateral PKR/US$ rate about Pakistan's overall external competitiveness.",
    ),
    SeriesSpec(
        slug="exchange_rate_reer",
        indicator_code="REER",
        source="GEM",
        description="Real Effective Exchange Rate (NEER adjusted for relative inflation)",
        unit="Index",
        frequency="monthly",
        base_year="varies by vintage",
        seasonal_adjustment="not applicable",
        transformation="none",
        notes="Adjusts NEER for inflation differentials with trading partners -- the standard measure of real external competitiveness.",
    ),
    SeriesSpec(
        slug="industrial_activity",
        indicator_code="IPTOTNSKD",
        source="GEM",
        description="Industrial Production, constant US$ -- proxy for real economic activity",
        unit="constant US$",
        frequency="monthly",
        base_year="varies by vintage",
        seasonal_adjustment="not seasonally adjusted",
        transformation="none",
    ),
    SeriesSpec(
        slug="reserves",
        indicator_code="TOTRESV",
        source="GEM",
        description="Total reserves",
        unit="current US$",
        frequency="monthly",
        base_year="n/a",
        seasonal_adjustment="not applicable (end-of-period stock)",
        transformation="none",
    ),
    SeriesSpec(
        slug="broad_money_m2",
        indicator_code="FM.LBL.BMNY.CN",
        source="WDI",
        description="Broad money (M2)",
        unit="current PKR (local currency units)",
        frequency="annual",
        base_year="n/a",
        seasonal_adjustment="not seasonally adjusted",
        transformation="none (nominal level, not deflated)",
        notes="No free monthly source found; World Bank GEM does not carry broad money. Annual WDI series used instead -- see DATA.md.",
    ),
    SeriesSpec(
        slug="policy_rate_proxy",
        indicator_code="FR.INR.LEND",
        source="WDI",
        description="Lending interest rate -- PROXY for SBP's policy (target) rate, "
        "which the World Bank does not publish. Replace with the actual SBP policy-rate "
        "series once collected during MPhil fieldwork (see DATA.md).",
        unit="percent per annum",
        frequency="annual",
        base_year="n/a",
        seasonal_adjustment="not applicable",
        transformation="none",
        notes="TEMPORARY PROXY -- not the SBP policy rate. See DATA.md.",
    ),
]
