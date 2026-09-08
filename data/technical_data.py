import yfinance as yf


def get_technical_data(ticker="BTC-USD"):
    try:
        history = yf.Ticker(ticker).history(
            period="6mo",
            interval="1d"
        )

        if history.empty or len(history) < 60:
            return {
                "error": "Insufficient technical market data."
            }

        close = history["Close"].dropna()

        if len(close) < 60:
            return {
                "error": "Insufficient closing price history."
            }

        # --------------------------------------------------
        # EMA
        # --------------------------------------------------

        ema20 = close.ewm(
            span=20,
            adjust=False
        ).mean()

        ema50 = close.ewm(
            span=50,
            adjust=False
        ).mean()

        # --------------------------------------------------
        # RSI 14
        # --------------------------------------------------

        delta = close.diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = gain.ewm(
            alpha=1 / 14,
            adjust=False
        ).mean()

        avg_loss = loss.ewm(
            alpha=1 / 14,
            adjust=False
        ).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (
            100 / (1 + rs)
        )

        # --------------------------------------------------
        # MACD
        # --------------------------------------------------

        ema12 = close.ewm(
            span=12,
            adjust=False
        ).mean()

        ema26 = close.ewm(
            span=26,
            adjust=False
        ).mean()

        macd = ema12 - ema26

        macd_signal = macd.ewm(
            span=9,
            adjust=False
        ).mean()

        macd_histogram = (
            macd - macd_signal
        )

        # --------------------------------------------------
        # PRICE MOMENTUM
        # --------------------------------------------------

        price = float(
            close.iloc[-1]
        )

        price_1d_change = (
            (
                close.iloc[-1]
                - close.iloc[-2]
            )
            / close.iloc[-2]
        ) * 100

        price_7d_change = (
            (
                close.iloc[-1]
                - close.iloc[-8]
            )
            / close.iloc[-8]
        ) * 100

        # --------------------------------------------------
        # OUTPUT
        # --------------------------------------------------

        return {
            "TICKER": ticker,

            "PRICE": round(
                price,
                2
            ),

            "EMA20": round(
                float(ema20.iloc[-1]),
                2
            ),

            "EMA50": round(
                float(ema50.iloc[-1]),
                2
            ),

            "RSI": round(
                float(rsi.iloc[-1]),
                2
            ),

            "MACD": round(
                float(macd.iloc[-1]),
                2
            ),

            "MACD_SIGNAL": round(
                float(macd_signal.iloc[-1]),
                2
            ),

            "MACD_HISTOGRAM": round(
                float(macd_histogram.iloc[-1]),
                2
            ),

            "PRICE_CHANGE_1D_PCT": round(
                float(price_1d_change),
                2
            ),

            "PRICE_CHANGE_7D_PCT": round(
                float(price_7d_change),
                2
            ),
        }

    except Exception as error:
        return {
            "error": str(error)
        }