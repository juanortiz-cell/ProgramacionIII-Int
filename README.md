# ProgramacionIII-Int
Producto integrador para el curso Programación 3
# Proyecto Integrador: FeatureForge AI
**Motor de Feature Store & Auditoría de Calidad de Datos (MLOps / Data Engineering)**

---

## 1. Contexto del Problema

En los sistemas de aprendizaje automático en producción (**MLOps**), las canalizaciones (*pipelines*) de datos deben procesar, validar e indexar diariamente millones de vectores de características (*embeddings*) generados por modelos de Inteligencia Artificial (modelos de lenguaje, visión computacional o audio). Si estos vectores presentan degradación en su distribución (**Data Drift**), inconsistencia de dimensiones o corrupción estructural, los modelos sufren pérdidas críticas de precisión en entornos reales.

**FeatureForge AI** es un motor *Feature Store & Data Quality Engine* en Python diseñado para la ingesta por *streaming*, validación de esquemas, indexación algorítmica en memoria, visualización interactiva y persistencia relacional transaccional de conjuntos de datos vectoriales.

---

## 2. Arquitectura del Sistema y Estructura del Proyecto

La solución adopta una arquitectura en capas (**Patrón MVC / Repository**) con separación estricta entre presentación (`ui`), lógica algorítmica (`core`), procesamiento de entrada/salida (`io`) y persistencia relacional (`database`).

```text
featureforge_ai/
│
├── config/
│   ├── __init__.py
│   └── settings.py              # Modelo FeatureVector, constantes de dimensión, rutas y logger
├── src/
│   ├── __init__.py
│   ├── core/                    # [HITO 1] Algoritmos y Estructuras de Datos Avanzadas
│   │   ├── __init__.py
│   │   ├── feature_tree.py      # DriftIndexBST: Árbol Binario de Búsqueda por Drift Score
│   │   └── vector_hash.py       # FeatureHashTable: Tabla Hash con encadenamiento separado
│   ├── io/                      # [HITO 2] Serialización JSON/CSV, Streaming, Logs y Excepciones
│   │   ├── __init__.py
│   │   ├── exceptions.py        # Jerarquía de excepciones personalizadas de dominio (MLOpsError)
│   │   └── json_feature_io.py   # EmbeddingJSONManager: Generadores JSON <-> CSV y validación
│   ├── ui/                      # [HITO 3] Dashboard Operativo GUI (Tkinter / MVC)
│   │   ├── __init__.py
│   │   ├── app_window.py        # MLOpsDashboard: Layout principal, eventos y controlador
│   │   └── views.py             # VectorTableView y cálculo de KPIs (MetricsSummary)
│   └── database/                # [HITO 4] Persistencia Relacional SQL (SQLite)
│       ├── __init__.py
│       └── feature_store_db.py  # FeatureStoreDB: Repositorio CRUD parametrizado y transacciones
├── data/
│   ├── embeddings_raw.json      # Dataset semilla de vectores de características
│   ├── feature_store.db         # Base de datos relacional SQLite (generada en ejecución)
│   └── mlops_audit.log          # Bitácora de trazabilidad y errores (generada en ejecución)
├── tests/
│   ├── conftest.py              # Datos de prueba y utilidades compartidas
│   ├── test_hito1_core.py       # Pruebas unitarias del Hito 1 (BST y Tabla Hash)
│   ├── test_hito2_io.py         # Pruebas unitarias del Hito 2 (JSON, CSV, Excepciones y Logs)
│   ├── test_hito3_ui.py         # Pruebas unitarias del Hito 3 (Eventos GUI y Validación)
│   └── test_hito4_db.py         # Pruebas unitarias del Hito 4 (SQLite CRUD, ACID y Orquestación)
└── main.py                      # Punto de entrada y orquestación general (bootstrap_system)
```

---

## 3. Especificación de Módulos y Clases Críticas

| Módulo | Archivo | Clase Principal (y Alias) | Métodos Críticos |
| :--- | :--- | :--- | :--- |
| **Config** | `config/settings.py` | `FeatureVector` (`DatasetMetadata`) | `dimension`, `checksum`, `is_anomalous`, `to_dict()`, `from_dict()` |
| **Core (U1)** | `src/core/feature_tree.py` | `DriftIndexBST` (`BinarySearchTree`) | `insert(record)`, `search(drift_score)`, `range_query(min_drift, max_drift)` en $O(\log n + k)$, `inorder_traversal()` |
| **Core (U1)** | `src/core/vector_hash.py` | `FeatureHashTable` (`CustomHashTable`) | `_hash(key)`, `put(record)`, `search(feature_id)` en $O(1)$ promedio, `delete(feature_id)`, `load_factor()` |
| **E/S (U2)** | `src/io/exceptions.py` | `MLOpsError` (Base) | `SchemaValidationError`, `VectorDimensionMismatchError`, `CorruptFeatureFileError` (`DatasetCorruptError`), `FileIOError`, `DatabaseTransactionError` |
| **E/S (U2)** | `src/io/json_feature_io.py` | `EmbeddingJSONManager` (`JSONManager`) | `validate_schema(raw_record)`, `stream_parse_json(file_path)` (generador `yield`), `save_json()`, `json_to_csv()`, `csv_to_json()` |
| **UI (U3)** | `src/ui/app_window.py` | `MLOpsDashboard` | `validate_drift_inputs(min_str, max_str)`, `on_filter_drift_event()`, `on_search_id_event()`, `index_records()` |
| **UI (U3)** | `src/ui/views.py` | `VectorTableView` / `MetricsSummary` | `compute_metrics_summary(vectors)`, `update_rows(vectors)` |
| **DB (U4)** | `src/database/feature_store_db.py` | `FeatureStoreDB` (`DatabaseManager`) | `initialize_schema()`, `upsert_feature(record)`, `bulk_upsert(records)` (ACID), `get_feature()`, `delete_feature()`, `get_drift_report()` |

---

## 4. Plan de Entregas por Hitos

> **Nota sobre ponderación:** Los 4 hitos técnicos suman el **90%** de la calificación práctica (20% + 25% + 25% + 20%), reservando el **10%** restante para la defensa técnica, documentación de arquitectura e informe de complejidad Big-O, o bien ajustándose a **100%** sobre los 4 hitos según indique el docente.

---

### Hito 1 : Núcleo Algorítmico e Indexación en Memoria
* **Objetivo Pedagógico:** Elegir e implementar estructuras de datos avanzadas desde cero para optimizar la búsqueda y el filtrado de vectores sin depender de librerías externas (como `pandas` o `numpy`) ni delegar la tabla hash a un `dict` nativo.
* **Requisitos Técnicos:**
  1. Completar `DriftIndexBST` (`src/core/feature_tree.py`) para indexar objetos `FeatureVector` según su `drift_score` en el rango `[0.0, 1.0]`, soportando múltiples vectores con el mismo puntaje y consultas de rango podadas mediante `range_query(min_drift, max_drift)`.
  2. Completar `FeatureHashTable` (`src/core/vector_hash.py`) utilizando listas enlazadas (`HashNode`) para resolver colisiones por encadenamiento separado (*Separate Chaining*), garantizando búsqueda e inserción en $O(1)$ promedio.
  3. Documentar en los *docstrings* de ambos módulos el análisis formal de complejidad **Big-O** (temporal y espacial, caso promedio y peor caso).
* **Entregable y Verificación:**
  * Código funcional en `src/core/` que supere el 100% de las pruebas en `tests/test_hito1_core.py`:
    ```bash
    python -m unittest discover -s tests -p "test_hito1_*.py" -v
    ```

---

### Hito 2 : Pipeline de Persistencia JSON/CSV, Streaming y Excepciones
* **Objetivo Pedagógico:** Garantizar un flujo confiable de entrada/salida implementando validación de esquemas, generadores de lectura eficiente (*streaming*), trazabilidad con `logging` y manejo robusto de errores con bloques `try / except / finally`.
* **Requisitos Técnicos:**
  1. Verificar la jerarquía de excepciones personalizadas en `src/io/exceptions.py` heredando de `MLOpsError` (`SchemaValidationError`, `VectorDimensionMismatchError`, `CorruptFeatureFileError`, `FileIOError`).
  2. Completar `EmbeddingJSONManager.validate_schema()` en `src/io/json_feature_io.py` para detectar campos faltantes, tipos inválidos, `drift_score` fuera de `[0.0, 1.0]` o inconsistencias en la dimensión del vector (`DEFAULT_EMBEDDING_DIM = 8`).
  3. Implementar el generador `stream_parse_json(file_path)` utilizando `yield` y asegurando el cierre de descriptores de archivo dentro del bloque `finally`.
  4. Implementar el conversor bidireccional `json_to_csv()` y `csv_to_json()` registrando cada operación e incidencia en `data/mlops_audit.log`.
* **Entregable y Verificación:**
  * Módulo `src/io/` completo que supere el 100% de las pruebas en `tests/test_hito2_io.py`:
    ```bash
    python -m unittest discover -s tests -p "test_hito2_*.py" -v
    ```

---

### Hito 3 : Dashboard Gráfico e Interacción Orientada a Eventos
* **Objetivo Pedagógico:** Construir una interfaz gráfica de usuario (GUI) con `tkinter` / `ttk` aplicando programación orientada a eventos y el patrón Modelo-Vista-Controlador (MVC).
* **Requisitos Técnicos:**
  1. Implementar `compute_metrics_summary()` en `src/ui/views.py` para calcular el total de vectores, promedio de *drift*, *drift* máximo, conteo de vectores críticos (`drift_score >= 0.70`) y factor de carga de la tabla hash, manejando colecciones vacías sin división por cero.
  2. Completar `MLOpsDashboard` en `src/ui/app_window.py` conectando los eventos de usuario:
     * `on_filter_drift_event()`: Valida los límites ingresados mediante `validate_drift_inputs()`, consulta `DriftIndexBST.range_query()` y actualiza la tabla dinámica.
     * `on_search_id_event()`: Consulta `FeatureHashTable.search()` en $O(1)$ y muestra el vector localizado.
  3.Proveer retroalimentación visual de estado (`status_message` y bandera `has_error`) ante entradas no numéricas, vacías o rangos invertidos (`min_drift > max_drift`).
* **Entregable y Verificación:**
  * Módulo `src/ui/` funcional que supere el 100% de las pruebas en `tests/test_hito3_ui.py`:
    ```bash
    python -m unittest discover -s tests -p "test_hito3_*.py" -v
    ```

---

### Hito 4 : Persistencia Relacional SQLite y Orquestación Final
* **Objetivo Pedagógico:** Integrar bases de datos relacionales (`sqlite3`) con seguridad contra inyección SQL, atomicidad transaccional (ACID) y orquestación de extremo a extremo.
* **Requisitos Técnicos:**
  1. Completar `FeatureStoreDB` (`src/database/feature_store_db.py`) con operaciones CRUD completas (`initialize_schema`, `upsert_feature`, `get_feature`, `get_all_features`, `delete_feature`) utilizando **exclusivamente consultas parametrizadas (`?`)**.
  2. Implementar `bulk_upsert(records)` con control transaccional explícito (`commit` / `rollback`), garantizando que si un registro del lote falla, ningún cambio parcial quede persistido en la base de datos.
  3. Implementar `get_drift_report(threshold)` con consultas SQL de agregación (`COUNT`, `AVG`, `MAX`) y listado de vectores críticos.
  4. Completar `bootstrap_system()` en `main.py` para orquestar la carga desde JSON, indexación en memoria (BST + Hash Table), persistencia en SQLite y despliegue en el Dashboard.
* **Entregable y Verificación:**
  * Sistema completo integrado que supere las 4 suites de pruebas unitarias:
    ```bash
    python -m unittest discover -s tests -p "test_hito*.py" -v
    ```


## Comandos Rápidos de Evaluación para el Docente / Alumno

```powershell
# Evaluar Hito 1 (Core BST + Hash Table)
python -m unittest discover -s tests -p "test_hito1_*.py" -v

# Evaluar Hito 2 (JSON Streaming + CSV + Excepciones + Logs)
python -m unittest discover -s tests -p "test_hito2_*.py" -v

# Evaluar Hito 3 (Dashboard GUI + Eventos + Validaciones)
python -m unittest discover -s tests -p "test_hito3_*.py" -v

# Evaluar Hito 4 (SQLite CRUD + Inyección SQL + Rollback + Orquestación)
python -m unittest discover -s tests -p "test_hito4_*.py" -v

# Ejecutar la suite completa de los 4 hitos (32 pruebas)
python -m unittest discover -s tests -p "test_hito*.py" -v
```