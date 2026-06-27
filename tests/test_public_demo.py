import csv
import json
import tempfile
import unittest
from pathlib import Path

from quant_workbench.public_demo import build_public_demo


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class PublicDemoTests(unittest.TestCase):
    def test_build_public_demo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "examples").mkdir(parents=True)
            (root / "results" / "reference").mkdir(parents=True)
            (root / "docs").mkdir(parents=True)

            trades_path = root / "examples" / "anonymized_oos_trades.csv"
            _write_csv(
                trades_path,
                ["trade_id", "session_id", "event_family", "regime", "score_bucket", "bars_held", "outcome", "pnl"],
                [
                    {"trade_id": "T0001", "session_id": "S001", "event_family": "gap", "regime": "volatile", "score_bucket": "0.4-0.5", "bars_held": 1, "outcome": "win", "pnl": 120.0},
                    {"trade_id": "T0002", "session_id": "S001", "event_family": "impulse", "regime": "normal", "score_bucket": "0.2-0.3", "bars_held": 2, "outcome": "loss", "pnl": -90.0},
                    {"trade_id": "T0003", "session_id": "S002", "event_family": "gap", "regime": "volatile", "score_bucket": "0.5-0.6", "bars_held": 1, "outcome": "win", "pnl": 140.0},
                ],
            )

            (root / "results" / "reference" / "benchmark_summary.json").write_text(
                json.dumps({"trades": 100, "win_rate": 0.6, "expectancy": 10.0, "lifecycle_net_ev": 500.0, "lifecycle_prob_positive_net": 0.55, "zero_cross": False}, indent=2),
                encoding="utf-8",
            )
            (root / "results" / "reference" / "methodology.json").write_text(
                json.dumps({"public_boundary": {"includes": ["x"], "excludes": ["y"]}}, indent=2),
                encoding="utf-8",
            )
            (root / "results" / "reference" / "sample_dataset_metadata.json").write_text(
                json.dumps({"dataset": "anonymized_oos_trades", "rows": 3}, indent=2),
                encoding="utf-8",
            )
            _write_csv(
                root / "results" / "reference" / "window_checks.csv",
                ["recent_sessions", "trades", "expectancy", "benchmark_status"],
                [{"recent_sessions": 20, "trades": 3, "expectancy": 12.0, "benchmark_status": "watch"}],
            )
            _write_csv(
                root / "results" / "reference" / "monthly_stability.csv",
                ["month", "trades", "expectancy"],
                [{"month": "2026-06", "trades": 3, "expectancy": 12.0}],
            )
            _write_csv(
                root / "results" / "reference" / "policy_ablations.csv",
                ["policy", "trades", "expectancy", "ev_lower", "zero_cross", "benchmark_status", "lifecycle_net_ev", "lifecycle_prob_positive_net", "lifecycle_funded_payout_rate", "win_rate"],
                [{"policy": "baseline", "trades": 3, "expectancy": 12.0, "ev_lower": -1.0, "zero_cross": True, "benchmark_status": "watch", "lifecycle_net_ev": 100.0, "lifecycle_prob_positive_net": 0.5, "lifecycle_funded_payout_rate": 0.5, "win_rate": 0.67}],
            )
            _write_csv(
                root / "results" / "reference" / "stress_scenarios.csv",
                ["scenario", "net_ev", "funded_payout_rate", "prob_positive_net", "pass_rate", "median_net", "p05_net", "p95_net"],
                [{"scenario": "base", "net_ev": 100.0, "funded_payout_rate": 0.5, "prob_positive_net": 0.5, "pass_rate": 0.9, "median_net": 80.0, "p05_net": -30.0, "p95_net": 160.0}],
            )
            _write_csv(
                root / "results" / "reference" / "firm_comparison.csv",
                ["preset", "prop_firm", "program", "net_ev", "funded_payout_rate", "prob_positive_net", "pass_rate", "avg_payout_cash", "avg_fees_paid", "profit_split"],
                [{"preset": "firm-a", "prop_firm": "Firm A", "program": "Program A", "net_ev": 120.0, "funded_payout_rate": 0.55, "prob_positive_net": 0.52, "pass_rate": 0.9, "avg_payout_cash": 200.0, "avg_fees_paid": 80.0, "profit_split": 0.9}],
            )
            _write_csv(
                root / "results" / "reference" / "firm_comparison_plus2usd.csv",
                ["preset", "prop_firm", "program", "net_ev", "funded_payout_rate", "prob_positive_net", "pass_rate", "avg_payout_cash", "avg_fees_paid", "profit_split"],
                [{"preset": "firm-a", "prop_firm": "Firm A", "program": "Program A", "net_ev": 90.0, "funded_payout_rate": 0.5, "prob_positive_net": 0.49, "pass_rate": 0.9, "avg_payout_cash": 180.0, "avg_fees_paid": 90.0, "profit_split": 0.9}],
            )

            manifest = build_public_demo(root, iterations=100, seed=7)
            self.assertEqual(manifest["report"], "examples/anonymized_oos_report.html")
            self.assertTrue((root / "examples" / "anonymized_oos_report.html").exists())
            self.assertTrue((root / "docs" / "data" / "site_data.json").exists())

            site_data = json.loads((root / "docs" / "data" / "site_data.json").read_text(encoding="utf-8"))
            self.assertEqual(site_data["package"]["source_csv"], "examples/anonymized_oos_trades.csv")
            self.assertIn("benchmark_summary", site_data["reference"])
            self.assertEqual(site_data["reference"]["benchmark_summary"]["trades"], 100)
            self.assertEqual(site_data["package"]["data_profile"]["sessions"], 2)
            self.assertEqual(site_data["package"]["data_profile"]["event_families"][0]["label"], "gap")
            self.assertEqual(site_data["artifacts"][0]["group"], "example")
            self.assertEqual(site_data["manifest"]["report"], "examples/anonymized_oos_report.html")


if __name__ == "__main__":
    unittest.main()
