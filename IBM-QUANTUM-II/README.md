
# IBM-QUANTUM-II · Q‑Reality‑12D
## Tri‑Hypercube Structural Model and Quantum Experiments

Author: Sergi Garcia Mecinas  
Repository: https://github.com/sgarcia87/Q-Reality-12D

---

# Overview

This folder contains the **quantum implementation and experimental validation** of the **Tri‑Hypercube structural model** introduced in the Q‑Reality‑12D project.

The goal of the work is to explore how a **triadic structural constraint** behaves:

• mathematically  
• combinatorially  
• and on **real quantum hardware (NISQ devices)**

The project evolved through three stages:

1. **Classical model exploration**
2. **Quantum circuit implementation**
3. **Structural coherence benchmarking**

---

# Core Idea

The model uses three blocks of binary variables:

A = (A1, A2, A3, A4)  
B = (B1, B2, B3, B4)  
C = (C1, C2, C3, C4)

with the structural constraint:

C_i = A_i XOR B_i

This implies the parity relation:

A_i XOR B_i XOR C_i = 0

Each axis forms a **triadic relation**.

---

# Dimensional Reduction

Without constraints:

2^12 = 4096 states

With the four parity relations:

2^(12 − 4) = 256 coherent states

Therefore the system defines a **coherent subspace of dimension 8** embedded in a 12‑bit space.

This subspace is the object studied in both the classical and quantum experiments.

---

# Classical Model Exploration

The classical scripts study the combinatorial and information structure of the tri‑hypercube.

Main files:

```
tri_hipercubo_modelo_v0_4_explorador.html
tri_hipercubo_modelo_v0_4_resultado.json

tri_hipercubo_modelo_v0_5.py
tri_hipercubo_modelo_v0_5_explorador.html
tri_hipercubo_modelo_v0_5_resultado.json

tri_hipercubo_modelo_v0_6.py
tri_hipercubo_modelo_v0_6_explorador.html
tri_hipercubo_modelo_v0_6_resultado.json

tri_hipercubo_modelo_v0_7.py
tri_hipercubo_modelo_v0_7_explorador.html
tri_hipercubo_modelo_v0_7_resultado.json

modelo-12D.py
```

Key observations:

• Binary dimension: 12  
• Structural constraints: 4  
• Effective dimension: 8  
• Coherent states: 256  

Information analysis shows that the relations are **triadic rather than pairwise**.

Pairwise mutual information:

I(A;B) = 0  
I(A;C) = 0  
I(B;C) = 0  

but

I(A;B | C) = 1

---

# Quantum Experiments

The classical structure was implemented as quantum circuits on IBM Quantum hardware.

Constraint encoded as:

C_i = A_i XOR B_i

which prepares states of the form:

|A, B, A⊕B>

---

# Experiment v1 · Structural Coherence

File:

```
tri_hipercubo_quantum_v1.py
```

Objective:

Verify that the structural constraint survives hardware noise.

Typical result (IBM Marrakesh):

coherent_rate ≈ 0.87  
axis_consistency ≈ 0.96

Result file:

```
tri_hypercube_quantum_*.json
```

---

# Experiment v2 · Structural Amplification

File:

```
tri_hipercubo_quantum_v2.py
```

Adds a Grover step selecting **one‑hot states of A**.

Example results:

A_good_rate ≈ 0.49  
joint_rate ≈ 0.41

Meaning that a structural subset of states can be amplified without destroying coherence.

---

# Experiment v3 · Statistical Benchmark

File:

```
tri_hipercubo_quantum_v3.py
```

Compares baseline vs Grover selection.

Derived metrics include:

P(coherent | A_good)  
P(A_good | coherent)

Result file:

```
tri_hypercube_v1_v2_benchmark_*.json
```

---

# Experiment v4 · Grover Dynamics

File:

```
tri_hipercubo_quantum_v4.py
```

Performs a Grover sweep:

| k | A_good_rate |
|---|-------------|
| 0 | ~0.25 |
| 1 | ~0.62 |
| 2 | ~0.37 |

This matches the expected Grover amplification curve.

Result file:

```
tri_hypercube_k_sweep_*.json
```

---

# Experiment v5 · Geometric Selection

File:

```
tri_hipercubo_quantum_v5.py
```

Compares two types of structural subsets:

• one‑hot states → axes of the hypercube  
• two‑hot states → diagonals

Observation:

One‑hot structures preserve coherence slightly better.

---

# Structured Coherence Certificate

Inside the folder:

```
COHERENCE-TEST-NISQ/
```

You will find the **Structured Coherence Certificate** tool.

Main file:

```
structured_coherence_certificate_v0_1.py
```

This benchmark evaluates:

• coherent_rate  
• axis_consistency  
• A_good_rate  
• joint_rate  
• gain_A  
• P(coherent | A_good)  
• P(A_good | coherent)

Example result:

baseline_uniform score ≈ 79  
grover_one_hot score ≈ 87

This provides a lightweight **NISQ structural benchmark**.

---

# Repository Structure

```
IBM-QUANTUM-II

classical-model/
tri_hipercubo_modelo_v0_4 → v0_7

quantum-experiments/
tri_hipercubo_quantum_v1 → v5

COHERENCE-TEST-NISQ/
structured_coherence_certificate_v0_1.py

results/
*.json
```

---

# Interpretation

The experiments show that:

• The tri‑hypercube constraint defines a coherent subspace.  
• This structure survives realistic quantum hardware noise.  
• Grover amplification can bias the system toward structural subsets.  
• The geometry of the selected subset affects stability.

The model can be interpreted both as:

Geometric structure  
(three coupled 4‑dimensional hypercubes)

or as a parity‑based quantum subspace defined by

A_i XOR B_i XOR C_i = 0

---

# Status

This repository documents an **experimental exploration of structural coherence in NISQ quantum hardware**.

The focus is reproducibility and experimentation rather than proposing a finalized physical theory.
