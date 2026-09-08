import requests


BASE_URL = "https://fapi.binance.com"
FUTURES_DATA_URL = "https://fapi.binance.com/futures/data"


def _safe_get(url, params=None):
    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def _get_open_interest_history(symbol):
    try:
        history = _safe_get(
            f"{FUTURES_DATA_URL}/openInterestHist",
            params={
                "symbol": symbol,
                "period": "1h",
                "limit": 25,
            },
        )

        if not history or len(history) < 2:
            return {
                "oi_change_1h_pct": 0.0,
                "oi_change_24h_pct": 0.0,
            }

        latest_oi = float(
            history[-1]["sumOpenInterest"]
        )

        previous_oi = float(
            history[-2]["sumOpenInterest"]
        )

        oldest_oi = float(
            history[0]["sumOpenInterest"]
        )

        oi_change_1h = 0.0

        if previous_oi > 0:
            oi_change_1h = (
                (latest_oi - previous_oi)
                / previous_oi
            ) * 100

        oi_change_24h = 0.0

        if oldest_oi > 0:
            oi_change_24h = (
                (latest_oi - oldest_oi)
                / oldest_oi
            ) * 100

        return {
            "oi_change_1h_pct": round(
                oi_change_1h,
                2,
            ),
            "oi_change_24h_pct": round(
                oi_change_24h,
                2,
            ),
        }

    except Exception:
        return {
            "oi_change_1h_pct": 0.0,
            "oi_change_24h_pct": 0.0,
        }


def _get_funding_history(symbol):
    try:
        history = _safe_get(
            f"{BASE_URL}/fapi/v1/fundingRate",
            params={
                "symbol": symbol,
                "limit": 8,
            },
        )

        if not history:
            return {
                "avg_funding_8_periods_pct": 0.0,
                "funding_trend": "neutral",
            }

        funding_rates = [
            float(item["fundingRate"]) * 100
            for item in history
        ]

        avg_funding = (
            sum(funding_rates)
            / len(funding_rates)
        )

        first_funding = funding_rates[0]
        latest_funding = funding_rates[-1]

        if latest_funding > first_funding:
            funding_trend = "rising"

        elif latest_funding < first_funding:
            funding_trend = "falling"

        else:
            funding_trend = "neutral"

        return {
            "avg_funding_8_periods_pct": round(
                avg_funding,
                4,
            ),
            "funding_trend": funding_trend,
        }

    except Exception:
        return {
            "avg_funding_8_periods_pct": 0.0,
            "funding_trend": "neutral",
        }


def _get_symbol_data(symbol):
    funding_json = _safe_get(
        f"{BASE_URL}/fapi/v1/premiumIndex",
        params={
            "symbol": symbol,
        },
    )

    oi_json = _safe_get(
        f"{BASE_URL}/fapi/v1/openInterest",
        params={
            "symbol": symbol,
        },
    )

    mark_price = float(
        funding_json["markPrice"]
    )

    funding_rate = (
        float(
            funding_json["lastFundingRate"]
        )
        * 100
    )

    open_interest = float(
        oi_json["openInterest"]
    )

    oi_notional = (
        open_interest
        * mark_price
    )

    oi_history = (
        _get_open_interest_history(
            symbol
        )
    )

    funding_history = (
        _get_funding_history(
            symbol
        )
    )

    return {
        "symbol": symbol,

        "mark_price": round(
            mark_price,
            2,
        ),

        "funding_rate_pct": round(
            funding_rate,
            4,
        ),

        "avg_funding_8_periods_pct": (
            funding_history[
                "avg_funding_8_periods_pct"
            ]
        ),

        "funding_trend": (
            funding_history[
                "funding_trend"
            ]
        ),

        "open_interest": round(
            open_interest,
            2,
        ),

        "open_interest_notional": round(
            oi_notional,
            2,
        ),

        "oi_change_1h_pct": (
            oi_history[
                "oi_change_1h_pct"
            ]
        ),

        "oi_change_24h_pct": (
            oi_history[
                "oi_change_24h_pct"
            ]
        ),
    }


def get_derivatives_data():
    symbols = [
        "BTCUSDT",
        "ETHUSDT",
    ]

    data = {}

    try:
        for symbol in symbols:
            data[symbol] = (
                _get_symbol_data(
                    symbol
                )
            )

        funding_rates = [
            item["funding_rate_pct"]
            for item in data.values()
        ]

        funding_averages = [
            item[
                "avg_funding_8_periods_pct"
            ]
            for item in data.values()
        ]

        oi_1h_changes = [
            item["oi_change_1h_pct"]
            for item in data.values()
        ]

        oi_24h_changes = [
            item["oi_change_24h_pct"]
            for item in data.values()
        ]

        avg_funding = (
            sum(funding_rates)
            / len(funding_rates)
            if funding_rates
            else 0.0
        )

        avg_historical_funding = (
            sum(funding_averages)
            / len(funding_averages)
            if funding_averages
            else 0.0
        )

        avg_oi_change_1h = (
            sum(oi_1h_changes)
            / len(oi_1h_changes)
            if oi_1h_changes
            else 0.0
        )

        avg_oi_change_24h = (
            sum(oi_24h_changes)
            / len(oi_24h_changes)
            if oi_24h_changes
            else 0.0
        )

        total_oi_notional = sum(
            item[
                "open_interest_notional"
            ]
            for item in data.values()
        )

        data["summary"] = {
            "avg_funding_rate_pct": round(
                avg_funding,
                4,
            ),

            "avg_funding_8_periods_pct": round(
                avg_historical_funding,
                4,
            ),

            "avg_oi_change_1h_pct": round(
                avg_oi_change_1h,
                2,
            ),

            "avg_oi_change_24h_pct": round(
                avg_oi_change_24h,
                2,
            ),

            "total_open_interest_notional": round(
                total_oi_notional,
                2,
            ),
        }

        return data

    except Exception as error:
        return {
            "error": str(error)
        }