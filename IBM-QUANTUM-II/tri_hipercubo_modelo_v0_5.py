#!/usr/bin/env python3
"""
tri_hipercubo_modelo_v0_5.py

Versión 0.5 del modelo tri-hipercúbico dual.

Objetivos de esta versión:
1. Construir el subespacio coherente de 256 estados a partir de la ley c_i = a_i * b_i.
2. Separar claramente:
   - estructura del sistema
   - métrica combinatoria del grafo
   - métrica simbólica dual
3. Calcular una matriz de correlación/coherencia real del modelo (12x12) usando los 256 estados.
4. Calcular espectro (eigenvalores) de matrices relevantes.
5. Verificar simetrías naturales del sistema.
6. Verificar invariantes exactos inducidos por la regla de síntesis.
7. Exportar resultados a JSON y generar un HTML resumido.

Nota conceptual importante:
- La matriz combinatoria completa K12 no representa por sí sola el modelo.
- Aquí se construyen matrices que sí salen de la estructura del modelo:
  a) correlación signada entre dimensiones
  b) coincidencia binaria entre dimensiones
  c) una matriz estructural por bloques A/B/C
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import numpy as np

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
# 3. Validación de coherencia
# -----------------------------
def is_coherent(state: Sequence[int]) -> bool:
    """Comprueba que el estado cumple c_i = a_i * b_i para i=1..4."""
    a = state[:4]
    b = state[4:8]
    c = state[8:12]
    return all(c[i] == a[i] * b[i] for i in range(4))


# -----------------------------
# 4. Matrices derivadas del modelo
# -----------------------------
def correlation_matrix(states: Sequence[Sequence[int]]) -> np.ndarray:
    """Matriz de correlación signada C_ij = promedio(x_i * x_j).

    Esta matriz sí sale del modelo y revela dependencias reales entre dimensiones.
    """
    X = np.array(states, dtype=float)  # shape (256, 12)
    return (X.T @ X) / X.shape[0]


def equality_matrix(states: Sequence[Sequence[int]]) -> np.ndarray:
    """Matriz de coincidencia binaria E_ij = P(x_i == x_j).

    Como los valores son ±1, igualdad equivale a producto +1. Se usa fórmula:
        P(igualdad) = (1 + C_ij) / 2
    donde C_ij es la correlación signada.
    """
    C = correlation_matrix(states)
    return (1.0 + C) / 2.0


def structural_block_matrix() -> np.ndarray:
    """Matriz estructural mínima del modelo, no trivial.

    Reglas:
    - conexión interna dentro de cada bloque A, B, C: peso 1.0 (sin diagonal)
    - conexión horizontal A_i <-> B_i: peso 2.0
    - conexión emergente A_i <-> C_i y B_i <-> C_i: peso 2.0

    Esta matriz es una decisión de modelado explícita; no es el grafo completo K12.
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
# 5. Espectro e invariantes lineales
# -----------------------------
def eigensystem(matrix: np.ndarray) -> Dict[str, List[float]]:
    """Calcula eigenvalores ordenados y redondeados para lectura humana."""
    vals = np.linalg.eigvalsh(matrix)  # matriz simétrica -> espectro real
    vals = np.sort(vals)[::-1]
    rounded = [float(np.round(v, 8)) for v in vals]
    multiplicities: Dict[str, int] = {}
    for v in rounded:
        key = f"{v:.8f}"
        multiplicities[key] = multiplicities.get(key, 0) + 1
    return {
        "eigenvalores": rounded,
        "multiplicidades": [{"valor": k, "multiplicidad": v} for k, v in multiplicities.items()],
        "traza": float(np.trace(matrix)),
        "norma_frobenius": float(np.linalg.norm(matrix)),
    }


def pca_3d(matrix: np.ndarray) -> List[Dict[str, float]]:
    """Embedding 3D simple mediante PCA manual sobre filas centradas.

    Se usa SVD de numpy para evitar depender de sklearn.
    """
    X = np.array(matrix, dtype=float)
    Xc = X - X.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(Xc, full_matrices=False)
    components = vt[:3].T
    coords = Xc @ components
    return [
        {
            "label": LABELS[i],
            "x": float(np.round(coords[i, 0], 8)),
            "y": float(np.round(coords[i, 1], 8)),
            "z": float(np.round(coords[i, 2], 8)),
        }
        for i in range(coords.shape[0])
    ]


# -----------------------------
# 6. Simetrías naturales del modelo
# -----------------------------
def permute_within_blocks(state: Sequence[int], perm: Tuple[int, int, int, int]) -> Tuple[int, ...]:
    """Permuta coherentemente ejes dentro de A, B y C con la misma permutación."""
    a = tuple(state[i] for i in perm)
    b = tuple(state[4 + i] for i in perm)
    c = tuple(state[8 + i] for i in perm)
    return a + b + c


def swap_a_b(state: Sequence[int]) -> Tuple[int, ...]:
    """Intercambia los bloques A y B, dejando C intacto.

    Debe preservar el conjunto coherente porque c_i = a_i * b_i = b_i * a_i.
    """
    a = tuple(state[:4])
    b = tuple(state[4:8])
    c = tuple(state[8:12])
    return b + a + c


def global_sign_flip(state: Sequence[int]) -> Tuple[int, ...]:
    """Invierte signo de los 12 ejes.

    No preserva la ley c_i = a_i*b_i si se invierte también C,
    porque entonces C cambiaría a -C. Por tanto se usa como test negativo.
    """
    return tuple(-x for x in state)


def flip_a_and_c(state: Sequence[int]) -> Tuple[int, ...]:
    """Invierte simultáneamente A y C.

    Si A -> -A y B fijo, entonces C debería ir a -C para conservar C = A*B.
    """
    a = tuple(-x for x in state[:4])
    b = tuple(state[4:8])
    c = tuple(-x for x in state[8:12])
    return a + b + c


def flip_b_and_c(state: Sequence[int]) -> Tuple[int, ...]:
    """Invierte simultáneamente B y C, preservando la ley de síntesis."""
    a = tuple(state[:4])
    b = tuple(-x for x in state[4:8])
    c = tuple(-x for x in state[8:12])
    return a + b + c


def test_symmetry(states: Sequence[Tuple[int, ...]], transform: Callable[[Sequence[int]], Tuple[int, ...]]) -> bool:
    """Comprueba si una transformación deja invariante el conjunto coherente."""
    state_set = set(states)
    return all(transform(s) in state_set for s in states)


def symmetry_report(states: Sequence[Tuple[int, ...]]) -> Dict[str, object]:
    """Evalúa un conjunto de simetrías naturales del modelo."""
    perm_count = 0
    perms = list(itertools.permutations(range(4)))
    perm_ok = True
    for perm in perms:
        ok = test_symmetry(states, lambda s, p=perm: permute_within_blocks(s, p))
        perm_ok &= ok
        if ok:
            perm_count += 1

    report = {
        "permuta_misma_permutacion_en_A_B_C": {
            "total_probadas": len(perms),
            "total_que_preservan": perm_count,
            "preserva_todas": perm_ok,
            "interpretacion": "Esperable por simetría de ejes si la permutación se aplica coherentemente a los tres bloques.",
        },
        "intercambio_A_B": test_symmetry(states, swap_a_b),
        "flip_global_12_ejes": test_symmetry(states, global_sign_flip),
        "flip_A_y_C": test_symmetry(states, flip_a_and_c),
        "flip_B_y_C": test_symmetry(states, flip_b_and_c),
    }
    return report


# -----------------------------
# 7. Invariantes exactos y distribuciones
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

    unique_sums = sorted(set(sum_abc))
    unique_prods = sorted(set(prod_abc))

    return {
        "invariante_eje_a_eje_aibici_igual_1": all_axis_ok,
        "valores_unicos_suma_aibici": unique_sums,
        "valores_unicos_producto_aibici": unique_prods,
        "interpretacion": {
            "suma": "Si siempre vale 4, entonces cada eje satisface a_i*b_i*c_i = 1 y la suma total es constante.",
            "producto": "Si siempre vale 1, existe una restricción multiplicativa exacta en todo el subespacio coherente.",
        },
    }


# -----------------------------
# 8. Utilidades de presentación
# -----------------------------
def matrix_to_list(M: np.ndarray) -> List[List[float]]:
    return [[float(np.round(v, 8)) for v in row] for row in M.tolist()]


def print_section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def render_html(report: Dict[str, object], path: Path) -> None:
    """Genera un HTML simple, legible y sin dependencias externas."""
    combos = report["metrica_combinatoria"]
    invariants = report["invariantes"]
    sym = report["simetrias"]
    corr_spec = report["espectro_correlacion"]
    struct_spec = report["espectro_estructural"]
    coords = report["embedding_3d_correlacion"]

    rows = "".join(
        f"<tr><td>{c['label']}</td><td>{c['x']}</td><td>{c['y']}</td><td>{c['z']}</td></tr>"
        for c in coords
    )

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Tri-hipercubo dual v0.5</title>
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
<h1>Modelo tri-hipercúbico dual · v0.5</h1>
<p class="small">Versión centrada en coherencia, espectro, simetrías e invariantes.</p>

<div class="card">
<h2>Estructura del sistema</h2>
<ul>
<li>Hipercubo elemental: <b>{report['estructura']['hipercubo_elemental_estados']}</b> estados</li>
<li>Espacio bruto teórico: <b>{report['estructura']['espacio_bruto_teorico']}</b></li>
<li>Subespacio coherente: <b>{report['estructura']['subespacio_coherente']}</b></li>
<li>Dimensiones estructurales: <b>{report['estructura']['dimensiones_estructurales']}</b></li>
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
<h2>Invariantes</h2>
<ul>
<li>a_i·b_i·c_i = 1 eje a eje: <span class="{'ok' if invariants['invariante_eje_a_eje_aibici_igual_1'] else 'no'}">{invariants['invariante_eje_a_eje_aibici_igual_1']}</span></li>
<li>Suma única de a_i·b_i·c_i: <code>{invariants['valores_unicos_suma_aibici']}</code></li>
<li>Producto único de a_i·b_i·c_i: <code>{invariants['valores_unicos_producto_aibici']}</code></li>
</ul>
</div>

<div class="card">
<h2>Simetrías naturales</h2>
<ul>
<li>Permutaciones coherentes dentro de bloques: <b>{sym['permuta_misma_permutacion_en_A_B_C']['total_que_preservan']}/{sym['permuta_misma_permutacion_en_A_B_C']['total_probadas']}</b></li>
<li>Intercambio A ↔ B: <span class="{'ok' if sym['intercambio_A_B'] else 'no'}">{sym['intercambio_A_B']}</span></li>
<li>Flip global 12 ejes: <span class="{'ok' if sym['flip_global_12_ejes'] else 'no'}">{sym['flip_global_12_ejes']}</span></li>
<li>Flip A y C: <span class="{'ok' if sym['flip_A_y_C'] else 'no'}">{sym['flip_A_y_C']}</span></li>
<li>Flip B y C: <span class="{'ok' if sym['flip_B_y_C'] else 'no'}">{sym['flip_B_y_C']}</span></li>
</ul>
</div>

<div class="card">
<h2>Espectro</h2>
<p><b>Correlación:</b> {corr_spec['eigenvalores']}</p>
<p><b>Estructural:</b> {struct_spec['eigenvalores']}</p>
</div>

<div class="card">
<h2>Embedding 3D de las 12 dimensiones (PCA sobre correlación)</h2>
<table>
<thead><tr><th>Dimensión</th><th>X</th><th>Y</th><th>Z</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


# -----------------------------
# 9. Ejecución principal
# -----------------------------
def main() -> None:
    H = hypercube_4d()
    states = coherent_states()

    # Validación básica
    valid = sum(is_coherent(s) for s in states)

    # Métricas
    combos = graph_metrics(12)
    C = correlation_matrix(states)
    E = equality_matrix(states)
    S = structural_block_matrix()

    # Espectros
    corr_spec = eigensystem(C)
    eq_spec = eigensystem(E)
    struct_spec = eigensystem(S)

    # Embedding
    coords = pca_3d(C)

    # Simetrías e invariantes
    sym = symmetry_report(states)
    inv = invariant_report(states)

    report: Dict[str, object] = {
        "modelo": "tri_hipercubo_dual_v0_5",
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
        "matriz_correlacion": {
            "labels": LABELS,
            "matrix": matrix_to_list(C),
        },
        "matriz_igualdad": {
            "labels": LABELS,
            "matrix": matrix_to_list(E),
        },
        "matriz_estructural": {
            "labels": LABELS,
            "matrix": matrix_to_list(S),
        },
        "espectro_correlacion": corr_spec,
        "espectro_igualdad": eq_spec,
        "espectro_estructural": struct_spec,
        "embedding_3d_correlacion": coords,
        "simetrias": sym,
        "invariantes": inv,
        "hipotesis_interpretativa": {
            "residuo_seis": "La diferencia 78 - 72 = 6 puede leerse como observación interpretativa conectable con ±x, ±y, ±z. No se afirma como teorema.",
        },
    }

    # Consola
    print_section("MODELO TRI-HIPERCÚBICO DUAL · VERSIÓN 0.5")

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

    print_section("SIMETRÍAS NATURALES")
    ps = sym['permuta_misma_permutacion_en_A_B_C']
    print(f"Permutaciones coherentes A/B/C       : {ps['total_que_preservan']}/{ps['total_probadas']}")
    print(f"Intercambio A ↔ B                    : {sym['intercambio_A_B']}")
    print(f"Flip global 12 ejes                  : {sym['flip_global_12_ejes']}")
    print(f"Flip A y C                           : {sym['flip_A_y_C']}")
    print(f"Flip B y C                           : {sym['flip_B_y_C']}")

    print_section("ESPECTRO")
    print("Eigenvalores de la matriz de correlación:")
    print(corr_spec['eigenvalores'])
    print("Eigenvalores de la matriz estructural:")
    print(struct_spec['eigenvalores'])

    print_section("EMBEDDING 3D (PCA SOBRE CORRELACIÓN)")
    for item in coords:
        print(f"{item['label']:>2} -> ({item['x']:>8.4f}, {item['y']:>8.4f}, {item['z']:>8.4f})")

    # Exportación
    json_path = OUTDIR / "tri_hipercubo_modelo_v0_5_resultado.json"
    html_path = OUTDIR / "tri_hipercubo_modelo_v0_5_explorador.html"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    render_html(report, html_path)

    print_section("ARCHIVOS GENERADOS")
    print(f"JSON: {json_path}")
    print(f"HTML: {html_path}")


if __name__ == "__main__":
    main()
