import unittest

from quant_workbench.io import TradeRow
from quant_workbench.metrics import bootstrap_ev_ci, summarize_trades


class MetricsTests(unittest.TestCase):
    def test_summarize_trades_basic(self) -> None:
        rows = [TradeRow(100.0), TradeRow(-50.0), TradeRow(150.0)]
        summary = summarize_trades(rows)
        self.assertEqual(summary["trades"], 3)
        self.assertAlmostEqual(summary["win_rate"], 2 / 3, places=6)
        self.assertEqual(summary["total_pnl"], 200.0)
        self.assertAlmostEqual(summary["expectancy"], 200.0 / 3.0, places=6)
        self.assertEqual(summary["max_drawdown"], 50.0)

    def test_bootstrap_ev_ci_shape(self) -> None:
        rows = [TradeRow(100.0), TradeRow(-50.0), TradeRow(150.0), TradeRow(-25.0)]
        result = bootstrap_ev_ci(rows, iterations=200, seed=7)
        self.assertIn("ev", result)
        self.assertIn("lower", result)
        self.assertIn("upper", result)
        self.assertLessEqual(result["lower"], result["upper"])


if __name__ == "__main__":
    unittest.main()
