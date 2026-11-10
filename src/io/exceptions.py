"""[HITO 2] Jerarquía de excepciones personalizadas de dominio para FeatureForge AI."""

from __future__ import annotations


class MLOpsError(Exception):
    """Excepción base para todos los errores de dominio en FeatureForge AI."""


class SchemaValidationError(MLOpsError):
    """Se lanza cuando un registro incumple los campos, tipos o rangos requeridos."""


class VectorDimensionMismatchError(SchemaValidationError):
    """Se lanza cuando la longitud del vector (`values`) no coincide con la dimensión esperada."""


class CorruptFeatureFileError(MLOpsError):
    """Se lanza cuando un archivo JSON o CSV está corrupto, truncado o malformado."""


class FileIOError(MLOpsError):
    """Se lanza ante errores de lectura/escritura o archivos inexistentes en el sistema de archivos."""


class DatabaseTransactionError(MLOpsError):
    """Se lanza cuando ocurre un fallo en una consulta o transacción SQLite."""


# Alias de compatibilidad requerido por el enunciado
DatasetCorruptError = CorruptFeatureFileError

