# tubalcain-API

**Tubalcain — Structural Coherence Auditor API**

Tubalcain is an **API-first system** that audits the *structural coherence* of knowledge and reasoning systems.

It does **not** evaluate textual correctness, style, or factual truth.
It evaluates whether the **structure that sustains reasoning becomes fragile** under changes of perspective.

---

## What Tubalcain Does

Tubalcain detects **early structural failure signals** in systems such as:

- Retrieval-Augmented Generation (RAG)
- Knowledge graphs
- Agent systems with memory
- Hybrid architectures (LLM + tools + rules)

It answers one focused question:

> **Does this system remain coherent when the point of observation changes?**

---

## What Tubalcain Does NOT Do

Tubalcain does **not**:

- detect textual hallucinations
- verify factual truth
- certify legal compliance
- judge linguistic quality

Tubalcain is a **structural auditor**, not a semantic judge.

---

## Graph JSON Format (node-link)

Tubalcain accepts a **directed graph** in node-link format.
It supports both `links` and `edges`.

Minimal example:

```json
{
  "directed": true,
  "nodes": [{"id":"tiempo"}, {"id":"posición"}],
  "links": [{"source":"tiempo","target":"posición","tipo":"estructura","weight":1.0}]
}
```

### Required fields

- `nodes[].id` (string)
- `links[].source` (node id)
- `links[].target` (node id)

### Optional fields

- `links[].weight` (number, default 1.0)
- `links[].tipo` (string)
- `links[].axis` (string)
- `nodes[].tipo`, `nodes[].roles` (object)

---

## Limits (recommended defaults)

These defaults keep the API stable:

- **Request size** (`graph_json`): up to **5 MB**
- **Nodes**: up to **50,000**
- **Edges**: up to **300,000**
- **Global audit**: `auto_perspectives` defaults to **10–20**

For truly large graphs, prefer sending a `graph_id` (upload once, audit by id).

---

## API Overview

Main endpoints:

- `POST /v1/perspective/health`
- `POST /v1/perspective/equilibrium`
- `POST /v1/report`

The official contract is in **openapi.yaml**.

---

## Examples

See `examples/curl.md`.

---

## Contact

📩 contact@tubalcain.ai
