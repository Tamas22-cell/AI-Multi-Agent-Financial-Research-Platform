print("STOCK AGENT FILE:", __file__)

from data.stock_data import get_stock_data


class StockAgent:
    def analyze(self):
        stock_data = get_stock_data()

        if not stock_data:
            return {
                "agent": "stock",
                "signal": "neutral",
                "score": 0.50,
                "confidence": 0.30,
                "summary": "No stock market data available",
                "risks": ["Stock market data unavailable"],
                "evidence": []
            }

        changes = [
            stock_data.get("SP500", {}).get("change_pct", 0),
            stock_data.get("NASDAQ", {}).get("change_pct", 0),
            stock_data.get("NVDA", {}).get("change_pct", 0),
            stock_data.get("AAPL", {}).get("change_pct", 0),
            stock_data.get("MSFT", {}).get("change_pct", 0),
        ]

        avg_change = sum(changes) / len(changes)

        if avg_change > 0.75:
            signal = "bullish"
            score = 0.75
        elif avg_change < -0.75:
            signal = "bearish"
            score = 0.25
        else:
            signal = "neutral"
            score = 0.50

        return {
            "agent": "stock",
            "signal": signal,
            "score": score,
            "confidence": 0.70,
            "summary": (
                "Stock market signal based on S&P 500, NASDAQ, "
                f"NVDA, AAPL and MSFT. Average daily change: {avg_change:.2f}%"
            ),
            "risks": [],
            "evidence": stock_data
        }