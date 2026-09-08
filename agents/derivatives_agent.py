from data.derivatives_data import get_derivatives_data


class DerivativesAgent:
    def analyze(self):
        derivatives_data = get_derivatives_data()

        if (
            not derivatives_data
            or "error" in derivatives_data
        ):
            return {
                "agent": "derivatives",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": (
                    "No usable derivatives data available."
                ),
                "risks": [
                    "Derivatives data unavailable"
                ],
                "evidence": derivatives_data
            }

        score = 0.50
        risks = []

        btc = derivatives_data.get(
            "BTCUSDT",
            {}
        )

        eth = derivatives_data.get(
            "ETHUSDT",
            {}
        )

        summary = derivatives_data.get(
            "summary",
            {}
        )

        btc_funding = float(
            btc.get(
                "funding_rate_pct",
                0.0
            )
        )

        eth_funding = float(
            eth.get(
                "funding_rate_pct",
                0.0
            )
        )

        avg_funding = float(
            summary.get(
                "avg_funding_rate_pct",
                0.0
            )
        )

        avg_hist_funding = float(
            summary.get(
                "avg_funding_8_periods_pct",
                0.0
            )
        )

        avg_oi_1h = float(
            summary.get(
                "avg_oi_change_1h_pct",
                0.0
            )
        )

        avg_oi_24h = float(
            summary.get(
                "avg_oi_change_24h_pct",
                0.0
            )
        )

        btc_funding_trend = btc.get(
            "funding_trend",
            "neutral"
        )

        eth_funding_trend = eth.get(
            "funding_trend",
            "neutral"
        )

        # --------------------------------------------------
        # CURRENT FUNDING
        # --------------------------------------------------

        if avg_funding < 0:
            score += 0.04

        elif avg_funding <= 0.015:
            score += 0.02

        elif avg_funding >= 0.08:
            score -= 0.10
            risks.append(
                "Funding rates are excessively positive"
            )

        elif avg_funding >= 0.04:
            score -= 0.06
            risks.append(
                "Funding rates are elevated"
            )

        elif avg_funding >= 0.02:
            score -= 0.03

        # --------------------------------------------------
        # HISTORICAL FUNDING
        # --------------------------------------------------

        if avg_hist_funding < 0:
            score += 0.03

        elif avg_hist_funding <= 0.015:
            score += 0.01

        elif avg_hist_funding >= 0.06:
            score -= 0.07
            risks.append(
                "Sustained high funding suggests crowded longs"
            )

        elif avg_hist_funding >= 0.03:
            score -= 0.03

        # --------------------------------------------------
        # FUNDING TREND
        # --------------------------------------------------

        if (
            btc_funding_trend == "falling"
            and eth_funding_trend == "falling"
        ):
            score += 0.03

        elif (
            btc_funding_trend == "rising"
            and eth_funding_trend == "rising"
        ):
            if avg_funding >= 0.02:
                score -= 0.04
                risks.append(
                    "BTC and ETH funding are rising together"
                )

        # --------------------------------------------------
        # OPEN INTEREST 1H
        # --------------------------------------------------

        if avg_oi_1h >= 1.0:
            score += 0.04

        elif avg_oi_1h >= 0.30:
            score += 0.02

        elif avg_oi_1h <= -1.0:
            score -= 0.04
            risks.append(
                "Short-term open interest is falling sharply"
            )

        elif avg_oi_1h <= -0.30:
            score -= 0.02

        # --------------------------------------------------
        # OPEN INTEREST 24H
        # --------------------------------------------------

        if avg_oi_24h >= 2.0:
            score += 0.08

        elif avg_oi_24h >= 1.0:
            score += 0.05

        elif avg_oi_24h >= 0.50:
            score += 0.03

        elif avg_oi_24h <= -2.0:
            score -= 0.08
            risks.append(
                "Open interest declined sharply over 24 hours"
            )

        elif avg_oi_24h <= -1.0:
            score -= 0.05
            risks.append(
                "Open interest is weakening over 24 hours"
            )

        elif avg_oi_24h <= -0.50:
            score -= 0.03

        # --------------------------------------------------
        # BTC + ETH FUNDING CONFIRMATION
        # --------------------------------------------------

        if (
            btc_funding < 0
            and eth_funding < 0
        ):
            score += 0.04

        elif (
            btc_funding >= 0.04
            and eth_funding >= 0.04
        ):
            score -= 0.06
            risks.append(
                "BTC and ETH funding both indicate crowded long positioning"
            )

        # --------------------------------------------------
        # OI + FUNDING COMBINATION
        # --------------------------------------------------

        if (
            avg_oi_24h >= 0.50
            and avg_funding <= 0.015
        ):
            score += 0.05

        elif (
            avg_oi_24h >= 1.50
            and avg_funding >= 0.04
        ):
            score -= 0.06
            risks.append(
                "Rising open interest with elevated funding increases squeeze risk"
            )

        elif (
            avg_oi_24h <= -1.0
            and avg_funding < 0
        ):
            score -= 0.04
            risks.append(
                "Falling open interest with negative funding indicates deleveraging"
            )

        # --------------------------------------------------
        # FINAL SCORE
        # --------------------------------------------------

        score = max(
            0.0,
            min(1.0, score)
        )

        score = round(
            score,
            2
        )

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

        if btc:
            available_metrics += 1

        if eth:
            available_metrics += 1

        if summary:
            available_metrics += 1

        if available_metrics == 3:
            confidence = 0.80

        elif available_metrics == 2:
            confidence = 0.65

        elif available_metrics == 1:
            confidence = 0.50

        else:
            confidence = 0.30

        return {
            "agent": "derivatives",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Crypto derivatives assessment based on "
                "BTC and ETH funding, funding trends, "
                "open interest changes and positioning risk."
            ),
            "risks": risks,
            "evidence": derivatives_data
        }