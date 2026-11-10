"""[HITO 3] Componentes de vista y cálculo de métricas de calidad para el Dashboard MLOps."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from typing import Sequence

from config.settings import DEFAULT_DRIFT_THRESHOLD, FeatureVector


@dataclass(frozen=True)
class MetricsSummary:
    """Resumen inmutable de métricas operativas del Feature Store."""

    total_vectors: int
    avg_drift: float
    max_drift: float
    critical_count: int
    hash_load_factor: float


def compute_metrics_summary(
    vectors: Sequence[FeatureVector],
    hash_load_factor: float = 0.0,
    critical_threshold: float = DEFAULT_DRIFT_THRESHOLD,
) -> MetricsSummary:
    """Calcula los indicadores clave (KPIs) a partir de una secuencia de vectores.

    Requisitos de evaluación (Hito 3):
    - Si `vectors` está vacío, retornar `MetricsSummary(0, 0.0, 0.0, 0, hash_load_factor)`
      sin producir `ZeroDivisionError`.
    - Calcular `total_vectors`, `avg_drift` (redondeado a 4 decimales), `max_drift`
      y `critical_count` (vectores con `drift_score >= critical_threshold`).
    """
    raise NotImplementedError("TODO [Hito 3]: Implementar compute_metrics_summary()")


class VectorTableView(ttk.Frame):
    """Tabla dinámica basada en `ttk.Treeview` para visualizar vectores de características."""

    COLUMNS: tuple[str, ...] = (
        "feature_id",
        "model_name",
        "dimension",
        "drift_score",
        "status",
        "timestamp",
    )

    def __init__(self, parent: tk.Misc) -> None:
        """Construye el widget Treeview con barra de desplazamiento vertical."""
        super().__init__(parent)
        self.tree = ttk.Treeview(
            self,
            columns=self.COLUMNS,
            show="headings",
            selectmode="browse",
        )
        for col in self.COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def update_rows(self, vectors: Sequence[FeatureVector]) -> None:
        """Reemplaza las filas visibles de la tabla con la lista de vectores recibida."""
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        for vec in vectors:
            status = "CRÍTICO" if vec.is_anomalous else "ESTABLE"
            self.tree.insert(
                "",
                tk.END,
                iid=vec.feature_id,
                values=(
                    vec.feature_id,
                    vec.model_name,
                    vec.dimension,
                    f"{vec.drift_score:.4f}",
                    status,
                    vec.timestamp,
                ),
            )

