
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
```
A = (A1, A2, A3, A4)  
B = (B1, B2, B3, B4)  
C = (C1, C2, C3, C4)
```
with the structural constraint:
```
C_i = A_i XOR B_i
```
This implies the parity relation:
```
A_i XOR B_i XOR C_i = 0
```
Each axis forms a **triadic relation**.

---

# Dimensional Reduction

Without constraints:
```
2^12 = 4096 states
```
With the four parity relations:
```
2^(12 − 4) = 256 coherent states
```
Therefore the system defines a **coherent subspace of dimension 8** embedded in a 12‑bit space.
This subspace is the object studied in both the classical and quantum experiments.

---
# Mathematical Model

The core of the project is a structural model defined on 12 binary variables grouped into three blocks of four variables.

Let
```
A = (A₁, A₂, A₃, A₄)
B = (B₁, B₂, B₃, B₄)
C = (C₁, C₂, C₃, C₄)
```
Each axis of the system satisfies the triadic relation
```
Cᵢ = Aᵢ ⊕ Bᵢ
```
which is equivalent to the parity constraint
```
Aᵢ ⊕ Bᵢ ⊕ Cᵢ = 0
```
for every axis 𝑖 = 1,2,3,4


# Dimensional Structure

Without constraints the full system contains
```
2¹² = 4096
```
possible states.

The four parity constraints reduce the space to a coherent subspace
```
2^(12 − 4) = 256 states
```
Therefore the model can be described as
```
S = { (A,B,C) ∈ {0,1}¹² | C = A ⊕ B }
```
which defines an 8-dimensional binary subspace embedded in a 12-bit space.

# Interpretation

Each axis forms a triadic dependency between three variables:
```
(Aᵢ, Bᵢ, Cᵢ)
```
This dependency has the following information structure:
```
I(A;B) = 0
I(A;C) = 0
I(B;C) = 0
```
but
```
I(A;B | C) = 1
```
meaning that the relationship is not pairwise but triadic.

# Relation to Quantum Circuits

In the quantum experiments this constraint is implemented using CNOT gates:
```
qc.cx(A[i], C[i])
qc.cx(B[i], C[i])
```
which computes
```
Cᵢ = Aᵢ XOR Bᵢ
```
and prepares states of the form
```
|A, B, A⊕B⟩
```
These states lie inside the coherent subspace defined by the parity relations.

# Stabilizer Interpretation

The parity relations correspond to stabilizer operators of the form
```
Z_Aᵢ Z_Bᵢ Z_Cᵢ
```
which define a parity-constrained subspace of 12 qubits.

In this interpretation the model can be viewed as a simple example of a structured stabilizer subspace where coherence corresponds to the preservation of these parity constraints.

# Geometric View

Each block 𝐴,𝐵,𝐶 represents the vertices of a 4-dimensional hypercube.
The triadic constraint couples the three hypercubes axis by axis.

This structure can therefore be interpreted as three coupled 4-dimensional hypercubes forming a constrained 12-bit state space.

# Role in the Experiments

The experiments contained in this repository study:
- whether this constrained subspace survives real quantum hardware noise
- whether Grover amplification can bias the system toward structured subsets
- how different geometric subsets affect coherence stability

These experiments form the basis of the Structured Coherence Certificate benchmark included in this repository.

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
The goal of this first experiment is to test whether the structural constraint of the tri-hypercube model can survive the noise of real quantum hardware.
The classical model defines a triadic relation between three variables per axis:

```
C_i = A_i XOR B_i
```
which is equivalent to the parity constraint

```
A_i XOR B_i XOR C_i = 0
```
This relation must hold simultaneously for all four axes.
In other words, the valid states of the system belong to a coherent subspace of dimension 256 inside the full 12-qubit space.
The purpose of this experiment is simply:
prepare states inside this constrained subspace and measure how often the hardware preserves the structural relations.

## Circuit Structure

The circuit uses 12 qubits divided into three groups:

```
A1 A2 A3 A4
B1 B2 B3 B4
C1 C2 C3 C4
```
The preparation procedure is:
1- Create a uniform superposition over the registers A and B:
```
qc.h(A)
qc.h(B)
```
This produces all possible states of A and B simultaneously.

2- Compute register C from A and B using XOR relations:
```
C_i = A_i XOR B_i
```
implemented with two CNOT gates:
```
qc.cx(A[i], C[i])
qc.cx(B[i], C[i])
```
The resulting quantum state is therefore
```
|A, B, A⊕B>
```
which lies exactly in the coherent subspace defined by the model.

3- Measure all qubits.

## What the Experiment Tests
After execution, the results are analysed to check whether the structural relations remain valid.
For each measured state we verify:
```
A_i XOR B_i XOR C_i = 0
```
for every axis i = 1..4.
Two metrics are extracted.

### coherent_rate

Percentage of shots where all four parity relations are satisfied simultaneously.
```
coherent_rate =
shots where all constraints hold
--------------------------------
total shots
```
This measures how often the system remains inside the coherent structural subspace.

### axis_consistency

Average fraction of axes that satisfy the relation.
```
axis_consistency =
correct axes across all shots
-----------------------------
4 × total shots
```
This metric is useful because noise usually breaks individual axes, not the entire state.

## Results on Real Hardware
Example execution on IBM Marrakesh:
```
coherent_rate   ≈ 0.87
axis_consistency ≈ 0.96
```

## Interpretation:
- Around 87% of shots remain completely coherent
- Around 96% of individual axes satisfy the structural relation
This indicates that the hardware preserves the triadic parity constraints surprisingly well, even with hundreds of gates after transpilation.

## What This Demonstrates
This first experiment shows that:
- The tri-hypercube constraint can be implemented directly as a quantum circuit.
- The resulting states form a coherent parity-constrained subspace.
- Real NISQ hardware can maintain this structure with relatively high fidelity.

This provides the experimental foundation for the following experiments, which explore:
- amplification of structural subsets using Grover
- statistical behaviour of the constrained subspace
- geometric properties of different structural selections.

## Result Files

Example output:
```
tri_hypercube_quantum_20260314_202450.json
```
These files contain:
```
shots
coherent_rate
axis_consistency
counts
```
allowing full reproducibility of the experiment.

---

# Experiment v2 · Structural Amplification

File:

```
tri_hipercubo_quantum_v2.py
```
## Objective

Adds a Grover step selecting **one‑hot states of A**.
After verifying in Experiment v1 that the tri-hypercube constraint can survive hardware noise, the next question is:
```
Can we select or amplify a specific structural subset of that coherent subspace using quantum algorithms?
```

To explore this, the experiment introduces a Grover amplification step applied only to register A.
The goal is to bias the system toward a particular family of states without breaking the triadic constraint
```
C_i = A_i XOR B_i
```

## Structural Subset: One-Hot States

The subset selected by the oracle is the set of one-hot states of A:
```
0001
0010
0100
1000
```

These states correspond to unit vectors in the 4-dimensional hypercube, i.e. the axes of the hypercube.
Geometrically:
```
(1,0,0,0)
(0,1,0,0)
(0,0,1,0)
(0,0,0,1)
```
This subset contains:
```
4 states out of 16 possible A states
```

so the baseline probability without amplification is:
```
4 / 16 = 0.25
```

## Circuit Structure
The circuit begins exactly like the previous experiment.

### Step 1 — Superposition
Registers A and B are prepared in uniform superposition:
```
qc.h(A)
qc.h(B)
```
This creates all combinations of A and B.

### Step 2 — Grover Amplification on A
A single Grover iteration is applied to register A:
```
Oracle → Diffusion
```
The oracle marks the one-hot states and the diffusion operator amplifies their amplitude.
This increases the probability of measuring those states.

### Step 3 — Structural Constraint

After amplification, register C is computed from A and B:
```
C_i = A_i XOR B_i
```
using CNOT gates:
```
qc.cx(A[i], C[i])
qc.cx(B[i], C[i])
```
This ensures that the final state still lies in the tri-hypercube coherent subspace.

## What the Experiment Tests
This experiment evaluates whether Grover amplification can operate inside the constrained subspace without destroying the structural relations.
Four main metrics are extracted.

### coherent_rate
Percentage of shots where all parity relations hold simultaneously:
```
A_i XOR B_i XOR C_i = 0
```
This measures whether the structural model survives amplification.

### axis_consistency
Average fraction of axes satisfying the relation.
This reveals whether noise breaks constraints locally or globally.

### A_good_rate
Fraction of shots where register A belongs to the selected subset:
```
{0001,0010,0100,1000}
```
Without Grover this value should be:
```
≈ 0.25
```
After amplification it should increase.

### joint_rate
Fraction of shots where both conditions hold:
```
A ∈ one-hot subset
AND
tri-hypercube constraints satisfied
```
This metric is the most informative because it measures successful structural amplification.

## Example Results (IBM Marrakesh)

Typical values observed in hardware:
```
coherent_rate   ≈ 0.85
axis_consistency ≈ 0.96
A_good_rate     ≈ 0.49
joint_rate      ≈ 0.41
```

Interpretation:
The Grover step nearly doubles the probability of the selected subset:
```
baseline ≈ 0.25
observed ≈ 0.49
```
Structural coherence remains high.
This means the circuit successfully performs selective amplification within the coherent subspace.

## What This Demonstrates

This experiment shows that:
- The tri-hypercube constraint remains robust even after applying a Grover amplification step.
- Quantum amplitude amplification can bias the structural state space toward specific subsets.
- The resulting states remain largely inside the coherent subspace defined by the model.

In other words:
```
Grover amplification can operate within a structured parity-constrained subspace without destroying its coherence.
```

## Geometric Interpretation

In the hypercube representation of register A:
- one-hot states correspond to the axes of the 4D hypercube
Grover amplification therefore concentrates amplitude on these axis directions.

When propagated through the structural constraint
```
C = A XOR B
```
this selection defines families of coherent states inside the tri-hypercube.

## Result Files
Example output:
```
tri_hypercube_quantum_v2_20260314_203047.json
```
These files contain:
```
coherent_rate
axis_consistency
A_good_rate
joint_rate
counts
```
and allow full reproducibility of the experiment.

## Role in the Project
Experiment v2 establishes that the tri-hypercube model is not only structurally coherent but also dynamically manipulable using quantum algorithms.
This provides the foundation for the following experiments:
- statistical benchmarking (v3)
- Grover dynamics sweep (v4)
- geometric subset comparison (v5)

---

# Experiment v3 · Statistical Benchmark

File:

```
tri_hipercubo_quantum_v3.py
```
Compares baseline vs Grover selection.
Derived metrics include:
```
P(coherent | A_good)  
P(A_good | coherent)
```

## Objective 
The previous experiments demonstrated two key properties:
- The tri-hypercube constraint survives noise in real quantum hardware.
- Grover amplification can bias the system toward a structural subset of states.
However, those results alone do not reveal how the structural constraint and the Grover selection interact statistically.

This experiment introduces a statistical benchmark comparing two scenarios:
```
v1 → baseline structural coherence
v2 → structural coherence with Grover amplification
```

The goal is to measure how strongly the amplified subset remains compatible with the triadic constraint.

## Experimental Setup

Two circuits are executed:

### Baseline (v1)
Uniform superposition over registers A and B:
```
|A, B, A⊕B>
```
No selection is applied.
This produces the natural distribution of states in the coherent subspace.

### Grover selection (v2)
A Grover iteration is applied to register A to amplify the one-hot states:
```
0001
0010
0100
1000
```
After amplification the structural constraint
```
C_i = A_i XOR B_i
```
is computed as before.

## Metrics Introduced

The main contribution of this experiment is the introduction of conditional structural metrics.
These metrics allow us to measure how selection and coherence interact.

### coherent_rate
Fraction of shots satisfying the structural constraint:
```
A_i XOR B_i XOR C_i = 0
```
for all four axes.

### A_good_rate
Fraction of shots where register A belongs to the selected subset:
```
{0001,0010,0100,1000}
```
Baseline expectation without Grover:
```
0.25
```

### joint_rate
Fraction of shots satisfying both conditions:
```
A ∈ one-hot subset
AND
structural constraint holds
```
This measures the effective success rate of structured amplification.

## Conditional Metrics

The most informative quantities are two conditional probabilities.
### P(coherent | A_good)
Probability that the structural constraint holds given that the selected subset was measured.
```
P(coherent | A_good) =
joint_rate / A_good_rate
```
This answers the question:
If the Grover selection succeeds, how often does the structural model remain valid?

### P(A_good | coherent)
Probability that the measured state belongs to the selected subset given that the system is coherent.
```
P(A_good | coherent) =
joint_rate / coherent_rate
```
This measures how strongly the coherent subspace is biased toward the selected structural family.

## Example Results (IBM Marrakesh)

Typical results obtained on real hardware:
### Baseline (v1):
```
coherent_rate ≈ 0.885
axis_consistency ≈ 0.970
A_good_rate ≈ 0.255
joint_rate ≈ 0.229
```

### Grover selection (v2):
```
coherent_rate ≈ 0.824
axis_consistency ≈ 0.951
A_good_rate ≈ 0.416
joint_rate ≈ 0.346
```
### Derived conditional metrics:
```
P(coherent | A_good) ≈ 0.83
P(A_good | coherent) ≈ 0.42
```

## Interpretation
These results show that:
• The structural constraint remains robust even when Grover amplification is applied.
• The probability of observing the target structural subset increases significantly.
• The amplified states still remain largely inside the coherent tri-hypercube subspace.

In other words:
The Grover selection and the structural constraint are compatible rather than competing mechanisms.

## Why This Experiment Matters
Experiment v3 transforms the previous tests into a true statistical benchmark.
Instead of measuring only raw success rates, it measures:
```
how selection interacts with structural coherence
```
This provides a clearer picture of the system's behavior under noise.

## Result Files

Example outputs:
```
tri_hypercube_v1_v2_benchmark_20260314_205037.json
```
These JSON files include:
```
coherent_rate
axis_consistency
A_good_rate
joint_rate
conditional probabilities
```
allowing the benchmark to be reproduced and compared across hardware backends.

## Role in the Project
Experiment v3 provides the statistical framework used in the final benchmark stage.
The metrics introduced here are later used in:
- Structured Coherence Certificate

which summarizes the structural performance of a quantum backend.

---

# Experiment v4 · Grover Dynamics

File:
```
tri_hipercubo_quantum_v4.py
```
Performs a Grover sweep:
```
| k | A_good_rate |
|---|-------------|
| 0 | ~0.25 |
| 1 | ~0.62 |
| 2 | ~0.37 |
```
This matches the expected Grover amplification curve.

## Objective

The previous experiments showed that:
- the tri-hypercube constraint survives hardware noise (v1)
- structural subsets can be amplified (v2)
- the interaction between selection and coherence can be measured statistically (v3)

The next question is:
```
Does the amplification follow the expected Grover dynamics when we vary the number of iterations?
```
This experiment performs a Grover sweep by varying the number of Grover iterations applied to register A.

## Experimental Idea

Register A contains 4 qubits, therefore:
```
|A| = 2^4 = 16 states
```
The oracle marks the one-hot states:
```
0001
0010
0100
1000
```
Number of marked states:
```
M = 4
```
Total states:
```
N = 16
```
So the baseline probability of observing a marked state is:
```
M / N = 4 / 16 = 0.25
```
Grover amplification should increase this probability after one iteration.

## Circuit Procedure

For each value of k, the circuit performs:

1- Uniform superposition over registers A and B
```
qc.h(A)
qc.h(B)
```

2- k Grover iterations applied only to register A
Each iteration consists of:
```
oracle → diffusion
```

3- Propagation of the structural constraint
```
C_i = A_i XOR B_i
```
implemented with:
```
qc.cx(A[i], C[i])
qc.cx(B[i], C[i])
```

4- Measurement of all qubits.

## Metric Measured

The key metric for this experiment is:
```
A_good_rate
```
which measures the probability that the measured state of register A belongs to the one-hot subset.

## Grover Sweep

The experiment evaluates three values of k:
```
k	Description
0	No Grover step (baseline)
1	Single Grover amplification
2	Second Grover iteration
Example Results (IBM Marrakesh)
```
Typical results observed on real hardware:
```
k	A_good_rate
0	~0.25
1	~0.62
2	~0.37
```

## Interpretation:

### k = 0
Uniform distribution over A.

### k = 1
Amplitude amplification increases probability of the target states.

### k = 2
Probability decreases again due to Grover over-rotation.

This pattern matches the theoretical Grover behavior.

## Why This Matters

This experiment demonstrates that:
- The tri-hypercube subspace is compatible with Grover amplification.
- The quantum hardware reproduces the expected Grover oscillation.
- Structural coherence is preserved while the subset is amplified.
In other words:
```
The system behaves like a structured search space embedded inside the coherent tri-hypercube subspace.
```

## Result Files

Example output files:
```
tri_hypercube_k_sweep_20260314_205923.json
```
These files contain:
```
coherent_rate
axis_consistency
A_good_rate
joint_rate
```
for each value of k.

## Interpretation in the Model

Within the tri-hypercube framework:
- the coherent subspace contains 256 valid states
- Grover amplification selects families of states defined by the geometry of A
- the experiment confirms that this selection behaves according to the theoretical Grover dynamics
This result validates that the structural model can support controlled quantum amplitude amplification.

## Role in the Project

Experiment v4 demonstrates that the tri-hypercube model is not only structurally coherent but also dynamically manipulable using standard quantum algorithms.
It provides the bridge between:
```
structural coherence (v1)
subset amplification (v2)
statistical interaction (v3)
```
and the final benchmarking framework used in the Structural Coherence Certificate.

---

# Experiment v5 · Geometric Selection

File
```
tri_hipercubo_quantum_v5.py
```

## Objective

The previous experiments showed that:
- the tri-hypercube structural constraint can survive hardware noise (v1)
- Grover amplification can bias the system toward specific subsets (v2)
- the interaction between selection and structural coherence can be measured statistically (v3)
- Grover amplification follows the expected oscillation dynamics (v4)

The goal of this experiment is different:
```
Investigate how the geometry of the selected subset of states affects structural coherence.
```
In particular, the experiment compares two different subsets of register A:
```
one-hot states
two-hot states
```
These correspond to different geometric directions in the 4D hypercube of A.

## Structural Subsets Compared

Register A contains 4 qubits:
```
A1 A2 A3 A4
```
which define a 4-dimensional hypercube with 16 possible states.

The experiment compares two families of states.

### One-Hot States
```
0001
0010
0100
1000
```
These correspond to the axes of the hypercube.
Geometrically they represent unit vectors:
```
(1,0,0,0)
(0,1,0,0)
(0,0,1,0)
(0,0,0,1)
```
Number of states:
```
4
```
Baseline probability without amplification:
```
4 / 16 = 0.25
```

### Two-Hot States
```
1100
0011
1010
0101
1001
0110
```
These correspond to diagonal directions of the hypercube faces.
Example vectors:

(1,1,0,0)
(0,0,1,1)
(1,0,1,0)
...
Number of states:
```
6
```
Baseline probability without amplification:
```
6 / 16 = 0.375
```

## Circuit Procedure

The circuit structure is similar to Experiment v2.

1- Prepare uniform superposition over A and B
```
qc.h(A)
qc.h(B)
```

2- Apply a Grover oracle selecting either:
```
one-hot states
or
two-hot states
```

3- Apply Grover diffusion.

4- Compute the structural relation:
```
C_i = A_i XOR B_i
```

5- Measure all qubits.

## Metrics Measured

The same structural metrics from previous experiments are used.
```
coherent_rate
axis_consistency
A_good_rate
joint_rate
```
These allow direct comparison between the two geometries.

## Example Results (IBM Marrakesh)

Typical observed results:
```
Model	coherent_rate	axis_consistency	A_good_rate	joint_rate
one-hot	~0.86	~0.96	~0.57	~0.50
two-hot	~0.84	~0.96	~0.53	~0.46
```

Observation:
One-hot states maintain slightly higher coherence
than two-hot states.

Interpretation:
This suggests that the tri-hypercube structure interacts differently with different geometric subsets of the hypercube.
```
One-hot states correspond to axis directions, where only one coordinate is active.
Two-hot states correspond to face diagonals, where two coordinates are active simultaneously.
```
When two coordinates are active, more parity relations are affected simultaneously, which slightly increases the probability that noise breaks the structural constraint.
In practice this means:
Axis-aligned structures are slightly more robust than diagonal structures under realistic hardware noise.

## Geometric Interpretation

In the hypercube representation:
```
one-hot → axes of the hypercube
two-hot → diagonals of faces
```
Grover amplification therefore selects different geometric families of states.
This experiment shows that the geometry of the selected subset influences structural stability.

## Result Files

Example outputs:
```
tri_hypercube_onehot_vs_twohot_20260314_211217.json
```
These files contain the measured metrics for both subsets.

## Role in the Project

This experiment completes the structural exploration by showing that:
- the tri-hypercube model defines a coherent subspace
- Grover amplification can select subsets within that space
- the geometry of those subsets affects how well the structure survives hardware noise

This observation motivates the final component of the repository:
```
Structured Coherence Certificate
```
which summarizes structural performance of a quantum backend using these metrics.

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
