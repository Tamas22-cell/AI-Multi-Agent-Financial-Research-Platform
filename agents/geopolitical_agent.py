from data.geopolitical_data import get_geopolitical_data


class GeopoliticalAgent:
    def analyze(self):
        geopolitical_data = get_geopolitical_data()

        if (
            not geopolitical_data
            or "error" in geopolitical_data
        ):
            return {
                "agent": "geopolitical",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": (
                    "No usable geopolitical data available."
                ),
                "risks": [
                    "Geopolitical data unavailable"
                ],
                "evidence": geopolitical_data
            }

        score = 0.50
        risks = []

        # --------------------------------------------------
        # KEYWORD GROUPS
        # --------------------------------------------------

        severe_escalation = {
            "invasion": 3.5,
            "nuclear attack": 4.0,
            "nuclear strike": 4.0,
            "missile attack": 3.0,
            "missile strike": 3.0,
            "airstrike": 2.5,
            "air strike": 2.5,
            "military attack": 3.0,
            "war declared": 4.0,
            "declaration of war": 4.0,
            "troops invade": 3.5,
            "major offensive": 3.0,
            "military escalation": 3.0,
        }

        escalation_keywords = {
            "war": 1.5,
            "conflict": 1.2,
            "attack": 1.5,
            "strike": 1.3,
            "missile": 1.5,
            "drone attack": 1.8,
            "military": 0.8,
            "troops": 1.0,
            "tensions": 1.0,
            "escalation": 1.8,
            "retaliation": 1.5,
            "threat": 1.0,
            "clashes": 1.5,
            "combat": 1.5,
            "bombing": 2.0,
            "sanctions": 1.0,
            "embargo": 1.5,
            "blockade": 2.0,
        }

        energy_risk_keywords = {
            "oil disruption": 2.5,
            "oil supply disruption": 3.0,
            "gas disruption": 2.5,
            "energy crisis": 2.5,
            "pipeline attack": 3.0,
            "pipeline disruption": 2.5,
            "shipping disruption": 2.0,
            "strait closure": 3.0,
            "shipping attack": 2.5,
            "oil sanctions": 1.8,
            "energy sanctions": 1.8,
        }

        deescalation_keywords = {
            "ceasefire": 3.0,
            "peace deal": 3.5,
            "peace agreement": 3.5,
            "peace talks": 2.0,
            "negotiations": 1.3,
            "negotiation": 1.3,
            "diplomatic talks": 1.8,
            "diplomacy": 1.2,
            "de-escalation": 2.5,
            "deescalation": 2.5,
            "truce": 3.0,
            "withdrawal": 1.5,
            "agreement": 1.0,
            "sanctions lifted": 2.5,
            "sanctions eased": 2.0,
            "peace proposal": 1.8,
        }

        uncertainty_terms = [
            "may",
            "might",
            "could",
            "possible",
            "potential",
            "reportedly",
            "considering",
            "warning",
            "warns",
            "threatens",
        ]

        negation_terms = [
            "no attack",
            "no invasion",
            "no escalation",
            "avoids war",
            "avoid war",
            "prevent war",
            "prevents war",
            "tensions ease",
            "tensions eased",
            "risk declines",
            "risk falls",
        ]

        # --------------------------------------------------
        # EXTRACT HEADLINES
        # --------------------------------------------------

        headlines = []

        if isinstance(
            geopolitical_data,
            list
        ):
            headlines = geopolitical_data

        elif isinstance(
            geopolitical_data,
            dict
        ):
            for value in (
                geopolitical_data.values()
            ):
                if isinstance(value, list):
                    headlines.extend(value)

        escalation_score = 0.0
        deescalation_score = 0.0
        energy_risk_score = 0.0

        escalation_headlines = 0
        deescalation_headlines = 0
        mixed_headlines = 0

        severe_event_count = 0
        energy_event_count = 0

        processed_headlines = 0

        # --------------------------------------------------
        # HEADLINE ANALYSIS
        # --------------------------------------------------

        for item in headlines:
            if isinstance(item, dict):
                title = str(
                    item.get(
                        "title",
                        ""
                    )
                ).lower()

            else:
                title = str(
                    item
                ).lower()

            if not title:
                continue

            processed_headlines += 1

            headline_escalation = 0.0
            headline_deescalation = 0.0
            headline_energy_risk = 0.0

            uncertainty_factor = 1.0

            if any(
                term in title
                for term in uncertainty_terms
            ):
                uncertainty_factor = 0.70

            has_negation = any(
                term in title
                for term in negation_terms
            )

            # Severe escalation

            for keyword, weight in (
                severe_escalation.items()
            ):
                if keyword in title:
                    adjusted_weight = (
                        weight
                        * uncertainty_factor
                    )

                    if has_negation:
                        adjusted_weight *= 0.20

                    headline_escalation += (
                        adjusted_weight
                    )

            # Normal escalation

            for keyword, weight in (
                escalation_keywords.items()
            ):
                if keyword in title:
                    adjusted_weight = (
                        weight
                        * uncertainty_factor
                    )

                    if has_negation:
                        adjusted_weight *= 0.25

                    headline_escalation += (
                        adjusted_weight
                    )

            # Energy / supply risk

            for keyword, weight in (
                energy_risk_keywords.items()
            ):
                if keyword in title:
                    adjusted_weight = (
                        weight
                        * uncertainty_factor
                    )

                    if has_negation:
                        adjusted_weight *= 0.25

                    headline_energy_risk += (
                        adjusted_weight
                    )

            # De-escalation

            for keyword, weight in (
                deescalation_keywords.items()
            ):
                if keyword in title:
                    headline_deescalation += (
                        weight
                        * uncertainty_factor
                    )

            # Headline classification

            negative_total = (
                headline_escalation
                + headline_energy_risk
            )

            if (
                negative_total > 0
                and headline_deescalation > 0
            ):
                mixed_headlines += 1

                difference = (
                    headline_deescalation
                    - negative_total
                )

                if difference > 0:
                    deescalation_score += (
                        difference * 0.60
                    )

                elif difference < 0:
                    escalation_score += (
                        abs(difference) * 0.60
                    )

            elif negative_total > 0:
                escalation_headlines += 1

                escalation_score += (
                    headline_escalation
                )

                energy_risk_score += (
                    headline_energy_risk
                )

                if headline_escalation >= 3.0:
                    severe_event_count += 1

                if headline_energy_risk >= 2.0:
                    energy_event_count += 1

            elif headline_deescalation > 0:
                deescalation_headlines += 1

                deescalation_score += (
                    headline_deescalation
                )

        # --------------------------------------------------
        # SENTIMENT BALANCE
        # --------------------------------------------------

        total_negative = (
            escalation_score
            + energy_risk_score
        )

        total_signal = (
            total_negative
            + deescalation_score
        )

        if total_signal > 0:
            geopolitical_balance = (
                deescalation_score
                - total_negative
            ) / total_signal

        else:
            geopolitical_balance = 0.0

        # --------------------------------------------------
        # BASE GEOPOLITICAL SCORE
        # --------------------------------------------------

        if geopolitical_balance >= 0.50:
            score += 0.15

        elif geopolitical_balance >= 0.25:
            score += 0.09

        elif geopolitical_balance >= 0.10:
            score += 0.04

        elif geopolitical_balance <= -0.50:
            score -= 0.15

        elif geopolitical_balance <= -0.25:
            score -= 0.09

        elif geopolitical_balance <= -0.10:
            score -= 0.04

        # --------------------------------------------------
        # HEADLINE CONCENTRATION
        # --------------------------------------------------

        if processed_headlines > 0:
            escalation_ratio = (
                escalation_headlines
                / processed_headlines
            )

            deescalation_ratio = (
                deescalation_headlines
                / processed_headlines
            )

        else:
            escalation_ratio = 0.0
            deescalation_ratio = 0.0

        if escalation_ratio >= 0.50:
            score -= 0.08

            risks.append(
                "High concentration of geopolitical risk headlines"
            )

        elif escalation_ratio >= 0.35:
            score -= 0.04

        if deescalation_ratio >= 0.40:
            score += 0.07

        elif deescalation_ratio >= 0.25:
            score += 0.03

        # --------------------------------------------------
        # SEVERE EVENTS
        # --------------------------------------------------

        if severe_event_count >= 5:
            score -= 0.10

            risks.append(
                "Multiple severe geopolitical escalation events detected"
            )

        elif severe_event_count >= 3:
            score -= 0.06

            risks.append(
                "Several high-severity geopolitical events detected"
            )

        elif severe_event_count >= 1:
            score -= 0.02

        # --------------------------------------------------
        # ENERGY / SHIPPING RISK
        # --------------------------------------------------

        if energy_event_count >= 4:
            score -= 0.08

            risks.append(
                "Elevated geopolitical energy and supply-chain risk"
            )

        elif energy_event_count >= 2:
            score -= 0.04

            risks.append(
                "Energy or shipping disruption risk detected"
            )

        # --------------------------------------------------
        # MIXED ENVIRONMENT
        # --------------------------------------------------

        if (
            mixed_headlines >= 4
            and abs(
                geopolitical_balance
            ) < 0.20
        ):
            score = (
                score * 0.70
                + 0.50 * 0.30
            )

        # --------------------------------------------------
        # STRONG DE-ESCALATION CONFIRMATION
        # --------------------------------------------------

        if (
            deescalation_headlines >= 5
            and geopolitical_balance > 0.30
        ):
            score += 0.05

        # --------------------------------------------------
        # STRONG ESCALATION CONFIRMATION
        # --------------------------------------------------

        if (
            escalation_headlines >= 8
            and geopolitical_balance < -0.35
        ):
            score -= 0.05

            risks.append(
                "Broad geopolitical escalation is confirmed across headlines"
            )

        # --------------------------------------------------
        # FINAL SCORE
        # --------------------------------------------------

        score = max(
            0.0,
            min(
                1.0,
                score
            )
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
            "agent": "geopolitical",
            "signal": signal,
            "score": score,
            "confidence": confidence,
            "summary": (
                "Geopolitical assessment based on "
                "military escalation, de-escalation, "
                "sanctions, energy disruption and "
                "supply-chain risk headlines."
            ),
            "risks": risks,
            "evidence": {
                "processed_headlines": (
                    processed_headlines
                ),
                "escalation_headlines": (
                    escalation_headlines
                ),
                "deescalation_headlines": (
                    deescalation_headlines
                ),
                "mixed_headlines": (
                    mixed_headlines
                ),
                "escalation_score": round(
                    escalation_score,
                    2
                ),
                "deescalation_score": round(
                    deescalation_score,
                    2
                ),
                "energy_risk_score": round(
                    energy_risk_score,
                    2
                ),
                "geopolitical_balance": round(
                    geopolitical_balance,
                    3
                ),
                "severe_event_count": (
                    severe_event_count
                ),
                "energy_event_count": (
                    energy_event_count
                ),
                "raw_news": (
                    geopolitical_data
                ),
            }
        }