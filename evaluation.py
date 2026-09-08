import json
from datetime import datetime, timedelta
from pathlib import Path

import yfinance as yf


class SignalEvaluator:
    def __init__(
        self,
        history_file="reports/output/signal_history.json",
        evaluation_file="reports/output/evaluation_results.json",
    ):
        self.history_file = Path(
            history_file
        )

        self.evaluation_file = Path(
            evaluation_file
        )

        self.evaluation_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.primary_benchmark = "SPY"

        self.benchmark_symbols = {
            "SPY": "SPY",
            "BTC-USD": "BTC-USD",
        }

        self.agent_benchmarks = {
            "macro": "SPY",
            "stock": "SPY",
            "crypto": "BTC-USD",
            "onchain": "BTC-USD",
            "derivatives": "BTC-USD",
            "technical": "SPY",
            "news": "SPY",
            "geopolitical": "SPY",
            "risk": "SPY",
        }

        self.agent_order = [
            "macro",
            "stock",
            "crypto",
            "onchain",
            "derivatives",
            "technical",
            "news",
            "geopolitical",
            "risk",
        ]

        self.horizons = {
            "1d": 1,
            "7d": 7,
            "30d": 30,
        }

        self.horizon_weights = {
            "1d": 0.20,
            "7d": 0.30,
            "30d": 0.50,
        }

        self.minimum_samples_for_reliable_rank = 10

    def _load_json(
        self,
        file_path
    ):
        if not file_path.exists():
            return []

        try:
            with open(
                file_path,
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

    def _save_json(
        self,
        file_path,
        data
    ):
        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

    def _get_price_history(
        self,
        symbol
    ):
        try:
            history = yf.Ticker(
                symbol
            ).history(
                period="2y",
                interval="1d",
                auto_adjust=True,
            )

            if (
                history is None
                or history.empty
            ):
                return None

            return (
                history
                .dropna()
                .copy()
            )

        except Exception:
            return None

    def _load_all_price_histories(
        self
    ):
        histories = {}

        for (
            benchmark_name,
            symbol
        ) in self.benchmark_symbols.items():
            histories[
                benchmark_name
            ] = (
                self._get_price_history(
                    symbol
                )
            )

        return histories

    def _get_snapshot_start_price(
        self,
        record,
        benchmark_name
    ):
        benchmarks = record.get(
            "benchmarks",
            {}
        )

        benchmark_data = benchmarks.get(
            benchmark_name,
            {}
        )

        price = benchmark_data.get(
            "price"
        )

        if price is None:
            return None

        try:
            price = float(
                price
            )

            if price <= 0:
                return None

            return {
                "price": price,

                "date": record.get(
                    "date"
                ),

                "timestamp": benchmark_data.get(
                    "price_timestamp"
                ),

                "source": benchmark_data.get(
                    "source",
                    "signal_snapshot"
                ),

                "method": (
                    "signal_snapshot"
                ),
            }

        except Exception:
            return None

    def _find_historical_start_price(
        self,
        history,
        signal_date
    ):
        if (
            history is None
            or history.empty
        ):
            return None

        candidate = None

        for index, row in (
            history.iterrows()
        ):
            price_date = (
                index.date()
            )

            if (
                price_date
                <= signal_date
            ):
                try:
                    candidate = {
                        "price": float(
                            row["Close"]
                        ),

                        "date": (
                            price_date.isoformat()
                        ),

                        "timestamp": str(
                            index
                        ),

                        "source": (
                            "yfinance_daily"
                        ),

                        "method": (
                            "historical_fallback"
                        ),
                    }

                except Exception:
                    continue

            else:
                break

        return candidate

    def _get_start_price(
        self,
        record,
        benchmark_name,
        history,
        signal_date
    ):
        snapshot = (
            self._get_snapshot_start_price(
                record,
                benchmark_name
            )
        )

        if snapshot is not None:
            return snapshot

        return (
            self._find_historical_start_price(
                history,
                signal_date
            )
        )

    def _find_future_price(
        self,
        history,
        target_date
    ):
        if (
            history is None
            or history.empty
        ):
            return None

        for index, row in (
            history.iterrows()
        ):
            price_date = (
                index.date()
            )

            if (
                price_date
                >= target_date
            ):
                try:
                    return {
                        "date": (
                            price_date.isoformat()
                        ),

                        "price": float(
                            row["Close"]
                        ),
                    }

                except Exception:
                    return None

        return None

    def _calculate_return(
        self,
        start_price,
        future_price
    ):
        if (
            start_price is None
            or future_price is None
            or start_price == 0
        ):
            return None

        return (
            (
                future_price
                - start_price
            )
            / start_price
        ) * 100

    def _get_threshold(
        self,
        benchmark_name,
        horizon
    ):
        thresholds = {
            "SPY": {
                "1d": 0.50,
                "7d": 1.50,
                "30d": 3.00,
            },

            "BTC-USD": {
                "1d": 1.00,
                "7d": 3.00,
                "30d": 7.00,
            },
        }

        benchmark_thresholds = (
            thresholds.get(
                benchmark_name,
                thresholds["SPY"]
            )
        )

        return (
            benchmark_thresholds.get(
                horizon,
                1.00
            )
        )

    def _classify_market_move(
        self,
        benchmark_name,
        horizon,
        market_return
    ):
        if market_return is None:
            return "pending"

        threshold = (
            self._get_threshold(
                benchmark_name,
                horizon
            )
        )

        if (
            market_return
            >= threshold
        ):
            return "bullish"

        if (
            market_return
            <= -threshold
        ):
            return "bearish"

        return "neutral"

    def _classify_decision_outcome(
        self,
        decision,
        market_move
    ):
        if (
            market_move
            == "pending"
        ):
            return "pending"

        decision = str(
            decision
        ).upper()

        if (
            decision
            == "BUY"
        ):
            expected_move = (
                "bullish"
            )

        elif (
            decision
            == "AVOID"
        ):
            expected_move = (
                "bearish"
            )

        elif (
            decision
            == "HOLD"
        ):
            expected_move = (
                "neutral"
            )

        else:
            return "unknown"

        if (
            market_move
            == expected_move
        ):
            return "correct"

        return "incorrect"

    def _classify_agent_outcome(
        self,
        agent_signal,
        market_move
    ):
        if (
            market_move
            == "pending"
        ):
            return "pending"

        signal = str(
            agent_signal
        ).lower()

        if signal not in [
            "bullish",
            "neutral",
            "bearish",
        ]:
            return "unknown"

        if (
            signal
            == market_move
        ):
            return "correct"

        return "incorrect"

    def _evaluate_benchmark_horizon(
        self,
        record,
        signal_date,
        today,
        benchmark_name,
        price_history,
        horizon_name,
        days_forward
    ):
        target_date = (
            signal_date
            + timedelta(
                days=days_forward
            )
        )

        elapsed_days = (
            today
            - signal_date
        ).days

        start_data = (
            self._get_start_price(
                record,
                benchmark_name,
                price_history,
                signal_date
            )
        )

        if start_data:
            start_price = float(
                start_data[
                    "price"
                ]
            )

        else:
            start_price = None

        base_result = {
            "benchmark": (
                benchmark_name
            ),

            "target_days": (
                days_forward
            ),

            "target_date": (
                target_date.isoformat()
            ),

            "start_price": (
                round(
                    start_price,
                    4
                )
                if start_price is not None
                else None
            ),

            "start_price_date": (
                start_data.get(
                    "date"
                )
                if start_data
                else None
            ),

            "start_price_timestamp": (
                start_data.get(
                    "timestamp"
                )
                if start_data
                else None
            ),

            "start_price_source": (
                start_data.get(
                    "source"
                )
                if start_data
                else None
            ),

            "start_price_method": (
                start_data.get(
                    "method"
                )
                if start_data
                else None
            ),

            "future_date": None,

            "future_price": None,

            "return_pct": None,

            "market_move": (
                "pending"
            ),
        }

        if (
            elapsed_days
            < days_forward
        ):
            base_result[
                "status"
            ] = "pending"

            return base_result

        if (
            start_price is None
        ):
            base_result[
                "status"
            ] = (
                "start_price_unavailable"
            )

            return base_result

        future_market_data = (
            self._find_future_price(
                price_history,
                target_date
            )
        )

        if not future_market_data:
            base_result[
                "status"
            ] = (
                "market_data_unavailable"
            )

            return base_result

        future_price = float(
            future_market_data[
                "price"
            ]
        )

        market_return = (
            self._calculate_return(
                start_price,
                future_price
            )
        )

        if (
            market_return
            is not None
        ):
            market_return = round(
                market_return,
                2
            )

        market_move = (
            self._classify_market_move(
                benchmark_name,
                horizon_name,
                market_return
            )
        )

        base_result.update(
            {
                "status": (
                    "evaluated"
                ),

                "future_date": (
                    future_market_data[
                        "date"
                    ]
                ),

                "future_price": round(
                    future_price,
                    4
                ),

                "return_pct": (
                    market_return
                ),

                "market_move": (
                    market_move
                ),
            }
        )

        return base_result

    def evaluate_history(
        self
    ):
        signal_history = (
            self._load_json(
                self.history_file
            )
        )

        if not signal_history:
            return {
                "status": (
                    "no_history"
                ),

                "evaluated_records": 0,

                "results": [],
            }

        price_histories = (
            self._load_all_price_histories()
        )

        primary_history = (
            price_histories.get(
                self.primary_benchmark
            )
        )

        if (
            primary_history is None
        ):
            return {
                "status": (
                    "market_data_unavailable"
                ),

                "evaluated_records": 0,

                "results": [],
            }

        evaluation_results = []

        today = (
            datetime.now().date()
        )

        for record in (
            signal_history
        ):
            timestamp_text = (
                record.get(
                    "timestamp"
                )
            )

            if not timestamp_text:
                continue

            try:
                signal_datetime = (
                    datetime.fromisoformat(
                        timestamp_text
                    )
                )

                signal_date = (
                    signal_datetime.date()
                )

            except Exception:
                continue

            evaluation = {
                "timestamp": (
                    timestamp_text
                ),

                "signal_date": (
                    signal_date.isoformat()
                ),

                "decision": record.get(
                    "decision",
                    "HOLD"
                ),

                "market_regime": record.get(
                    "market_regime",
                    "MIXED"
                ),

                "market_score": float(
                    record.get(
                        "market_score",
                        0.50
                    )
                ),

                "average_confidence": float(
                    record.get(
                        "average_confidence",
                        0.0
                    )
                ),

                "agents": record.get(
                    "agents",
                    {}
                ),

                "benchmarks": {},
            }

            for (
                benchmark_name,
                price_history
            ) in price_histories.items():
                evaluation[
                    "benchmarks"
                ][benchmark_name] = {}

                for (
                    horizon_name,
                    days_forward
                ) in self.horizons.items():
                    benchmark_result = (
                        self._evaluate_benchmark_horizon(
                            record=record,
                            signal_date=signal_date,
                            today=today,
                            benchmark_name=benchmark_name,
                            price_history=price_history,
                            horizon_name=horizon_name,
                            days_forward=days_forward,
                        )
                    )

                    evaluation[
                        "benchmarks"
                    ][benchmark_name][
                        horizon_name
                    ] = (
                        benchmark_result
                    )

            evaluation[
                "horizons"
            ] = {}

            spy_results = (
                evaluation
                .get(
                    "benchmarks",
                    {}
                )
                .get(
                    self.primary_benchmark,
                    {}
                )
            )

            for horizon_name in (
                self.horizons
            ):
                spy_horizon = (
                    spy_results.get(
                        horizon_name,
                        {}
                    )
                )

                market_move = (
                    spy_horizon.get(
                        "market_move",
                        "pending"
                    )
                )

                decision_outcome = (
                    self._classify_decision_outcome(
                        record.get(
                            "decision",
                            "HOLD"
                        ),
                        market_move
                    )
                )

                combined_result = dict(
                    spy_horizon
                )

                combined_result[
                    "decision_outcome"
                ] = (
                    decision_outcome
                )

                evaluation[
                    "horizons"
                ][horizon_name] = (
                    combined_result
                )

            evaluation_results.append(
                evaluation
            )

        summary = (
            self._build_summary(
                evaluation_results
            )
        )

        decision_stats = (
            self._build_decision_stats(
                evaluation_results
            )
        )

        agent_stats = (
            self._build_agent_stats(
                evaluation_results
            )
        )

        benchmark_summary = (
            self._build_benchmark_summary(
                evaluation_results
            )
        )

        agent_leaderboard = (
            self._build_agent_leaderboard(
                agent_stats
            )
        )

        output_payload = {
            "generated_at": (
                datetime.now().isoformat()
            ),

            "primary_benchmark": (
                self.primary_benchmark
            ),

            "benchmark_symbols": (
                self.benchmark_symbols
            ),

            "agent_benchmarks": (
                self.agent_benchmarks
            ),

            "total_records": len(
                evaluation_results
            ),

            "summary": (
                summary
            ),

            "benchmark_summary": (
                benchmark_summary
            ),

            "decision_stats": (
                decision_stats
            ),

            "agent_stats": (
                agent_stats
            ),

            "agent_leaderboard": (
                agent_leaderboard
            ),

            "results": (
                evaluation_results
            ),
        }

        self._save_json(
            self.evaluation_file,
            output_payload
        )

        return {
            "status": (
                "success"
            ),

            "benchmark": (
                self.primary_benchmark
            ),

            "benchmarks": list(
                self.benchmark_symbols.keys()
            ),

            "agent_benchmarks": (
                self.agent_benchmarks
            ),

            "evaluated_records": len(
                evaluation_results
            ),

            "results": (
                evaluation_results
            ),

            "summary": (
                summary
            ),

            "benchmark_summary": (
                benchmark_summary
            ),

            "decision_stats": (
                decision_stats
            ),

            "agent_stats": (
                agent_stats
            ),

            "agent_leaderboard": (
                agent_leaderboard
            ),

            "evaluation_file": (
                self.evaluation_file
            ),
        }

    def _build_summary(
        self,
        evaluation_results
    ):
        summary = {}

        for horizon in [
            "1d",
            "7d",
            "30d",
        ]:
            correct = 0
            incorrect = 0
            pending = 0

            returns = []

            for result in (
                evaluation_results
            ):
                horizon_result = (
                    result
                    .get(
                        "horizons",
                        {}
                    )
                    .get(
                        horizon,
                        {}
                    )
                )

                outcome = (
                    horizon_result.get(
                        "decision_outcome"
                    )
                )

                market_return = (
                    horizon_result.get(
                        "return_pct"
                    )
                )

                if (
                    outcome
                    == "correct"
                ):
                    correct += 1

                elif (
                    outcome
                    == "incorrect"
                ):
                    incorrect += 1

                else:
                    pending += 1

                if (
                    market_return
                    is not None
                ):
                    returns.append(
                        float(
                            market_return
                        )
                    )

            evaluated = (
                correct
                + incorrect
            )

            if (
                evaluated
                > 0
            ):
                accuracy = (
                    correct
                    / evaluated
                    * 100
                )

            else:
                accuracy = None

            if returns:
                average_return = (
                    sum(
                        returns
                    )
                    / len(
                        returns
                    )
                )

                best_return = max(
                    returns
                )

                worst_return = min(
                    returns
                )

            else:
                average_return = None
                best_return = None
                worst_return = None

            summary[
                horizon
            ] = {
                "correct": (
                    correct
                ),

                "incorrect": (
                    incorrect
                ),

                "pending": (
                    pending
                ),

                "total_evaluated": (
                    evaluated
                ),

                "accuracy_pct": (
                    round(
                        accuracy,
                        2
                    )
                    if accuracy is not None
                    else None
                ),

                "average_market_return_pct": (
                    round(
                        average_return,
                        2
                    )
                    if average_return is not None
                    else None
                ),

                "best_market_return_pct": (
                    round(
                        best_return,
                        2
                    )
                    if best_return is not None
                    else None
                ),

                "worst_market_return_pct": (
                    round(
                        worst_return,
                        2
                    )
                    if worst_return is not None
                    else None
                ),
            }

        return summary

    def _build_decision_stats(
        self,
        evaluation_results
    ):
        decision_stats = {}

        for decision_name in [
            "BUY",
            "HOLD",
            "AVOID",
        ]:
            decision_stats[
                decision_name
            ] = {}

            for horizon in [
                "1d",
                "7d",
                "30d",
            ]:
                total = 0
                correct = 0
                incorrect = 0
                pending = 0

                returns = []

                for result in (
                    evaluation_results
                ):
                    decision = str(
                        result.get(
                            "decision",
                            "HOLD"
                        )
                    ).upper()

                    if (
                        decision
                        != decision_name
                    ):
                        continue

                    total += 1

                    horizon_result = (
                        result
                        .get(
                            "horizons",
                            {}
                        )
                        .get(
                            horizon,
                            {}
                        )
                    )

                    outcome = (
                        horizon_result.get(
                            "decision_outcome"
                        )
                    )

                    market_return = (
                        horizon_result.get(
                            "return_pct"
                        )
                    )

                    if (
                        outcome
                        == "correct"
                    ):
                        correct += 1

                    elif (
                        outcome
                        == "incorrect"
                    ):
                        incorrect += 1

                    else:
                        pending += 1

                    if (
                        market_return
                        is not None
                    ):
                        returns.append(
                            float(
                                market_return
                            )
                        )

                evaluated = (
                    correct
                    + incorrect
                )

                if (
                    evaluated
                    > 0
                ):
                    accuracy = (
                        correct
                        / evaluated
                        * 100
                    )

                else:
                    accuracy = None

                if returns:
                    average_return = (
                        sum(
                            returns
                        )
                        / len(
                            returns
                        )
                    )

                else:
                    average_return = None

                decision_stats[
                    decision_name
                ][horizon] = {
                    "total_signals": (
                        total
                    ),

                    "evaluated": (
                        evaluated
                    ),

                    "correct": (
                        correct
                    ),

                    "incorrect": (
                        incorrect
                    ),

                    "pending": (
                        pending
                    ),

                    "accuracy_pct": (
                        round(
                            accuracy,
                            2
                        )
                        if accuracy is not None
                        else None
                    ),

                    "average_return_pct": (
                        round(
                            average_return,
                            2
                        )
                        if average_return is not None
                        else None
                    ),
                }

        return decision_stats

    def _build_agent_stats(
        self,
        evaluation_results
    ):
        agent_stats = {}

        for agent_name in (
            self.agent_order
        ):
            benchmark_name = (
                self.agent_benchmarks.get(
                    agent_name,
                    "SPY"
                )
            )

            agent_stats[
                agent_name
            ] = {}

            for horizon in [
                "1d",
                "7d",
                "30d",
            ]:
                total_signals = 0
                evaluated = 0
                correct = 0
                incorrect = 0
                pending = 0

                bullish_signals = 0
                neutral_signals = 0
                bearish_signals = 0

                confidence_values = []
                score_values = []
                benchmark_returns = []

                for result in (
                    evaluation_results
                ):
                    agents = (
                        result.get(
                            "agents",
                            {}
                        )
                    )

                    agent_data = (
                        agents.get(
                            agent_name
                        )
                    )

                    if not agent_data:
                        continue

                    total_signals += 1

                    agent_signal = str(
                        agent_data.get(
                            "signal",
                            "neutral"
                        )
                    ).lower()

                    if (
                        agent_signal
                        == "bullish"
                    ):
                        bullish_signals += 1

                    elif (
                        agent_signal
                        == "bearish"
                    ):
                        bearish_signals += 1

                    else:
                        neutral_signals += 1

                    try:
                        confidence_values.append(
                            float(
                                agent_data.get(
                                    "confidence",
                                    0.0
                                )
                            )
                        )

                    except Exception:
                        pass

                    try:
                        score_values.append(
                            float(
                                agent_data.get(
                                    "score",
                                    0.50
                                )
                            )
                        )

                    except Exception:
                        pass

                    benchmark_result = (
                        result
                        .get(
                            "benchmarks",
                            {}
                        )
                        .get(
                            benchmark_name,
                            {}
                        )
                        .get(
                            horizon,
                            {}
                        )
                    )

                    market_move = (
                        benchmark_result.get(
                            "market_move",
                            "pending"
                        )
                    )

                    benchmark_return = (
                        benchmark_result.get(
                            "return_pct"
                        )
                    )

                    agent_outcome = (
                        self._classify_agent_outcome(
                            agent_signal,
                            market_move
                        )
                    )

                    if (
                        agent_outcome
                        == "correct"
                    ):
                        correct += 1
                        evaluated += 1

                    elif (
                        agent_outcome
                        == "incorrect"
                    ):
                        incorrect += 1
                        evaluated += 1

                    else:
                        pending += 1

                    if (
                        benchmark_return
                        is not None
                    ):
                        benchmark_returns.append(
                            float(
                                benchmark_return
                            )
                        )

                if (
                    evaluated
                    > 0
                ):
                    accuracy = (
                        correct
                        / evaluated
                        * 100
                    )

                else:
                    accuracy = None

                if confidence_values:
                    average_confidence = (
                        sum(
                            confidence_values
                        )
                        / len(
                            confidence_values
                        )
                    )

                else:
                    average_confidence = None

                if score_values:
                    average_score = (
                        sum(
                            score_values
                        )
                        / len(
                            score_values
                        )
                    )

                else:
                    average_score = None

                if benchmark_returns:
                    average_benchmark_return = (
                        sum(
                            benchmark_returns
                        )
                        / len(
                            benchmark_returns
                        )
                    )

                else:
                    average_benchmark_return = None

                agent_stats[
                    agent_name
                ][horizon] = {
                    "benchmark": (
                        benchmark_name
                    ),

                    "total_signals": (
                        total_signals
                    ),

                    "evaluated": (
                        evaluated
                    ),

                    "correct": (
                        correct
                    ),

                    "incorrect": (
                        incorrect
                    ),

                    "pending": (
                        pending
                    ),

                    "accuracy_pct": (
                        round(
                            accuracy,
                            2
                        )
                        if accuracy is not None
                        else None
                    ),

                    "average_confidence": (
                        round(
                            average_confidence,
                            2
                        )
                        if average_confidence is not None
                        else None
                    ),

                    "average_score": (
                        round(
                            average_score,
                            2
                        )
                        if average_score is not None
                        else None
                    ),

                    "average_benchmark_return_pct": (
                        round(
                            average_benchmark_return,
                            2
                        )
                        if average_benchmark_return is not None
                        else None
                    ),

                    "bullish_signals": (
                        bullish_signals
                    ),

                    "neutral_signals": (
                        neutral_signals
                    ),

                    "bearish_signals": (
                        bearish_signals
                    ),
                }

        return agent_stats

    def _build_benchmark_summary(
        self,
        evaluation_results
    ):
        benchmark_summary = {}

        for benchmark_name in (
            self.benchmark_symbols
        ):
            benchmark_summary[
                benchmark_name
            ] = {}

            for horizon in [
                "1d",
                "7d",
                "30d",
            ]:
                evaluated = 0
                pending = 0

                bullish = 0
                neutral = 0
                bearish = 0

                returns = []

                for result in (
                    evaluation_results
                ):
                    benchmark_result = (
                        result
                        .get(
                            "benchmarks",
                            {}
                        )
                        .get(
                            benchmark_name,
                            {}
                        )
                        .get(
                            horizon,
                            {}
                        )
                    )

                    status = (
                        benchmark_result.get(
                            "status"
                        )
                    )

                    market_move = (
                        benchmark_result.get(
                            "market_move",
                            "pending"
                        )
                    )

                    market_return = (
                        benchmark_result.get(
                            "return_pct"
                        )
                    )

                    if (
                        status
                        == "evaluated"
                    ):
                        evaluated += 1

                    else:
                        pending += 1

                    if (
                        market_move
                        == "bullish"
                    ):
                        bullish += 1

                    elif (
                        market_move
                        == "bearish"
                    ):
                        bearish += 1

                    elif (
                        market_move
                        == "neutral"
                    ):
                        neutral += 1

                    if (
                        market_return
                        is not None
                    ):
                        returns.append(
                            float(
                                market_return
                            )
                        )

                if returns:
                    average_return = (
                        sum(
                            returns
                        )
                        / len(
                            returns
                        )
                    )

                else:
                    average_return = None

                benchmark_summary[
                    benchmark_name
                ][horizon] = {
                    "evaluated": (
                        evaluated
                    ),

                    "pending": (
                        pending
                    ),

                    "bullish_moves": (
                        bullish
                    ),

                    "neutral_moves": (
                        neutral
                    ),

                    "bearish_moves": (
                        bearish
                    ),

                    "average_return_pct": (
                        round(
                            average_return,
                            2
                        )
                        if average_return is not None
                        else None
                    ),

                    "threshold_pct": (
                        self._get_threshold(
                            benchmark_name,
                            horizon
                        )
                    ),
                }

        return benchmark_summary

    def _build_agent_leaderboard(
        self,
        agent_stats
    ):
        leaderboard = []

        for agent_name in (
            self.agent_order
        ):
            benchmark_name = (
                self.agent_benchmarks.get(
                    agent_name,
                    "SPY"
                )
            )

            horizon_data = (
                agent_stats.get(
                    agent_name,
                    {}
                )
            )

            total_evaluated = 0
            total_correct = 0
            total_incorrect = 0
            total_pending = 0

            weighted_accuracy_total = 0.0
            available_weight_total = 0.0

            horizon_accuracy = {}

            for horizon_name in [
                "1d",
                "7d",
                "30d",
            ]:
                data = (
                    horizon_data.get(
                        horizon_name,
                        {}
                    )
                )

                evaluated = int(
                    data.get(
                        "evaluated",
                        0
                    )
                )

                correct = int(
                    data.get(
                        "correct",
                        0
                    )
                )

                incorrect = int(
                    data.get(
                        "incorrect",
                        0
                    )
                )

                pending = int(
                    data.get(
                        "pending",
                        0
                    )
                )

                accuracy = (
                    data.get(
                        "accuracy_pct"
                    )
                )

                total_evaluated += (
                    evaluated
                )

                total_correct += (
                    correct
                )

                total_incorrect += (
                    incorrect
                )

                total_pending += (
                    pending
                )

                horizon_accuracy[
                    horizon_name
                ] = (
                    accuracy
                )

                if (
                    accuracy
                    is not None
                    and evaluated > 0
                ):
                    horizon_weight = (
                        self.horizon_weights.get(
                            horizon_name,
                            0.0
                        )
                    )

                    weighted_accuracy_total += (
                        float(
                            accuracy
                        )
                        * horizon_weight
                    )

                    available_weight_total += (
                        horizon_weight
                    )

            if (
                total_evaluated
                > 0
            ):
                raw_accuracy = (
                    total_correct
                    / total_evaluated
                    * 100
                )

            else:
                raw_accuracy = None

            if (
                available_weight_total
                > 0
            ):
                weighted_accuracy = (
                    weighted_accuracy_total
                    / available_weight_total
                )

            else:
                weighted_accuracy = None

            if (
                total_evaluated
                > 0
            ):
                sample_factor = min(
                    total_evaluated
                    / self.minimum_samples_for_reliable_rank,
                    1.0
                )

            else:
                sample_factor = 0.0

            if (
                weighted_accuracy
                is not None
            ):
                leaderboard_score = (
                    weighted_accuracy
                    * sample_factor
                )

            else:
                leaderboard_score = None

            reliable = (
                total_evaluated
                >= self.minimum_samples_for_reliable_rank
            )

            if (
                total_evaluated
                == 0
            ):
                status = (
                    "pending"
                )

            elif reliable:
                status = (
                    "reliable"
                )

            else:
                status = (
                    "provisional"
                )

            leaderboard.append(
                {
                    "rank": None,

                    "agent": (
                        agent_name
                    ),

                    "benchmark": (
                        benchmark_name
                    ),

                    "status": (
                        status
                    ),

                    "reliable": (
                        reliable
                    ),

                    "samples": (
                        total_evaluated
                    ),

                    "correct": (
                        total_correct
                    ),

                    "incorrect": (
                        total_incorrect
                    ),

                    "pending": (
                        total_pending
                    ),

                    "accuracy_pct": (
                        round(
                            raw_accuracy,
                            2
                        )
                        if raw_accuracy is not None
                        else None
                    ),

                    "weighted_accuracy_pct": (
                        round(
                            weighted_accuracy,
                            2
                        )
                        if weighted_accuracy is not None
                        else None
                    ),

                    "sample_factor": (
                        round(
                            sample_factor,
                            4
                        )
                    ),

                    "leaderboard_score": (
                        round(
                            leaderboard_score,
                            2
                        )
                        if leaderboard_score is not None
                        else None
                    ),

                    "horizon_accuracy": (
                        horizon_accuracy
                    ),
                }
            )

        leaderboard.sort(
            key=lambda item: (
                item.get(
                    "leaderboard_score"
                )
                if item.get(
                    "leaderboard_score"
                )
                is not None
                else -1.0,

                item.get(
                    "samples",
                    0
                ),

                item.get(
                    "weighted_accuracy_pct"
                )
                if item.get(
                    "weighted_accuracy_pct"
                )
                is not None
                else -1.0,
            ),
            reverse=True,
        )

        rank = 1

        for item in leaderboard:
            if (
                item.get(
                    "samples",
                    0
                )
                > 0
            ):
                item[
                    "rank"
                ] = rank

                rank += 1

        return leaderboard