"""Offline ETL quality gate. Caller supplies raw data; no automatic network calls."""
import json
from pathlib import Path
from typing import Mapping, Any

from data.quality import validate_market_batch


def export_validated_market_snapshot(
    records: Mapping[str, Mapping[str, Any]], output_path: str | Path
) -> dict[str, int]:
    issues = validate_market_batch(records)
    if issues:
        raise ValueError(f"Market data rejected: {issues}")
    payload = {
        ticker: record
        for ticker, record in records.items()
        if ticker != "RELATIVE_STRENGTH"
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # No partial output on validation failure; write only clean data.
    destination.write_text(json.dumps(payload, allow_nan=False, indent=2), encoding="utf-8")
    return {"accepted": len(payload), "rejected": 0}
