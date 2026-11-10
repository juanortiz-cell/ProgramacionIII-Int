"""[HITO 1] Árbol Binario de Búsqueda (BST) para indexación por puntaje de Data Drift.

TODO [Hito 1 - Informe Big-O]:
Documenta en este docstring el análisis formal de complejidad temporal y espacial
(promedio y peor caso) para `insert`, `search`, `range_query` e `inorder_traversal`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from config.settings import FeatureVector


@dataclass
class BSTNode:
    """Nodo del Árbol Binario de Búsqueda indexado por `drift_score`.

    Attributes:
        drift_score: Clave numérica de ordenamiento en el rango [0.0, 1.0].
        records: Lista de vectores que comparten exactamente este `drift_score`.
        left: Subárbol izquierdo (`drift_score` menores).
        right: Subárbol derecho (`drift_score` mayores).
    """

    drift_score: float
    records: list[FeatureVector] = field(default_factory=list)
    left: Optional[BSTNode] = None
    right: Optional[BSTNode] = None


class DriftIndexBST:
    """Árbol Binario de Búsqueda que organiza vectores según su Drift Score [0.0, 1.0]."""

    def __init__(self) -> None:
        """Inicializa un árbol BST vacío."""
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        """Devuelve la cantidad total de vectores indexados en el árbol."""
        return self._size

    def insert(self, record: FeatureVector) -> None:
        """Inserta un registro `FeatureVector` en el árbol según su `drift_score`.

        Requisitos de evaluación (Casos Borde):
        - Validar que `record` sea instancia de `FeatureVector` (`TypeError` si no).
        - Validar que `0.0 <= record.drift_score <= 1.0` (`ValueError` si está fuera de rango).
        - Soportar múltiples vectores con el mismo `drift_score` almacenándolos en `node.records`.
        - Si el `feature_id` ya existe en ese nodo, actualizarlo sin incrementar `_size`.
        """
        raise NotImplementedError("TODO [Hito 1]: Implementar DriftIndexBST.insert()")

    def search(self, drift_score: float) -> list[FeatureVector]:
        """Busca todos los vectores que tengan exactamente el `drift_score` indicado.

        Requisitos de evaluación:
        - Validar que `drift_score` esté en `[0.0, 1.0]` (`ValueError` si no).
        - Retornar lista vacía `[]` si el árbol está vacío o el puntaje no existe.
        """
        raise NotImplementedError("TODO [Hito 1]: Implementar DriftIndexBST.search()")

    def range_query(self, min_drift: float, max_drift: float) -> list[FeatureVector]:
        """Extrae en orden ascendente todos los vectores cuyo drift esté en [min_drift, max_drift].

        Requisitos de evaluación:
        - Validar que `0.0 <= min_drift <= 1.0` y `0.0 <= max_drift <= 1.0`.
        - Lanzar `ValueError` si `min_drift > max_drift`.
        - Aplicar poda recursiva (no recorrer subárbol izquierdo si `node.drift_score <= min_drift`,
          ni subárbol derecho si `node.drift_score >= max_drift`) para lograr O(log n + k).
        """
        raise NotImplementedError("TODO [Hito 1]: Implementar DriftIndexBST.range_query()")

    def inorder_traversal(self) -> list[FeatureVector]:
        """Devuelve todos los vectores almacenados ordenados ascendentemente por `drift_score`."""
        raise NotImplementedError("TODO [Hito 1]: Implementar DriftIndexBST.inorder_traversal()")

    def clear(self) -> None:
        """Vacía el árbol por completo."""
        self.root = None
        self._size = 0


# Alias de compatibilidad requerido por el enunciado
BinarySearchTree = DriftIndexBST

