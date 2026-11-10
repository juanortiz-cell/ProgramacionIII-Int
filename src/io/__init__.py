"""Módulo E/S (Unidad 2): Serialización JSON, streaming, conversión CSV y excepciones."""

from src.io.exceptions import (
    CorruptFeatureFileError,
    DatabaseTransactionError,
    DatasetCorruptError,
    FileIOError,
    MLOpsError,
    SchemaValidationError,
    VectorDimensionMismatchError,
)
from src.io.json_feature_io import EmbeddingJSONManager, JSONManager

__all__ = [
    "CorruptFeatureFileError",
    "DatabaseTransactionError",
    "DatasetCorruptError",
    "EmbeddingJSONManager",
    "FileIOError",
    "JSONManager",
    "MLOpsError",
    "SchemaValidationError",
    "VectorDimensionMismatchError",
]

