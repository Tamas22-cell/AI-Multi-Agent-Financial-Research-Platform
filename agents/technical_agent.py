from data.technical_data import get_technical_data


class TechnicalAgent:
    def analyze(self):
        technical_data = get_technical_data()

        if (
            not technical_data
            or "error" in technical_data
        ):
            return {
                "agent": "technical",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": (
                    "No usable technical data available."
                ),
                "risks": [
                    "Technical data unavailable"
                ],
                "evidence": technical_data
            }

        score = 0.50
        risks = []

        rsi = float(
            technical_data.get(
                "RSI",
                50.0
            )
        )

        ema20 = float(
            technical_data.get(
                "EMA20",
                0.0
            )
        )

        ema50 = float(
            technical_data.get(
                "EMA50",
                0.0
            )
        )

        price = float(
            technical_data.get(
                "PRICE",
                0.0
            )
        )

        macd = float(
            technical_data.get(
                "MACD",
                0.0
            )
        )

        macd_signal = float(
            technical_data.get(
                "MACD_SIGNAL",
                0.0
            )
        )

        macd_hist = float(
            technical_data.get(
                "MACD_HISTOGRAM",
                0.0
            )
        )

        change_1d = float(
            technical_data.get(
                "CHANGE_1D_PCT",
                0.0
            )
        )

        change_7d = float(
            technical_data.get(
                "CHANGE_7D_PCT",
                0.0
            )
        )

        # --------------------------------------------------
        # RSI
        # --------------------------------------------------

        if 55 <= rsi <= 70:
            score += 0.06

        elif 50 <= rsi < 55:
            score += 0.03

        elif rsi >= 75:
            score -= 0.05
            risks.append(
                "RSI indicates overbought conditions"
            )

        elif rsi <= 30:
            score += 0.04

        elif 30 < rsi < 45:
            score -= 0.04

        # --------------------------------------------------
        # PRICE VS EMA20
        # --------------------------------------------------

        if price > 0 and ema20 > 0:
            if price > ema20:
                score += 0.05

            elif price < ema20:
                score -= 0.05
                risks.append(
                    "Price is below the 20-day EMA"
                )

        # --------------------------------------------------
        # EMA20 VS EMA50
        # --------------------------------------------------

        if ema20 > 0 and ema50 > 0:
            if ema20 > ema50:
                score += 0.07

            elif ema20 < ema50:
                score -= 0.07
                risks.append(
                    "Short-term trend is below the medium-term trend"
                )

        # --------------------------------------------------
        # MACD
        # --------------------------------------------------

        if macd > macd_signal:
            score += 0.05

        elif macd < macd_signal:
            score -= 0.05
            risks.append(
                "MACD is below its signal line"
            )

        # --------------------------------------------------
        # MACD HISTOGRAM
        # --------------------------------------------------

        if macd_hist > 0:
            score += 0.03

        elif macd_hist < 0:
            score -= 0.03

        # --------------------------------------------------
        # 1-DAY MOMENTUM
        # --------------------------------------------------

        if change_1d >= 1.5:
            score += 0.05

        elif change_1d >= 0.40:
            score += 0.02

        elif change_1d <= -1.5:
            score -= 0.05
            risks.append(
                "Strong negative 1-day price momentum"
            )

        elif change_1d <= -0.40:
            score -= 0.02

        # --------------------------------------------------
        # 7-DAY MOMENTUM
        # --------------------------------------------------

        if change_7d >= 3.0:
            score += 0.08

        elif change_7d >= 1.0:
            score += 0.04

        elif change_7d <= -3.0:
            score -= 0.08
            risks.append(
                "Strong negative 7-day price momentum"
            )

        elif change_7d <= -1.0:
            score -= 0.04

        # --------------------------------------------------
        # TREND CONFIRMATION
        # --------------------------------------------------

        bullish_confirmations = 0
        bearish_confirmations = 0

        if price > ema20:
            bullish_confirmations += 1
        else:
            bearish_confirmations += 1

        if ema20 > ema50:
            bullish_confirmations += 1
        else:
            bearish_confirmations += 1

        if macd > macd_signal:
            bullish_confirmations += 1
        else:
            bearish_confirmations += 1

        if macd_hist > 0:
            bullish_confirmations += 1
        else:
            bearish_confirmations += 1

        if change_7d > 0:
            bullish_confirmations += 1
        elif change_7d < 0:
            bearish_confirmations += 1

        if bullish_confirmations >= 4:
            score += 0.08

        elif bearish_confirmations >= 4:
            score -= 0.08
            risks.append(
                "Multiple technical indicators confirm bearish momentum"
            )

        # --------------------------------------------------
        # STRONG BULLISH SETUP
        # --------------------------------------------------

        if (
            price > ema20
            and ema20 > ema50
            and macd > macd_signal
            and macd_hist > 0
            and change_7d > 1.0
        ):
            score += 0.07

        # --------------------------------------------------
        # STRONG BEARISH SETUP
        # --------------------------------------------------

        elif (
            price < ema20
            and ema20 < ema50
            and macd < macd_signal
            and macd_hist < 0
            and change_7d < -1.0
        ):
            score -= 0.07
            risks.append(
                "Technical indicators confirm a strong bearish setup"
            )

        # --------------------------------------------------
        # RSI DIVERGENCE / EXHAUSTION
        # --------------------------------------------------

        if (
            rsi >= 70
            and change_7d > 3.0
        ):
            score -= 0.04
            risks.append(
                "Momentum may be overextended"
            )

        elif (
            rsi <= 35
            and change_7d < -3.0
        ):
            score += 0.03

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
            "RSI",
            "EMA20",
            "EMA50",
            "PRICE",
            "MACD",
            "MACD_SIGNAL",
            "MACD_HISTOGRAM",
            "CHANGE_1D_PCT",
            "CHANGE_7D_PCT",
        ]

        for metric_name in metric_names:
            if metric_name in technical_data:
                available_metrics += 1

        if available_metrics >= 9:
            confidence = 0.85

        elif available_metrics >= 7:
            confidence = 0.80

        elif available_metrics >= 5:
            confidence = 0.70

        elif available_metrics >= 3:
            confidence = 0.55

        else:
            confidence = 0.35

        return {
            "agent": "technical",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Technical market assessment based on "
                "RSI, EMA structure, MACD, MACD histogram "
                "and short-term price momentum."
            ),
            "risks": risks,
            "evidence": technical_data
        }