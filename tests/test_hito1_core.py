"""Pruebas Unitarias — Hito 1 (20%): Núcleo Algorítmico e Indexación (BST y Tabla Hash).

Ejecución sin dependencias externas:
    python -m unittest discover -s reference_solution/tests -p "test_hito1_*.py" -v
O con pytest:
    pytest reference_solution/tests/test_hito1_core.py -v
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import FeatureVector
from src.core.feature_tree import BinarySearchTree, DriftIndexBST
from src.core.vector_hash import CustomHashTable, FeatureHashTable
from tests.conftest import make_sample_vectors


class TestDriftIndexBST(unittest.TestCase):
    """Suite de pruebas para `DriftIndexBST` (alias `BinarySearchTree`)."""

    def setUp(self) -> None:
        self.sample_vectors = make_sample_vectors()

    def test_alias_compatibility(self) -> None:
        """Verifica que `BinarySearchTree` apunte a `DriftIndexBST`."""
        self.assertIs(BinarySearchTree, DriftIndexBST)

    def test_insert_and_inorder_traversal_sorted(self) -> None:
        """[Caso Principal] Inserta vectores y verifica ordenamiento ascendente por drift_score."""
        bst = DriftIndexBST()
        for vec in self.sample_vectors:
            bst.insert(vec)

        self.assertEqual(len(bst), len(self.sample_vectors))
        ordered = bst.inorder_traversal()
        scores = [v.drift_score for v in ordered]
        self.assertEqual(scores, sorted(scores))

    def test_search_exact_drift_score(self) -> None:
        """[Caso Principal] Busca un vector por su `drift_score` exacto."""
        bst = DriftIndexBST()
        for vec in self.sample_vectors:
            bst.insert(vec)

        found = bst.search(0.82)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].feature_id, "vec_gamma")
        self.assertEqual(bst.search(0.55), [])

    def test_range_query_extracts_matching_subset(self) -> None:
        """[Caso Principal] `range_query(min_drift, max_drift)` devuelve el subconjunto ordenado."""
        bst = DriftIndexBST()
        for vec in self.sample_vectors:
            bst.insert(vec)

        in_range = bst.range_query(0.25, 0.70)
        ids = [v.feature_id for v in in_range]
        self.assertEqual(ids, ["vec_delta", "vec_alpha", "vec_zeta"])

    def test_edge_case_empty_tree(self) -> None:
        """[Caso Borde] Operaciones sobre un árbol vacío no lanzan error y devuelven vacío."""
        bst = DriftIndexBST()
        self.assertEqual(len(bst), 0)
        self.assertEqual(bst.search(0.5), [])
        self.assertEqual(bst.range_query(0.0, 1.0), [])
        self.assertEqual(bst.inorder_traversal(), [])

    def test_edge_case_duplicate_drift_scores_preserved(self) -> None:
        """[Caso Borde] Dos vectores distintos con el mismo `drift_score` se conservan."""
        bst = DriftIndexBST()
        v1 = FeatureVector("dup_1", "m1", [0.1] * 8, 0.50)
        v2 = FeatureVector("dup_2", "m1", [0.2] * 8, 0.50)
        bst.insert(v1)
        bst.insert(v2)

        self.assertEqual(len(bst), 2)
        found = bst.search(0.50)
        self.assertEqual({v.feature_id for v in found}, {"dup_1", "dup_2"})

    def test_edge_case_invalid_drift_score_and_inverted_range(self) -> None:
        """[Caso Borde] Rechaza `drift_score` fuera de [0.0, 1.0] y `min_drift > max_drift`."""
        bst = DriftIndexBST()
        bad_vec = FeatureVector("bad_1", "m1", [0.1] * 8, 1.25)

        with self.assertRaises(ValueError):
            bst.insert(bad_vec)

        with self.assertRaises(ValueError):
            bst.range_query(0.80, 0.20)

        with self.assertRaises(ValueError):
            bst.range_query(-0.1, 0.5)


class TestFeatureHashTable(unittest.TestCase):
    """Suite de pruebas para `FeatureHashTable` (alias `CustomHashTable`)."""

    def setUp(self) -> None:
        self.sample_vectors = make_sample_vectors()

    def test_alias_compatibility(self) -> None:
        """Verifica que `CustomHashTable` apunte a `FeatureHashTable`."""
        self.assertIs(CustomHashTable, FeatureHashTable)

    def test_put_and_search_o1(self) -> None:
        """[Caso Principal] Inserta y recupera registros por `feature_id`."""
        table = FeatureHashTable(capacity=11)
        for vec in self.sample_vectors:
            table.put(vec)

        self.assertEqual(len(table), len(self.sample_vectors))
        target = table.search("vec_gamma")
        self.assertIsNotNone(target)
        assert target is not None
        self.assertEqual(target.model_name, "resnet50_v2")
        self.assertIsNone(table.search("non_existent_id"))

    def test_delete_existing_and_missing(self) -> None:
        """[Caso Principal] Elimina un registro existente y verifica que ya no se encuentre."""
        table = FeatureHashTable(capacity=7)
        for vec in self.sample_vectors:
            table.put(vec)

        self.assertTrue(table.delete("vec_beta"))
        self.assertIsNone(table.search("vec_beta"))
        self.assertEqual(len(table), len(self.sample_vectors) - 1)
        self.assertFalse(table.delete("vec_beta"))

    def test_edge_case_forced_collisions_chaining(self) -> None:
        """[Caso Borde] Con `capacity=1`, todos los elementos colisionan en el mismo bucket."""
        table = FeatureHashTable(capacity=1)
        for vec in self.sample_vectors:
            table.put(vec)

        self.assertEqual(len(table), len(self.sample_vectors))
        self.assertEqual(table.load_factor(), float(len(self.sample_vectors)))

        for vec in self.sample_vectors:
            recovered = table.search(vec.feature_id)
            self.assertIsNotNone(recovered)
            assert recovered is not None
            self.assertEqual(recovered.feature_id, vec.feature_id)

        self.assertTrue(table.delete("vec_delta"))
        self.assertIsNone(table.search("vec_delta"))
        self.assertIsNotNone(table.search("vec_alpha"))
        self.assertIsNotNone(table.search("vec_zeta"))

    def test_edge_case_update_existing_key_does_not_duplicate(self) -> None:
        """[Caso Borde] Insertar un `feature_id` repetido actualiza el valor sin incrementar tamaño."""
        table = FeatureHashTable(capacity=5)
        original = FeatureVector("vec_dup", "m_old", [0.1] * 8, 0.10)
        updated = FeatureVector("vec_dup", "m_new", [0.9] * 8, 0.85)

        table.put(original)
        table.put(updated)

        self.assertEqual(len(table), 1)
        found = table.search("vec_dup")
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.model_name, "m_new")
        self.assertEqual(found.drift_score, 0.85)

    def test_edge_case_invalid_capacity_and_empty_key(self) -> None:
        """[Caso Borde] Rechaza capacidades no positivas y claves vacías."""
        with self.assertRaises(ValueError):
            FeatureHashTable(capacity=0)

        table = FeatureHashTable(capacity=5)
        with self.assertRaises(ValueError):
            table.search("   ")


if __name__ == "__main__":
    unittest.main()
