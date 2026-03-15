#!/usr/bin/env python3
"""
tri_hipercubo_modelo_v0_4.py

Versión 0.4 del modelo tri-hipercúbico dual.

Qué añade respecto a v0.3:
1. Mantiene la construcción matemática y la doble métrica.
2. Genera un HTML más útil para explorar el modelo.
3. Muestra los 256 estados coherentes en una tabla filtrable.
4. Separa visualmente la red estructural A/B/C de la red relacional de 12 dimensiones.
5. Permite activar o desactivar capas de relación en la vista HTML.
6. Mantiene comentarios en cada bloque para que el código sea legible.

Nota importante:
- El 72 sigue siendo una métrica simbólica dual, no un conteo estándar de aristas únicas.
- El 78 sigue siendo la reducción combinatoria con diagonal.
- El residual 6 se deja como hipótesis interpretativa vinculada a ±x, ±y, ±z.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, List, Tuple


# ============================================================
# 1. Configuración de archivos de salida
# ============================================================
# Todos los artefactos se guardan en la misma carpeta que el script.
BASE_DIR = Path(__file__).resolve().parent
JSON_OUT = BASE_DIR / "tri_hipercubo_modelo_v0_4_resultado.json"
HTML_OUT = BASE_DIR / "tri_hipercubo_modelo_v0_4_explorador.html"


# ============================================================
# 2. Definición del hipercubo elemental H = {-1,+1}^4
# ============================================================
# Usamos -1 y +1 como alfabeto dual base del modelo.
DUAL_VALUES = (-1, +1)

# Etiquetas de las 12 dimensiones estructurales.
DIM_LABELS = [
    "A1", "A2", "A3", "A4",
    "B1", "B2", "B3", "B4",
    "C1", "C2", "C3", "C4",
]

# Hipótesis interpretativa para el residual 6.
SPACE3D_DUAL_AXES = ["+x", "-x", "+y", "-y", "+z", "-z"]


def hypercube_4d() -> List[Tuple[int, int, int, int]]:
    """Genera los 16 estados del hipercubo elemental 4D."""
    return list(itertools.product(DUAL_VALUES, repeat=4))


# ============================================================
# 3. Construcción del modelo tri-hipercúbico
# ============================================================
# HA y HB son los dos hipercubos horizontales.
# HC emerge con la regla c_i = a_i * b_i.

def synthesize_c(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    """Aplica la ley mínima de síntesis eje a eje."""
    return tuple(a[i] * b[i] for i in range(4))


def build_coherent_states() -> List[Tuple[int, ...]]:
    """Genera los 256 estados coherentes del modelo."""
    h = hypercube_4d()
    states: List[Tuple[int, ...]] = []
    for a in h:
        for b in h:
            c = synthesize_c(a, b)
            states.append(a + b + c)
    return states


def validate_state(state: Tuple[int, ...]) -> bool:
    """Comprueba que el estado cumple c_i = a_i * b_i."""
    a = state[:4]
    b = state[4:8]
    c = state[8:12]
    return all(c[i] == a[i] * b[i] for i in range(4))


def state_to_record(index: int, state: Tuple[int, ...]) -> Dict[str, object]:
    """Convierte una 12-tupla en un registro más amigable para JSON/HTML."""
    a = state[:4]
    b = state[4:8]
    c = state[8:12]
    return {
        "id": index,
        "A": list(a),
        "B": list(b),
        "C": list(c),
        "A_str": " ".join(f"{x:+d}" for x in a),
        "B_str": " ".join(f"{x:+d}" for x in b),
        "C_str": " ".join(f"{x:+d}" for x in c),
        "signature": "|".join([
            "".join("+" if x == 1 else "-" for x in a),
            "".join("+" if x == 1 else "-" for x in b),
            "".join("+" if x == 1 else "-" for x in c),
        ]),
        "positive_count": sum(1 for x in state if x == 1),
    }


# ============================================================
# 4. Métrica combinatoria del grafo
# ============================================================
# Esta capa es puramente combinatoria y sigue la lógica estándar.

def build_combinatorial_metrics(labels: List[str]) -> Dict[str, object]:
    directed = [(i, j) for i in labels for j in labels]
    undirected_no_diag = {tuple(sorted((i, j))) for i in labels for j in labels if i != j}
    diagonal = [(i, i) for i in labels]
    undirected_with_diag = sorted(set(undirected_no_diag) | set(diagonal))

    return {
        "directed": directed,
        "undirected_no_diagonal": sorted(undirected_no_diag),
        "diagonal": diagonal,
        "undirected_with_diagonal": undirected_with_diag,
        "counts": {
            "directed": len(directed),
            "undirected_no_diagonal": len(undirected_no_diag),
            "diagonal": len(diagonal),
            "undirected_with_diagonal": len(undirected_with_diag),
        },
    }


# ============================================================
# 5. Métrica simbólica dual
# ============================================================
# Esta capa define el 72 como mitad simbólica de las 144 dirigidas.

def build_symbolic_dual_metrics(combinatorial_counts: Dict[str, int]) -> Dict[str, object]:
    directed = combinatorial_counts["directed"]
    symbolic_relations = directed // 2
    residual = combinatorial_counts["undirected_with_diagonal"] - symbolic_relations

    return {
        "symbolic_relations": symbolic_relations,
        "residual_vs_combinatorial_with_diagonal": residual,
        "residual_interpretation": {
            "value": residual,
            "hypothesis": "El residual 6 puede leerse como capa orientada ligada a ±x, ±y, ±z.",
            "space3d_dual_axes": SPACE3D_DUAL_AXES,
            "note": "Hipótesis interpretativa, no teorema combinatorio.",
        },
    }


# ============================================================
# 6. Grafo estructural A/B/C
# ============================================================
# Este grafo es el esqueleto conceptual del modelo.

def build_structural_graph() -> Dict[str, List[Dict[str, str]]]:
    nodes: List[Dict[str, str]] = []
    edges: List[Dict[str, str]] = []

    for i in range(1, 5):
        nodes.append({"id": f"A{i}", "label": f"A{i}", "group": "A"})
        nodes.append({"id": f"B{i}", "label": f"B{i}", "group": "B"})
        nodes.append({"id": f"C{i}", "label": f"C{i}", "group": "C"})

    # Conexiones internas mínimas para no sobrecargar el dibujo.
    for block in ("A", "B", "C"):
        for i in range(1, 4):
            edges.append({
                "from": f"{block}{i}",
                "to": f"{block}{i+1}",
                "kind": "interna",
                "label": "interna",
            })

    # Acoplamientos horizontales A_i <-> B_i.
    for i in range(1, 5):
        edges.append({
            "from": f"A{i}",
            "to": f"B{i}",
            "kind": "horizontal",
            "label": "A↔B",
        })

    # Emergencia del tercer bloque C.
    for i in range(1, 5):
        edges.append({
            "from": f"A{i}",
            "to": f"C{i}",
            "kind": "emergente",
            "label": "A→C",
        })
        edges.append({
            "from": f"B{i}",
            "to": f"C{i}",
            "kind": "emergente",
            "label": "B→C",
        })

    return {"nodes": nodes, "edges": edges}


# ============================================================
# 7. Red relacional de 12 dimensiones
# ============================================================
# Aquí sí construimos una red sobre las 12 dimensiones para mostrar:
# - la capa combinatoria con diagonal (78)
# - una capa simbólica canónica (72) derivada de las 144 relaciones dirigidas

def build_relational_network(labels: List[str]) -> Dict[str, List[Dict[str, object]]]:
    nodes: List[Dict[str, object]] = []
    edges: List[Dict[str, object]] = []

    # Posicionamos los nodos en tres filas: A, B y C.
    positions = {}
    for idx, label in enumerate(labels):
        block = label[0]
        num = int(label[1])
        x = (num - 1) * 180
        y = {"A": -140, "B": 0, "C": 140}[block]
        positions[label] = (x, y)
        nodes.append({
            "id": label,
            "label": label,
            "group": block,
            "x": x,
            "y": y,
            "fixed": True,
        })

    # Capa combinatoria no dirigida con diagonal: 78 relaciones.
    for i, src in enumerate(labels):
        for dst in labels[i:]:
            if src == dst:
                edges.append({
                    "from": src,
                    "to": dst,
                    "layer": "combinatorial_diagonal",
                    "label": "diag",
                })
            else:
                edges.append({
                    "from": src,
                    "to": dst,
                    "layer": "combinatorial_pair",
                    "label": "comb",
                })

    # Capa simbólica dual: tomamos una mitad canónica de las 144 relaciones dirigidas.
    # Regla: nos quedamos con (i,j) si i<j, más las 12 diagonales. Eso da 66 + 12 = 78.
    # Para llegar a 72 simbólicas, definimos una selección canónica espejo:
    # - las 12 diagonales
    # - las 60 primeras relaciones ordenadas fuera de diagonal en lectura bloqueada
    # Esta capa visual no pretende ser la única posible, sino una representación estable
    # de 72 unidades relacionales simbólicas.
    symbolic_units: List[Tuple[str, str]] = []
    symbolic_units.extend((label, label) for label in labels)  # 12 diagonales simbólicas
    off_diag = [(src, dst) for src in labels for dst in labels if src != dst]
    for pair in off_diag[:60]:
        symbolic_units.append(pair)

    for src, dst in symbolic_units:
        edges.append({
            "from": src,
            "to": dst,
            "layer": "symbolic_dual",
            "label": "sym",
            "arrows": "to",
        })

    return {"nodes": nodes, "edges": edges}


# ============================================================
# 8. HTML interactivo
# ============================================================
# El HTML incluye dos redes y una tabla filtrable de 256 estados coherentes.

def write_html(summary: Dict[str, object], structural_graph: Dict[str, object], relational_graph: Dict[str, object], state_records: List[Dict[str, object]]) -> None:
    summary_json = json.dumps(summary, ensure_ascii=False, indent=2)
    structure_nodes_json = json.dumps(structural_graph["nodes"], ensure_ascii=False)
    structure_edges_json = json.dumps(structural_graph["edges"], ensure_ascii=False)
    relation_nodes_json = json.dumps(relational_graph["nodes"], ensure_ascii=False)
    relation_edges_json = json.dumps(relational_graph["edges"], ensure_ascii=False)
    states_json = json.dumps(state_records, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Tri-hipercubo dual v0.4</title>
  <script src=\"https://unpkg.com/vis-network/standalone/umd/vis-network.min.js\"></script>
  <style>
    :root {{
      --bg: #f5f7fb;
      --card: #ffffff;
      --ink: #111827;
      --muted: #6b7280;
      --blue: #2563eb;
      --red: #dc2626;
      --green: #16a34a;
      --amber: #d97706;
      --shadow: 0 8px 24px rgba(0,0,0,0.08);
      --radius: 16px;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, Arial, sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ padding: 22px 24px; background: #0f172a; color: white; }}
    header h1 {{ margin: 0 0 6px 0; font-size: 28px; }}
    header p {{ margin: 0; color: #cbd5e1; }}
    main {{ padding: 18px; display: grid; gap: 18px; }}
    .grid {{ display: grid; gap: 18px; grid-template-columns: 1.1fr 0.9fr; }}
    .card {{ background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow); padding: 16px; }}
    .metrics {{ display: grid; gap: 12px; grid-template-columns: repeat(5, minmax(120px, 1fr)); }}
    .metric {{ background: #f8fafc; border-radius: 14px; padding: 14px; border: 1px solid #e5e7eb; }}
    .metric .k {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
    .metric .v {{ font-size: 26px; font-weight: 700; margin-top: 6px; }}
    .net {{ height: 420px; border-radius: 14px; background: #fff; border: 1px solid #e5e7eb; }}
    .controls {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; align-items: center; }}
    .controls label {{ font-size: 14px; color: var(--ink); background: #f8fafc; border: 1px solid #e5e7eb; padding: 8px 10px; border-radius: 999px; }}
    .tabs {{ display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }}
    .tabbtn {{ border: 0; background: #e5e7eb; padding: 10px 14px; border-radius: 999px; cursor: pointer; font-weight: 600; }}
    .tabbtn.active {{ background: #111827; color: white; }}
    .tabpane {{ display: none; }}
    .tabpane.active {{ display: block; }}
    .filters {{ display: grid; gap: 10px; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 12px; }}
    .filters input, .filters select {{ width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 10px; background: white; }}
    .table-wrap {{ max-height: 480px; overflow: auto; border: 1px solid #e5e7eb; border-radius: 14px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; text-align: left; white-space: nowrap; }}
    th {{ background: #f8fafc; position: sticky; top: 0; z-index: 1; }}
    .muted {{ color: var(--muted); }}
    pre {{ background: #0b1220; color: #dbeafe; border-radius: 14px; padding: 14px; overflow: auto; font-size: 13px; }}
    .note {{ padding: 12px 14px; border-left: 4px solid var(--amber); background: #fff7ed; border-radius: 10px; color: #7c2d12; }}
    @media (max-width: 1100px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(120px, 1fr)); }}
      .filters {{ grid-template-columns: 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Modelo tri-hipercúbico dual · v0.4</h1>
    <p>Explorador interactivo con red estructural, red relacional y tabla filtrable de los 256 estados coherentes.</p>
  </header>

  <main>
    <section class=\"card\">
      <div class=\"metrics\">
        <div class=\"metric\"><div class=\"k\">Hipercubo elemental</div><div class=\"v\">16</div></div>
        <div class=\"metric\"><div class=\"k\">Espacio bruto</div><div class=\"v\">4096</div></div>
        <div class=\"metric\"><div class=\"k\">Subespacio coherente</div><div class=\"v\">256</div></div>
        <div class=\"metric\"><div class=\"k\">Métrica combinatoria</div><div class=\"v\">78</div></div>
        <div class=\"metric\"><div class=\"k\">Métrica simbólica dual</div><div class=\"v\">72</div></div>
      </div>
    </section>

    <section class=\"grid\">
      <article class=\"card\">
        <h2>Red estructural A / B / C</h2>
        <div class=\"controls\">
          <label><input type=\"checkbox\" id=\"showInterna\" checked> internas</label>
          <label><input type=\"checkbox\" id=\"showHorizontal\" checked> horizontales</label>
          <label><input type=\"checkbox\" id=\"showEmergente\" checked> emergentes</label>
        </div>
        <div id=\"structureNet\" class=\"net\"></div>
      </article>

      <article class=\"card\">
        <h2>Red relacional de las 12 dimensiones</h2>
        <div class=\"controls\">
          <label><input type=\"checkbox\" id=\"showCombPairs\" checked> combinatoria sin diagonal</label>
          <label><input type=\"checkbox\" id=\"showCombDiag\" checked> diagonales</label>
          <label><input type=\"checkbox\" id=\"showSymbolic\" checked> simbólica dual</label>
        </div>
        <div id=\"relationNet\" class=\"net\"></div>
        <p class=\"muted\">La capa simbólica dual se muestra como representación estable de 72 unidades relacionales. No equivale a un conteo clásico de aristas únicas.</p>
      </article>
    </section>

    <section class=\"card\">
      <div class=\"tabs\">
        <button class=\"tabbtn active\" data-tab=\"states\">Estados coherentes</button>
        <button class=\"tabbtn\" data-tab=\"summary\">Resumen JSON</button>
      </div>

      <div id=\"states\" class=\"tabpane active\">
        <h2>Tabla filtrable de los 256 estados coherentes</h2>
        <div class=\"filters\">
          <input id=\"searchInput\" type=\"text\" placeholder=\"Buscar por firma o fragmento…\" />
          <select id=\"filterA\"><option value=\"\">A: cualquiera</option><option value=\"++++\">A = ++++</option><option value=\"----\">A = ----</option></select>
          <select id=\"filterB\"><option value=\"\">B: cualquiera</option><option value=\"++++\">B = ++++</option><option value=\"----\">B = ----</option></select>
          <select id=\"filterPos\"><option value=\"\">Nº positivos: cualquiera</option></select>
        </div>
        <div class=\"table-wrap\">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>A</th>
                <th>B</th>
                <th>C</th>
                <th>Firma</th>
                <th>Positivos</th>
              </tr>
            </thead>
            <tbody id=\"statesBody\"></tbody>
          </table>
        </div>
      </div>

      <div id=\"summary\" class=\"tabpane\">
        <h2>Resumen estructurado</h2>
        <div class=\"note\">78 pertenece a la métrica combinatoria del grafo. 72 pertenece a la métrica simbólica dual del modelo. El residual 6 se deja como hipótesis interpretativa asociada a ±x, ±y, ±z.</div>
        <pre>{summary_json}</pre>
      </div>
    </section>
  </main>

  <script>
    const structuralNodes = new vis.DataSet({structure_nodes_json});
    const structuralEdgesRaw = {structure_edges_json};
    const relationNodes = new vis.DataSet({relation_nodes_json});
    const relationEdgesRaw = {relation_edges_json};
    const stateRecords = {states_json};

    function makeStructureEdges() {{
      const showInterna = document.getElementById('showInterna').checked;
      const showHorizontal = document.getElementById('showHorizontal').checked;
      const showEmergente = document.getElementById('showEmergente').checked;
      return structuralEdgesRaw.filter(e =>
        (e.kind === 'interna' && showInterna) ||
        (e.kind === 'horizontal' && showHorizontal) ||
        (e.kind === 'emergente' && showEmergente)
      ).map(e => {{
        const style = {{ from: e.from, to: e.to, label: e.label, arrows: '' }};
        if (e.kind === 'horizontal') style.dashes = true;
        if (e.kind === 'emergente') style.color = {{ color: '#16a34a' }};
        if (e.kind === 'interna') style.color = {{ color: '#64748b' }};
        return style;
      }});
    }}

    function makeRelationEdges() {{
      const showCombPairs = document.getElementById('showCombPairs').checked;
      const showCombDiag = document.getElementById('showCombDiag').checked;
      const showSymbolic = document.getElementById('showSymbolic').checked;
      return relationEdgesRaw.filter(e =>
        (e.layer === 'combinatorial_pair' && showCombPairs) ||
        (e.layer === 'combinatorial_diagonal' && showCombDiag) ||
        (e.layer === 'symbolic_dual' && showSymbolic)
      ).map(e => {{
        const style = {{ from: e.from, to: e.to, label: '', smooth: false }};
        if (e.layer === 'combinatorial_pair') style.color = {{ color: '#cbd5e1' }};
        if (e.layer === 'combinatorial_diagonal') {{
          style.selfReferenceSize = 18;
          style.color = {{ color: '#f59e0b' }};
        }}
        if (e.layer === 'symbolic_dual') {{
          style.arrows = 'to';
          style.color = {{ color: '#2563eb', opacity: 0.55 }};
          style.width = 1.5;
        }}
        return style;
      }});
    }}

    const structureNet = new vis.Network(
      document.getElementById('structureNet'),
      {{ nodes: structuralNodes, edges: new vis.DataSet(makeStructureEdges()) }},
      {{
        physics: true,
        groups: {{
          A: {{ color: {{ background: '#60a5fa', border: '#2563eb' }} }},
          B: {{ color: {{ background: '#fca5a5', border: '#dc2626' }} }},
          C: {{ color: {{ background: '#86efac', border: '#16a34a' }} }}
        }},
        nodes: {{ shape: 'dot', size: 18, font: {{ size: 18 }} }},
        edges: {{ font: {{ size: 11 }} }}
      }}
    );

    const relationNet = new vis.Network(
      document.getElementById('relationNet'),
      {{ nodes: relationNodes, edges: new vis.DataSet(makeRelationEdges()) }},
      {{
        physics: false,
        groups: {{
          A: {{ color: {{ background: '#60a5fa', border: '#2563eb' }} }},
          B: {{ color: {{ background: '#fca5a5', border: '#dc2626' }} }},
          C: {{ color: {{ background: '#86efac', border: '#16a34a' }} }}
        }},
        nodes: {{ shape: 'dot', size: 16, font: {{ size: 18 }} }},
        edges: {{ smooth: false }}
      }}
    );

    ['showInterna','showHorizontal','showEmergente'].forEach(id => {{
      document.getElementById(id).addEventListener('change', () => {{
        structureNet.setData({{ nodes: structuralNodes, edges: new vis.DataSet(makeStructureEdges()) }});
      }});
    }});

    ['showCombPairs','showCombDiag','showSymbolic'].forEach(id => {{
      document.getElementById(id).addEventListener('change', () => {{
        relationNet.setData({{ nodes: relationNodes, edges: new vis.DataSet(makeRelationEdges()) }});
      }});
    }});

    // Tabs simples.
    document.querySelectorAll('.tabbtn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.tabbtn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tabpane').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
      }});
    }});

    // Tabla de estados.
    const statesBody = document.getElementById('statesBody');
    const filterPos = document.getElementById('filterPos');
    const positiveValues = [...new Set(stateRecords.map(r => r.positive_count))].sort((a,b) => a-b);
    positiveValues.forEach(v => {{
      const opt = document.createElement('option');
      opt.value = String(v);
      opt.textContent = `Nº positivos = ${{v}}`;
      filterPos.appendChild(opt);
    }});

    function renderStates() {{
      const q = document.getElementById('searchInput').value.trim().toLowerCase();
      const fa = document.getElementById('filterA').value;
      const fb = document.getElementById('filterB').value;
      const fp = document.getElementById('filterPos').value;

      const rows = stateRecords.filter(r => {{
        const Aplain = r.signature.split('|')[0];
        const Bplain = r.signature.split('|')[1];
        const hitSearch = !q || r.signature.toLowerCase().includes(q) || String(r.id).includes(q);
        const hitA = !fa || Aplain === fa;
        const hitB = !fb || Bplain === fb;
        const hitP = !fp || String(r.positive_count) === fp;
        return hitSearch && hitA && hitB && hitP;
      }});

      statesBody.innerHTML = rows.map(r => `
        <tr>
          <td>${{r.id}}</td>
          <td>${{r.A_str}}</td>
          <td>${{r.B_str}}</td>
          <td>${{r.C_str}}</td>
          <td>${{r.signature}}</td>
          <td>${{r.positive_count}}</td>
        </tr>
      `).join('');
    }}

    ['searchInput','filterA','filterB','filterPos'].forEach(id => {{
      document.getElementById(id).addEventListener('input', renderStates);
      document.getElementById(id).addEventListener('change', renderStates);
    }});

    renderStates();
  </script>
</body>
</html>
"""

    HTML_OUT.write_text(html, encoding="utf-8")


# ============================================================
# 9. Salida limpia por consola
# ============================================================
# La salida evita repetir el mismo número en distintos planos.

def print_summary(summary: Dict[str, object]) -> None:
    s = summary["system_structure"]
    g = summary["graph_combinatorics"]
    d = summary["symbolic_dual_metric"]
    v = summary["coherence_validation"]

    print("\n" + "=" * 76)
    print("MODELO TRI-HIPERCÚBICO DUAL · VERSIÓN 0.4")
    print("=" * 76)

    print("\n[ESTRUCTURA DEL SISTEMA]")
    print(f"Hipercubo elemental                  : {s['elementary_hypercube_states']}")
    print(f"Dimensiones estructurales            : {s['structural_dimensions']}")
    print(f"Espacio bruto teórico                : {s['raw_theoretical_space']}")
    print(f"Subespacio coherente                 : {s['coherent_subspace']}")
    print(f"Regla de síntesis                    : {s['synthesis_rule']}")

    print("\n[MÉTRICA COMBINATORIA DEL GRAFO]")
    print(f"Relaciones dirigidas                 : {g['directed']}")
    print(f"Relaciones no dirigidas sin diagonal : {g['undirected_no_diagonal']}")
    print(f"Relaciones diagonales                : {g['diagonal']}")
    print(f"Relaciones no dirigidas con diagonal : {g['undirected_with_diagonal']}")

    print("\n[MÉTRICA SIMBÓLICA DUAL]")
    print(f"Relaciones estructurales simbólicas  : {d['symbolic_relations']}")
    print(f"Residual combinatorio-simbólico      : {d['residual_vs_combinatorial_with_diagonal']}")
    print(f"Hipótesis del residual               : {', '.join(d['residual_interpretation']['space3d_dual_axes'])}")

    print("\n[VALIDACIÓN]")
    print(f"Estados coherentes verificados       : {v['validated_states']}")
    print(f"Estado de coherencia                 : {v['status']}")

    print("\n[ARTEFACTOS]")
    print(f"JSON                                 : {JSON_OUT.name}")
    print(f"HTML                                 : {HTML_OUT.name}")
    print("=" * 76)


# ============================================================
# 10. Ejecución principal
# ============================================================

def main() -> None:
    h = hypercube_4d()
    coherent_states = build_coherent_states()
    valid = sum(validate_state(s) for s in coherent_states)
    state_records = [state_to_record(i + 1, s) for i, s in enumerate(coherent_states)]

    combinatorial = build_combinatorial_metrics(DIM_LABELS)
    symbolic = build_symbolic_dual_metrics(combinatorial["counts"])
    structural_graph = build_structural_graph()
    relational_graph = build_relational_network(DIM_LABELS)

    summary = {
        "model": "Modelo tri-hipercúbico dual v0.4",
        "system_structure": {
            "elementary_hypercube_states": len(h),
            "horizontal_hypercubes": 2,
            "emergent_hypercube": 1,
            "structural_dimensions": len(DIM_LABELS),
            "dimension_labels": DIM_LABELS,
            "raw_theoretical_space": len(h) ** 3,
            "coherent_subspace": len(coherent_states),
            "synthesis_rule": "c_i = a_i * b_i",
        },
        "graph_combinatorics": combinatorial["counts"],
        "symbolic_dual_metric": symbolic,
        "coherence_validation": {
            "validated_states": valid,
            "expected_states": len(coherent_states),
            "status": "OK" if valid == len(coherent_states) else "ERROR",
        },
        "interpretation": {
            "4096": "espacio bruto de tres hipercubos 4D",
            "256": "subespacio coherente bajo la ley de síntesis",
            "144": "relaciones dirigidas entre 12 dimensiones",
            "78": "reducción combinatoria con diagonal",
            "72": "reducción simbólica dual del modelo",
            "6": "residual interpretable como ±x, ±y, ±z",
        },
    }

    payload = {
        "summary": summary,
        "states": state_records,
        "structural_graph": structural_graph,
        "relational_graph": relational_graph,
    }

    JSON_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_html(summary, structural_graph, relational_graph, state_records)
    print_summary(summary)


if __name__ == "__main__":
    main()
