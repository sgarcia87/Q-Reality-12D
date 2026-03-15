
# IBM-QUANTUM — Hardware Validation Experiments

This directory contains experiments executed on **IBM Quantum hardware** to evaluate how structured quantum circuits behave under realistic **NISQ (Noisy Intermediate-Scale Quantum) noise conditions**.

Backends used in these tests include:

- ibm_torino
- ibm_fez
- ibm_marrakesh

The goal of these experiments is to evaluate how **small amplified quantum cores propagate state information and derived parity relations across larger registers** when executed on real quantum processors.

These experiments **do not claim quantum advantage**.  
They are intended as **hardware benchmarking and validation experiments** for structured circuits on current quantum hardware.

---

# Experimental Design

All experiments follow a common architecture composed of four steps:

1. **Core preparation**
   - A 4‑qubit register is initialized in superposition.

2. **Amplitude amplification**
   - A Grover iteration is applied on the core register to amplify a subset of states.

3. **State propagation**
   - The amplified core is propagated to additional qubit layers via direct copying and derived relations.

4. **Measurement**
   - The entire register is measured and analyzed.

This architecture allows us to observe:

- amplification behavior
- propagation fidelity
- stability of derived parity relations
- noise sensitivity in real NISQ devices

---

# Methodology

The experiments are implemented in **Qiskit** and executed on IBM Quantum backends using the following general methodology.

## Circuit Structure

Each experiment uses a layered structure:

Core register → Amplification → Propagation → Measurement

The propagation stage includes:

- **bitwise copy layers**
- **XOR parity relation layers**

These layers allow evaluation of how structural relations degrade under hardware noise.

## Measurement Metrics

Three metrics are used to evaluate behavior:

### 1. P_good_base

Probability that the **core register collapses into the amplified subset of states**.

### 2. bit_exact

Fraction of measurement shots where the copied register matches the core register exactly.

### 3. rel_consistency

Fraction of shots where the XOR relations derived from the core are preserved.

These metrics provide a simple way to distinguish:

- amplification success
- propagation fidelity
- robustness of relational constraints

---

# Experiment 1 — qIBM_V3.7 (12 Qubits)

## Architecture

Total qubits: 12

q0–q3   → Core register (Grover amplification)  
q4–q7   → Bitwise copy of core  
q8–q11  → XOR parity relations

## Workflow

1. Initialize superposition on the 4‑qubit core.
2. Apply one Grover iteration.
3. Copy the amplified state to a second register.
4. Compute XOR relations.
5. Measure all qubits.

## Observations

Results on real IBM hardware show:

- clear amplification of the selected core states
- moderate degradation of copied states
- relatively stable XOR relations

Typical relational consistency observed:

≈ 0.85 – 0.90

This suggests **derived parity relations degrade more slowly than exact state replication** under hardware noise.

---

# Experiment 2 — qIBM_V3.7_2 (16 Qubits)

## Architecture

Total qubits: 16

q0–q3     → Core register  
q4–q7     → Bitwise copy layer  
q8–q11    → XOR neighbor relations  
q12–q15   → XOR cross relations

## Purpose

This experiment evaluates the behavior of **multiple parity relation layers simultaneously**.

## Observations

Hardware execution shows:

- amplification still observable
- parity layers remain stable
- cross relations degrade slightly faster than neighbor relations

However, both relation layers remain more robust than direct state copying.

---

# Experiment 3 — qIBM12D-MENSAJE-V3

## Purpose

This experiment isolates the **physical transmission fidelity of a 12‑qubit classical pattern**.

It provides a baseline measurement for:

- exact match rate
- bit error rate (BER)
- Hamming distance distribution
- backend variability
- readout mitigation effects

---

# Test Execution

Example command:

python3 qIBM12D-MENSAJE-V3.py --platform ibm --backends ibm_torino,ibm_fez,ibm_marrakesh --msg 010011001010 --shots 4096 --layout best_readout --mitigate_readout --save_json

---

# Results

Example results obtained from the experiment:

ibm_torino
exact_match ≈ 0.9729  
BER ≈ 0.0023

ibm_fez
exact_match ≈ 0.9727  
BER ≈ 0.0024

ibm_marrakesh
exact_match ≈ 0.9919  
BER ≈ 0.0008

---

# Result Interpretation

### Layout Selection

Selecting qubits with the lowest readout error improves fidelity significantly.

### Readout Mitigation

Per‑qubit readout calibration reduces BER by roughly **50–70%**.

### Backend Differences

Different devices show different stability depending on:

- calibration state
- qubit connectivity
- readout fidelity

---

# Empirical Observations

Across the experiments we observe:

- amplified cores remain observable on real hardware
- relational constraints are relatively robust
- state copying propagates noise more quickly
- readout mitigation significantly improves fidelity
- backend-aware compilation is critical

---

# Relevance for NISQ Hardware

These experiments illustrate several practical aspects of current quantum devices:

- multi‑controlled operations are costly
- noise propagates through copied registers
- backend calibration strongly affects results
- readout errors dominate shallow circuits

Therefore:

- layout selection is important
- parity checks can serve as useful diagnostics
- hardware benchmarking is necessary before algorithm design

---

# Files Included

qIBM_V3.7.py  
qIBM_V3.7_2.py  
qIBM12D-MENSAJE-V3.py  

results_qIBM_v3_7_*.json  
results_qIBM_v3_7_2_*.json  
results_qIBM12D_MENSAJE_ibm_*.json

---

# Scope and Limitations

These experiments:

- operate within NISQ constraints
- use shallow circuits
- are intended as hardware validation experiments
- do not demonstrate quantum speedup
- do not implement fault‑tolerant computation

---

# Summary

The IBM‑QUANTUM experiments validate on real hardware:

- Grover amplification on a small core register
- propagation of states and parity relations
- robustness of XOR invariants
- importance of layout selection
- effectiveness of readout mitigation

These results establish an experimental baseline for studying **structured circuits on current NISQ devices**.
