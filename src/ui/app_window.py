"""[HITO 3] Layout principal, validación de entradas y callbacks del Dashboard MLOps."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Optional, Sequence

from config.settings import FeatureVector
from src.core.feature_tree import DriftIndexBST
from src.core.vector_hash import FeatureHashTable
from src.database.feature_store_db import FeatureStoreDB
from src.io.json_feature_io import EmbeddingJSONManager
from src.ui.views import MetricsSummary, VectorTableView, compute_metrics_summary


class MLOpsDashboard:
    """Controlador y vista principal del Dashboard Operativo FeatureForge AI (Patrón MVC)."""

    def __init__(
        self,
        bst_index: Optional[DriftIndexBST] = None,
        hash_table: Optional[FeatureHashTable] = None,
        json_manager: Optional[EmbeddingJSONManager] = None,
        db_manager: Optional[FeatureStoreDB] = None,
        root: Optional[tk.Misc] = None,
    ) -> None:
        """Inicializa el Dashboard conectando las capas de datos."""
        self.bst_index: DriftIndexBST = bst_index if bst_index is not None else DriftIndexBST()
        self.hash_table: FeatureHashTable = (
            hash_table if hash_table is not None else FeatureHashTable()
        )
        self.json_manager: EmbeddingJSONManager = (
            json_manager if json_manager is not None else EmbeddingJSONManager()
        )
        self.db_manager: Optional[FeatureStoreDB] = db_manager

        self.root: Optional[tk.Misc] = root
        self.displayed_vectors: list[FeatureVector] = []
        self.status_message: str = "Sistema listo."
        self.has_error: bool = False

        self.table_view: Optional[VectorTableView] = None
        self.min_drift_entry: Optional[ttk.Entry] = None
        self.max_drift_entry: Optional[ttk.Entry] = None
        self.search_id_entry: Optional[ttk.Entry] = None
        self.status_label: Optional[ttk.Label] = None

    @staticmethod
    def validate_drift_inputs(min_str: str, max_str: str) -> tuple[float, float]:
        """Valida las cadenas de entrada del usuario para el filtro de rango de Drift.

        Requisitos de evaluación (Hito 3):
        - Lanzar `ValueError` si `min_str` o `max_str` están vacíos o no son numéricos.
        - Lanzar `ValueError` si los valores están fuera de `[0.0, 1.0]` o si `min > max`.
        - Retornar la tupla `(min_val, max_val)` como `float`.
        """
        raise NotImplementedError(
            "TODO [Hito 3]: Implementar MLOpsDashboard.validate_drift_inputs()"
        )

    def index_records(self, records: Sequence[FeatureVector], persist_db: bool = False) -> int:
        """Indexa una colección de vectores en el BST y en la Tabla Hash, actualizando la vista."""
        raise NotImplementedError(
            "TODO [Hito 3]: Implementar MLOpsDashboard.index_records()"
        )

    def load_dataset_from_json(self, file_path: str | Path, persist_db: bool = True) -> int:
        """Carga vectores desde un archivo JSON, los indexa y opcionalmente persiste en SQLite."""
        raise NotImplementedError(
            "TODO [Hito 3]: Implementar MLOpsDashboard.load_dataset_from_json()"
        )

    def on_filter_drift_event(
        self,
        min_str: Optional[str] = None,
        max_str: Optional[str] = None,
    ) -> list[FeatureVector]:
        """Callback del evento de filtrado por rango de Drift usando `DriftIndexBST.range_query`.

        Requisitos de evaluación (Hito 3):
        - Validar las entradas con `validate_drift_inputs`.
        - Si hay un `ValueError`, activar `self.has_error = True`, guardar un mensaje que
          contenga `'Error'` en `self.status_message` y retornar `[]`.
        - Si es válido, consultar `self.bst_index.range_query`, actualizar `self.displayed_vectors`,
          marcar `self.has_error = False` y retornar los vectores filtrados.
        """
        raise NotImplementedError(
            "TODO [Hito 3]: Implementar MLOpsDashboard.on_filter_drift_event()"
        )

    def on_search_id_event(self, feature_id: Optional[str] = None) -> Optional[FeatureVector]:
        """Callback de búsqueda O(1) usando `FeatureHashTable.search`.

        Requisitos de evaluación (Hito 3):
        - Si `feature_id` es vacío o no existe en `self.hash_table`, marcar `self.has_error = True`,
          vaciar `self.displayed_vectors = []` y retornar `None`.
        - Si se encuentra, actualizar `self.displayed_vectors = [found]`, `self.has_error = False`
          y retornar el vector.
        """
        raise NotImplementedError(
            "TODO [Hito 3]: Implementar MLOpsDashboard.on_search_id_event()"
        )

    def get_metrics_summary(self) -> MetricsSummary:
        """Devuelve las métricas actuales sobre los vectores visualizados."""
        return compute_metrics_summary(
            self.displayed_vectors,
            hash_load_factor=self.hash_table.load_factor(),
        )

