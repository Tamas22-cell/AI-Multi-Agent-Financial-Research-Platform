import json
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    def __init__(self, output_dir="reports/output"):
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def _format_agent_name(self, agent_name):
        if not agent_name:
            return "UNKNOWN"

        return str(
            agent_name
        ).upper()

    def _format_strongest_agent(
        self,
        agent_data
    ):
        if not agent_data:
            return "None"

        agent_name = self._format_agent_name(
            agent_data.get(
                "agent"
            )
        )

        score = float(
            agent_data.get(
                "score",
                0.50
            )
        )

        signal = str(
            agent_data.get(
                "signal",
                "neutral"
            )
        ).upper()

        return (
            f"{agent_name} | "
            f"{signal} | "
            f"score={score:.2f}"
        )

    def _consensus_interpretation(
        self,
        output
    ):
        bullish_pct = float(
            output.get(
                "bullish_pct",
                0.0
            )
        )

        neutral_pct = float(
            output.get(
                "neutral_pct",
                0.0
            )
        )

        bearish_pct = float(
            output.get(
                "bearish_pct",
                0.0
            )
        )

        consensus_strength = float(
            output.get(
                "consensus_strength",
                0.0
            )
        )

        if (
            neutral_pct >= bullish_pct
            and neutral_pct >= bearish_pct
        ):
            return (
                f"{consensus_strength:.1f}% of agents "
                f"agree that current conditions are neutral."
            )

        if bullish_pct >= bearish_pct:
            return (
                f"{consensus_strength:.1f}% consensus "
                f"toward bullish conditions."
            )

        return (
            f"{consensus_strength:.1f}% consensus "
            f"toward bearish conditions."
        )

    def generate_text_report(
        self,
        output
    ):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
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

        average_confidence = float(
            output.get(
                "average_confidence",
                0.0
            )
        )

        consensus_text = (
            self._consensus_interpretation(
                output
            )
        )

        strongest_positive = (
            self._format_strongest_agent(
                output.get(
                    "strongest_bullish_agent"
                )
            )
        )

        strongest_negative = (
            self._format_strongest_agent(
                output.get(
                    "strongest_bearish_agent"
                )
            )
        )

        lines = [
            "AI MULTI-AGENT FINANCIAL RESEARCH PLATFORM",
            "=" * 78,
            f"Generated: {timestamp}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 78,
            f"FINAL DECISION      : {output.get('decision', 'HOLD')}",
            f"MARKET REGIME       : {output.get('market_regime', 'MIXED')}",
            f"MARKET SCORE        : {float(output.get('market_score', 0.50)):.2f}",
            f"AVERAGE CONFIDENCE  : {average_confidence:.2f}",
            "",
            "MARKET INTERPRETATION",
            "-" * 78,
            output.get(
                "market_interpretation",
                "No market interpretation available."
            ),
            "",
            "CONSENSUS",
            "-" * 78,
            f"BULLISH             : {float(output.get('bullish_pct', 0.0)):.1f}%",
            f"NEUTRAL             : {float(output.get('neutral_pct', 0.0)):.1f}%",
            f"BEARISH             : {float(output.get('bearish_pct', 0.0)):.1f}%",
            f"CONSENSUS STRENGTH  : {float(output.get('consensus_strength', 0.0)):.1f}%",
            f"INTERPRETATION      : {consensus_text}",
            f"SIGNAL CONFLICT     : {output.get('signal_conflict', False)}",
            f"RISK OVERRIDE       : {output.get('risk_override', False)}",
            "",
            "AGENT DISTRIBUTION",
            "-" * 78,
            f"BULLISH AGENTS      : {bullish_agents}",
            f"NEUTRAL AGENTS      : {neutral_agents}",
            f"BEARISH AGENTS      : {bearish_agents}",
            "",
            "STRONGEST SIGNALS",
            "-" * 78,
            f"STRONGEST POSITIVE  : {strongest_positive}",
            f"STRONGEST NEGATIVE  : {strongest_negative}",
            "",
            "TOP POSITIVE SIGNALS",
            "-" * 78,
        ]

        positive_signals = output.get(
            "top_positive_signals",
            []
        )

        if positive_signals:
            for index, signal in enumerate(
                positive_signals,
                start=1
            ):
                lines.append(
                    f"{index}. {signal}"
                )

        else:
            lines.append(
                "No material positive signals detected."
            )

        lines.extend([
            "",
            "TOP RISKS",
            "-" * 78,
        ])

        top_risks = output.get(
            "top_risks",
            []
        )

        if top_risks:
            for index, risk in enumerate(
                top_risks,
                start=1
            ):
                lines.append(
                    f"{index}. {risk}"
                )

        else:
            lines.append(
                "No major bearish risks detected."
            )

        lines.extend([
            "",
            "AGENT RESULTS",
            "-" * 78,
        ])

        for result in output.get(
            "agents",
            []
        ):
            agent_name = (
                self._format_agent_name(
                    result.get(
                        "agent"
                    )
                )
            )

            signal = str(
                result.get(
                    "signal",
                    "neutral"
                )
            ).upper()

            score = float(
                result.get(
                    "score",
                    0.50
                )
            )

            confidence = float(
                result.get(
                    "confidence",
                    0.0
                )
            )

            lines.append(
                f"{agent_name:15} | "
                f"{signal:8} | "
                f"score={score:.2f} | "
                f"confidence={confidence:.2f}"
            )

        lines.extend([
            "",
            "DETAILED AGENT ANALYSIS",
            "=" * 78,
        ])

        for result in output.get(
            "agents",
            []
        ):
            agent_name = (
                self._format_agent_name(
                    result.get(
                        "agent"
                    )
                )
            )

            signal = str(
                result.get(
                    "signal",
                    "neutral"
                )
            ).upper()

            score = float(
                result.get(
                    "score",
                    0.50
                )
            )

            confidence = float(
                result.get(
                    "confidence",
                    0.0
                )
            )

            summary = str(
                result.get(
                    "summary",
                    ""
                )
            )

            lines.extend([
                "",
                agent_name,
                "-" * 78,
                f"Signal      : {signal}",
                f"Score       : {score:.2f}",
                f"Confidence  : {confidence:.2f}",
                f"Summary     : {summary}",
            ])

            risks = result.get(
                "risks",
                []
            )

            if risks:
                lines.append(
                    "Risks:"
                )

                for risk in risks:
                    lines.append(
                        f"  - {risk}"
                    )

            else:
                lines.append(
                    "Risks       : None"
                )

        lines.extend([
            "",
            "=" * 78,
            "END OF REPORT",
            "=" * 78,
        ])

        report_text = "\n".join(
            lines
        )

        filename = (
            self.output_dir
            / "latest_market_report.txt"
        )

        filename.write_text(
            report_text,
            encoding="utf-8"
        )

        return filename

    def generate_json_report(
        self,
        output
    ):
        report_payload = {
            "generated_at": (
                datetime.now().isoformat()
            ),
            "platform": (
                "AI Multi-Agent Financial Research Platform"
            ),
            "version": "1.0",
            "report": output,
        }

        filename = (
            self.output_dir
            / "latest_market_report.json"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report_payload,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

        return filename