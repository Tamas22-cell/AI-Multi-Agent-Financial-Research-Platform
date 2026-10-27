"""Offline, deterministic validation for normalized market records."""
from __future__ import annotations

import math
from typing import Mapping, Any


def validate_market_record(record: Mapping[str, Any]) -> list[str]:
    """Return actionable validation errors without contacting market providers."""
    issues: list[str] = []
    for field in ("price", "change_pct"):
        value = record.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            issues.append(f"{field}: numeric value required")
        elif not math.isfinite(value):
            issues.append(f"{field}: finite value required")
    price = record.get("price")
    if isinstance(price, (int, float)) and not isinstance(price, bool) and math.isfinite(price) and price <= 0:
        issues.append("price: must be positive")
    return issues


def validate_market_batch(records: Mapping[str, Mapping[str, Any]]) -> dict[str, list[str]]:
    """Filter out relative-strength metadata and validate individual tickers."""
    return {
        ticker: errors
        for ticker, record in records.items()
        if ticker != "RELATIVE_STRENGTH"
        if (errors := validate_market_record(record))
    }
