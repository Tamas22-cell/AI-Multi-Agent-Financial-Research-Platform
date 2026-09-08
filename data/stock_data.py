import yfinance as yf


def get_stock_data():
    symbols = {
        "SPY": "SPY",
        "QQQ": "QQQ",
        "DIA": "DIA",
        "IWM": "IWM",
        "NVDA": "NVDA",
        "AAPL": "AAPL",
        "MSFT": "MSFT",
    }

    data = {}

    for name, ticker in symbols.items():
        try:
            history = yf.Ticker(ticker).history(
                period="3mo",
                interval="1d",
            )

            if history.empty or len(history) < 8:
                continue

            close = history["Close"].dropna()

            if len(close) < 8:
                continue

            # 1-day change
            last_close = float(close.iloc[-1])
            prev_close = float(close.iloc[-2])

            change_1d = (
                (last_close - prev_close)
                / prev_close
            ) * 100

            # 7-day change
            close_7d = float(close.iloc[-8])

            change_7d = (
                (last_close - close_7d)
                / close_7d
            ) * 100

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
            }

        except Exception:
            continue

    return data