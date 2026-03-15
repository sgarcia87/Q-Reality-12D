
# Q-Reality-12D
### Structured Subspace Experiments in Quantum Search Algorithms

## Overview

This repository contains a collection of experiments exploring how **highly structured subsets of quantum state spaces behave under amplitude amplification algorithms**, particularly variants of **Grover's algorithm**.

The experiments are implemented using **Qiskit** and operate on systems of **12 qubits (or 12 classical bits in simulation)**. The project investigates how imposing **geometric and algebraic constraints on the state space** dramatically reduces the number of valid configurations and how quantum amplitude amplification concentrates probability on those configurations.

The goal is not to propose a physical theory of the universe, but to study how **structured constraints interact with quantum search dynamics**.

---

# Core Idea

Consider the full state space of a 12-qubit system:

2^12 = 4096

Each experiment defines a **subset of states** that satisfy specific structural constraints.

Examples of such constraints include:

- fixed **Hamming weight**
- **axis alignment** between groups of qubits
- global **parity conditions**
- algebraic relations between registers

These constraints typically reduce the valid state space to a **very small set of solutions** (often 6 or 8 states).

Grover-style amplitude amplification is then used to concentrate measurement probability on those structured states.

---

# Conceptual Structure

In most experiments, the 12 qubits are conceptually grouped into three blocks of four qubits:

Plane A : q0 q1 q2 q3  
Plane B : q4 q5 q6 q7  
Plane C : q8 q9 q10 q11

This organization allows the experiments to impose relationships such as:

- alignment of corresponding qubits across planes
- repeated bit patterns
- parity relations across the entire system

These constraints define a **structured subspace** within the full 12-qubit Hilbert space.

---

# Why This Is Interesting

Many quantum algorithms operate over large state spaces without additional structure.

These experiments explore a different scenario:

**What happens when the search space itself has strong internal structure?**

Key questions explored include:

- How quickly does Grover amplification converge when the solution space is extremely small?
- How robust are structured constraints under quantum operations?
- How does probability flow within constrained subspaces?

---

# Experiments Included

The repository contains several experiment families.

## quant_v5_3axes.py

Applies Grover amplification to a 12-qubit register where:

- each 4-qubit block has **Hamming weight = 2**
- corresponding qubits across planes are aligned

These constraints reduce the 4096-state space to **6 valid configurations**.

Grover amplification concentrates the probability entirely on these states.

Example output:

Shots coherentes: 4096 / 4096 = 1.000000

---

## quant_v8_3axes_parity_pm.py

Extends the previous experiment by introducing a **global parity condition** across the full 12-qubit system.

Two branches are tested:

SIGN = +  → even parity  
SIGN = −  → odd parity

Only one parity branch is structurally compatible with the geometric constraints, leaving **6 valid states**.

---

## quant_v10_12sign_product_pm.py

Defines the ± condition using the **global bit product / parity of the full system**.

This experiment demonstrates that certain global constraints can eliminate entire branches of the solution space.

---

## Q-12_v13.py

Implements **exact amplitude amplification** (phase-matched Grover).

Instead of standard Grover iterations, the final step uses specially calculated phases to rotate the system exactly into the solution subspace.

The result matches theoretical predictions:

P_theory ≈ 1.0

---

# What These Experiments Demonstrate

These experiments illustrate several properties of amplitude amplification algorithms:

1. **State-space reduction**

Structural constraints drastically reduce the number of valid states within a large Hilbert space.

2. **Amplification efficiency**

Grover amplification rapidly concentrates probability on these structured subsets.

3. **Sensitivity to constraints**

Small changes in global constraints can eliminate entire branches of the solution space.

---

# Relation to NISQ Experiments

Several versions of these circuits are also executed on **IBM Quantum hardware**.

These runs are used to study:

- how structured constraints degrade under noise
- how well parity relations survive decoherence
- how amplitude amplification behaves on real NISQ devices

The repository includes JSON result files exported from IBM Quantum runs.

---

# Important Clarification

This repository **does not claim to prove any physical theory about the structure of the universe**.

The experiments are computational and algorithmic in nature and should be understood as:

- explorations of structured search spaces
- demonstrations of amplitude amplification dynamics
- small-scale benchmarks of constrained quantum circuits

---

# Requirements

pip install qiskit qiskit-aer

---

# Running Experiments

Example:

python3 quant_v5_3axes.py

---

# Future Work

Possible extensions include:

- benchmarking on multiple IBM Quantum backends
- comparison with noisy simulators
- analysis of error propagation in constrained subspaces
- connection with stabilizer verification and parity-based codes

---

# Author

Sergi Garcia Mecinas

---

# Related Material

The repository is conceptually inspired by ideas developed in the manuscript **“La Realidad”**, but the experiments themselves should be interpreted strictly as **computational investigations of structured quantum state spaces**.
