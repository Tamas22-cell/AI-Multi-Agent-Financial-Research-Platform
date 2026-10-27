import unittest
from data.quality import validate_market_batch, validate_market_record


class QualityTests(unittest.TestCase):
    def test_accepts_finite_market_record(self):
        self.assertEqual(validate_market_record({"price": 102.5, "change_pct": -1.2}), [])

    def test_rejects_nonfinite_zero_and_missing(self):
        errors = validate_market_record({"price": 0.0, "change_pct": float("nan")})
        self.assertIn("price: must be positive", errors)
        self.assertIn("change_pct: finite value required", errors)
        self.assertTrue(validate_market_record({"price": None, "change_pct": 2.0}))

    def test_batch_reports_only_invalid_symbols(self):
        issues = validate_market_batch({
            "BTC": {"price": 100.0, "change_pct": 1.0},
            "ETH": {"price": -20.0, "change_pct": 2.0},
            "RELATIVE_STRENGTH": {"btc_vs_eth_7d": 1.0},
        })
        self.assertEqual(list(issues), ["ETH"])


if __name__ == "__main__":
    unittest.main()
