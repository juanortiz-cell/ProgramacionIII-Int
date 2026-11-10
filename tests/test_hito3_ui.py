"""Pruebas Unitarias — Hito 3 (25%): Dashboard Gráfico e Interacción Orientada a Eventos.

Ejecución sin dependencias externas:
    python -m unittest discover -s reference_solution/tests -p "test_hito3_*.py" -v
O con pytest:
    pytest reference_solution/tests/test_hito3_ui.py -v
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.app_window import MLOpsDashboard
from src.ui.views import compute_metrics_summary
from tests.conftest import make_sample_vectors


class TestMLOpsDashboardController(unittest.TestCase):
    """Pruebas orientadas a eventos y validación del controlador `MLOpsDashboard`."""

    def setUp(self) -> None:
        self.sample_vectors = make_sample_vectors()

    def test_index_and_metrics_summary(self) -> None:
        """[Caso Principal] Indexa vectores y calcula KPIs de calidad correctamente."""
        dashboard = MLOpsDashboard(root=None)
        count = dashboard.index_records(self.sample_vectors)

        self.assertEqual(count, len(self.sample_vectors))
        self.assertFalse(dashboard.has_error)

        metrics = dashboard.get_metrics_summary()
        self.assertEqual(metrics.total_vectors, 6)
        self.assertEqual(metrics.critical_count, 2)
        self.assertEqual(metrics.max_drift, 0.91)

    def test_on_filter_drift_event_updates_displayed_vectors(self) -> None:
        """[Caso Principal] `on_filter_drift_event` consulta el BST y filtra los vectores visibles."""
        dashboard = MLOpsDashboard(root=None)
        dashboard.index_records(self.sample_vectors)

        filtered = dashboard.on_filter_drift_event("0.40", "0.85")
        self.assertFalse(dashboard.has_error)
        self.assertEqual(
            [v.feature_id for v in filtered],
            ["vec_alpha", "vec_zeta", "vec_gamma"],
        )
        self.assertEqual(dashboard.displayed_vectors, filtered)

    def test_on_search_id_event_queries_hash_table(self) -> None:
        """[Caso Principal] `on_search_id_event` localiza en O(1) el vector solicitado."""
        dashboard = MLOpsDashboard(root=None)
        dashboard.index_records(self.sample_vectors)

        found = dashboard.on_search_id_event("vec_epsilon")
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.feature_id, "vec_epsilon")
        self.assertFalse(dashboard.has_error)
        self.assertEqual(len(dashboard.displayed_vectors), 1)

    def test_edge_case_invalid_drift_input_feedback(self) -> None:
        """[Caso Borde] Entradas no numéricas o fuera de rango activan retroalimentación de error."""
        dashboard = MLOpsDashboard(root=None)
        dashboard.index_records(self.sample_vectors)

        res_alpha = dashboard.on_filter_drift_event("abc", "0.8")
        self.assertEqual(res_alpha, [])
        self.assertTrue(dashboard.has_error)
        self.assertIn("Error", dashboard.status_message)

        res_inverted = dashboard.on_filter_drift_event("0.9", "0.2")
        self.assertEqual(res_inverted, [])
        self.assertTrue(dashboard.has_error)

        with self.assertRaises(ValueError):
            dashboard.validate_drift_inputs("-0.1", "1.2")

    def test_edge_case_search_empty_or_unknown_id_feedback(self) -> None:
        """[Caso Borde] Búsqueda de ID vacío o inexistente notifica error en la barra de estado."""
        dashboard = MLOpsDashboard(root=None)
        dashboard.index_records(self.sample_vectors)

        self.assertIsNone(dashboard.on_search_id_event("   "))
        self.assertTrue(dashboard.has_error)

        self.assertIsNone(dashboard.on_search_id_event("vec_inexistente_999"))
        self.assertTrue(dashboard.has_error)
        self.assertEqual(dashboard.displayed_vectors, [])

    def test_edge_case_metrics_on_empty_dataset(self) -> None:
        """[Caso Borde] `compute_metrics_summary` sobre lista vacía no divide por cero."""
        summary = compute_metrics_summary([], hash_load_factor=0.0)
        self.assertEqual(summary.total_vectors, 0)
        self.assertEqual(summary.avg_drift, 0.0)
        self.assertEqual(summary.critical_count, 0)


if __name__ == "__main__":
    unittest.main()
