#!/usr/bin/env python3
"""
tri_hipercubo_modelo_v0_6.py

Versión 0.6 del modelo tri-hipercúbico dual.

Qué añade respecto a v0.5:
1. Matriz 12x12 de información mutua entre A1..C4 sobre los 256 estados coherentes.
2. Análisis de triadas (A_i, B_i, C_i): entropías, información mutua por pares,
   información mutua condicional y una medida simple de sinergia.
3. Tamaño del grupo de automorfismos de la matriz estructural y generadores evidentes.
4. Matriz de distancias de Hamming entre los 256 estados coherentes, espectro y clustering.
5. Embeddings más útiles:
   - embedding 3D de las 12 dimensiones usando la matriz estructural
   - embedding 3D de las 12 dimensiones usando distancia entre perfiles de estado
   - embedding 3D de los 256 estados usando distancia de Hamming

Idea conceptual central:
- La correlación lineal y la información mutua por pares pueden resultar triviales,
  porque la restricción c_i = a_i * b_i es una dependencia conjunta de tipo XOR/producto.
- Por eso esta versión pone el foco en la estructura de triadas y en las simetrías.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import networkx as nx
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score


# -----------------------------
# Configuración general
# -----------------------------
VALS = (-1, +1)
LABELS = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4"]
OUTDIR = Path(".")


# -----------------------------
# 1. Construcción del modelo
# -----------------------------
def hypercube_4d() -> List[Tuple[int, int, int, int]]:
    """Genera los 16 estados de un hipercubo 4D con coordenadas en {-1,+1}."""
    return list(itertools.product(VALS, repeat=4))


def synthesize_c(a: Sequence[int], b: Sequence[int]) -> Tuple[int, int, int, int]:
    """Ley de síntesis eje a eje: c_i = a_i * b_i."""
    return tuple(a[i] * b[i] for i in range(4))


def coherent_states() -> List[Tuple[int, ...]]:
    """Construye los 256 estados coherentes del modelo.

    Cada estado es una 12-tupla: A1..A4, B1..B4, C1..C4.
    """
    H = hypercube_4d()
    states: List[Tuple[int, ...]] = []
    for a in H:
        for b in H:
            c = synthesize_c(a, b)
            states.append(tuple(a + b + c))
    return states


def is_coherent(state: Sequence[int]) -> bool:
    """Comprueba que el estado cumple c_i = a_i * b_i para i=1..4."""
    a = state[:4]
    b = state[4:8]
    c = state[8:12]
    return all(c[i] == a[i] * b[i] for i in range(4))


# -----------------------------
# 2. Métrica combinatoria y simbólica
# -----------------------------
def graph_metrics(n_dims: int = 12) -> Dict[str, int]:
    """Calcula las métricas combinatorias clásicas y la métrica simbólica dual."""
    dims = list(range(n_dims))
    directed = [(i, j) for i in dims for j in dims]
    undirected_no_diag = {(min(i, j), max(i, j)) for i in dims for j in dims if i != j}
    diagonal = [(i, i) for i in dims]
    undirected_with_diag = undirected_no_diag | set(diagonal)
    symbolic_half = len(directed) // 2
    return {
        "relaciones_dirigidas": len(directed),
        "relaciones_no_dirigidas_sin_diagonal": len(undirected_no_diag),
        "relaciones_diagonales": len(diagonal),
        "relaciones_no_dirigidas_con_diagonal": len(undirected_with_diag),
        "relaciones_estructurales_simbolicas": symbolic_half,
        "residuo_78_menos_72": len(undirected_with_diag) - symbolic_half,
    }


# -----------------------------
# 3. Matrices derivadas del modelo
# -----------------------------
def correlation_matrix(states: Sequence[Sequence[int]]) -> np.ndarray:
    """Matriz de correlación signada C_ij = promedio(x_i * x_j)."""
    X = np.array(states, dtype=float)
    return (X.T @ X) / X.shape[0]


def equality_matrix(states: Sequence[Sequence[int]]) -> np.ndarray:
    """Matriz de coincidencia binaria E_ij = P(x_i == x_j)."""
    C = correlation_matrix(states)
    return (1.0 + C) / 2.0


def structural_block_matrix() -> np.ndarray:
    """Matriz estructural del modelo, no trivial.

    Reglas:
    - conexión interna dentro de cada bloque A, B, C: peso 1.0 (sin diagonal)
    - conexión horizontal A_i <-> B_i: peso 2.0
    - conexión emergente A_i <-> C_i y B_i <-> C_i: peso 2.0

    Esta matriz representa la arquitectura explícita del modelo,
    no el grafo completo K12.
    """
    M = np.zeros((12, 12), dtype=float)
    blocks = [range(0, 4), range(4, 8), range(8, 12)]

    for block in blocks:
        for i in block:
            for j in block:
                if i != j:
                    M[i, j] = 1.0

    for i in range(4):
        ai, bi, ci = i, 4 + i, 8 + i
        M[ai, bi] = M[bi, ai] = 2.0
        M[ai, ci] = M[ci, ai] = 2.0
        M[bi, ci] = M[ci, bi] = 2.0

    return M


# -----------------------------
# 4. Información discreta
# -----------------------------
def entropy_from_probs(probs: Iterable[float]) -> float:
    """Entropía en bits a partir de probabilidades."""
    probs = [p for p in probs if p > 0]
    if not probs:
        return 0.0
    return float(-sum(p * np.log2(p) for p in probs))


def entropy_of_columns(columns: Sequence[Sequence[int]]) -> float:
    """Entropía conjunta en bits de una o varias columnas discretas."""
    tuples = list(zip(*columns))
    counts = Counter(tuples)
    total = len(tuples)
    probs = [c / total for c in counts.values()]
    return entropy_from_probs(probs)


def mutual_information_columns(x: Sequence[int], y: Sequence[int]) -> float:
    """Información mutua I(X;Y) para variables discretas."""
    hx = entropy_of_columns([x])
    hy = entropy_of_columns([y])
    hxy = entropy_of_columns([x, y])
    return float(hx + hy - hxy)


def conditional_mutual_information(x: Sequence[int], y: Sequence[int], z: Sequence[int]) -> float:
    """Información mutua condicional I(X;Y|Z)."""
    hxz = entropy_of_columns([x, z])
    hyz = entropy_of_columns([y, z])
    hz = entropy_of_columns([z])
    hxyz = entropy_of_columns([x, y, z])
    return float(hxz + hyz - hz - hxyz)


def interaction_information(x: Sequence[int], y: Sequence[int], z: Sequence[int]) -> float:
    """Información de interacción I(X;Y;Z) = I(X;Y) - I(X;Y|Z).

    Para una estructura XOR ideal suele salir negativa.
    """
    return float(mutual_information_columns(x, y) - conditional_mutual_information(x, y, z))


def mutual_information_matrix(states: Sequence[Sequence[int]]) -> np.ndarray:
    """Matriz 12x12 de información mutua entre variables A1..C4.

    Nota conceptual:
    la dependencia c_i = a_i*b_i es de orden superior. Por ello, aunque
    la información mutua pairwise puede revelar algo en otros modelos,
    aquí puede salir trivial fuera de la diagonal.
    """
    X = np.array(states, dtype=int)
    n = X.shape[1]
    M = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            M[i, j] = mutual_information_columns(X[:, i], X[:, j])
    return M


def triad_information_report(states: Sequence[Sequence[int]]) -> List[Dict[str, float]]:
    """Analiza la estructura de información de cada triada (A_i, B_i, C_i)."""
    X = np.array(states, dtype=int)
    reports: List[Dict[str, float]] = []
    for i in range(4):
        a = X[:, i]
        b = X[:, 4 + i]
        c = X[:, 8 + i]

        ha = entropy_of_columns([a])
        hb = entropy_of_columns([b])
        hc = entropy_of_columns([c])
        hab = entropy_of_columns([a, b])
        hac = entropy_of_columns([a, c])
        hbc = entropy_of_columns([b, c])
        habc = entropy_of_columns([a, b, c])

        iab = mutual_information_columns(a, b)
        iac = mutual_information_columns(a, c)
        ibc = mutual_information_columns(b, c)
        iab_c = conditional_mutual_information(a, b, c)
        synergy = iab_c - iab
        interaction = interaction_information(a, b, c)

        reports.append({
            "eje": i + 1,
            "H_A": float(np.round(ha, 8)),
            "H_B": float(np.round(hb, 8)),
            "H_C": float(np.round(hc, 8)),
            "H_AB": float(np.round(hab, 8)),
            "H_AC": float(np.round(hac, 8)),
            "H_BC": float(np.round(hbc, 8)),
            "H_ABC": float(np.round(habc, 8)),
            "I_A_B": float(np.round(iab, 8)),
            "I_A_C": float(np.round(iac, 8)),
            "I_B_C": float(np.round(ibc, 8)),
            "I_A_B_cond_C": float(np.round(iab_c, 8)),
            "sinergia_proxy": float(np.round(synergy, 8)),
            "informacion_interaccion": float(np.round(interaction, 8)),
        })
    return reports


# -----------------------------
# 5. Espectro y embeddings
# -----------------------------
def eigensystem(matrix: np.ndarray) -> Dict[str, object]:
    """Calcula eigenvalores de matrices simétricas o reales.

    Si la matriz es simétrica usa eigvalsh; si no, eigvals.
    """
    if np.allclose(matrix, matrix.T):
        vals = np.linalg.eigvalsh(matrix)
    else:
        vals = np.linalg.eigvals(matrix)
    vals = np.sort(np.real_if_close(vals))[::-1]
    rounded = [float(np.round(v, 8)) for v in vals]
    multiplicities: Dict[str, int] = {}
    for v in rounded:
        key = f"{v:.8f}"
        multiplicities[key] = multiplicities.get(key, 0) + 1
    return {
        "eigenvalores": rounded,
        "multiplicidades": [{"valor": k, "multiplicidad": v} for k, v in multiplicities.items()],
        "traza": float(np.round(np.trace(matrix), 8)),
        "norma_frobenius": float(np.round(np.linalg.norm(matrix), 8)),
    }


def classical_mds(distance_matrix: np.ndarray, labels: Sequence[str], n_components: int = 3) -> List[Dict[str, float]]:
    """Embedding clásico MDS a partir de una matriz de distancias."""
    D = np.array(distance_matrix, dtype=float)
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    vals, vecs = np.linalg.eigh(B)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    positive = np.clip(vals[:n_components], a_min=0.0, a_max=None)
    coords = vecs[:, :n_components] * np.sqrt(positive)

    return [
        {
            "label": labels[i],
            "x": float(np.round(coords[i, 0], 8)) if n_components >= 1 else 0.0,
            "y": float(np.round(coords[i, 1], 8)) if n_components >= 2 else 0.0,
            "z": float(np.round(coords[i, 2], 8)) if n_components >= 3 else 0.0,
        }
        for i in range(n)
    ]


def spectral_embedding_from_affinity(affinity: np.ndarray, labels: Sequence[str], n_components: int = 3) -> List[Dict[str, float]]:
    """Embedding espectral simple de una matriz de afinidad."""
    A = np.array(affinity, dtype=float)
    degrees = A.sum(axis=1)
    L = np.diag(degrees) - A
    vals, vecs = np.linalg.eigh(L)
    order = np.argsort(vals)
    vals = vals[order]
    vecs = vecs[:, order]

    # Se ignora el primer autovector (autovalor ~0) y se toman los siguientes.
    coords = vecs[:, 1 : 1 + n_components]
    return [
        {
            "label": labels[i],
            "x": float(np.round(coords[i, 0], 8)) if n_components >= 1 else 0.0,
            "y": float(np.round(coords[i, 1], 8)) if n_components >= 2 else 0.0,
            "z": float(np.round(coords[i, 2], 8)) if n_components >= 3 else 0.0,
        }
        for i in range(A.shape[0])
    ]


# -----------------------------
# 6. Simetrías y automorfismos
# -----------------------------
def permute_within_blocks(state: Sequence[int], perm: Tuple[int, int, int, int]) -> Tuple[int, ...]:
    """Permuta coherentemente ejes dentro de A, B y C con la misma permutación."""
    a = tuple(state[i] for i in perm)
    b = tuple(state[4 + i] for i in perm)
    c = tuple(state[8 + i] for i in perm)
    return a + b + c


def swap_a_b(state: Sequence[int]) -> Tuple[int, ...]:
    """Intercambia A y B, dejando C intacto."""
    a = tuple(state[:4])
    b = tuple(state[4:8])
    c = tuple(state[8:12])
    return b + a + c


def global_sign_flip(state: Sequence[int]) -> Tuple[int, ...]:
    """Invierte signo de los 12 ejes. Test negativo esperado."""
    return tuple(-x for x in state)


def flip_a_and_c(state: Sequence[int]) -> Tuple[int, ...]:
    """Invierte simultáneamente A y C, preservando C = A*B."""
    a = tuple(-x for x in state[:4])
    b = tuple(state[4:8])
    c = tuple(-x for x in state[8:12])
    return a + b + c


def flip_b_and_c(state: Sequence[int]) -> Tuple[int, ...]:
    """Invierte simultáneamente B y C, preservando C = A*B."""
    a = tuple(state[:4])
    b = tuple(-x for x in state[4:8])
    c = tuple(-x for x in state[8:12])
    return a + b + c


def test_symmetry(states: Sequence[Tuple[int, ...]], transform) -> bool:
    """Comprueba si una transformación deja invariante el conjunto coherente."""
    state_set = set(states)
    return all(transform(s) in state_set for s in states)


def symmetry_report(states: Sequence[Tuple[int, ...]]) -> Dict[str, object]:
    """Evalúa simetrías naturales del modelo."""
    perms = list(itertools.permutations(range(4)))
    ok_count = 0
    for perm in perms:
        if test_symmetry(states, lambda s, p=perm: permute_within_blocks(s, p)):
            ok_count += 1

    return {
        "permuta_misma_permutacion_en_A_B_C": {
            "total_probadas": len(perms),
            "total_que_preservan": ok_count,
            "preserva_todas": ok_count == len(perms),
        },
        "intercambio_A_B": test_symmetry(states, swap_a_b),
        "flip_global_12_ejes": test_symmetry(states, global_sign_flip),
        "flip_A_y_C": test_symmetry(states, flip_a_and_c),
        "flip_B_y_C": test_symmetry(states, flip_b_and_c),
    }


def structural_automorphisms(structural_matrix: np.ndarray) -> Dict[str, object]:
    """Calcula el tamaño del grupo de automorfismos de la matriz estructural.

    Se usa un grafo ponderado y GraphMatcher de networkx. Para 12 nodos es viable.
    """
    G = nx.Graph()
    for i, label in enumerate(LABELS):
        G.add_node(i, label=label)
    for i in range(structural_matrix.shape[0]):
        for j in range(i + 1, structural_matrix.shape[1]):
            if structural_matrix[i, j] != 0:
                G.add_edge(i, j, weight=float(structural_matrix[i, j]))

    gm = nx.algorithms.isomorphism.GraphMatcher(
        G,
        G,
        edge_match=lambda a, b: float(a["weight"]) == float(b["weight"]),
    )

    count = 0
    examples = []
    for mapping in gm.isomorphisms_iter():
        count += 1
        if len(examples) < 6:
            pretty = {LABELS[k]: LABELS[v] for k, v in sorted(mapping.items())}
            examples.append(pretty)

    return {
        "tamano_grupo_automorfismos": count,
        "generadores_evidentes": [
            "Permutación simultánea de los 4 índices de eje en A, B y C (grupo S4).",
            "Permutación de los tres bloques A, B y C en la matriz estructural por su simetría formal (grupo S3).",
            "Composición de ambas familias, compatible con un tamaño 4! * 3! = 144.",
        ],
        "ejemplos_isomorfismos": examples,
    }


# -----------------------------
# 7. Invariantes exactos
# -----------------------------
def invariant_report(states: Sequence[Sequence[int]]) -> Dict[str, object]:
    """Evalúa invariantes inducidos por la ley c_i = a_i*b_i."""
    sum_abc = []
    prod_abc = []
    all_axis_ok = True
    for s in states:
        a = s[:4]
        b = s[4:8]
        c = s[8:12]
        axis_terms = [a[i] * b[i] * c[i] for i in range(4)]
        all_axis_ok &= all(t == 1 for t in axis_terms)
        sum_abc.append(sum(axis_terms))
        p = 1
        for t in axis_terms:
            p *= t
        prod_abc.append(p)

    return {
        "invariante_eje_a_eje_aibici_igual_1": all_axis_ok,
        "valores_unicos_suma_aibici": sorted(set(sum_abc)),
        "valores_unicos_producto_aibici": sorted(set(prod_abc)),
    }


# -----------------------------
# 8. Distancias de Hamming y clustering
# -----------------------------
def hamming_distance_matrix(items: Sequence[Sequence[int]]) -> np.ndarray:
    """Matriz de distancias de Hamming normalizada (en número de bits distintos)."""
    X = np.array(items, dtype=int)
    n = X.shape[0]
    D = np.zeros((n, n), dtype=float)
    for i in range(n):
        diff = (X[i] != X).sum(axis=1)
        D[i, :] = diff
    return D


def state_distance_report(states: Sequence[Sequence[int]]) -> Dict[str, object]:
    """Analiza la geometría de los 256 estados coherentes."""
    D = hamming_distance_matrix(states)
    offdiag = D[np.triu_indices_from(D, k=1)]
    spectrum = eigensystem(D)

    # Clustering natural: se prueba k = 2..8 y se elige por silhouette.
    best = None
    best_labels = None
    for k in range(2, 9):
        try:
            try:
                model = AgglomerativeClustering(n_clusters=k, metric="precomputed", linkage="average")
            except TypeError:
                model = AgglomerativeClustering(n_clusters=k, affinity="precomputed", linkage="average")
            labels = model.fit_predict(D)
            sil = silhouette_score(D, labels, metric="precomputed")
            if best is None or sil > best["silhouette"]:
                best = {"k": k, "silhouette": float(np.round(sil, 8))}
                best_labels = labels
        except Exception:
            continue

    cluster_sizes = {}
    if best_labels is not None:
        counts = Counter(best_labels)
        cluster_sizes = {str(int(k)): int(v) for k, v in sorted(counts.items())}

    return {
        "matrix": D,
        "distribucion_distancias": {str(int(k)): int(v) for k, v in sorted(Counter(offdiag.astype(int)).items())},
        "distancia_media": float(np.round(offdiag.mean(), 8)),
        "distancia_minima_fuera_diagonal": float(np.round(offdiag.min(), 8)),
        "distancia_maxima": float(np.round(offdiag.max(), 8)),
        "espectro": spectrum,
        "clustering_natural": {
            "mejor_k_por_silhouette": best["k"] if best else None,
            "silhouette": best["silhouette"] if best else None,
            "tamano_clusters": cluster_sizes,
        },
    }


def dimension_profile_distance(states: Sequence[Sequence[int]]) -> np.ndarray:
    """Distancia de Hamming entre dimensiones vistas como perfiles sobre los 256 estados."""
    X = np.array(states, dtype=int).T  # 12 x 256
    n = X.shape[0]
    D = np.zeros((n, n), dtype=float)
    for i in range(n):
        diff = (X[i] != X).sum(axis=1)
        D[i, :] = diff
    return D


# -----------------------------
# 9. Utilidades de presentación
# -----------------------------
def matrix_to_list(M: np.ndarray) -> List[List[float]]:
    return [[float(np.round(v, 8)) for v in row] for row in M.tolist()]


def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def render_html(report: Dict[str, object], path: Path) -> None:
    """Genera un HTML simple, legible y sin dependencias externas."""
    combos = report["metrica_combinatoria"]
    invariants = report["invariantes"]
    sym = report["simetrias"]
    auto = report["automorfismos"]
    triads = report["triadas_informacion"]
    hamming = report["distancias_estados"]
    spec_struct = report["espectro_estructural"]
    spec_mi = report["espectro_informacion_mutua"]

    triad_rows = "".join(
        f"<tr><td>{t['eje']}</td><td>{t['H_A']}</td><td>{t['H_B']}</td><td>{t['H_C']}</td>"
        f"<td>{t['I_A_B']}</td><td>{t['I_A_C']}</td><td>{t['I_B_C']}</td>"
        f"<td>{t['I_A_B_cond_C']}</td><td>{t['sinergia_proxy']}</td><td>{t['informacion_interaccion']}</td></tr>"
        for t in triads
    )

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Tri-hipercubo dual v0.6</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; line-height: 1.45; color: #222; }}
h1,h2 {{ margin-bottom: 0.4rem; }}
.card {{ border: 1px solid #ddd; border-radius: 10px; padding: 16px; margin: 14px 0; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }}
th {{ background: #f6f6f6; }}
code {{ background: #f6f6f6; padding: 2px 5px; border-radius: 4px; }}
.small {{ color: #666; font-size: 13px; }}
.ok {{ color: #0a7a24; font-weight: 700; }}
.no {{ color: #a11; font-weight: 700; }}
</style>
</head>
<body>
<h1>Modelo tri-hipercúbico dual · v0.6</h1>
<p class="small">Versión centrada en información mutua, triadas, automorfismos, distancias y embeddings.</p>

<div class="card">
<h2>Estructura e invariantes</h2>
<ul>
<li>Subespacio coherente: <b>{report['estructura']['subespacio_coherente']}</b></li>
<li>a_i·b_i·c_i = 1 eje a eje: <span class="{'ok' if invariants['invariante_eje_a_eje_aibici_igual_1'] else 'no'}">{invariants['invariante_eje_a_eje_aibici_igual_1']}</span></li>
<li>Suma única de a_i·b_i·c_i: <code>{invariants['valores_unicos_suma_aibici']}</code></li>
<li>Producto único de a_i·b_i·c_i: <code>{invariants['valores_unicos_producto_aibici']}</code></li>
</ul>
</div>

<div class="card">
<h2>Doble métrica</h2>
<ul>
<li>Relaciones dirigidas: <b>{combos['relaciones_dirigidas']}</b></li>
<li>No dirigidas sin diagonal: <b>{combos['relaciones_no_dirigidas_sin_diagonal']}</b></li>
<li>Diagonales: <b>{combos['relaciones_diagonales']}</b></li>
<li>No dirigidas con diagonal: <b>{combos['relaciones_no_dirigidas_con_diagonal']}</b></li>
<li>Relaciones estructurales simbólicas: <b>{combos['relaciones_estructurales_simbolicas']}</b></li>
<li>Residuo 78 − 72: <b>{combos['residuo_78_menos_72']}</b></li>
</ul>
</div>

<div class="card">
<h2>Información mutua y espectro</h2>
<p><b>Espectro de la matriz de información mutua:</b> {spec_mi['eigenvalores']}</p>
<p><b>Espectro de la matriz estructural:</b> {spec_struct['eigenvalores']}</p>
<p class="small">Si la información mutua pairwise sale casi trivial, eso sugiere dependencia de orden superior en las triadas.</p>
</div>

<div class="card">
<h2>Triadas (A_i, B_i, C_i)</h2>
<table>
<thead>
<tr><th>Eje</th><th>H(A)</th><th>H(B)</th><th>H(C)</th><th>I(A;B)</th><th>I(A;C)</th><th>I(B;C)</th><th>I(A;B|C)</th><th>Sinergia</th><th>Interacción</th></tr>
</thead>
<tbody>{triad_rows}</tbody>
</table>
</div>

<div class="card">
<h2>Automorfismos</h2>
<ul>
<li>Tamaño del grupo: <b>{auto['tamano_grupo_automorfismos']}</b></li>
<li>Generadores evidentes:</li>
<ul>{''.join(f'<li>{g}</li>' for g in auto['generadores_evidentes'])}</ul>
</ul>
</div>

<div class="card">
<h2>Simetrías naturales</h2>
<ul>
<li>Permutaciones coherentes A/B/C: <b>{sym['permuta_misma_permutacion_en_A_B_C']['total_que_preservan']}/{sym['permuta_misma_permutacion_en_A_B_C']['total_probadas']}</b></li>
<li>Intercambio A ↔ B: <span class="{'ok' if sym['intercambio_A_B'] else 'no'}">{sym['intercambio_A_B']}</span></li>
<li>Flip global 12 ejes: <span class="{'ok' if sym['flip_global_12_ejes'] else 'no'}">{sym['flip_global_12_ejes']}</span></li>
<li>Flip A y C: <span class="{'ok' if sym['flip_A_y_C'] else 'no'}">{sym['flip_A_y_C']}</span></li>
<li>Flip B y C: <span class="{'ok' if sym['flip_B_y_C'] else 'no'}">{sym['flip_B_y_C']}</span></li>
</ul>
</div>

<div class="card">
<h2>Estados coherentes: distancia de Hamming</h2>
<ul>
<li>Distancia media: <b>{hamming['distancia_media']}</b></li>
<li>Distancia mínima (fuera diagonal): <b>{hamming['distancia_minima_fuera_diagonal']}</b></li>
<li>Distancia máxima: <b>{hamming['distancia_maxima']}</b></li>
<li>Mejor k por silhouette: <b>{hamming['clustering_natural']['mejor_k_por_silhouette']}</b></li>
<li>Silhouette: <b>{hamming['clustering_natural']['silhouette']}</b></li>
<li>Tamaños de clusters: <code>{hamming['clustering_natural']['tamano_clusters']}</code></li>
</ul>
</div>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


# -----------------------------
# 10. Ejecución principal
# -----------------------------
def main() -> None:
    H = hypercube_4d()
    states = coherent_states()
    valid = sum(is_coherent(s) for s in states)

    # Métricas básicas
    combos = graph_metrics(12)
    C = correlation_matrix(states)
    E = equality_matrix(states)
    S = structural_block_matrix()
    MI = mutual_information_matrix(states)

    # Distancias y embeddings
    state_dist = state_distance_report(states)
    dim_profile_dist = dimension_profile_distance(states)
    embed_struct = spectral_embedding_from_affinity(S, LABELS, n_components=3)
    embed_dim_hamming = classical_mds(dim_profile_dist, LABELS, n_components=3)
    embed_state_hamming = classical_mds(
        state_dist["matrix"], [f"s{i}" for i in range(len(states))], n_components=3
    )

    # Espectros
    corr_spec = eigensystem(C)
    eq_spec = eigensystem(E)
    struct_spec = eigensystem(S)
    mi_spec = eigensystem(MI)
    dim_dist_spec = eigensystem(dim_profile_dist)

    # Informacion de triadas
    triads = triad_information_report(states)

    # Simetrías, automorfismos e invariantes
    sym = symmetry_report(states)
    auto = structural_automorphisms(S)
    inv = invariant_report(states)

    report: Dict[str, object] = {
        "modelo": "tri_hipercubo_dual_v0_6",
        "estructura": {
            "hipercubo_elemental_estados": len(H),
            "hipercubos_horizontales": 2,
            "hipercubo_emergente": 1,
            "dimensiones_estructurales": len(states[0]),
            "espacio_bruto_teorico": len(H) ** 3,
            "subespacio_coherente": len(states),
        },
        "validacion": {
            "estados_coherentes_verificados": valid,
            "coherencia_total": valid == len(states),
        },
        "metrica_combinatoria": combos,
        "matriz_correlacion": {"labels": LABELS, "matrix": matrix_to_list(C)},
        "matriz_igualdad": {"labels": LABELS, "matrix": matrix_to_list(E)},
        "matriz_estructural": {"labels": LABELS, "matrix": matrix_to_list(S)},
        "matriz_informacion_mutua": {"labels": LABELS, "matrix": matrix_to_list(MI)},
        "matriz_distancia_dimensiones": {"labels": LABELS, "matrix": matrix_to_list(dim_profile_dist)},
        "espectro_correlacion": corr_spec,
        "espectro_igualdad": eq_spec,
        "espectro_estructural": struct_spec,
        "espectro_informacion_mutua": mi_spec,
        "espectro_distancia_dimensiones": dim_dist_spec,
        "triadas_informacion": triads,
        "simetrias": sym,
        "automorfismos": auto,
        "invariantes": inv,
        "distancias_estados": {
            "distribucion_distancias": state_dist["distribucion_distancias"],
            "distancia_media": state_dist["distancia_media"],
            "distancia_minima_fuera_diagonal": state_dist["distancia_minima_fuera_diagonal"],
            "distancia_maxima": state_dist["distancia_maxima"],
            "espectro": state_dist["espectro"],
            "clustering_natural": state_dist["clustering_natural"],
        },
        "embeddings": {
            "dimensiones_estructural_3d": embed_struct,
            "dimensiones_hamming_3d": embed_dim_hamming,
            "estados_hamming_3d_sample": embed_state_hamming[:20],
            "nota_estados": "Se guarda una muestra de 20 coordenadas para no inflar innecesariamente el JSON. El script calcula las 256.",
        },
        "hipotesis_interpretativa": {
            "residuo_seis": "La diferencia 78 - 72 = 6 puede leerse como observación interpretativa conectable con ±x, ±y, ±z. No se afirma como teorema.",
            "nota_mi": "Si la información mutua pairwise sale casi trivial, eso refuerza que la dependencia fuerte del modelo es triádica y no simplemente binaria.",
        },
    }

    # Guardar JSON completo, incluyendo matrices grandes útiles para análisis posterior.
    json_path = OUTDIR / "tri_hipercubo_modelo_v0_6_resultado.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # HTML resumen.
    html_path = OUTDIR / "tri_hipercubo_modelo_v0_6_explorador.html"
    render_html(report, html_path)

    # Consola
    print_section("MODELO TRI-HIPERCÚBICO DUAL · VERSIÓN 0.6")

    print_section("ESTRUCTURA DEL SISTEMA")
    print(f"Hipercubo elemental                  : {len(H)} estados")
    print(f"Espacio bruto teórico                : {len(H) ** 3}")
    print(f"Subespacio coherente                 : {len(states)}")
    print(f"Dimensiones estructurales            : {len(states[0])}")

    print_section("VALIDACIÓN")
    print(f"Estados coherentes verificados       : {valid}")
    print(f"Coherencia total                     : {'OK' if valid == len(states) else 'ERROR'}")

    print_section("DOBLE MÉTRICA")
    print(f"Relaciones dirigidas                 : {combos['relaciones_dirigidas']}")
    print(f"Relaciones no dirigidas sin diagonal : {combos['relaciones_no_dirigidas_sin_diagonal']}")
    print(f"Relaciones diagonales                : {combos['relaciones_diagonales']}")
    print(f"Relaciones no dirigidas con diagonal : {combos['relaciones_no_dirigidas_con_diagonal']}")
    print(f"Relaciones estructurales simbólicas  : {combos['relaciones_estructurales_simbolicas']}")
    print(f"Residuo 78 - 72                      : {combos['residuo_78_menos_72']}")

    print_section("INVARIANTES EXACTOS")
    print(f"a_i*b_i*c_i = 1 eje a eje            : {inv['invariante_eje_a_eje_aibici_igual_1']}")
    print(f"Valores únicos de suma               : {inv['valores_unicos_suma_aibici']}")
    print(f"Valores únicos de producto           : {inv['valores_unicos_producto_aibici']}")

    print_section("INFORMACIÓN MUTUA")
    print(f"Espectro MI                          : {mi_spec['eigenvalores']}")
    print("Nota                                 : si MI pairwise es casi trivial, la dependencia fuerte es triádica.")

    print_section("TRIADAS (A_i, B_i, C_i)")
    for t in triads:
        print(
            f"Eje {t['eje']}: H(A)={t['H_A']} H(B)={t['H_B']} H(C)={t['H_C']} | "
            f"I(A;B)={t['I_A_B']} I(A;C)={t['I_A_C']} I(B;C)={t['I_B_C']} | "
            f"I(A;B|C)={t['I_A_B_cond_C']} sinergia={t['sinergia_proxy']} interacción={t['informacion_interaccion']}"
        )

    print_section("SIMETRÍAS Y AUTOMORFISMOS")
    ps = sym['permuta_misma_permutacion_en_A_B_C']
    print(f"Permutaciones coherentes A/B/C       : {ps['total_que_preservan']}/{ps['total_probadas']}")
    print(f"Intercambio A ↔ B                    : {sym['intercambio_A_B']}")
    print(f"Flip global 12 ejes                  : {sym['flip_global_12_ejes']}")
    print(f"Flip A y C                           : {sym['flip_A_y_C']}")
    print(f"Flip B y C                           : {sym['flip_B_y_C']}")
    print(f"Tamaño grupo de automorfismos        : {auto['tamano_grupo_automorfismos']}")

    print_section("DISTANCIAS ENTRE ESTADOS")
    print(f"Distancia media                      : {state_dist['distancia_media']}")
    print(f"Distancia mínima fuera diagonal      : {state_dist['distancia_minima_fuera_diagonal']}")
    print(f"Distancia máxima                     : {state_dist['distancia_maxima']}")
    print(f"Distribución distancias              : {state_dist['distribucion_distancias']}")
    print(f"Clustering natural                   : {state_dist['clustering_natural']}")

    print_section("ESPECTRO ESTRUCTURAL")
    print(f"Espectro matriz estructural          : {struct_spec['eigenvalores']}")
    print(f"Espectro distancias dimensiones      : {dim_dist_spec['eigenvalores']}")

    print_section("ARCHIVOS GENERADOS")
    print(f"JSON                                 : {json_path.name}")
    print(f"HTML                                 : {html_path.name}")


if __name__ == "__main__":
    main()
