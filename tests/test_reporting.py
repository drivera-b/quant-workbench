import tempfile
import unittest
from pathlib import Path

from quant_workbench.io import TradeRow
from quant_workbench.lifecycle import LifecycleConfig, simulate_lifecycle
from quant_workbench.metrics import bootstrap_ev_ci, summarize_trades
from quant_workbench.reporting import write_report_html


class ReportingTests(unittest.TestCase):
    def test_write_report_html(self) -> None:
        rows = [TradeRow(100.0), TradeRow(-50.0), TradeRow(150.0), TradeRow(-25.0)]
        summary = summarize_trades(rows)
        ev_ci = bootstrap_ev_ci(rows, iterations=100, seed=7)
        lifecycle = simulate_lifecycle(rows, config=LifecycleConfig(combine_trade_limit=10, funded_trade_limit=10), iterations=100, seed=7)
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "report.html"
            write_report_html(rows, summary, ev_ci, lifecycle, source_name="sample.csv", out_path=target)
            html = target.read_text(encoding="utf-8")
            self.assertIn("Empirical Trade Summary", html)
            self.assertIn("sample.csv", html)
            self.assertIn("Lifecycle simulation", html)


if __name__ == "__main__":
    unittest.main()
