"""[HITO 4] Repositorio SQLite con consultas CRUD parametrizadas y control transaccional."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import sqlite3
from typing import Any, Optional

from config.settings import (
    DEFAULT_DB_PATH,
    DEFAULT_DRIFT_THRESHOLD,
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_LOG_PATH,
    FeatureVector,
    configure_logger,
)


class FeatureStoreDB:
    """Gestor de persistencia relacional SQLite para FeatureForge AI."""

    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB_PATH,
        expected_dim: int = DEFAULT_EMBEDDING_DIM,
        log_path: str | Path = DEFAULT_LOG_PATH,
    ) -> None:
        """Inicializa la conexión SQLite y llama a `initialize_schema()`."""
        self.db_path_str: str = str(db_path)
        self.expected_dim: int = expected_dim
        self.logger = configure_logger(log_path)

        if self.db_path_str != ":memory:":
            Path(self.db_path_str).parent.mkdir(parents=True, exist_ok=True)

        self._connection: sqlite3.Connection = sqlite3.connect(self.db_path_str)
        self._connection.row_factory = sqlite3.Row
        self.initialize_schema()

    def initialize_schema(self) -> None:
        """Crea la tabla `feature_vectors` si no existe.

        Columnas esperadas:
        `feature_id TEXT PRIMARY KEY, model_name TEXT NOT NULL, values_json TEXT NOT NULL,
        dimension INTEGER NOT NULL, drift_score REAL NOT NULL, checksum TEXT NOT NULL,
        timestamp TEXT NOT NULL`.
        """
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.initialize_schema()"
        )

    def upsert_feature(self, record: FeatureVector) -> None:
        """Inserta o actualiza un vector usando consultas SQL estrictamente parametrizadas (`?`).

        Requisitos de evaluación (Hito 4):
        - Validar dimensión y rango de `record` antes de ejecutar SQL.
        - PROHIBIDO usar f-strings o concatenación en SQL (vulnerabilidad de inyección SQL).
        - Manejar `commit()` y `rollback()` dentro de bloques `try / except / finally`.
        """
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.upsert_feature()"
        )

    def bulk_upsert(self, records: Iterable[FeatureVector]) -> int:
        """Inserta un lote de vectores en una única transacción atómica (todo o nada).

        Requisitos de evaluación (Hito 4):
        - Iniciar transacción; si cualquier vector del lote es inválido o falla, ejecutar
          `self._connection.rollback()` y lanzar `DatabaseTransactionError`.
        """
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.bulk_upsert()"
        )

    def get_feature(self, feature_id: str) -> Optional[FeatureVector]:
        """Recupera un vector por su `feature_id` usando consulta parametrizada."""
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.get_feature()"
        )

    def get_all_features(self) -> list[FeatureVector]:
        """Recupera todos los vectores almacenados en la tabla `feature_vectors`."""
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.get_all_features()"
        )

    def delete_feature(self, feature_id: str) -> bool:
        """Elimina un vector por su `feature_id` y retorna `True` si existía."""
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.delete_feature()"
        )

    def get_drift_report(self, threshold: float = DEFAULT_DRIFT_THRESHOLD) -> dict[str, Any]:
        """Genera el reporte analítico de Drift desde SQLite.

        Returns:
            Diccionario con claves: `'total_vectors'`, `'avg_drift'`, `'max_drift'`,
            `'threshold'`, `'critical_count'` y `'critical_vectors'`.
        """
        raise NotImplementedError(
            "TODO [Hito 4]: Implementar FeatureStoreDB.get_drift_report()"
        )

    def close(self) -> None:
        """Cierra la conexión activa a la base de datos SQLite."""
        if self._connection is not None:
            self._connection.close()


# Alias de compatibilidad requerido por el enunciado
DatabaseManager = FeatureStoreDB

