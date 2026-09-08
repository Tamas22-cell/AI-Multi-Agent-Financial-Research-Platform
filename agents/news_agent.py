from data.news_data import get_news_data


class NewsAgent:
    def analyze(self):
        news_data = get_news_data()

        if (
            not news_data
            or "error" in news_data
        ):
            return {
                "agent": "news",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": (
                    "No usable financial news data available."
                ),
                "risks": [
                    "Financial news data unavailable"
                ],
                "evidence": news_data
            }

        score = 0.50
        risks = []

        bearish_keywords = {
            "crash": 3.0,
            "collapse": 3.0,
            "plunge": 2.5,
            "selloff": 2.5,
            "recession": 2.5,
            "default": 3.0,
            "bankruptcy": 3.0,
            "downgrade": 1.5,
            "warning": 1.0,
            "risk": 0.8,
            "fear": 1.0,
            "decline": 1.0,
            "drop": 1.0,
            "falls": 1.0,
            "fall": 1.0,
            "slump": 1.5,
            "weakness": 1.2,
            "inflation": 0.7,
            "tariff": 0.7,
            "sanctions": 1.0,
            "layoffs": 1.2,
            "loss": 1.0,
            "losses": 1.0,
            "cuts forecast": 1.2,
            "profit warning": 2.0,
        }

        bullish_keywords = {
            "rally": 2.0,
            "surge": 2.0,
            "record high": 2.0,
            "breakout": 1.8,
            "gain": 1.0,
            "gains": 1.0,
            "rise": 1.0,
            "rises": 1.0,
            "growth": 1.0,
            "strong": 1.0,
            "beats expectations": 2.0,
            "beats estimates": 2.0,
            "upgrade": 1.5,
            "optimism": 1.2,
            "recovery": 1.5,
            "rebound": 1.5,
            "easing": 1.0,
            "rate cut": 1.4,
            "rate cuts": 1.4,
            "stimulus": 1.2,
            "profit growth": 1.5,
            "bullish": 1.5,
        }

        neutralizers = [
            "may",
            "could",
            "might",
            "possible",
            "potential",
            "uncertain",
            "uncertainty",
            "mixed",
        ]

        negation_terms = [
            "not",
            "no",
            "without",
            "avoids",
            "avoid",
            "eases",
            "eased",
            "lower risk",
            "risk falls",
        ]

        headlines = []

        if isinstance(news_data, list):
            headlines = news_data

        elif isinstance(news_data, dict):
            for value in news_data.values():
                if isinstance(value, list):
                    headlines.extend(value)

        bearish_score = 0.0
        bullish_score = 0.0

        bearish_headlines = 0
        bullish_headlines = 0
        mixed_headlines = 0

        extreme_negative_count = 0
        strong_positive_count = 0

        processed_headlines = 0

        for item in headlines:
            if isinstance(item, dict):
                title = str(
                    item.get(
                        "title",
                        ""
                    )
                ).lower()

            else:
                title = str(item).lower()

            if not title:
                continue

            processed_headlines += 1

            headline_bearish = 0.0
            headline_bullish = 0.0

            has_negation = any(
                term in title
                for term in negation_terms
            )

            uncertainty_factor = 1.0

            if any(
                term in title
                for term in neutralizers
            ):
                uncertainty_factor = 0.75

            for keyword, weight in bearish_keywords.items():
                if keyword in title:
                    adjusted_weight = weight

                    if has_negation:
                        adjusted_weight *= 0.35

                    adjusted_weight *= uncertainty_factor

                    headline_bearish += adjusted_weight

            for keyword, weight in bullish_keywords.items():
                if keyword in title:
                    adjusted_weight = (
                        weight
                        * uncertainty_factor
                    )

                    headline_bullish += adjusted_weight

            if (
                headline_bearish > 0
                and headline_bullish > 0
            ):
                mixed_headlines += 1

                net_difference = (
                    headline_bullish
                    - headline_bearish
                )

                if net_difference > 0:
                    bullish_score += (
                        net_difference * 0.60
                    )

                elif net_difference < 0:
                    bearish_score += (
                        abs(net_difference) * 0.60
                    )

            elif headline_bearish > 0:
                bearish_headlines += 1
                bearish_score += headline_bearish

                if headline_bearish >= 2.5:
                    extreme_negative_count += 1

            elif headline_bullish > 0:
                bullish_headlines += 1
                bullish_score += headline_bullish

                if headline_bullish >= 2.0:
                    strong_positive_count += 1

        total_sentiment_score = (
            bullish_score
            + bearish_score
        )

        if total_sentiment_score > 0:
            sentiment_balance = (
                bullish_score
                - bearish_score
            ) / total_sentiment_score

        else:
            sentiment_balance = 0.0

        # --------------------------------------------------
        # BASE SENTIMENT
        # --------------------------------------------------

        if sentiment_balance >= 0.45:
            score += 0.15

        elif sentiment_balance >= 0.20:
            score += 0.08

        elif sentiment_balance >= 0.08:
            score += 0.04

        elif sentiment_balance <= -0.45:
            score -= 0.15

        elif sentiment_balance <= -0.20:
            score -= 0.08

        elif sentiment_balance <= -0.08:
            score -= 0.04

        # --------------------------------------------------
        # HEADLINE CONCENTRATION
        # --------------------------------------------------

        if processed_headlines > 0:
            bearish_ratio = (
                bearish_headlines
                / processed_headlines
            )

            bullish_ratio = (
                bullish_headlines
                / processed_headlines
            )
        else:
            bearish_ratio = 0.0
            bullish_ratio = 0.0

        if bearish_ratio >= 0.45:
            score -= 0.08
            risks.append(
                "Strong concentration of negative financial headlines"
            )

        elif bearish_ratio >= 0.30:
            score -= 0.04

        if bullish_ratio >= 0.45:
            score += 0.08

        elif bullish_ratio >= 0.30:
            score += 0.04

        # --------------------------------------------------
        # EXTREME NEWS EVENTS
        # --------------------------------------------------

        if extreme_negative_count >= 5:
            score -= 0.08
            risks.append(
                "Multiple high-severity negative financial headlines detected"
            )

        elif extreme_negative_count >= 3:
            score -= 0.04

        if strong_positive_count >= 5:
            score += 0.06

        elif strong_positive_count >= 3:
            score += 0.03

        # --------------------------------------------------
        # MIXED NEWS PENALTY
        # --------------------------------------------------

        if (
            mixed_headlines >= 5
            and abs(sentiment_balance) < 0.20
        ):
            score = (
                score * 0.70
                + 0.50 * 0.30
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

        if processed_headlines >= 40:
            confidence = 0.85

        elif processed_headlines >= 25:
            confidence = 0.80

        elif processed_headlines >= 15:
            confidence = 0.70

        elif processed_headlines >= 8:
            confidence = 0.60

        elif processed_headlines >= 3:
            confidence = 0.45

        else:
            confidence = 0.30

        return {
            "agent": "news",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Financial news sentiment assessment based on "
                "weighted bullish and bearish headlines, "
                "headline concentration, uncertainty and "
                "high-severity news events."
            ),
            "risks": risks,
            "evidence": {
                "processed_headlines": processed_headlines,
                "bullish_headlines": bullish_headlines,
                "bearish_headlines": bearish_headlines,
                "mixed_headlines": mixed_headlines,
                "bullish_score": round(
                    bullish_score,
                    2
                ),
                "bearish_score": round(
                    bearish_score,
                    2
                ),
                "sentiment_balance": round(
                    sentiment_balance,
                    3
                ),
                "extreme_negative_count": (
                    extreme_negative_count
                ),
                "strong_positive_count": (
                    strong_positive_count
                ),
                "raw_news": news_data,
            }
        }