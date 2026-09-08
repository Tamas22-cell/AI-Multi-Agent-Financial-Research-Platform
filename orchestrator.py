from agents.macro_agent import MacroAgent
from agents.stock_agent import StockAgent
from agents.crypto_agent import CryptoAgent
from agents.onchain_agent import OnChainAgent
from agents.derivatives_agent import DerivativesAgent
from agents.technical_agent import TechnicalAgent
from agents.news_agent import NewsAgent
from agents.geopolitical_agent import GeopoliticalAgent
from agents.risk_agent import RiskAgent


class Orchestrator:
    def __init__(self):
        self.agents = [
            MacroAgent(),
            StockAgent(),
            CryptoAgent(),
            OnChainAgent(),
            DerivativesAgent(),
            TechnicalAgent(),
            NewsAgent(),
            GeopoliticalAgent(),
            RiskAgent(),
        ]

        self.agent_weights = {
            "macro": 1.20,
            "stock": 1.00,
            "crypto": 1.00,
            "onchain": 1.10,
            "derivatives": 1.10,
            "technical": 0.90,
            "news": 0.70,
            "geopolitical": 0.80,
            "risk": 1.30,
        }

    def run(self):
        results = []

        for agent in self.agents:
            try:
                result = agent.analyze()

                if result:
                    results.append(result)

            except Exception as error:
                results.append({
                    "agent": (
                        agent.__class__.__name__
                        .replace("Agent", "")
                        .lower()
                    ),
                    "signal": "neutral",
                    "score": 0.50,
                    "confidence": 0.20,
                    "summary": (
                        f"Agent error: {error}"
                    ),
                    "risks": [
                        "Agent execution failed"
                    ],
                    "evidence": [],
                })

        # --------------------------------------------------
        # WEIGHTED MARKET SCORE
        # --------------------------------------------------

        weighted_score = 0.0
        total_weight = 0.0

        for result in results:
            score = float(
                result.get(
                    "score",
                    0.50
                )
            )

            confidence = float(
                result.get(
                    "confidence",
                    0.30
                )
            )

            agent_name = result.get(
                "agent",
                "unknown"
            )

            weight = self.agent_weights.get(
                agent_name,
                1.0
            )

            effective_weight = (
                confidence * weight
            )

            weighted_score += (
                score * effective_weight
            )

            total_weight += (
                effective_weight
            )

        if total_weight > 0:
            market_score = (
                weighted_score
                / total_weight
            )

        else:
            market_score = 0.50

        market_score = round(
            market_score,
            2
        )

        # --------------------------------------------------
        # AGENT GROUPS
        # --------------------------------------------------

        bullish_agents = [
            result["agent"]
            for result in results
            if result.get("signal") == "bullish"
        ]

        neutral_agents = [
            result["agent"]
            for result in results
            if result.get("signal") == "neutral"
        ]

        bearish_agents = [
            result["agent"]
            for result in results
            if result.get("signal") == "bearish"
        ]

        total_agents = len(results)

        bullish_count = len(
            bullish_agents
        )

        neutral_count = len(
            neutral_agents
        )

        bearish_count = len(
            bearish_agents
        )

        # --------------------------------------------------
        # SIGNAL PERCENTAGES
        # --------------------------------------------------

        if total_agents > 0:
            bullish_pct = round(
                bullish_count
                / total_agents
                * 100,
                1
            )

            neutral_pct = round(
                neutral_count
                / total_agents
                * 100,
                1
            )

            bearish_pct = round(
                bearish_count
                / total_agents
                * 100,
                1
            )

        else:
            bullish_pct = 0.0
            neutral_pct = 0.0
            bearish_pct = 0.0

        # --------------------------------------------------
        # AVERAGE CONFIDENCE
        # --------------------------------------------------

        confidences = [
            float(
                result.get(
                    "confidence",
                    0.0
                )
            )
            for result in results
        ]

        if confidences:
            average_confidence = round(
                sum(confidences)
                / len(confidences),
                2
            )

        else:
            average_confidence = 0.0

        # --------------------------------------------------
        # CONSENSUS
        # --------------------------------------------------

        consensus_strength = round(
            max(
                bullish_pct,
                neutral_pct,
                bearish_pct
            ),
            1
        )

        signal_conflict = (
            bullish_count > 0
            and bearish_count > 0
        )

        # --------------------------------------------------
        # STRONGEST AGENTS
        # --------------------------------------------------

        strongest_bullish_agent = None
        strongest_bearish_agent = None

        if results:
            strongest_bullish_result = max(
                results,
                key=lambda item: float(
                    item.get(
                        "score",
                        0.50
                    )
                )
            )

            strongest_bearish_result = min(
                results,
                key=lambda item: float(
                    item.get(
                        "score",
                        0.50
                    )
                )
            )

            strongest_bullish_agent = {
                "agent": strongest_bullish_result.get(
                    "agent"
                ),
                "score": float(
                    strongest_bullish_result.get(
                        "score",
                        0.50
                    )
                ),
                "signal": strongest_bullish_result.get(
                    "signal",
                    "neutral"
                ),
            }

            strongest_bearish_agent = {
                "agent": strongest_bearish_result.get(
                    "agent"
                ),
                "score": float(
                    strongest_bearish_result.get(
                        "score",
                        0.50
                    )
                ),
                "signal": strongest_bearish_result.get(
                    "signal",
                    "neutral"
                ),
            }

        # --------------------------------------------------
        # RISK OVERRIDE
        # --------------------------------------------------

        risk_result = next(
            (
                result
                for result in results
                if result.get("agent") == "risk"
            ),
            None
        )

        risk_override = False

        if risk_result:
            risk_score = float(
                risk_result.get(
                    "score",
                    0.50
                )
            )

            if risk_score <= 0.25:
                risk_override = True

        # --------------------------------------------------
        # FINAL DECISION
        # --------------------------------------------------

        if risk_override:
            decision = "AVOID"

        elif (
            market_score >= 0.65
            and bearish_count <= 1
        ):
            decision = "BUY"

        elif (
            market_score <= 0.35
            or bearish_pct >= 55.0
        ):
            decision = "AVOID"

        else:
            decision = "HOLD"

        # --------------------------------------------------
        # MARKET REGIME
        # --------------------------------------------------

        if (
            market_score >= 0.65
            and bullish_pct >= bearish_pct
        ):
            market_regime = "RISK-ON"

        elif (
            market_score <= 0.40
            or bearish_pct >= 55.0
        ):
            market_regime = "RISK-OFF"

        else:
            market_regime = "MIXED"

        # --------------------------------------------------
        # TOP POSITIVE SIGNALS
        # --------------------------------------------------

        positive_results = sorted(
            results,
            key=lambda item: float(
                item.get(
                    "score",
                    0.50
                )
            ),
            reverse=True
        )

        top_positive_signals = []

        for result in positive_results:
            result_score = float(
                result.get(
                    "score",
                    0.50
                )
            )

            if result_score <= 0.50:
                continue

            top_positive_signals.append(
                (
                    f"{result.get('agent', 'unknown').upper()}: "
                    f"{result.get('summary', '')}"
                )
            )

            if len(top_positive_signals) >= 5:
                break

        # --------------------------------------------------
        # TOP RISKS
        # --------------------------------------------------

        risk_candidates = sorted(
            results,
            key=lambda item: float(
                item.get(
                    "score",
                    0.50
                )
            )
        )

        top_risks = []

        for result in risk_candidates:
            result_score = float(
                result.get(
                    "score",
                    0.50
                )
            )

            agent_risks = result.get(
                "risks",
                []
            )

            if (
                result_score >= 0.50
                and not agent_risks
            ):
                continue

            agent_name = result.get(
                "agent",
                "unknown"
            ).upper()

            for risk in agent_risks:
                risk_text = (
                    f"{agent_name}: {risk}"
                )

                if risk_text not in top_risks:
                    top_risks.append(
                        risk_text
                    )

                if len(top_risks) >= 10:
                    break

            if len(top_risks) >= 10:
                break

        # --------------------------------------------------
        # MARKET INTERPRETATION
        # --------------------------------------------------

        if decision == "BUY":
            interpretation = (
                "The multi-agent system indicates a "
                "constructive market environment. "
                "Weighted market conditions are bullish "
                "and downside signals remain limited."
            )

        elif decision == "AVOID":
            interpretation = (
                "The multi-agent system indicates elevated "
                "downside risk. Defensive positioning is "
                "favored until market conditions improve."
            )

        elif (
            market_score >= 0.55
        ):
            interpretation = (
                "Market conditions are mixed but show a "
                "moderate positive bias. Several indicators "
                "are constructive, although confirmation is "
                "not yet strong enough for a BUY decision."
            )

        elif (
            market_score <= 0.45
        ):
            interpretation = (
                "Market conditions are mixed with a "
                "moderate defensive bias. Risk signals "
                "remain present, but they are not strong "
                "enough to justify an AVOID decision."
            )

        else:
            interpretation = (
                "The multi-agent system indicates a "
                "balanced market environment. Bullish and "
                "bearish forces remain insufficient for a "
                "strong directional decision."
            )

        return {
            "agents": results,

            "market_score": market_score,

            "decision": decision,

            "market_regime": (
                market_regime
            ),

            "market_interpretation": (
                interpretation
            ),

            "bullish_agents": (
                bullish_agents
            ),

            "neutral_agents": (
                neutral_agents
            ),

            "bearish_agents": (
                bearish_agents
            ),

            "bullish_pct": bullish_pct,

            "neutral_pct": neutral_pct,

            "bearish_pct": bearish_pct,

            "consensus_strength": (
                consensus_strength
            ),

            "average_confidence": (
                average_confidence
            ),

            "signal_conflict": (
                signal_conflict
            ),

            "risk_override": (
                risk_override
            ),

            "strongest_bullish_agent": (
                strongest_bullish_agent
            ),

            "strongest_bearish_agent": (
                strongest_bearish_agent
            ),

            "top_positive_signals": (
                top_positive_signals
            ),

            "top_risks": (
                top_risks
            ),
        }