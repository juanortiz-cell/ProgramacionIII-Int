"""Pruebas Unitarias — Hito 4 (20%): Persistencia Relacional CRUD SQLite y Orquestación Final.

Ejecución sin dependencias externas:
    python -m unittest discover -s reference_solution/tests -p "test_hito4_*.py" -v
O con pytest:
    pytest reference_solution/tests/test_hito4_db.py -v
"""

from __future__ import annotations

import logging
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import FeatureVector
from main import bootstrap_system
from src.database.feature_store_db import DatabaseManager, FeatureStoreDB
from src.io.exceptions import DatabaseTransactionError
from tests.conftest import make_sample_vectors, write_sample_json_file


class TestFeatureStoreDB(unittest.TestCase):
    """Suite de pruebas para `FeatureStoreDB` (alias `DatabaseManager`)."""

    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="featureforge_hito4_"))
        self.sample_vectors = make_sample_vectors()
        self.sample_json_file = write_sample_json_file(self.tmp_dir)
        self.log_file = self.tmp_dir / "mlops_audit.log"

    def tearDown(self) -> None:
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith("featureforge_mlops"):
                logger = logging.getLogger(name)
                for handler in list(logger.handlers):
                    handler.close()
                    logger.removeHandler(handler)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_alias_compatibility(self) -> None:
        """Verifica que `DatabaseManager` apunte a `FeatureStoreDB`."""
        self.assertIs(DatabaseManager, FeatureStoreDB)

    def test_crud_lifecycle_in_sqlite(self) -> None:
        """[Caso Principal] Ejecuta Create, Read, Update y Delete sobre SQLite."""
        db_file = self.tmp_dir / "test_store.db"
        db = FeatureStoreDB(db_path=db_file, expected_dim=8, log_path=self.log_file)

        try:
            vec = self.sample_vectors[0]
            db.upsert_feature(vec)

            fetched = db.get_feature(vec.feature_id)
            self.assertIsNotNone(fetched)
            assert fetched is not None
            self.assertEqual(fetched.feature_id, vec.feature_id)
            self.assertEqual(fetched.drift_score, vec.drift_score)

            updated_vec = FeatureVector(
                feature_id=vec.feature_id,
                model_name="bert_v2_upgraded",
                values=vec.values,
                drift_score=0.88,
                timestamp=vec.timestamp,
            )
            db.upsert_feature(updated_vec)
            fetched_updated = db.get_feature(vec.feature_id)
            self.assertIsNotNone(fetched_updated)
            assert fetched_updated is not None
            self.assertEqual(fetched_updated.model_name, "bert_v2_upgraded")
            self.assertEqual(fetched_updated.drift_score, 0.88)

            self.assertTrue(db.delete_feature(vec.feature_id))
            self.assertIsNone(db.get_feature(vec.feature_id))
            self.assertFalse(db.delete_feature(vec.feature_id))
        finally:
            db.close()

    def test_get_drift_report_aggregation(self) -> None:
        """[Caso Principal] `get_drift_report` calcula totales, promedios y vectores críticos."""
        db = FeatureStoreDB(db_path=":memory:", expected_dim=8, log_path=self.log_file)
        try:
            db.bulk_upsert(self.sample_vectors)
            report = db.get_drift_report(threshold=0.70)

            self.assertEqual(report["total_vectors"], 6)
            self.assertEqual(report["critical_count"], 2)
            self.assertEqual(report["max_drift"], 0.91)
            critical_ids = [v.feature_id for v in report["critical_vectors"]]
            self.assertEqual(critical_ids, ["vec_epsilon", "vec_gamma"])
        finally:
            db.close()

    def test_edge_case_sql_injection_prevention(self) -> None:
        """[Sobresaliente - Seguridad] Intento de inyección SQL no destruye la tabla `feature_vectors`."""
        db = FeatureStoreDB(db_path=":memory:", expected_dim=8, log_path=self.log_file)
        try:
            db.upsert_feature(self.sample_vectors[0])

            malicious_id = "vec_1'; DROP TABLE feature_vectors; --"
            malicious_vec = FeatureVector(
                feature_id=malicious_id,
                model_name="hacker_model",
                values=[0.1] * 8,
                drift_score=0.5,
            )
            db.upsert_feature(malicious_vec)

            all_records = db.get_all_features()
            self.assertEqual(len(all_records), 2)
            recovered = db.get_feature(malicious_id)
            self.assertIsNotNone(recovered)
            assert recovered is not None
            self.assertEqual(recovered.feature_id, malicious_id)
        finally:
            db.close()

    def test_edge_case_transaction_rollback_on_batch_failure(self) -> None:
        """[Sobresaliente - ACID] Si un vector del lote es inválido, `bulk_upsert` hace rollback total."""
        db = FeatureStoreDB(db_path=":memory:", expected_dim=8, log_path=self.log_file)
        try:
            db.upsert_feature(self.sample_vectors[0])
            self.assertEqual(len(db.get_all_features()), 1)

            corrupt_vec = FeatureVector("vec_bad", "m1", [0.1, 0.2, 0.3], 0.5)
            batch_with_failure = [self.sample_vectors[1], self.sample_vectors[2], corrupt_vec]

            with self.assertRaises(DatabaseTransactionError):
                db.bulk_upsert(batch_with_failure)

            remaining = db.get_all_features()
            self.assertEqual(len(remaining), 1)
            self.assertEqual(remaining[0].feature_id, self.sample_vectors[0].feature_id)
        finally:
            db.close()

    def test_full_system_orchestration_bootstrap(self) -> None:
        """[Integración Final] Verifica el flujo completo JSON -> Core (BST/Hash) -> SQLite -> UI."""
        db_path = self.tmp_dir / "orchestrated.db"
        log_path = self.tmp_dir / "orchestrated.log"

        result = bootstrap_system(
            json_path=self.sample_json_file,
            db_path=db_path,
            log_path=log_path,
            launch_gui=False,
        )
        try:
            self.assertEqual(result["indexed_count"], 6)
            self.assertEqual(result["drift_report"]["total_vectors"], 6)
            self.assertEqual(result["drift_report"]["critical_count"], 2)
        finally:
            result["db_manager"].close()


if __name__ == "__main__":
    unittest.main()
