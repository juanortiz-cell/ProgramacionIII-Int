"""Pruebas Unitarias — Hito 2 (25%): Pipeline de Persistencia JSON, Streaming y Excepciones.

Ejecución sin dependencias externas:
    python -m unittest discover -s reference_solution/tests -p "test_hito2_*.py" -v
O con pytest:
    pytest reference_solution/tests/test_hito2_io.py -v
"""

from __future__ import annotations

import inspect
import logging
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import FeatureVector
from src.io.exceptions import (
    CorruptFeatureFileError,
    DatasetCorruptError,
    FileIOError,
    MLOpsError,
    SchemaValidationError,
    VectorDimensionMismatchError,
)
from src.io.json_feature_io import EmbeddingJSONManager, JSONManager
from tests.conftest import make_sample_vectors, write_sample_json_file


class TestEmbeddingJSONManager(unittest.TestCase):
    """Suite de pruebas para jerarquía de excepciones y `EmbeddingJSONManager`."""

    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="featureforge_hito2_"))
        self.sample_vectors = make_sample_vectors()
        self.sample_json_file = write_sample_json_file(self.tmp_dir)
        self.log_file = self.tmp_dir / "mlops_audit.log"

    def tearDown(self) -> None:
        # Cierra FileHandlers abiertos para permitir borrar el directorio en Windows
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith("featureforge_mlops"):
                logger = logging.getLogger(name)
                for handler in list(logger.handlers):
                    handler.close()
                    logger.removeHandler(handler)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_custom_exceptions_inheritance_and_aliases(self) -> None:
        """[Caso Principal] Verifica herencia desde `MLOpsError` y alias de compatibilidad."""
        self.assertTrue(issubclass(SchemaValidationError, MLOpsError))
        self.assertTrue(issubclass(VectorDimensionMismatchError, SchemaValidationError))
        self.assertTrue(issubclass(CorruptFeatureFileError, MLOpsError))
        self.assertTrue(issubclass(FileIOError, MLOpsError))
        self.assertIs(DatasetCorruptError, CorruptFeatureFileError)
        self.assertIs(JSONManager, EmbeddingJSONManager)

    def test_stream_parse_json_returns_generator(self) -> None:
        """[Caso Principal] `stream_parse_json` debe ser un generador y emitir `FeatureVector`."""
        manager = EmbeddingJSONManager(expected_dim=8, log_path=self.log_file)
        stream = manager.stream_parse_json(self.sample_json_file)

        self.assertTrue(
            isinstance(stream, types.GeneratorType) or inspect.isgenerator(stream)
        )
        loaded = list(stream)
        self.assertEqual(len(loaded), len(self.sample_vectors))
        self.assertTrue(all(isinstance(v, FeatureVector) for v in loaded))
        self.assertEqual(loaded[0].feature_id, "vec_alpha")

    def test_bidirectional_json_csv_conversion(self) -> None:
        """[Caso Principal] Conversión JSON -> CSV -> JSON preserva integridad de los vectores."""
        csv_file = self.tmp_dir / "exported_vectors.csv"
        roundtrip_json = self.tmp_dir / "roundtrip_vectors.json"
        manager = EmbeddingJSONManager(expected_dim=8, log_path=self.log_file)

        csv_count = manager.json_to_csv(self.sample_json_file, csv_file)
        self.assertEqual(csv_count, len(self.sample_vectors))
        self.assertTrue(csv_file.exists())

        json_count = manager.csv_to_json(csv_file, roundtrip_json)
        self.assertEqual(json_count, len(self.sample_vectors))

        reloaded = manager.load_json(roundtrip_json)
        self.assertEqual(
            [v.feature_id for v in reloaded],
            [v.feature_id for v in self.sample_vectors],
        )
        self.assertEqual(
            [v.drift_score for v in reloaded],
            [v.drift_score for v in self.sample_vectors],
        )
        self.assertEqual(reloaded[2].values, self.sample_vectors[2].values)

    def test_edge_case_vector_dimension_mismatch_raises(self) -> None:
        """[Caso Borde] Lanza `VectorDimensionMismatchError` si el vector no tiene 8 dimensiones."""
        manager = EmbeddingJSONManager(expected_dim=8, log_path=self.log_file)
        bad_record = {
            "feature_id": "vec_wrong_dim",
            "model_name": "bert_v1",
            "values": [0.1, 0.2, 0.3],
            "drift_score": 0.2,
        }
        with self.assertRaises(VectorDimensionMismatchError):
            manager.validate_schema(bad_record)

    def test_edge_case_missing_fields_or_out_of_range_drift(self) -> None:
        """[Caso Borde] Lanza `SchemaValidationError` ante campos faltantes o drift > 1.0."""
        manager = EmbeddingJSONManager(expected_dim=8, log_path=self.log_file)
        missing_field = {
            "feature_id": "vec_incomplete",
            "values": [0.1] * 8,
            "drift_score": 0.4,
        }
        with self.assertRaises(SchemaValidationError):
            manager.validate_schema(missing_field)

        invalid_drift = {
            "feature_id": "vec_bad_drift",
            "model_name": "bert_v1",
            "values": [0.1] * 8,
            "drift_score": 1.45,
        }
        with self.assertRaises(SchemaValidationError):
            manager.validate_schema(invalid_drift)

    def test_edge_case_corrupt_json_and_missing_file(self) -> None:
        """[Caso Borde] Lanza `CorruptFeatureFileError` en JSON truncado y `FileIOError` si no existe."""
        manager = EmbeddingJSONManager(expected_dim=8, log_path=self.log_file)

        missing_path = self.tmp_dir / "no_existe.json"
        with self.assertRaises(FileIOError):
            list(manager.stream_parse_json(missing_path))

        corrupt_path = self.tmp_dir / "corrupt.json"
        corrupt_path.write_text("{malformed_json: [1, 2, ", encoding="utf-8")
        with self.assertRaises(CorruptFeatureFileError):
            list(manager.stream_parse_json(corrupt_path))

    def test_audit_log_records_events_and_errors(self) -> None:
        """[Sobresaliente - Trazabilidad] Verifica que `mlops_audit.log` registre eventos e incidencias."""
        manager = EmbeddingJSONManager(expected_dim=8, log_path=self.log_file)
        _ = manager.load_json(self.sample_json_file)

        with self.assertRaises(FileIOError):
            manager.load_json(self.tmp_dir / "ghost.json")

        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertIn("INFO", log_content)
        self.assertIn("ERROR", log_content)


if __name__ == "__main__":
    unittest.main()
