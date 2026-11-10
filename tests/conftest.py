"""Utilidades y datos de prueba compartidos (compatibles con `unittest` y `pytest`)."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import FeatureVector


def make_sample_vectors() -> list[FeatureVector]:
    """Devuelve una lista de 6 vectores de muestra con distintos puntajes de drift."""
    return [
        FeatureVector(
            feature_id="vec_alpha",
            model_name="bert_v1",
            values=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            drift_score=0.45,
            timestamp="2026-10-01T10:00:00+00:00",
        ),
        FeatureVector(
            feature_id="vec_beta",
            model_name="bert_v1",
            values=[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            drift_score=0.15,
            timestamp="2026-10-01T10:05:00+00:00",
        ),
        FeatureVector(
            feature_id="vec_gamma",
            model_name="resnet50_v2",
            values=[-0.1, -0.2, 0.3, 0.4, -0.5, 0.6, 0.7, -0.8],
            drift_score=0.82,
            timestamp="2026-10-01T10:10:00+00:00",
        ),
        FeatureVector(
            feature_id="vec_delta",
            model_name="resnet50_v2",
            values=[0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75],
            drift_score=0.28,
            timestamp="2026-10-01T10:15:00+00:00",
        ),
        FeatureVector(
            feature_id="vec_epsilon",
            model_name="whisper_v3",
            values=[0.9, -0.8, 0.7, -0.6, 0.5, -0.4, 0.3, -0.2],
            drift_score=0.91,
            timestamp="2026-10-01T10:20:00+00:00",
        ),
        FeatureVector(
            feature_id="vec_zeta",
            model_name="whisper_v3",
            values=[0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.77, 0.88],
            drift_score=0.60,
            timestamp="2026-10-01T10:25:00+00:00",
        ),
    ]


def write_sample_json_file(directory: Path) -> Path:
    """Crea un archivo JSON temporal válido con los vectores de muestra."""
    file_path = directory / "valid_embeddings.json"
    payload = [v.to_dict() for v in make_sample_vectors()]
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return file_path
