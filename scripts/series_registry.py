"""The registry of series this repository tracks.

Each entry is deliberately minimal and explicit: a World Bank indicator code
plus the metadata fields the project's own data-quality protocol requires
(source, frequency, unit, base year, seasonal-adjustment status,
transformation, last-updated). Adding a new series -- e.g. swapping in an
SBP-collected monthly policy rate once that data collection happens -- means
adding one entry here; ``fetch_data.py`` and the tests both key off this
registry, so nothing else needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesSpec:
    slug: str
    indicator_code: str
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
        indicator_code="FP.CPI.TOTL",
        description="Consumer Price Index, all items",
        unit="Index (2010 = 100)",
        frequency="annual",
        base_year="2010",
        seasonal_adjustment="not seasonally adjusted (annual average)",
        transformation="none (raw index as published by World Bank / source: Pakistan Bureau of Statistics via World Bank WDI)",
    ),
    SeriesSpec(
        slug="exchange_rate",
        indicator_code="PA.NUS.FCRF",
        description="Official exchange rate, period average",
        unit="PKR per US$",
        frequency="annual",
        base_year="n/a",
        seasonal_adjustment="not applicable",
        transformation="none (annual average of official rate, source: IMF International Financial Statistics via World Bank WDI)",
    ),
    SeriesSpec(
        slug="broad_money_m2",
        indicator_code="FM.LBL.BMNY.CN",
        description="Broad money (M2)",
        unit="current PKR (local currency units)",
        frequency="annual",
        base_year="n/a",
        seasonal_adjustment="not seasonally adjusted",
        transformation="none (nominal level, not deflated)",
    ),
    SeriesSpec(
        slug="reserves",
        indicator_code="FI.RES.TOTL.CD",
        description="Total reserves (includes gold, valued at end of period)",
        unit="current US$",
        frequency="annual",
        base_year="n/a",
        seasonal_adjustment="not applicable (end-of-period stock)",
        transformation="none",
    ),
    SeriesSpec(
        slug="industrial_activity",
        indicator_code="NV.IND.TOTL.KD",
        description="Industry (including construction), value added -- proxy for industrial activity",
        unit="constant 2015 US$",
        frequency="annual",
        base_year="2015",
        seasonal_adjustment="not applicable (annual)",
        transformation="none",
    ),
    SeriesSpec(
        slug="policy_rate_proxy",
        indicator_code="FR.INR.LEND",
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
