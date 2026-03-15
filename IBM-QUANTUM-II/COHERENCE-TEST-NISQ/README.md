
# Structured Coherence Benchmark (SCB) — NISQ Structural Parity Test

Author: Sergi Garcia Mecinas  
Repository: https://github.com/sgarcia87/Q-Reality-12D

---

# Overview

This directory contains a **structural benchmarking tool for NISQ quantum hardware** based on the preservation of **parity‑constrained subspaces**.

The benchmark evaluates how reliably a quantum device preserves a set of **triadic parity relations** of the form:

A_i ⊕ B_i ⊕ C_i = 0

for i = 1..4.

These relations define a **structured subspace of a 12‑qubit system**.  
The benchmark measures how well real hardware preserves these relations when circuits are executed under realistic noise.

Unlike raw fidelity metrics, this benchmark evaluates **structural coherence**, i.e., whether **logical constraints between qubits remain satisfied after circuit execution**.

The tool outputs a **Structured Coherence Benchmark (SCB)** report containing several metrics and an aggregated score.

---

# Conceptual Basis

## Parity‑Constrained Subspace

The benchmark operates on a 12‑qubit system organized into three registers:

A = (A₁,A₂,A₃,A₄)  
B = (B₁,B₂,B₃,B₄)  
C = (C₁,C₂,C₃,C₄)

with the structural constraint

Cᵢ = Aᵢ ⊕ Bᵢ

equivalently

Aᵢ ⊕ Bᵢ ⊕ Cᵢ = 0

These relations define a **parity‑constrained subspace**

S = { (A,B,C) ∈ {0,1}¹² | C = A ⊕ B }

Dimension of the state space:

Full space:

2¹² = 4096 states

Constrained subspace:

2^(12 − 4) = 256 states

Therefore the system forms an **8‑dimensional binary subspace embedded in a 12‑qubit system**.

---

# Why Structural Metrics Matter

Typical NISQ benchmarks measure:

• circuit fidelity  
• error rates  
• quantum volume  
• random circuit sampling  

These metrics evaluate **generic circuit performance**, but they do not test whether **logical relations between qubits survive hardware noise**.

The SCB benchmark instead measures:

• preservation of parity relations  
• propagation of structural dependencies  
• interaction between algorithmic amplification and structural constraints

This approach is similar in spirit to tests used in:

• stabilizer verification  
• parity checks in quantum error correction  
• constraint‑based quantum circuits

The advantage is that **logical structure can be preserved even when individual qubits experience errors**, making these metrics informative about correlated noise behavior.

---

# Benchmark Pipeline

The benchmark executes several circuit families derived from the experiments in the repository.

Each circuit follows the same high‑level pipeline.

1. State preparation
2. Structural constraint construction
3. Optional Grover amplification
4. Measurement
5. Structural validation

---

# Circuit Preparation

Registers A and B are placed in uniform superposition:

qc.h(A)  
qc.h(B)

Register C is computed via XOR relations using CNOT gates:

qc.cx(A[i], C[i])  
qc.cx(B[i], C[i])

The resulting quantum state is

|A, B, A⊕B⟩

which lies in the parity‑constrained subspace.

---

# Circuit Families Tested

The benchmark evaluates multiple circuit variants.

## Baseline Uniform

Uniform sampling of the parity‑constrained subspace.

No Grover amplification applied.

Purpose:

Measure baseline structural coherence.

---

## Grover One‑Hot Selection

A Grover oracle selects the one‑hot states of register A:

0001  
0010  
0100  
1000

These correspond to **axis directions in the 4‑dimensional hypercube of A**.

Purpose:

Test whether amplitude amplification operates correctly within the constrained subspace.

---

## Grover Two‑Hot Selection

The oracle selects states where exactly two bits of A are active:

1100  
1010  
1001  
0110  
0101  
0011

These correspond to **diagonal directions in the hypercube**.

Purpose:

Evaluate how subset geometry interacts with structural stability.

---

# Structural Metrics

Several metrics are extracted from measurement results.

---

## coherent_rate

Fraction of shots satisfying all parity relations simultaneously.

coherent_rate =
valid shots
----------------
total shots

This measures whether the measured state lies inside the structural subspace.

---

## axis_consistency

Average fraction of axes where the relation

A_i ⊕ B_i ⊕ C_i = 0

is satisfied.

axis_consistency =
correct axes
----------------------------
4 × total shots

This metric captures **local structural preservation**.

Noise typically breaks individual axes rather than the full constraint set.

---

## A_good_rate

Probability that register A belongs to the selected subset.

Example:

one‑hot subset size = 4

baseline probability =

4 / 16 = 0.25

Deviation from baseline indicates successful amplification.

---

## joint_rate

Fraction of shots satisfying:

A ∈ selected subset
AND
structural constraint holds

joint_rate =
valid selected shots
------------------------
total shots

This measures **successful structural amplification**.

---

## gain_A

Amplification factor of the selected subset.

gain_A =
observed A_good_rate
------------------------
baseline probability

Example:

baseline ≈ 0.25  
observed ≈ 0.69

gain ≈ 2.76

---

# Conditional Metrics

Two conditional probabilities provide deeper insight.

## P(coherent | A_good)

Probability that the structural constraint holds given successful selection.

P(coherent | A_good) =
joint_rate / A_good_rate

This evaluates whether **Grover amplification disrupts structural coherence**.

---

## P(A_good | coherent)

Probability that a coherent state belongs to the selected subset.

P(A_good | coherent) =
joint_rate / coherent_rate

This measures **how strongly the coherent subspace aligns with the selected geometry**.

---

# Coherence Score

All metrics are aggregated into a single **Structured Coherence Score (0–100)**.

The score combines:

• coherent_rate  
• axis_consistency  
• amplification gain  
• conditional coherence metrics

The purpose of the score is **not to replace raw metrics**, but to provide a quick summary of device performance under structural constraints.

Example results on IBM Marrakesh:

baseline_uniform ≈ 79  
grover_one_hot ≈ 87  
grover_two_hot ≈ 83

Higher scores indicate stronger preservation of structural parity relations.

---

# Structured Coherence Score Definition
The SCB score aggregates the structural metrics into a single normalized indicator in the range [0,100].
The score is computed as a weighted combination of the measured metrics:

SCB =
100 × (
  w1 · coherent_rate
+ w2 · axis_consistency
+ w3 · normalized_gain_A
+ w4 · P(coherent | A_good)

)
with weights:

w1 = 0.35
w2 = 0.25
w3 = 0.20
w4 = 0.20
subject to

w1 + w2 + w3 + w4 = 1
where

normalized_gain_A = min(gain_A / G_max, 1)
and
G_max = theoretical Grover amplification bound
This formulation ensures:
• structural preservation dominates the score
• amplification contributes but does not dominate
• conditional coherence validates compatibility between amplification and structure
The score is therefore not arbitrary, but derived from observable structural properties of the circuit execution.

---

# Simulator vs Hardware Validation
To distinguish hardware noise from structural effects, the benchmark can be executed in three environments:

Aer ideal simulator
Aer noisy simulator (backend noise model)
IBM Quantum hardware

Typical behavior:
Backend.    coherent_rate.    axis_consistency
Aer ideal.   ~1.00.            ~1.00
Aer noisy.   ~0.90–0.95.       ~0.97
Hardware.    ~0.82–0.90.       ~0.95–0.97

This confirms that deviations from ideal coherence are consistent with expected NISQ noise sources:
• gate errors
• decoherence
• readout errors
rather than artifacts of the structural model.

---

# Circuit Complexity
Typical circuit characteristics for the benchmark:

qubits: 12
parity constraints: 4
CNOT gates: ≈ 8–16
single-qubit gates: ≈ 8–12
depth: ≈ 30–80 (after transpilation)
The circuits are intentionally shallow to ensure that structural degradation reflects hardware noise rather than excessive circuit depth.

---

# Why These Metrics Are Valid
The metrics used in SCB are derived from the logical structure of the circuit.
They correspond to parity invariants that must hold for states inside the constrained subspace.
Such invariants are commonly used in:
• stabilizer verification
• parity checks in quantum error correction
• constraint-based quantum circuits

Because the parity relations are deterministic properties of the target state space, measuring their preservation provides a direct test of whether the hardware maintains the logical structure of the circuit.
This makes the benchmark particularly sensitive to:
• correlated errors
• propagation of noise through CNOT networks
• stability of constraint-based quantum circuits

---

# Reproducibility
All experiments produce structured JSON outputs containing:

counts
coherent_rate
axis_consistency
A_good_rate
joint_rate
conditional metrics
SCB score
Example output file:

structured_coherence_certificate_20260315_003254.json
These files allow full reproducibility and cross-backend comparison.

---

# Running the Benchmark

Install dependencies:

pip install qiskit qiskit-ibm-runtime

Run the benchmark:

python structured_coherence_certificate_v0_1.py --backend ibm_marrakesh

Optional:

--cases v1,onehot,twohot

Example:

python structured_coherence_certificate_v0_1.py \
--backend ibm_marrakesh \
--cases v1,onehot,twohot

---

# Output

The benchmark produces a JSON report:

structured_coherence_certificate_TIMESTAMP.json

The report includes:

• raw measurement counts  
• structural metrics  
• conditional probabilities  
• coherence score  

This allows full reproducibility and cross‑backend comparison.

---

# Relation to Existing Benchmarks

The SCB benchmark complements existing NISQ metrics such as:

• Quantum Volume  
• Random Circuit Sampling  
• Mirror Circuit Benchmarks  

Those tests evaluate **generic circuit complexity**, while SCB evaluates **preservation of logical structure**.

---

# Scope and Limitations

The benchmark:

• operates within NISQ noise regimes  
• uses shallow circuits  
• evaluates parity‑constrained subspaces

It does **not claim**:

• quantum advantage  
• fault tolerance  
• universal device characterization

The goal is simply to provide **a reproducible structural benchmark for parity‑based quantum circuits**.

---

# Related Concepts
The SCB benchmark is conceptually related to several areas in quantum information:
• stabilizer formalism (Gottesman)
• parity checks in quantum error detection codes
• constraint-based quantum circuits
• Grover amplitude amplification

The benchmark can therefore be interpreted as a lightweight diagnostic test for parity-constrained quantum subspaces in NISQ hardware.

---

# Conclusion

The Structured Coherence Benchmark evaluates how well a quantum device preserves **triadic parity constraints** under realistic hardware noise.

The benchmark demonstrates that:

• parity‑constrained subspaces can be prepared in NISQ hardware  
• Grover amplification can operate within these subspaces  
• structural relations may survive noise more robustly than raw state fidelity

This makes SCB a useful experimental tool for studying **structured quantum state spaces on present‑day quantum processors**.
