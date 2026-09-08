import yfinance as yf


def get_crypto_data():
    symbols = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
    }

    data = {}

    for name, ticker in symbols.items():
        try:
            history = yf.Ticker(ticker).history(
                period="10d",
                interval="1d",
            )

            if history.empty or len(history) < 2:
                continue

            history = history.dropna()

            last_close = float(
                history["Close"].iloc[-1]
            )

            prev_close = float(
                history["Close"].iloc[-2]
            )

            change_1d = (
                (last_close - prev_close)
                / prev_close
            ) * 100

            change_7d = 0.0

            if len(history) >= 8:
                close_7d_ago = float(
                    history["Close"].iloc[-8]
                )

                change_7d = (
                    (last_close - close_7d_ago)
                    / close_7d_ago
                ) * 100

            latest_volume = 0.0
            avg_volume = 0.0
            volume_ratio = 1.0

            if "Volume" in history.columns:
                latest_volume = float(
                    history["Volume"].iloc[-1]
                )

                volume_window = (
                    history["Volume"]
                    .tail(7)
                    .dropna()
                )

                if not volume_window.empty:
                    avg_volume = float(
                        volume_window.mean()
                    )

                    if avg_volume > 0:
                        volume_ratio = (
                            latest_volume
                            / avg_volume
                        )

            data[name] = {
                "price": round(
                    last_close,
                    2,
                ),
                "change_pct": round(
                    change_1d,
                    2,
                ),
                "change_7d_pct": round(
                    change_7d,
                    2,
                ),
                "latest_volume": round(
                    latest_volume,
                    2,
                ),
                "avg_volume_7d": round(
                    avg_volume,
                    2,
                ),
                "volume_ratio": round(
                    volume_ratio,
                    2,
                ),
            }

        except Exception:
            continue

    if "BTC" in data and "ETH" in data:
        btc_7d = float(
            data["BTC"].get(
                "change_7d_pct",
                0.0
            )
        )

        eth_7d = float(
            data["ETH"].get(
                "change_7d_pct",
                0.0
            )
        )

        data["RELATIVE_STRENGTH"] = {
            "btc_vs_eth_7d": round(
                btc_7d - eth_7d,
                2,
            )
        }

    return data