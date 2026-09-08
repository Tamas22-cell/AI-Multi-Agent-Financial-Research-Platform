import json
from datetime import datetime
from pathlib import Path

import yfinance as yf


class SignalHistory:
    def __init__(
        self,
        history_file="reports/output/signal_history.json"
    ):
        self.history_file = Path(
            history_file
        )

        self.history_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.benchmark_symbols = {
            "SPY": "SPY",
            "BTC-USD": "BTC-USD",
        }

    def _load_history(self):
        if not self.history_file.exists():
            return []

        try:
            with open(
                self.history_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(
                    file
                )

            if isinstance(
                data,
                list
            ):
                return data

            return []

        except Exception:
            return []

    def _save_history(
        self,
        history
    ):
        with open(
            self.history_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

    def _get_record_date(
        self,
        record
    ):
        timestamp_text = record.get(
            "timestamp"
        )

        if not timestamp_text:
            return None

        try:
            timestamp = (
                datetime.fromisoformat(
                    timestamp_text
                )
            )

            return (
                timestamp.date()
            )

        except Exception:
            return None

    def _get_current_price(
        self,
        symbol
    ):
        try:
            ticker = yf.Ticker(
                symbol
            )

            intraday = ticker.history(
                period="1d",
                interval="1m",
                auto_adjust=True,
            )

            if (
                intraday is not None
                and not intraday.empty
            ):
                price = float(
                    intraday["Close"].iloc[-1]
                )

                price_timestamp = (
                    intraday.index[-1]
                )

                return {
                    "symbol": symbol,
                    "price": round(
                        price,
                        4
                    ),
                    "price_timestamp": str(
                        price_timestamp
                    ),
                    "source": "yfinance_1m",
                }

            daily = ticker.history(
                period="5d",
                interval="1d",
                auto_adjust=True,
            )

            if (
                daily is not None
                and not daily.empty
            ):
                price = float(
                    daily["Close"].iloc[-1]
                )

                price_timestamp = (
                    daily.index[-1]
                )

                return {
                    "symbol": symbol,
                    "price": round(
                        price,
                        4
                    ),
                    "price_timestamp": str(
                        price_timestamp
                    ),
                    "source": "yfinance_1d_fallback",
                }

            return {
                "symbol": symbol,
                "price": None,
                "price_timestamp": None,
                "source": "unavailable",
            }

        except Exception:
            return {
                "symbol": symbol,
                "price": None,
                "price_timestamp": None,
                "source": "unavailable",
            }

    def _get_benchmark_snapshot(
        self
    ):
        benchmark_snapshot = {}

        for (
            benchmark_name,
            symbol
        ) in self.benchmark_symbols.items():
            benchmark_snapshot[
                benchmark_name
            ] = (
                self._get_current_price(
                    symbol
                )
            )

        return benchmark_snapshot

    def record_signal(
        self,
        output
    ):
        history = (
            self._load_history()
        )

        now = datetime.now()

        timestamp = (
            now.isoformat()
        )

        current_date = (
            now.date()
        )

        agent_results = {}

        for result in output.get(
            "agents",
            []
        ):
            agent_name = result.get(
                "agent",
                "unknown"
            )

            agent_results[
                agent_name
            ] = {
                "signal": result.get(
                    "signal",
                    "neutral"
                ),

                "score": float(
                    result.get(
                        "score",
                        0.50
                    )
                ),

                "confidence": float(
                    result.get(
                        "confidence",
                        0.0
                    )
                ),
            }

        benchmark_snapshot = (
            self._get_benchmark_snapshot()
        )

        record = {
            "timestamp": timestamp,

            "date": (
                current_date.isoformat()
            ),

            "decision": output.get(
                "decision",
                "HOLD"
            ),

            "market_regime": (
                output.get(
                    "market_regime",
                    "MIXED"
                )
            ),

            "market_score": float(
                output.get(
                    "market_score",
                    0.50
                )
            ),

            "average_confidence": float(
                output.get(
                    "average_confidence",
                    0.0
                )
            ),

            "bullish_pct": float(
                output.get(
                    "bullish_pct",
                    0.0
                )
            ),

            "neutral_pct": float(
                output.get(
                    "neutral_pct",
                    0.0
                )
            ),

            "bearish_pct": float(
                output.get(
                    "bearish_pct",
                    0.0
                )
            ),

            "consensus_strength": float(
                output.get(
                    "consensus_strength",
                    0.0
                )
            ),

            "signal_conflict": output.get(
                "signal_conflict",
                False
            ),

            "risk_override": output.get(
                "risk_override",
                False
            ),

            "benchmarks": (
                benchmark_snapshot
            ),

            "agents": (
                agent_results
            ),
        }

        updated_history = []

        replaced_today = False

        for existing_record in history:
            existing_date = (
                self._get_record_date(
                    existing_record
                )
            )

            if (
                existing_date
                == current_date
            ):
                if not replaced_today:
                    updated_history.append(
                        record
                    )

                    replaced_today = True

                continue

            updated_history.append(
                existing_record
            )

        if not replaced_today:
            updated_history.append(
                record
            )

        updated_history.sort(
            key=lambda item: (
                item.get(
                    "timestamp",
                    ""
                )
            )
        )

        self._save_history(
            updated_history
        )

        return {
            "record": (
                record
            ),

            "history_file": (
                self.history_file
            ),

            "total_records": len(
                updated_history
            ),

            "daily_record_replaced": (
                replaced_today
            ),

            "benchmarks": (
                benchmark_snapshot
            ),
        }

    def get_history(self):
        return (
            self._load_history()
        )

    def get_latest_signal(self):
        history = (
            self._load_history()
        )

        if not history:
            return None

        return history[-1]

    def get_total_records(self):
        history = (
            self._load_history()
        )

        return len(
            history
        )