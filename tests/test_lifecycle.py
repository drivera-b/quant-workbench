import unittest

from quant_workbench.io import TradeRow
from quant_workbench.lifecycle import LifecycleConfig, simulate_lifecycle


class LifecycleTests(unittest.TestCase):
    def test_simulate_lifecycle_shape(self) -> None:
        rows = [TradeRow(200.0), TradeRow(-100.0), TradeRow(150.0), TradeRow(-75.0)]
        result = simulate_lifecycle(
            rows,
            config=LifecycleConfig(combine_trade_limit=10, funded_trade_limit=10),
            iterations=200,
            seed=7,
        )
        self.assertGreaterEqual(result["pass_rate"], 0.0)
        self.assertLessEqual(result["pass_rate"], 1.0)
        self.assertGreaterEqual(result["payout_rate"], 0.0)
        self.assertLessEqual(result["payout_rate"], 1.0)
        self.assertGreaterEqual(result["prob_positive_net"], 0.0)
        self.assertLessEqual(result["prob_positive_net"], 1.0)
        self.assertIn("net_ev", result)


if __name__ == "__main__":
    unittest.main()
