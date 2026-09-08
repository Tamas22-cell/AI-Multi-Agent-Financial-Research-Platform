import yfinance as yf
import numpy as np


def get_risk_data():
    symbols = ["SPY", "QQQ", "BTC-USD", "ETH-USD"]

    prices = yf.download(
        symbols,
        period="3mo",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )["Close"]

    if prices.empty:
        return {}

    prices = prices.dropna(how="all")

    returns = prices.pct_change().dropna()

    if returns.empty:
        return {}

    # --------------------------------------------------
    # VOLATILITY
    # --------------------------------------------------

    volatility = returns.std() * np.sqrt(252)
    avg_volatility = float(volatility.mean())

    # --------------------------------------------------
    # CORRELATION
    # --------------------------------------------------

    correlation = returns.corr()

    correlation_values = correlation.values

    upper_triangle = correlation_values[
        np.triu_indices_from(correlation_values, k=1)
    ]

    if len(upper_triangle) > 0:
        avg_correlation = float(
            np.nanmean(upper_triangle)
        )
    else:
        avg_correlation = 0.0

    # --------------------------------------------------
    # MAX DRAWDOWN
    # --------------------------------------------------

    normalized_prices = prices / prices.iloc[0]

    rolling_peak = normalized_prices.cummax()

    drawdown = (
        normalized_prices - rolling_peak
    ) / rolling_peak

    max_drawdowns = drawdown.min()

    worst_drawdown = float(
        max_drawdowns.min()
    )

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------

    return {
        "avg_volatility": round(
            avg_volatility,
            4
        ),

        "avg_correlation": round(
            avg_correlation,
            4
        ),

        "max_drawdown": round(
            worst_drawdown,
            4
        ),

        "volatility": {
            symbol: round(
                float(volatility[symbol]),
                4
            )
            for symbol in volatility.index
        },

        "max_drawdowns": {
            symbol: round(
                float(max_drawdowns[symbol]),
                4
            )
            for symbol in max_drawdowns.index
        },

        "correlation": (
            correlation
            .round(2)
            .to_dict()
        ),
    }