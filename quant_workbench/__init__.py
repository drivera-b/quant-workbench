"""Public-safe quantitative research workbench utilities."""

from .lifecycle import LifecycleConfig, simulate_lifecycle
from .metrics import bootstrap_ev_ci, summarize_by_regime, summarize_trades
from .public_demo import build_public_demo
from .reporting import write_report_html

__all__ = [
    "LifecycleConfig",
    "bootstrap_ev_ci",
    "build_public_demo",
    "simulate_lifecycle",
    "summarize_by_regime",
    "summarize_trades",
    "write_report_html",
]
