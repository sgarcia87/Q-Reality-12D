
# Q-Reality-12D
## Structured Parity Subspace Experiments on NISQ Quantum Hardware

Author: Sergi Garcia Mecinas  
Repository: https://github.com/sgarcia87/Q-Reality-12D

---

# Abstract

This repository investigates a **structured parity‑constrained subspace of 12 qubits** and studies how well this structure is preserved on **real NISQ quantum hardware** (IBM Quantum).

The project explores three main aspects:

1. Definition of a **structured binary subspace** based on triadic XOR constraints
2. Implementation of this structure as **quantum circuits**
3. Measurement of **structural coherence metrics** under realistic noise conditions

The goal is **not to propose a cosmological model**, but to study how **structured subspaces behave under noise in near‑term quantum devices**.

The experiments demonstrate that parity‑constrained subspaces can be prepared and manipulated while preserving structural relations with relatively high stability.

---

# Core Mathematical Model

The system is defined on **12 binary variables** grouped into three blocks:

A = (A₁, A₂, A₃, A₄)  
B = (B₁, B₂, B₃, B₄)  
C = (C₁, C₂, C₃, C₄)

The defining constraint is:

Cᵢ = Aᵢ ⊕ Bᵢ

Equivalent parity relation:

Aᵢ ⊕ Bᵢ ⊕ Cᵢ = 0

for each axis i = 1..4.

---

# Dimensional Reduction

Without constraints:

2¹² = 4096 states

With the four parity constraints:

2^(12 − 4) = 256 coherent states

Formally:

S = { (A,B,C) ∈ {0,1}¹² | C = A ⊕ B }

dim(S) = 8

This subspace is the object studied throughout the repository.

---

# Relation to Quantum Information Theory

The parity relations correspond to stabilizer‑like operators:

Z_Aᵢ Z_Bᵢ Z_Cᵢ

Thus the model can be interpreted as a **simple parity‑constrained stabilizer subspace** embedded in a 12‑qubit Hilbert space.

The experiments test how well real hardware preserves this structure.

---

# Classical Model Exploration

The first stage analyzes the combinatorial and informational structure of the model.

Key scripts:

tri_hipercubo_modelo_v0_4_explorador.html  
tri_hipercubo_modelo_v0_5.py  
tri_hipercubo_modelo_v0_6.py  
tri_hipercubo_modelo_v0_7.py  
modelo-12D.py

Findings:

Binary dimension: 12  
Parity constraints: 4  
Effective dimension: 8  
Coherent states: 256  

Information analysis shows that the relations are **triadic rather than pairwise**.

Pairwise mutual information:

I(A;B) = 0  
I(A;C) = 0  
I(B;C) = 0  

but

I(A;B | C) = 1

---

# Quantum Experiments

The structural constraint is implemented in quantum circuits as:

Cᵢ = Aᵢ XOR Bᵢ

using CNOT gates.

This prepares states of the form:

|A, B, A⊕B⟩

which belong to the coherent subspace S.

---

# Experiment v1 — Structural Coherence

File:

tri_hipercubo_quantum_v1.py

Purpose:

Verify whether the structural parity relations survive realistic quantum hardware noise.

Typical results (IBM Marrakesh):

coherent_rate ≈ 0.87  
axis_consistency ≈ 0.96

Interpretation:

Most measurement outcomes remain inside the parity‑constrained subspace despite hardware noise.

---

# Experiment v2 — Structural Amplification

File:

tri_hipercubo_quantum_v2.py

A Grover step is applied to amplify **one‑hot states of register A**:

0001  
0010  
0100  
1000

Baseline probability:

4 / 16 = 0.25

Observed amplification:

A_good_rate ≈ 0.49

This demonstrates that amplitude amplification can bias the system toward structured subsets while maintaining parity relations.

---

# Experiment v3 — Statistical Benchmark

File:

tri_hipercubo_quantum_v3.py

This experiment compares baseline and amplified circuits and introduces conditional metrics:

P(coherent | A_good)  
P(A_good | coherent)

These quantify the interaction between structural coherence and subset amplification.

---

# Experiment v4 — Grover Dynamics

File:

tri_hipercubo_quantum_v4.py

Grover iteration sweep results:

k = 0 → A_good_rate ≈ 0.25  
k = 1 → A_good_rate ≈ 0.62  
k = 2 → A_good_rate ≈ 0.37

This matches the expected oscillatory behavior of Grover amplitude amplification.

---

# Experiment v5 — Geometric Subset Selection

File:

tri_hipercubo_quantum_v5.py

Two geometric subsets are compared:

• one‑hot states (axes of the 4D hypercube)  
• two‑hot states (face diagonals)

Results indicate that axis‑aligned subsets maintain slightly higher structural coherence under noise.

---

# Structured Coherence Certificate

Folder:

COHERENCE-TEST-NISQ/

The repository includes a prototype benchmark called the **Structured Coherence Certificate**.

Metrics evaluated:

coherent_rate  
axis_consistency  
A_good_rate  
joint_rate  
gain_A  
P(coherent | A_good)  
P(A_good | coherent)

Example score:

baseline_uniform ≈ 79  
grover_one_hot ≈ 87

---

# Interpretation

The experiments suggest that:

• parity‑constrained subspaces can be prepared reliably on NISQ hardware  
• amplitude amplification can operate inside structured subspaces  
• geometric properties of selected subsets affect robustness under noise

The repository therefore proposes a **structured parity subspace benchmark** complementary to existing NISQ diagnostics.

---

# Limitations

The current experiments measure **parity preservation after measurement** and do not yet certify full quantum coherence in terms of:

• state tomography  
• entanglement witnesses  
• fidelity estimation

Future work may incorporate these analyses.

---

# Status

This repository documents an **experimental exploration of structured subspaces in NISQ devices**.

The work should be interpreted as:

• a reproducible experimental framework  
• a prototype structural benchmark

rather than a finalized theoretical model.
