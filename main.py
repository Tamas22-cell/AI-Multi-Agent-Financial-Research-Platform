from orchestrator import Orchestrator
from reports.report_generator import ReportGenerator
from signal_history import SignalHistory
from evaluation import SignalEvaluator


def format_accuracy(value):
    if value is None:
        return "pending"

    return f"{value:.2f}%"


def format_return(value):
    if value is None:
        return "pending"

    return f"{value:+.2f}%"


def format_number(value):
    if value is None:
        return "pending"

    return f"{value:.2f}"


def main():
    print("=" * 78)
    print("AI MULTI-AGENT FINANCIAL RESEARCH PLATFORM")
    print("=" * 78)

    orchestrator = Orchestrator()
    output = orchestrator.run()

    print()

    # --------------------------------------------------
    # AGENT RESULTS
    # --------------------------------------------------

    for result in output["agents"]:
        print(
            f"{result['agent'].upper():15} | "
            f"{result['signal'].upper():8} | "
            f"score={result['score']:.2f} | "
            f"confidence={result['confidence']:.2f}"
        )

    # --------------------------------------------------
    # FINAL MARKET REPORT
    # --------------------------------------------------

    print()
    print("=" * 78)
    print("ORCHESTRATOR FINAL MARKET REPORT")
    print("=" * 78)

    print(
        f"Decision          : "
        f"{output['decision']}"
    )

    print(
        f"Market Regime     : "
        f"{output['market_regime']}"
    )

    print(
        f"Market Score      : "
        f"{output['market_score']:.2f}"
    )

    print(
        f"Average Confidence: "
        f"{output.get('average_confidence', 0.0):.2f}"
    )

    print(
        f"Consensus Strength: "
        f"{output.get('consensus_strength', 0.0):.1f}%"
    )

    print(
        f"Bullish %         : "
        f"{output.get('bullish_pct', 0.0):.1f}%"
    )

    print(
        f"Neutral %         : "
        f"{output.get('neutral_pct', 0.0):.1f}%"
    )

    print(
        f"Bearish %         : "
        f"{output.get('bearish_pct', 0.0):.1f}%"
    )

    print(
        f"Signal Conflict   : "
        f"{output.get('signal_conflict', False)}"
    )

    print(
        f"Risk Override     : "
        f"{output.get('risk_override', False)}"
    )

    bullish_agents = ", ".join(
        output.get(
            "bullish_agents",
            []
        )
    ) or "None"

    neutral_agents = ", ".join(
        output.get(
            "neutral_agents",
            []
        )
    ) or "None"

    bearish_agents = ", ".join(
        output.get(
            "bearish_agents",
            []
        )
    ) or "None"

    print(
        f"Bullish Agents    : "
        f"{bullish_agents}"
    )

    print(
        f"Neutral Agents    : "
        f"{neutral_agents}"
    )

    print(
        f"Bearish Agents    : "
        f"{bearish_agents}"
    )

    # --------------------------------------------------
    # MARKET INTERPRETATION
    # --------------------------------------------------

    print()
    print("MARKET INTERPRETATION")
    print("-" * 78)

    print(
        output.get(
            "market_interpretation",
            "No interpretation available."
        )
    )

    # --------------------------------------------------
    # STRONGEST SIGNALS
    # --------------------------------------------------

    strongest_positive = output.get(
        "strongest_bullish_agent"
    )

    strongest_negative = output.get(
        "strongest_bearish_agent"
    )

    print()
    print("STRONGEST SIGNALS")
    print("-" * 78)

    if strongest_positive:
        print(
            f"Strongest Positive : "
            f"{strongest_positive.get('agent', 'unknown').upper()} | "
            f"{strongest_positive.get('signal', 'neutral').upper()} | "
            f"score={strongest_positive.get('score', 0.50):.2f}"
        )

    else:
        print(
            "Strongest Positive : None"
        )

    if strongest_negative:
        print(
            f"Strongest Negative : "
            f"{strongest_negative.get('agent', 'unknown').upper()} | "
            f"{strongest_negative.get('signal', 'neutral').upper()} | "
            f"score={strongest_negative.get('score', 0.50):.2f}"
        )

    else:
        print(
            "Strongest Negative : None"
        )

    # --------------------------------------------------
    # TOP POSITIVE SIGNALS
    # --------------------------------------------------

    print()
    print("TOP POSITIVE SIGNALS")
    print("-" * 78)

    positive_signals = output.get(
        "top_positive_signals",
        []
    )

    if positive_signals:
        for index, signal in enumerate(
            positive_signals,
            start=1
        ):
            print(
                f"{index}. {signal}"
            )

    else:
        print(
            "No material positive signals detected."
        )

    # --------------------------------------------------
    # TOP RISKS
    # --------------------------------------------------

    print()
    print("TOP RISKS")
    print("-" * 78)

    top_risks = output.get(
        "top_risks",
        []
    )

    if top_risks:
        for index, risk in enumerate(
            top_risks,
            start=1
        ):
            print(
                f"{index}. {risk}"
            )

    else:
        print(
            "No major bearish risks detected."
        )

    # --------------------------------------------------
    # REPORT FILES
    # --------------------------------------------------

    report_generator = ReportGenerator()

    txt_report = (
        report_generator.generate_text_report(
            output
        )
    )

    json_report = (
        report_generator.generate_json_report(
            output
        )
    )

    print()
    print("REPORT FILES")
    print("-" * 78)

    print(
        f"TXT  : {txt_report}"
    )

    print(
        f"JSON : {json_report}"
    )

    # --------------------------------------------------
    # SIGNAL HISTORY
    # --------------------------------------------------

    signal_history = SignalHistory()

    history_result = (
        signal_history.record_signal(
            output
        )
    )

    print()
    print("SIGNAL HISTORY")
    print("-" * 78)

    print(
        f"Total Records : "
        f"{history_result['total_records']}"
    )

    print(
        f"Saved To      : "
        f"{history_result['history_file']}"
    )

    benchmark_snapshot = (
        history_result.get(
            "benchmarks",
            {}
        )
    )

    if benchmark_snapshot:
        print()
        print("BENCHMARK SNAPSHOT")
        print("-" * 78)

        for benchmark_name in [
            "SPY",
            "BTC-USD",
        ]:
            benchmark_data = (
                benchmark_snapshot.get(
                    benchmark_name,
                    {}
                )
            )

            price = benchmark_data.get(
                "price"
            )

            source = benchmark_data.get(
                "source",
                "unknown"
            )

            timestamp = benchmark_data.get(
                "price_timestamp"
            )

            if price is None:
                price_text = "unavailable"

            else:
                price_text = (
                    f"{price:.4f}"
                )

            print(
                f"{benchmark_name:10} | "
                f"Price={price_text} | "
                f"Source={source} | "
                f"Time={timestamp}"
            )

    # --------------------------------------------------
    # SIGNAL EVALUATION
    # --------------------------------------------------

    evaluator = SignalEvaluator()

    evaluation_result = (
        evaluator.evaluate_history()
    )

    print()
    print("EVALUATION")
    print("-" * 78)

    evaluation_status = (
        evaluation_result.get(
            "status",
            "unknown"
        )
    )

    print(
        f"Status           : "
        f"{evaluation_status}"
    )

    if evaluation_status == "success":
        print(
            f"Primary Benchmark: "
            f"{evaluation_result.get('benchmark', 'SPY')}"
        )

        benchmarks = (
            evaluation_result.get(
                "benchmarks",
                []
            )
        )

        print(
            f"Benchmarks       : "
            f"{', '.join(benchmarks) if benchmarks else 'None'}"
        )

        print(
            f"Records          : "
            f"{evaluation_result.get('evaluated_records', 0)}"
        )

        summary = (
            evaluation_result.get(
                "summary",
                {}
            )
        )

        for horizon in [
            "1d",
            "7d",
            "30d",
        ]:
            horizon_data = (
                summary.get(
                    horizon,
                    {}
                )
            )

            accuracy = (
                horizon_data.get(
                    "accuracy_pct"
                )
            )

            avg_return = (
                horizon_data.get(
                    "average_market_return_pct"
                )
            )

            pending = (
                horizon_data.get(
                    "pending",
                    0
                )
            )

            evaluated = (
                horizon_data.get(
                    "total_evaluated",
                    0
                )
            )

            print(
                f"{horizon.upper():4} Accuracy      : "
                f"{format_accuracy(accuracy)}"
            )

            print(
                f"{horizon.upper():4} Avg Return    : "
                f"{format_return(avg_return)}"
            )

            print(
                f"{horizon.upper():4} Evaluated     : "
                f"{evaluated}"
            )

            print(
                f"{horizon.upper():4} Pending       : "
                f"{pending}"
            )

        print(
            f"Saved To         : "
            f"{evaluation_result.get('evaluation_file')}"
        )

        # --------------------------------------------------
        # BENCHMARK PERFORMANCE
        # --------------------------------------------------

        print()
        print("=" * 78)
        print("BENCHMARK PERFORMANCE")
        print("=" * 78)

        benchmark_summary = (
            evaluation_result.get(
                "benchmark_summary",
                {}
            )
        )

        for benchmark_name in [
            "SPY",
            "BTC-USD",
        ]:
            benchmark_data = (
                benchmark_summary.get(
                    benchmark_name,
                    {}
                )
            )

            print()
            print(
                benchmark_name
            )

            print("-" * 78)

            for horizon in [
                "1d",
                "7d",
                "30d",
            ]:
                horizon_data = (
                    benchmark_data.get(
                        horizon,
                        {}
                    )
                )

                evaluated = (
                    horizon_data.get(
                        "evaluated",
                        0
                    )
                )

                pending = (
                    horizon_data.get(
                        "pending",
                        0
                    )
                )

                bullish_moves = (
                    horizon_data.get(
                        "bullish_moves",
                        0
                    )
                )

                neutral_moves = (
                    horizon_data.get(
                        "neutral_moves",
                        0
                    )
                )

                bearish_moves = (
                    horizon_data.get(
                        "bearish_moves",
                        0
                    )
                )

                avg_return = (
                    horizon_data.get(
                        "average_return_pct"
                    )
                )

                threshold = (
                    horizon_data.get(
                        "threshold_pct"
                    )
                )

                print(
                    f"{horizon.upper():4} | "
                    f"Evaluated={evaluated} | "
                    f"Pending={pending} | "
                    f"Avg Return={format_return(avg_return)}"
                )

                print(
                    f"     Bullish={bullish_moves} | "
                    f"Neutral={neutral_moves} | "
                    f"Bearish={bearish_moves} | "
                    f"Threshold={format_number(threshold)}%"
                )

        # --------------------------------------------------
        # DECISION PERFORMANCE
        # --------------------------------------------------

        print()
        print("=" * 78)
        print("DECISION PERFORMANCE")
        print("=" * 78)

        decision_stats = (
            evaluation_result.get(
                "decision_stats",
                {}
            )
        )

        for decision_name in [
            "BUY",
            "HOLD",
            "AVOID",
        ]:
            print()
            print(
                decision_name
            )

            decision_data = (
                decision_stats.get(
                    decision_name,
                    {}
                )
            )

            for horizon in [
                "1d",
                "7d",
                "30d",
            ]:
                horizon_data = (
                    decision_data.get(
                        horizon,
                        {}
                    )
                )

                total_signals = (
                    horizon_data.get(
                        "total_signals",
                        0
                    )
                )

                evaluated = (
                    horizon_data.get(
                        "evaluated",
                        0
                    )
                )

                pending = (
                    horizon_data.get(
                        "pending",
                        0
                    )
                )

                correct = (
                    horizon_data.get(
                        "correct",
                        0
                    )
                )

                incorrect = (
                    horizon_data.get(
                        "incorrect",
                        0
                    )
                )

                accuracy = (
                    horizon_data.get(
                        "accuracy_pct"
                    )
                )

                avg_return = (
                    horizon_data.get(
                        "average_return_pct"
                    )
                )

                print(
                    f"  {horizon.upper():4} | "
                    f"Signals={total_signals} | "
                    f"Evaluated={evaluated} | "
                    f"Pending={pending} | "
                    f"Correct={correct} | "
                    f"Incorrect={incorrect} | "
                    f"Accuracy={format_accuracy(accuracy)} | "
                    f"Avg Return={format_return(avg_return)}"
                )

        # --------------------------------------------------
        # AGENT PERFORMANCE
        # --------------------------------------------------

        print()
        print("=" * 78)
        print("AGENT PERFORMANCE")
        print("=" * 78)

        agent_stats = (
            evaluation_result.get(
                "agent_stats",
                {}
            )
        )

        agent_order = [
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

        for agent_name in agent_order:
            agent_data = (
                agent_stats.get(
                    agent_name,
                    {}
                )
            )

            benchmark_name = (
                evaluation_result
                .get(
                    "agent_benchmarks",
                    {}
                )
                .get(
                    agent_name,
                    "SPY"
                )
            )

            print()
            print(
                agent_name.upper()
            )

            print(
                f"Benchmark: "
                f"{benchmark_name}"
            )

            print("-" * 78)

            for horizon in [
                "1d",
                "7d",
                "30d",
            ]:
                horizon_data = (
                    agent_data.get(
                        horizon,
                        {}
                    )
                )

                total_signals = (
                    horizon_data.get(
                        "total_signals",
                        0
                    )
                )

                evaluated = (
                    horizon_data.get(
                        "evaluated",
                        0
                    )
                )

                pending = (
                    horizon_data.get(
                        "pending",
                        0
                    )
                )

                correct = (
                    horizon_data.get(
                        "correct",
                        0
                    )
                )

                incorrect = (
                    horizon_data.get(
                        "incorrect",
                        0
                    )
                )

                accuracy = (
                    horizon_data.get(
                        "accuracy_pct"
                    )
                )

                avg_confidence = (
                    horizon_data.get(
                        "average_confidence"
                    )
                )

                avg_score = (
                    horizon_data.get(
                        "average_score"
                    )
                )

                avg_benchmark_return = (
                    horizon_data.get(
                        "average_benchmark_return_pct"
                    )
                )

                bullish_signals = (
                    horizon_data.get(
                        "bullish_signals",
                        0
                    )
                )

                neutral_signals = (
                    horizon_data.get(
                        "neutral_signals",
                        0
                    )
                )

                bearish_signals = (
                    horizon_data.get(
                        "bearish_signals",
                        0
                    )
                )

                print(
                    f"{horizon.upper():4} | "
                    f"Signals={total_signals} | "
                    f"Evaluated={evaluated} | "
                    f"Pending={pending}"
                )

                print(
                    f"     Correct={correct} | "
                    f"Incorrect={incorrect} | "
                    f"Accuracy={format_accuracy(accuracy)}"
                )

                print(
                    f"     Avg Score={format_number(avg_score)} | "
                    f"Avg Confidence={format_number(avg_confidence)}"
                )

                print(
                    f"     Benchmark Return="
                    f"{format_return(avg_benchmark_return)}"
                )

                print(
                    f"     Bullish={bullish_signals} | "
                    f"Neutral={neutral_signals} | "
                    f"Bearish={bearish_signals}"
                )

        # --------------------------------------------------
        # AGENT LEADERBOARD
        # --------------------------------------------------

        print()
        print("=" * 78)
        print("AGENT LEADERBOARD")
        print("=" * 78)

        leaderboard = (
            evaluation_result.get(
                "agent_leaderboard",
                []
            )
        )

        if leaderboard:
            for item in leaderboard:
                rank = (
                    item.get(
                        "rank"
                    )
                )

                agent_name = str(
                    item.get(
                        "agent",
                        "unknown"
                    )
                ).upper()

                benchmark_name = (
                    item.get(
                        "benchmark",
                        "SPY"
                    )
                )

                status = str(
                    item.get(
                        "status",
                        "pending"
                    )
                ).upper()

                samples = (
                    item.get(
                        "samples",
                        0
                    )
                )

                correct = (
                    item.get(
                        "correct",
                        0
                    )
                )

                incorrect = (
                    item.get(
                        "incorrect",
                        0
                    )
                )

                accuracy = (
                    item.get(
                        "accuracy_pct"
                    )
                )

                weighted_accuracy = (
                    item.get(
                        "weighted_accuracy_pct"
                    )
                )

                leaderboard_score = (
                    item.get(
                        "leaderboard_score"
                    )
                )

                reliable = (
                    item.get(
                        "reliable",
                        False
                    )
                )

                horizon_accuracy = (
                    item.get(
                        "horizon_accuracy",
                        {}
                    )
                )

                if rank is None:
                    rank_text = "-"

                else:
                    rank_text = str(
                        rank
                    )

                print()
                print(
                    f"Rank {rank_text} | "
                    f"{agent_name}"
                )

                print(
                    f"Benchmark        : "
                    f"{benchmark_name}"
                )

                print(
                    f"Status           : "
                    f"{status}"
                )

                print(
                    f"Reliable         : "
                    f"{reliable}"
                )

                print(
                    f"Samples          : "
                    f"{samples}"
                )

                print(
                    f"Correct          : "
                    f"{correct}"
                )

                print(
                    f"Incorrect        : "
                    f"{incorrect}"
                )

                print(
                    f"Raw Accuracy     : "
                    f"{format_accuracy(accuracy)}"
                )

                print(
                    f"Weighted Accuracy: "
                    f"{format_accuracy(weighted_accuracy)}"
                )

                print(
                    f"Leaderboard Score: "
                    f"{format_number(leaderboard_score)}"
                )

                print(
                    f"1D Accuracy      : "
                    f"{format_accuracy(horizon_accuracy.get('1d'))}"
                )

                print(
                    f"7D Accuracy      : "
                    f"{format_accuracy(horizon_accuracy.get('7d'))}"
                )

                print(
                    f"30D Accuracy     : "
                    f"{format_accuracy(horizon_accuracy.get('30d'))}"
                )

                print("-" * 78)

        else:
            print(
                "No leaderboard data available."
            )

    elif evaluation_status == "no_history":
        print(
            "No signal history available for evaluation."
        )

    elif evaluation_status == "market_data_unavailable":
        print(
            "Benchmark market data is currently unavailable."
        )

    else:
        print(
            "Evaluation could not be completed."
        )

    # --------------------------------------------------
    # FINAL AGENT CHECK
    # --------------------------------------------------

    print()
    print("=" * 78)
    print("FINAL AGENT CHECK")
    print("=" * 78)

    agent_order = [
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

    for agent_name in agent_order:
        result = next(
            (
                item
                for item in output["agents"]
                if item.get("agent") == agent_name
            ),
            None
        )

        if result:
            print(
                f"{agent_name.upper():15} | "
                f"{result['signal'].upper():8} | "
                f"score={result['score']:.2f} | "
                f"confidence={result['confidence']:.2f}"
            )

    # --------------------------------------------------
    # DERIVATIVES RAW DATA
    # --------------------------------------------------

    derivatives_result = next(
        (
            result
            for result in output["agents"]
            if result.get("agent") == "derivatives"
        ),
        None
    )

    print()
    print("=" * 78)
    print("DERIVATIVES RAW DATA")
    print("=" * 78)

    if derivatives_result:
        evidence = (
            derivatives_result.get(
                "evidence",
                {}
            )
        )

        btc_data = (
            evidence.get(
                "BTCUSDT",
                {}
            )
        )

        eth_data = (
            evidence.get(
                "ETHUSDT",
                {}
            )
        )

        summary_data = (
            evidence.get(
                "summary",
                {}
            )
        )

        print(
            f"BTC Funding Current   : "
            f"{btc_data.get('funding_rate_pct', 0.0)}%"
        )

        print(
            f"ETH Funding Current   : "
            f"{eth_data.get('funding_rate_pct', 0.0)}%"
        )

        print(
            f"BTC Funding 8 Periods : "
            f"{btc_data.get('avg_funding_8_periods_pct', 0.0)}%"
        )

        print(
            f"ETH Funding 8 Periods : "
            f"{eth_data.get('avg_funding_8_periods_pct', 0.0)}%"
        )

        print(
            f"BTC Funding Trend     : "
            f"{btc_data.get('funding_trend', 'unknown')}"
        )

        print(
            f"ETH Funding Trend     : "
            f"{eth_data.get('funding_trend', 'unknown')}"
        )

        print(
            f"BTC OI 1H Change      : "
            f"{btc_data.get('oi_change_1h_pct', 0.0)}%"
        )

        print(
            f"ETH OI 1H Change      : "
            f"{eth_data.get('oi_change_1h_pct', 0.0)}%"
        )

        print(
            f"BTC OI 24H Change     : "
            f"{btc_data.get('oi_change_24h_pct', 0.0)}%"
        )

        print(
            f"ETH OI 24H Change     : "
            f"{eth_data.get('oi_change_24h_pct', 0.0)}%"
        )

        print(
            f"Average Funding       : "
            f"{summary_data.get('avg_funding_rate_pct', 0.0)}%"
        )

        print(
            f"Average Funding 8P    : "
            f"{summary_data.get('avg_funding_8_periods_pct', 0.0)}%"
        )

        print(
            f"Average OI 1H Change  : "
            f"{summary_data.get('avg_oi_change_1h_pct', 0.0)}%"
        )

        print(
            f"Average OI 24H Change : "
            f"{summary_data.get('avg_oi_change_24h_pct', 0.0)}%"
        )

        print(
            f"Total OI Notional     : "
            f"{summary_data.get('total_open_interest_notional', 0.0)}"
        )

    else:
        print(
            "No derivatives result available."
        )

    # --------------------------------------------------
    # COMPLETED
    # --------------------------------------------------

    print()
    print("=" * 78)
    print("RESEARCH COMPLETED SUCCESSFULLY")
    print("=" * 78)


if __name__ == "__main__":
    main()