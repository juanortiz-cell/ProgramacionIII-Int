"""Módulo UI (Unidad 3): Dashboard Operativo GUI orientado a eventos con Tkinter."""

from src.ui.app_window import MLOpsDashboard
from src.ui.views import MetricsSummary, VectorTableView, compute_metrics_summary

__all__ = [
    "MLOpsDashboard",
    "MetricsSummary",
    "VectorTableView",
    "compute_metrics_summary",
]

