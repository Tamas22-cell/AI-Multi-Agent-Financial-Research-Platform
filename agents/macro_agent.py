from data.macro_data import get_macro_data


class MacroAgent:
    def analyze(self):
        macro_data = get_macro_data()

        if not macro_data or "error" in macro_data:
            return {
                "agent": "macro",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": "No macro data available.",
                "risks": ["Macro data unavailable"],
                "evidence": macro_data
            }

        score = 0.50
        risks = []

        dxy = macro_data.get("DXY", {})
        us10y = macro_data.get("US10Y", {})
        sp500 = macro_data.get("SP500", {})
        nasdaq = macro_data.get("NASDAQ", {})

        dxy_1d = float(
            dxy.get("change_pct", 0.0)
        )

        dxy_7d = float(
            dxy.get("change_7d_pct", 0.0)
        )

        us10y_1d = float(
            us10y.get("change_pct", 0.0)
        )

        us10y_7d = float(
            us10y.get("change_7d_pct", 0.0)
        )

        sp500_1d = float(
            sp500.get("change_pct", 0.0)
        )

        sp500_7d = float(
            sp500.get("change_7d_pct", 0.0)
        )

        nasdaq_1d = float(
            nasdaq.get("change_pct", 0.0)
        )

        nasdaq_7d = float(
            nasdaq.get("change_7d_pct", 0.0)
        )

        # --------------------------------------------------
        # DXY SHORT TERM
        # --------------------------------------------------

        if dxy_1d <= -0.75:
            score += 0.06

        elif dxy_1d < -0.20:
            score += 0.03

        elif dxy_1d >= 0.75:
            score -= 0.06
            risks.append(
                "Strong short-term US dollar appreciation"
            )

        elif dxy_1d > 0.20:
            score -= 0.03

        # --------------------------------------------------
        # DXY 7 DAY
        # --------------------------------------------------

        if dxy_7d <= -1.50:
            score += 0.08

        elif dxy_7d <= -0.50:
            score += 0.04

        elif dxy_7d >= 1.50:
            score -= 0.08
            risks.append(
                "Strong 7-day US dollar appreciation"
            )

        elif dxy_7d >= 0.50:
            score -= 0.04

        # --------------------------------------------------
        # US10Y SHORT TERM
        # --------------------------------------------------

        if us10y_1d <= -1.50:
            score += 0.06

        elif us10y_1d < -0.50:
            score += 0.03

        elif us10y_1d >= 1.50:
            score -= 0.06
            risks.append(
                "US Treasury yields rising sharply"
            )

        elif us10y_1d > 0.50:
            score -= 0.03

        # --------------------------------------------------
        # US10Y 7 DAY
        # --------------------------------------------------

        if us10y_7d <= -3.0:
            score += 0.08

        elif us10y_7d <= -1.0:
            score += 0.04

        elif us10y_7d >= 3.0:
            score -= 0.08
            risks.append(
                "US Treasury yields show strong 7-day increase"
            )

        elif us10y_7d >= 1.0:
            score -= 0.04

        # --------------------------------------------------
        # S&P 500 SHORT TERM
        # --------------------------------------------------

        if sp500_1d >= 1.0:
            score += 0.06

        elif sp500_1d > 0.25:
            score += 0.03

        elif sp500_1d <= -1.0:
            score -= 0.06
            risks.append(
                "S&P 500 shows strong short-term weakness"
            )

        elif sp500_1d < -0.25:
            score -= 0.03

        # --------------------------------------------------
        # S&P 500 7 DAY
        # --------------------------------------------------

        if sp500_7d >= 2.5:
            score += 0.08

        elif sp500_7d >= 0.75:
            score += 0.04

        elif sp500_7d <= -2.5:
            score -= 0.08
            risks.append(
                "S&P 500 shows strong 7-day weakness"
            )

        elif sp500_7d <= -0.75:
            score -= 0.04

        # --------------------------------------------------
        # NASDAQ SHORT TERM
        # --------------------------------------------------

        if nasdaq_1d >= 1.25:
            score += 0.06

        elif nasdaq_1d > 0.30:
            score += 0.03

        elif nasdaq_1d <= -1.25:
            score -= 0.06
            risks.append(
                "NASDAQ shows strong short-term weakness"
            )

        elif nasdaq_1d < -0.30:
            score -= 0.03

        # --------------------------------------------------
        # NASDAQ 7 DAY
        # --------------------------------------------------

        if nasdaq_7d >= 3.0:
            score += 0.08

        elif nasdaq_7d >= 1.0:
            score += 0.04

        elif nasdaq_7d <= -3.0:
            score -= 0.08
            risks.append(
                "NASDAQ shows strong 7-day weakness"
            )

        elif nasdaq_7d <= -1.0:
            score -= 0.04

        # --------------------------------------------------
        # DXY + US10Y CONFIRMATION
        # --------------------------------------------------

        if (
            dxy_7d < -0.50
            and us10y_7d < -1.0
        ):
            score += 0.08

        elif (
            dxy_7d > 0.50
            and us10y_7d > 1.0
        ):
            score -= 0.08
            risks.append(
                "US dollar and Treasury yields are rising together"
            )

        # --------------------------------------------------
        # EQUITY CONFIRMATION
        # --------------------------------------------------

        if (
            sp500_7d > 0.75
            and nasdaq_7d > 1.0
        ):
            score += 0.07

        elif (
            sp500_7d < -0.75
            and nasdaq_7d < -1.0
        ):
            score -= 0.07
            risks.append(
                "S&P 500 and NASDAQ confirm broad equity weakness"
            )

        # --------------------------------------------------
        # FULL RISK-ON CONFIRMATION
        # --------------------------------------------------

        if (
            dxy_7d < -0.50
            and us10y_7d < -1.0
            and sp500_7d > 0.75
            and nasdaq_7d > 1.0
        ):
            score += 0.10

        # --------------------------------------------------
        # FULL RISK-OFF CONFIRMATION
        # --------------------------------------------------

        elif (
            dxy_7d > 0.50
            and us10y_7d > 1.0
            and sp500_7d < -0.75
            and nasdaq_7d < -1.0
        ):
            score -= 0.10
            risks.append(
                "Macro conditions show broad risk-off confirmation"
            )

        # --------------------------------------------------
        # EQUITY VS RATES DIVERGENCE
        # --------------------------------------------------

        if (
            us10y_7d > 1.0
            and nasdaq_7d > 1.0
        ):
            score -= 0.03
            risks.append(
                "NASDAQ strength is developing alongside rising yields"
            )

        elif (
            us10y_7d < -1.0
            and nasdaq_7d > 1.0
        ):
            score += 0.04

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

        for metric in [
            dxy,
            us10y,
            sp500,
            nasdaq,
        ]:
            if metric:
                available_metrics += 1

        if available_metrics == 4:
            confidence = 0.80

        elif available_metrics == 3:
            confidence = 0.70

        elif available_metrics == 2:
            confidence = 0.60

        elif available_metrics == 1:
            confidence = 0.45

        else:
            confidence = 0.30

        return {
            "agent": "macro",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Macro market assessment based on "
                "US dollar strength, Treasury yields, "
                "S&P 500 and NASDAQ momentum across "
                "1-day and 7-day horizons."
            ),
            "risks": risks,
            "evidence": macro_data
        }