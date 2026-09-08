from data.stock_data import get_stock_data


class StockAgent:
    def analyze(self):
        stock_data = get_stock_data()

        if (
            not stock_data
            or "error" in stock_data
        ):
            return {
                "agent": "stock",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": (
                    "No usable stock market data available."
                ),
                "risks": [
                    "Stock market data unavailable"
                ],
                "evidence": stock_data
            }

        score = 0.50
        risks = []

        spy = stock_data.get("SPY", {})
        qqq = stock_data.get("QQQ", {})
        dia = stock_data.get("DIA", {})
        iwm = stock_data.get("IWM", {})

        nvda = stock_data.get("NVDA", {})
        aapl = stock_data.get("AAPL", {})
        msft = stock_data.get("MSFT", {})

        spy_1d = float(
            spy.get("change_pct", 0.0)
        )

        spy_7d = float(
            spy.get("change_7d_pct", 0.0)
        )

        qqq_1d = float(
            qqq.get("change_pct", 0.0)
        )

        qqq_7d = float(
            qqq.get("change_7d_pct", 0.0)
        )

        dia_1d = float(
            dia.get("change_pct", 0.0)
        )

        dia_7d = float(
            dia.get("change_7d_pct", 0.0)
        )

        iwm_1d = float(
            iwm.get("change_pct", 0.0)
        )

        iwm_7d = float(
            iwm.get("change_7d_pct", 0.0)
        )

        nvda_7d = float(
            nvda.get("change_7d_pct", 0.0)
        )

        aapl_7d = float(
            aapl.get("change_7d_pct", 0.0)
        )

        msft_7d = float(
            msft.get("change_7d_pct", 0.0)
        )

        # --------------------------------------------------
        # SPY
        # --------------------------------------------------

        if spy_1d >= 1.0:
            score += 0.05

        elif spy_1d >= 0.30:
            score += 0.02

        elif spy_1d <= -1.0:
            score -= 0.05
            risks.append(
                "S&P 500 shows strong short-term weakness"
            )

        elif spy_1d <= -0.30:
            score -= 0.02

        if spy_7d >= 2.0:
            score += 0.08

        elif spy_7d >= 0.75:
            score += 0.04

        elif spy_7d <= -2.0:
            score -= 0.08
            risks.append(
                "S&P 500 shows strong 7-day weakness"
            )

        elif spy_7d <= -0.75:
            score -= 0.04

        # --------------------------------------------------
        # QQQ
        # --------------------------------------------------

        if qqq_1d >= 1.25:
            score += 0.05

        elif qqq_1d >= 0.35:
            score += 0.02

        elif qqq_1d <= -1.25:
            score -= 0.05
            risks.append(
                "NASDAQ-100 shows strong short-term weakness"
            )

        elif qqq_1d <= -0.35:
            score -= 0.02

        if qqq_7d >= 2.5:
            score += 0.08

        elif qqq_7d >= 1.0:
            score += 0.04

        elif qqq_7d <= -2.5:
            score -= 0.08
            risks.append(
                "NASDAQ-100 shows strong 7-day weakness"
            )

        elif qqq_7d <= -1.0:
            score -= 0.04

        # --------------------------------------------------
        # DIA
        # --------------------------------------------------

        if dia_7d >= 1.5:
            score += 0.05

        elif dia_7d >= 0.50:
            score += 0.02

        elif dia_7d <= -1.5:
            score -= 0.05
            risks.append(
                "Dow Jones shows broad-market weakness"
            )

        elif dia_7d <= -0.50:
            score -= 0.02

        # --------------------------------------------------
        # IWM
        # --------------------------------------------------

        if iwm_7d >= 2.0:
            score += 0.07

        elif iwm_7d >= 0.75:
            score += 0.03

        elif iwm_7d <= -2.0:
            score -= 0.07
            risks.append(
                "Small-cap stocks show strong weakness"
            )

        elif iwm_7d <= -0.75:
            score -= 0.03

        # --------------------------------------------------
        # BROAD MARKET CONFIRMATION
        # --------------------------------------------------

        broad_positive = 0
        broad_negative = 0

        for change in [
            spy_7d,
            qqq_7d,
            dia_7d,
            iwm_7d,
        ]:
            if change > 0.50:
                broad_positive += 1

            elif change < -0.50:
                broad_negative += 1

        if broad_positive == 4:
            score += 0.10

        elif broad_positive >= 3:
            score += 0.06

        if broad_negative == 4:
            score -= 0.10
            risks.append(
                "Major US equity indexes confirm broad weakness"
            )

        elif broad_negative >= 3:
            score -= 0.06
            risks.append(
                "Most major US equity indexes are weakening"
            )

        # --------------------------------------------------
        # TECHNOLOGY LEADERSHIP
        # --------------------------------------------------

        tech_positive = 0
        tech_negative = 0

        for change in [
            nvda_7d,
            aapl_7d,
            msft_7d,
        ]:
            if change > 1.0:
                tech_positive += 1

            elif change < -1.0:
                tech_negative += 1

        if tech_positive == 3:
            score += 0.08

        elif tech_positive == 2:
            score += 0.04

        if tech_negative == 3:
            score -= 0.08
            risks.append(
                "Mega-cap technology leaders confirm weakness"
            )

        elif tech_negative == 2:
            score -= 0.04
            risks.append(
                "Multiple mega-cap technology stocks are weakening"
            )

        # --------------------------------------------------
        # QQQ VS SPY RELATIVE STRENGTH
        # --------------------------------------------------

        qqq_vs_spy = (
            qqq_7d - spy_7d
        )

        if qqq_vs_spy >= 1.0:
            score += 0.04

        elif qqq_vs_spy <= -1.0:
            score -= 0.04
            risks.append(
                "Technology is underperforming the broad market"
            )

        # --------------------------------------------------
        # SMALL CAPS VS LARGE CAPS
        # --------------------------------------------------

        iwm_vs_spy = (
            iwm_7d - spy_7d
        )

        if iwm_vs_spy >= 1.0:
            score += 0.04

        elif iwm_vs_spy <= -1.5:
            score -= 0.04
            risks.append(
                "Small caps are significantly underperforming large caps"
            )

        # --------------------------------------------------
        # STRONG RISK-ON EQUITY CONFIRMATION
        # --------------------------------------------------

        if (
            spy_7d > 1.0
            and qqq_7d > 1.0
            and iwm_7d > 1.0
            and tech_positive >= 2
        ):
            score += 0.08

        # --------------------------------------------------
        # STRONG RISK-OFF EQUITY CONFIRMATION
        # --------------------------------------------------

        elif (
            spy_7d < -1.0
            and qqq_7d < -1.0
            and iwm_7d < -1.0
            and tech_negative >= 2
        ):
            score -= 0.08
            risks.append(
                "Equity market shows strong risk-off confirmation"
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

        available_assets = 0

        for asset in [
            spy,
            qqq,
            dia,
            iwm,
            nvda,
            aapl,
            msft,
        ]:
            if asset:
                available_assets += 1

        if available_assets >= 7:
            confidence = 0.85

        elif available_assets >= 5:
            confidence = 0.80

        elif available_assets >= 4:
            confidence = 0.70

        elif available_assets >= 2:
            confidence = 0.55

        else:
            confidence = 0.35

        return {
            "agent": "stock",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "US equity assessment based on broad "
                "market indexes, technology leadership, "
                "small-cap participation and relative "
                "strength across 1-day and 7-day horizons."
            ),
            "risks": risks,
            "evidence": stock_data
        }