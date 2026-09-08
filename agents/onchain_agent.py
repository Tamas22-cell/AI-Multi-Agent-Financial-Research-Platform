from data.onchain_data import get_onchain_data


class OnChainAgent:
    def analyze(self):
        onchain_data = get_onchain_data()

        if not onchain_data or "error" in onchain_data:
            return {
                "agent": "onchain",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": "No usable on-chain data available.",
                "risks": ["On-chain data unavailable"],
                "evidence": onchain_data
            }

        score = 0.50
        risks = []

        hashrate_1d = float(
            onchain_data.get(
                "hashrate_change_pct",
                0.0
            )
        )

        hashrate_7d = float(
            onchain_data.get(
                "hashrate_7d_change_pct",
                0.0
            )
        )

        btc_price_1d = float(
            onchain_data.get(
                "btc_price_change_pct",
                0.0
            )
        )

        btc_price_7d = float(
            onchain_data.get(
                "btc_price_7d_change_pct",
                0.0
            )
        )

        tx_1d = float(
            onchain_data.get(
                "transactions_change_pct",
                0.0
            )
        )

        tx_7d = float(
            onchain_data.get(
                "transactions_7d_change_pct",
                0.0
            )
        )

        # --------------------------------------------------
        # HASHRATE
        # --------------------------------------------------

        if hashrate_1d >= 3.0:
            score += 0.06

        elif hashrate_1d <= -3.0:
            score -= 0.06
            risks.append(
                "Short-term BTC hashrate weakness"
            )

        if hashrate_7d >= 5.0:
            score += 0.10

        elif hashrate_7d >= 2.0:
            score += 0.05

        elif hashrate_7d <= -5.0:
            score -= 0.10
            risks.append(
                "Sharp BTC hashrate decline"
            )

        elif hashrate_7d <= -2.0:
            score -= 0.05
            risks.append(
                "BTC hashrate weakening over 7 days"
            )

        # --------------------------------------------------
        # BTC PRICE MOMENTUM
        # --------------------------------------------------

        if btc_price_1d >= 2.0:
            score += 0.06

        elif btc_price_1d <= -2.0:
            score -= 0.06
            risks.append(
                "BTC short-term price weakness"
            )

        if btc_price_7d >= 5.0:
            score += 0.10

        elif btc_price_7d >= 2.0:
            score += 0.05

        elif btc_price_7d <= -5.0:
            score -= 0.10
            risks.append(
                "BTC 7-day price momentum is strongly negative"
            )

        elif btc_price_7d <= -2.0:
            score -= 0.05
            risks.append(
                "BTC 7-day price momentum is negative"
            )

        # --------------------------------------------------
        # NETWORK ACTIVITY
        # --------------------------------------------------

        if tx_1d >= 5.0:
            score += 0.05

        elif tx_1d <= -5.0:
            score -= 0.05
            risks.append(
                "BTC transaction activity declined sharply"
            )

        if tx_7d >= 8.0:
            score += 0.08

        elif tx_7d >= 3.0:
            score += 0.04

        elif tx_7d <= -8.0:
            score -= 0.08
            risks.append(
                "BTC network activity weakened significantly"
            )

        elif tx_7d <= -3.0:
            score -= 0.04
            risks.append(
                "BTC network activity is weakening"
            )

        # --------------------------------------------------
        # CONFIRMATION
        # --------------------------------------------------

        bullish_confirmations = 0
        bearish_confirmations = 0

        if hashrate_7d > 0:
            bullish_confirmations += 1
        elif hashrate_7d < 0:
            bearish_confirmations += 1

        if btc_price_7d > 0:
            bullish_confirmations += 1
        elif btc_price_7d < 0:
            bearish_confirmations += 1

        if tx_7d > 0:
            bullish_confirmations += 1
        elif tx_7d < 0:
            bearish_confirmations += 1

        if bullish_confirmations == 3:
            score += 0.10

        elif bearish_confirmations == 3:
            score -= 0.10
            risks.append(
                "Hashrate, BTC price and network activity confirm weakness"
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

        metric_names = [
            "hashrate_change_pct",
            "hashrate_7d_change_pct",
            "btc_price_change_pct",
            "btc_price_7d_change_pct",
            "transactions_change_pct",
            "transactions_7d_change_pct",
        ]

        for metric_name in metric_names:
            if metric_name in onchain_data:
                available_metrics += 1

        if available_metrics >= 6:
            confidence = 0.80

        elif available_metrics >= 4:
            confidence = 0.70

        elif available_metrics >= 2:
            confidence = 0.55

        else:
            confidence = 0.35

        return {
            "agent": "onchain",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Bitcoin on-chain assessment based on "
                "hashrate, BTC price momentum and "
                "network transaction activity across "
                "1-day and 7-day trends."
            ),
            "risks": risks,
            "evidence": onchain_data
        }