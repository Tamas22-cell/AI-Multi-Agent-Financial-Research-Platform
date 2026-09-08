from data.risk_data import get_risk_data


class RiskAgent:
    def analyze(self):
        risk_data = get_risk_data()

        if not risk_data:
            return {
                "agent": "risk",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": "No risk data available.",
                "risks": ["Risk data unavailable"],
                "evidence": []
            }

        avg_volatility = float(
            risk_data.get("avg_volatility", 0.0)
        )

        avg_correlation = float(
            risk_data.get("avg_correlation", 0.0)
        )

        max_drawdown = float(
            risk_data.get("max_drawdown", 0.0)
        )

        score = 0.50
        risks = []

        # --------------------------------------------------
        # VOLATILITY
        # --------------------------------------------------

        if avg_volatility >= 0.60:
            score -= 0.25
            risks.append("High cross-asset volatility")

        elif avg_volatility >= 0.40:
            score -= 0.15
            risks.append("Elevated cross-asset volatility")

        elif avg_volatility >= 0.25:
            score -= 0.05

        else:
            score += 0.10

        # --------------------------------------------------
        # CORRELATION
        #
        # High positive correlation means diversification
        # becomes weaker during market stress.
        # --------------------------------------------------

        if avg_correlation >= 0.75:
            score -= 0.15
            risks.append(
                "High cross-asset correlation reduces diversification"
            )

        elif avg_correlation >= 0.55:
            score -= 0.08
            risks.append(
                "Elevated cross-asset correlation"
            )

        elif avg_correlation <= 0.30:
            score += 0.05

        # --------------------------------------------------
        # DRAWDOWN
        # --------------------------------------------------

        drawdown_abs = abs(max_drawdown)

        if drawdown_abs >= 0.25:
            score -= 0.20
            risks.append("Severe portfolio drawdown risk")

        elif drawdown_abs >= 0.15:
            score -= 0.12
            risks.append("Elevated portfolio drawdown")

        elif drawdown_abs >= 0.08:
            score -= 0.05

        # Keep score inside valid range
        score = max(0.0, min(1.0, score))
        score = round(score, 2)

        # --------------------------------------------------
        # SIGNAL
        # --------------------------------------------------

        if score >= 0.65:
            signal = "bullish"

        elif score <= 0.35:
            signal = "bearish"

        else:
            signal = "neutral"

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        available_metrics = 0

        if "avg_volatility" in risk_data:
            available_metrics += 1

        if "avg_correlation" in risk_data:
            available_metrics += 1

        if "max_drawdown" in risk_data:
            available_metrics += 1

        confidence_map = {
            0: 0.30,
            1: 0.50,
            2: 0.65,
            3: 0.80,
        }

        confidence = confidence_map.get(
            available_metrics,
            0.30
        )

        return {
            "agent": "risk",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Portfolio risk assessment based on "
                "cross-asset volatility, correlation and drawdown."
            ),
            "risks": risks,
            "evidence": risk_data
        }