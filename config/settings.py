"""Esquemas de validación, modelo de dominio, dimensionalidad y constantes de MLOps."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
from typing import Any

BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
DEFAULT_JSON_PATH: Path = DATA_DIR / "embeddings_raw.json"
DEFAULT_DB_PATH: Path = DATA_DIR / "feature_store.db"
DEFAULT_LOG_PATH: Path = DATA_DIR / "mlops_audit.log"

DEFAULT_EMBEDDING_DIM: int = 8
DEFAULT_HASH_CAPACITY: int = 17
DEFAULT_DRIFT_THRESHOLD: float = 0.70

REQUIRED_SCHEMA_FIELDS: tuple[str, ...] = (
    "feature_id",
    "model_name",
    "values",
    "drift_score",
)


def configure_logger(
    log_path: str | Path = DEFAULT_LOG_PATH,
    logger_name: str = "featureforge_mlops",
) -> logging.Logger:
    """Configura y devuelve un logger con escritura en archivo para auditoría MLOps."""
    target_path = Path(log_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"{logger_name}:{target_path.resolve()}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    resolved_target = str(target_path.resolve())
    has_handler = any(
        isinstance(h, logging.FileHandler)
        and getattr(h, "baseFilename", None) == resolved_target
        for h in logger.handlers
    )

    if not has_handler:
        file_handler = logging.FileHandler(target_path, mode="a", encoding="utf-8")
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


@dataclass(slots=True)
class FeatureVector:
    """Representa un vector de características (embedding) auditado en FeatureForge AI."""

    feature_id: str
    model_name: str
    values: list[float]
    drift_score: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    @property
    def dimension(self) -> int:
        """Devuelve la dimensionalidad del vector de características."""
        return len(self.values)

    @property
    def checksum(self) -> str:
        """Calcula el hash SHA-256 corto (16 hex chars) determinista del vector."""
        payload = json.dumps(
            {
                "feature_id": self.feature_id,
                "model_name": self.model_name,
                "values": [round(float(v), 6) for v in self.values],
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @property
    def is_anomalous(self) -> bool:
        """Indica si el vector supera el umbral crítico de Data Drift."""
        return self.drift_score >= DEFAULT_DRIFT_THRESHOLD

    def to_dict(self) -> dict[str, Any]:
        """Serializa la instancia a un diccionario compatible con JSON."""
        return {
            "feature_id": self.feature_id,
            "model_name": self.model_name,
            "values": [float(v) for v in self.values],
            "drift_score": float(self.drift_score),
            "timestamp": self.timestamp,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureVector:
        """Construye un `FeatureVector` a partir de un diccionario crudo."""
        return cls(
            feature_id=str(data["feature_id"]),
            model_name=str(data["model_name"]),
            values=[float(v) for v in data["values"]],
            drift_score=float(data["drift_score"]),
            timestamp=str(
                data.get(
                    "timestamp",
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                )
            ),
        )


DatasetMetadata = FeatureVector

