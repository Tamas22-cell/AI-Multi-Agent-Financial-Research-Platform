import requests


BASE_URL = "https://api.blockchain.info/charts"


def _get_chart(chart_name, timespan="7days"):
    response = requests.get(
        f"{BASE_URL}/{chart_name}",
        params={
            "timespan": timespan,
            "format": "json",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("values", [])


def _calculate_change(values):
    if len(values) < 2:
        return None

    latest = float(values[-1]["y"])
    previous = float(values[-2]["y"])

    if previous == 0:
        return None

    return ((latest - previous) / previous) * 100


def _calculate_period_change(values):
    if len(values) < 2:
        return None

    latest = float(values[-1]["y"])
    first = float(values[0]["y"])

    if first == 0:
        return None

    return ((latest - first) / first) * 100


def get_onchain_data():
    try:
        data = {}

        # --------------------------------------------------
        # HASHRATE
        # --------------------------------------------------

        hash_rate = _get_chart(
            "hash-rate",
            "7days",
        )

        hashrate_1d = _calculate_change(
            hash_rate
        )

        hashrate_7d = _calculate_period_change(
            hash_rate
        )

        if hashrate_1d is not None:
            data["hashrate_change_pct"] = round(
                hashrate_1d,
                2,
            )

        if hashrate_7d is not None:
            data["hashrate_7d_change_pct"] = round(
                hashrate_7d,
                2,
            )

        # --------------------------------------------------
        # BTC PRICE
        # --------------------------------------------------

        market_price = _get_chart(
            "market-price",
            "7days",
        )

        price_1d = _calculate_change(
            market_price
        )

        price_7d = _calculate_period_change(
            market_price
        )

        if price_1d is not None:
            data["btc_price_change_pct"] = round(
                price_1d,
                2,
            )

        if price_7d is not None:
            data["btc_price_7d_change_pct"] = round(
                price_7d,
                2,
            )

        # --------------------------------------------------
        # TRANSACTION ACTIVITY
        # --------------------------------------------------

        transactions = _get_chart(
            "n-transactions",
            "7days",
        )

        tx_change = _calculate_change(
            transactions
        )

        tx_7d_change = _calculate_period_change(
            transactions
        )

        if tx_change is not None:
            data["transactions_change_pct"] = round(
                tx_change,
                2,
            )

        if tx_7d_change is not None:
            data["transactions_7d_change_pct"] = round(
                tx_7d_change,
                2,
            )

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not data:
            return {
                "error": "No usable on-chain data returned."
            }

        return data

    except requests.RequestException as error:
        return {
            "error": f"On-chain API request failed: {error}"
        }

    except (KeyError, TypeError, ValueError, IndexError) as error:
        return {
            "error": f"On-chain data parsing failed: {error}"
        }