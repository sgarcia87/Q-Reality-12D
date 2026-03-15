
# Q‑Reality‑12D
## Tri‑Hypercube Structural Model and Quantum Experiments

Author: Sergi Garcia Mecinas

This repository documents the development of a structural model based on three interconnected 4‑dimensional hypercubes and its implementation on real quantum hardware.

The project evolved in three stages:

1. Classical structural model
2. Quantum implementation experiments
3. Structural coherence certification

The goal is not to claim a new physical theory, but to explore how a triadic structural constraint behaves mathematically and experimentally in NISQ quantum computers.

---------------------------------------------------------------------
1. CORE IDEA
---------------------------------------------------------------------

The system consists of three blocks of binary variables:

A = (A1, A2, A3, A4)  
B = (B1, B2, B3, B4)  
C = (C1, C2, C3, C4)

with the structural constraint:

C_i = A_i XOR B_i

Each axis therefore satisfies the relation:

A_i XOR B_i XOR C_i = 0

This constraint reduces the state space.

Total binary space:

2^12 = 4096 states

Structural constraints:

4 independent relations

Effective coherent subspace:

2^8 = 256 states

---------------------------------------------------------------------
2. CLASSICAL STRUCTURAL MODEL
---------------------------------------------------------------------

Initial exploration of the constrained system was performed classically.

Main files:

tri_hipercubo_modelo_v0_4_explorador.html  
tri_hipercubo_modelo_v0_4_resultado.json

Observation:

The constraint generates exactly 256 coherent states.

---------------------------------------------------------------------
STRUCTURAL GRAPH ANALYSIS
---------------------------------------------------------------------

Files:

tri_hipercubo_modelo_v0_5.py  
tri_hipercubo_modelo_v0_5_explorador.html  
tri_hipercubo_modelo_v0_5_resultado.json

Graph metrics of the system:

Directed relations: 144  
Undirected relations: 66  
Diagonal relations: 12  
Undirected with diagonal: 78  
Symbolic structural relations: 72

Residual:

78 − 72 = 6

---------------------------------------------------------------------
INFORMATION STRUCTURE
---------------------------------------------------------------------

Files:

tri_hipercubo_modelo_v0_6.py  
tri_hipercubo_modelo_v0_6_explorador.html  
tri_hipercubo_modelo_v0_6_resultado.json

Information analysis shows:

I(A;B) = 0  
I(A;C) = 0  
I(B;C) = 0  

but

I(A;B | C) = 1

Meaning that dependency is triadic rather than pairwise.

---------------------------------------------------------------------
FINAL CLASSICAL MODEL
---------------------------------------------------------------------

Files:

tri_hipercubo_modelo_v0_7.py  
tri_hipercubo_modelo_v0_7_explorador.html  
tri_hipercubo_modelo_v0_7_resultado.json  
modelo-12D.py

Final model parameters:

Binary dimension: 12  
Constraints: 4  
Effective dimension: 8  
Coherent states: 256

Each triad forms a tetrahedral structure.

States per triad: 4  
Total structure: (tetrahedron)^4

Symmetry group:

S4 × S3

---------------------------------------------------------------------
3. QUANTUM EXPERIMENTS
---------------------------------------------------------------------

The constraint was implemented on quantum hardware using:

C_i = A_i XOR B_i

This prepares states of the form:

|A, B, A⊕B>

---------------------------------------------------------------------
v1 — STRUCTURAL COHERENCE TEST
---------------------------------------------------------------------

File:

tri_hipercubo_quantum_v1.py

Measured on IBM Marrakesh.

Results:

coherent_rate ≈ 0.87  
axis_consistency ≈ 0.96

Result file:

tri_hypercube_quantum_20260314_202450.json

---------------------------------------------------------------------
v2 — STRUCTURAL AMPLIFICATION
---------------------------------------------------------------------

File:

tri_hipercubo_quantum_v2.py

Adds a Grover step selecting one‑hot states of A.

Results:

A_good_rate ≈ 0.49  
joint_rate ≈ 0.41

Result file:

tri_hypercube_quantum_v2_20260314_203047.json

---------------------------------------------------------------------
v3 — BENCHMARK v1 vs v2
---------------------------------------------------------------------

File:

tri_hipercubo_quantum_v3.py

Comparison metrics:

P(coherent | A_good)  
P(A_good | coherent)

Result file:

tri_hypercube_v1_v2_benchmark_20260314_205037.json

---------------------------------------------------------------------
v4 — GROVER DYNAMICS
---------------------------------------------------------------------

File:

tri_hipercubo_quantum_v4.py

Grover sweep results:

k = 0 → A_good_rate ≈ 0.25  
k = 1 → A_good_rate ≈ 0.62  
k = 2 → A_good_rate ≈ 0.37

Result file:

tri_hypercube_k_sweep_20260314_205923.json

---------------------------------------------------------------------
v5 — GEOMETRIC COMPARISON
---------------------------------------------------------------------

File:

tri_hipercubo_quantum_v5.py

Comparison of two structures:

one‑hot states (axes of hypercube)  
two‑hot states (diagonals)

Result file:

tri_hypercube_onehot_vs_twohot_20260314_211217.json

Observation:

One‑hot selections maintain slightly higher coherence.

---------------------------------------------------------------------
4. STRUCTURAL COHERENCE CERTIFICATE
---------------------------------------------------------------------

Files:

structured_coherence_certificate_v0_1.py  
STRUCTURED_COHERENCE_CERTIFICATE_README.md  
structured_coherence_certificate_*.json

Metrics:

coherent_rate  
axis_consistency  
A_good_rate  
joint_rate  
gain_A  
P(coherent | A_good)  
P(A_good | coherent)

Example result:

baseline_uniform score ≈ 79.7  
grover_one_hot score ≈ 87.6

---------------------------------------------------------------------
5. INTERPRETATION
---------------------------------------------------------------------

These experiments show that:

• The tri‑hypercube constraint defines a coherent subspace  
• The subspace survives realistic quantum hardware noise  
• Grover amplification can bias the space toward structured subsets  
• The geometry of the subset affects stability

---------------------------------------------------------------------
6. CONCEPTUAL INTERPRETATION
---------------------------------------------------------------------

The system can be described as:

Geometric:
three 4D hypercubes linked by triadic relations

Quantum information:
a stabilizer‑like parity subspace defined by

A_i XOR B_i XOR C_i = 0

---------------------------------------------------------------------
7. STATUS
---------------------------------------------------------------------

This repository documents an experimental exploration of structural coherence in NISQ quantum hardware.

The focus is reproducibility and experimentation rather than proposing a finished physical theory.
