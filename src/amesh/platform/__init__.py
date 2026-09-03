"""Operator-facing platform services."""

from .dashboard import (
    apply_dashboard_filters,
    builtin_dashboard,
    builtin_dashboards,
    can_edit_dashboard,
    can_view_dashboard,
)
from .flow_test import FlowTestService, FlowTestSimulator, aggregate_coverage

__all__ = [
    "FlowTestService",
    "FlowTestSimulator",
    "aggregate_coverage",
    "apply_dashboard_filters",
    "builtin_dashboard",
    "builtin_dashboards",
    "can_edit_dashboard",
    "can_view_dashboard",
]
