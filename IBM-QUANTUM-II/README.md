
# IBM-QUANTUM-II — Parity‑Constrained Triadic Subspace Experiments

Author: Sergi Garcia Mecinas  
Repository: https://github.com/sgarcia87/Q-Reality-12D

---

# Overview

This directory contains the **quantum implementation and experimental evaluation of a parity‑constrained triadic subspace** defined over 12 binary variables and implemented as quantum circuits on **IBM Quantum NISQ hardware**.

The project investigates how a **structured subspace defined by XOR parity constraints** behaves:

- mathematically
- combinatorially
- and under **real hardware noise** in superconducting quantum processors.

The work progresses through three stages:

1. **Classical model exploration**
2. **Quantum circuit implementation**
3. **Hardware‑level structural benchmarking**

The goal is **not to propose a physical theory**, but to experimentally evaluate how **parity‑constrained state spaces behave under quantum circuit execution and noise**.

---

# Core Mathematical Model

The model is defined on **12 binary variables** grouped into three registers:

A = (A₁, A₂, A₃, A₄)  
B = (B₁, B₂, B₃, B₄)  
C = (C₁, C₂, C₃, C₄)

Each axis satisfies the triadic parity relation

Cᵢ = Aᵢ ⊕ Bᵢ

which is equivalent to the constraint

Aᵢ ⊕ Bᵢ ⊕ Cᵢ = 0

for i = 1..4.

This relation defines a **parity‑constrained subspace** inside the 12‑bit state space.

---

# Dimensional Structure

Without constraints the system contains

2¹² = 4096 states

The four parity relations reduce the space to

2^(12 − 4) = 256 states

Thus the system defines a subspace

S = { (A,B,C) ∈ {0,1}¹² | C = A ⊕ B }

with effective binary dimension:

dim(S) = 8

embedded in a 12‑bit state space.

---

# Information Structure

Each axis forms a **triadic dependency** among three variables.

The information relationships satisfy

I(A;B) = 0  
I(A;C) = 0  
I(B;C) = 0  

but

I(A;B | C) = 1

This means the dependency is **not pairwise but conditional**, a property characteristic of XOR relations.

---

# Quantum Circuit Implementation

The constraint

Cᵢ = Aᵢ ⊕ Bᵢ

is implemented using two CNOT gates:

qc.cx(A[i], C[i])  
qc.cx(B[i], C[i])

This prepares quantum states of the form

|A, B, A⊕B⟩

which lie entirely within the parity‑constrained subspace.

---

# Stabilizer Interpretation

The parity relations correspond to stabilizer operators

Z_Aᵢ Z_Bᵢ Z_Cᵢ

for each axis i.

These stabilizers define a **structured stabilizer subspace** of the Hilbert space.

Coherence in this model corresponds to the preservation of these stabilizer constraints.

---

# Geometric Interpretation

Each register (A,B,C) corresponds to the vertices of a **4‑dimensional hypercube**.

The constraint

C = A ⊕ B

couples the three hypercubes axis‑by‑axis.

The resulting structure can therefore be interpreted as **three coupled 4‑dimensional hypercubes embedded in a constrained 12‑bit space**.

---

# Experimental Methodology

All experiments follow the same pipeline:

1. **State preparation**
   - Uniform superposition over registers A and B

2. **Constraint construction**
   - Register C computed using XOR relations

3. **Optional algorithmic stage**
   - Grover amplification applied to register A

4. **Measurement**
   - Full measurement of the 12‑qubit system

5. **Post‑processing**
   - Verification of parity constraints
   - Statistical evaluation of structural metrics

---

# Structural Metrics

Several metrics are used to quantify behavior.

### coherent_rate

Fraction of shots where all four parity relations hold simultaneously.

coherent_rate =
(valid shots)
----------------
(total shots)

### axis_consistency

Average fraction of axes satisfying the relation.

axis_consistency =
(correct axes)
-------------------------
(4 × total shots)

### A_good_rate

Probability that register A belongs to a selected subset.

### joint_rate

Probability that both conditions hold simultaneously:

(A ∈ selected subset) AND (parity constraints satisfied)

---

# Experiment v1 — Structural Coherence

File:

tri_hipercubo_quantum_v1.py

### Objective

Test whether the parity‑constrained subspace survives realistic hardware noise.

### Circuit

1. Superposition on A and B

qc.h(A)  
qc.h(B)

2. Compute C from XOR relations

qc.cx(A[i],C[i])  
qc.cx(B[i],C[i])

3. Measurement

### Typical Hardware Result

coherent_rate ≈ 0.87  
axis_consistency ≈ 0.96

This indicates that most axes preserve the structural relation even under noise.

---

# Experiment v2 — Structural Amplification

File:

tri_hipercubo_quantum_v2.py

### Objective

Evaluate whether **Grover amplification can operate within the constrained subspace**.

The oracle selects **one‑hot states of A**

0001  
0010  
0100  
1000

Baseline probability:

4 / 16 = 0.25

Observed after Grover:

A_good_rate ≈ 0.49

Structural coherence remains high, indicating compatibility between amplification and the parity subspace.

---

# Experiment v3 — Statistical Benchmark

File:

tri_hipercubo_quantum_v3.py

Introduces conditional metrics:

P(coherent | A_good)  
P(A_good | coherent)

Example hardware results:

Baseline:

coherent_rate ≈ 0.885  
A_good_rate ≈ 0.255

With Grover:

coherent_rate ≈ 0.824  
A_good_rate ≈ 0.416

Derived:

P(coherent | A_good) ≈ 0.83  
P(A_good | coherent) ≈ 0.42

These values indicate that amplification and structural coherence remain statistically compatible.

---

# Experiment v4 — Grover Dynamics

File:

tri_hipercubo_quantum_v4.py

Grover iterations sweep:

k | A_good_rate  
0 | ~0.25  
1 | ~0.62  
2 | ~0.37  

The observed curve matches theoretical Grover oscillation behavior.

---

# Experiment v5 — Geometric Subset Comparison

File:

tri_hipercubo_quantum_v5.py

Two structural subsets are compared:

one‑hot states  
two‑hot states

Typical results:

one‑hot coherence ≈ 0.86  
two‑hot coherence ≈ 0.84

Axis‑aligned structures appear slightly more robust under noise.

---

# Structured Coherence Certificate

Located in:

COHERENCE-TEST-NISQ/

Main file:

structured_coherence_certificate_v0_1.py

The benchmark evaluates:

- coherent_rate
- axis_consistency
- A_good_rate
- joint_rate
- conditional probabilities

Example score:

baseline_uniform ≈ 79  
grover_one_hot ≈ 87

This provides a lightweight **structural benchmark for NISQ hardware**.

---

# Repository Structure

IBM-QUANTUM-II

classical-model/  
tri_hipercubo_modelo_v0_4 → v0_7

quantum-experiments/  
tri_hipercubo_quantum_v1 → v5

COHERENCE-TEST-NISQ/

results/

---

# Experimental Scope

These experiments:

• evaluate parity‑constrained subspaces  
• analyze Grover amplification in structured spaces  
• measure robustness under real NISQ noise

They do **not claim**:

• quantum advantage  
• fault‑tolerant computation  
• new physical laws.

---

# Conclusion

The experiments demonstrate that:

• XOR parity constraints define a stable subspace  
• this subspace survives realistic hardware noise  
• Grover amplification can bias subsets within the subspace  
• geometric structure influences noise robustness

The project therefore serves as an **experimental investigation of structured quantum state spaces on current NISQ hardware**.
