from data.crypto_data import get_crypto_data


class CryptoAgent:
    def analyze(self):
        crypto_data = get_crypto_data()

        if not crypto_data:
            return {
                "agent": "crypto",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": "No crypto market data available.",
                "risks": ["Crypto market data unavailable"],
                "evidence": []
            }

        score = 0.50
        risks = []

        btc = crypto_data.get("BTC", {})
        eth = crypto_data.get("ETH", {})
        sol = crypto_data.get("SOL", {})
        relative = crypto_data.get("RELATIVE_STRENGTH", {})

        # --------------------------------------------------
        # 1D MOMENTUM
        # --------------------------------------------------

        for asset_name, asset_data, weight in [
            ("BTC", btc, 0.12),
            ("ETH", eth, 0.10),
            ("SOL", sol, 0.08),
        ]:
            change_1d = float(
                asset_data.get("change_pct", 0.0)
            )

            if change_1d >= 3.0:
                score += weight

            elif change_1d >= 1.0:
                score += weight * 0.5

            elif change_1d <= -3.0:
                score -= weight
                risks.append(
                    f"Strong {asset_name} downside momentum"
                )

            elif change_1d <= -1.0:
                score -= weight * 0.5
                risks.append(
                    f"Negative {asset_name} momentum"
                )

        # --------------------------------------------------
        # 7D MOMENTUM
        # --------------------------------------------------

        for asset_name, asset_data, weight in [
            ("BTC", btc, 0.12),
            ("ETH", eth, 0.10),
            ("SOL", sol, 0.08),
        ]:
            change_7d = float(
                asset_data.get("change_7d_pct", 0.0)
            )

            if change_7d >= 7.0:
                score += weight

            elif change_7d >= 3.0:
                score += weight * 0.5

            elif change_7d <= -7.0:
                score -= weight
                risks.append(
                    f"Strong 7-day {asset_name} weakness"
                )

            elif change_7d <= -3.0:
                score -= weight * 0.5
                risks.append(
                    f"Negative 7-day {asset_name} trend"
                )

        # --------------------------------------------------
        # VOLUME CONFIRMATION
        # --------------------------------------------------

        for asset_name, asset_data in [
            ("BTC", btc),
            ("ETH", eth),
            ("SOL", sol),
        ]:
            volume_ratio = float(
                asset_data.get("volume_ratio", 1.0)
            )

            change_1d = float(
                asset_data.get("change_pct", 0.0)
            )

            if volume_ratio >= 1.30:
                if change_1d > 0:
                    score += 0.04
                elif change_1d < 0:
                    score -= 0.04
                    risks.append(
                        f"{asset_name} selloff confirmed by high volume"
                    )

        # --------------------------------------------------
        # BTC / ETH RELATIVE STRENGTH
        # --------------------------------------------------

        btc_vs_eth = float(
            relative.get("btc_vs_eth_7d", 0.0)
        )

        if btc_vs_eth >= 5.0:
            risks.append(
                "BTC significantly outperforming ETH"
            )

        elif btc_vs_eth <= -5.0:
            risks.append(
                "ETH significantly outperforming BTC"
            )

        # --------------------------------------------------
        # MARKET CONFIRMATION
        # --------------------------------------------------

        btc_7d = float(
            btc.get("change_7d_pct", 0.0)
        )

        eth_7d = float(
            eth.get("change_7d_pct", 0.0)
        )

        sol_7d = float(
            sol.get("change_7d_pct", 0.0)
        )

        if (
            btc_7d > 0
            and eth_7d > 0
            and sol_7d > 0
        ):
            score += 0.08

        elif (
            btc_7d < 0
            and eth_7d < 0
            and sol_7d < 0
        ):
            score -= 0.08
            risks.append(
                "Broad crypto market weakness"
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

        available_assets = sum(
            1
            for asset in [btc, eth, sol]
            if asset
        )

        confidence_map = {
            0: 0.30,
            1: 0.55,
            2: 0.70,
            3: 0.80,
        }

        confidence = confidence_map.get(
            available_assets,
            0.30
        )

        return {
            "agent": "crypto",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Crypto market assessment based on "
                "1-day and 7-day momentum, volume confirmation, "
                "BTC/ETH relative strength and broad market participation."
            ),
            "risks": risks,
            "evidence": crypto_data
        }