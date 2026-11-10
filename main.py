"""[HITO 4] Punto de entrada principal de FeatureForge AI: orquesta DB + IO + Core + GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import DEFAULT_DB_PATH, DEFAULT_JSON_PATH, DEFAULT_LOG_PATH


def bootstrap_system(
    json_path: str | Path = DEFAULT_JSON_PATH,
    db_path: str | Path = DEFAULT_DB_PATH,
    log_path: str | Path = DEFAULT_LOG_PATH,
    launch_gui: bool = False,
) -> dict[str, Any]:
    """Orquesta el flujo completo de FeatureForge AI (Ingesta JSON -> Core -> SQLite -> UI).

    Requisitos de evaluación (Hito 4):
    - Instanciar `EmbeddingJSONManager`, `FeatureStoreDB`, `DriftIndexBST`, `FeatureHashTable`
      y `MLOpsDashboard`.
    - Cargar los datos desde `json_path`, indexarlos en memoria y persistirlos en SQLite.
    - Retornar un diccionario con `'indexed_count'`, `'drift_report'`, `'dashboard'` y `'db_manager'`.
    """
    raise NotImplementedError("TODO [Hito 4]: Implementar bootstrap_system() en main.py")


if __name__ == "__main__":
    bootstrap_system(launch_gui=True)

