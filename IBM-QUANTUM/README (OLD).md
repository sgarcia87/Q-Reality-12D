# IBM-QUANTUM — Hardware Validation Experiments

This folder contains hardware validation experiments executed on IBM Quantum backends (`ibm_torino`, `ibm_fez`, `ibm_marrakesh`).

The objective of these experiments is to test, under real NISQ noise conditions, the following architectural principle:

> Concentrate coherence in a small structural nucleus first,  
> then propagate structure (state and/or relations) afterward.

These experiments do **not** claim quantum advantage.  
They evaluate structural robustness, propagation behavior, and effective physical channel fidelity under realistic hardware noise.

---

# 1. Conceptual Overview

All structural experiments are based on a 4-qubit core (the "nucleus") and structured propagation to higher-dimensional layers.

The system evaluates three aspects simultaneously:

1. **Core amplification** (Grover on 4 qubits)
2. **Bitwise propagation** (state replication)
3. **Relational propagation** (XOR-based structural invariants)

Additionally, a complementary benchmark (`qIBM12D-MENSAJE`) evaluates raw hardware transmission fidelity independently of Grover dynamics.

---

# 2. qIBM_V3.7 — Hybrid (12 qubits)

## Architecture

Total qubits: 12

- q0–q3   → Core (4D nucleus)
- q4–q7   → Bitwise copy of core
- q8–q11  → Structural relations (XOR neighbors)

Workflow:

1. Prepare superposition on core.
2. Apply 1 Grover iteration on the 4-qubit nucleus.
3. After amplification:
   - Copy core state bitwise.
   - Compute XOR structural relations.
4. Measure entire system.

---

## What It Measures

- `P_good_base`  
  Probability that the core collapses into the selected coherent subset.

- `bit_exact`  
  Bitwise consistency between core and copied layer.

- `rel_consistency`  
  Consistency of relational XOR invariants derived from the core.

---

## Hardware Behavior

Observed behavior on real IBM hardware:

- Significant increase in `P_good_base` when k=1.
- Bitwise copy remains reasonably stable.
- Relational invariants remain highly consistent (~0.85–0.90 range).

This validates:

- Core amplification is physically observable in NISQ hardware.
- Structural invariants are robust under realistic noise.
- Propagating structure **after** amplification preserves coherence better than early replication.

---

# 3. qIBM_V3.7_2 — Full Structural Propagation (16 qubits)

## Architecture

Total qubits: 16

- q0–q3     → Core (4D nucleus)
- q4–q7     → Bitwise copy
- q8–q11    → XOR neighbor relations
- q12–q15   → XOR cross relations

This version evaluates two independent invariant layers simultaneously.

---

## What It Demonstrates

1. Core amplification remains observable in hardware.
2. Both local (neighbor) and cross relations remain highly stable.
3. Structural invariants survive hardware noise better than exact state fidelity.

---

# 4. qIBM12D-MENSAJE-V3 — 12D Physical Channel Benchmark

This experiment isolates the physical transmission fidelity of a 12-bit classical pattern in hardware.

It serves as a calibration and baseline reference for the structural experiments.

---

## Purpose

Before evaluating structural coherence, we quantify:

- Exact match rate of a 12-bit state
- Bit Error Rate (BER)
- Hamming distance distribution
- Backend-to-backend variation
- Impact of qubit layout selection
- Impact of readout mitigation

---

## Test Execution

The following command was executed:

```bash
python3 qIBM12D-MENSAJE-V3.py --platform ibm --backends ibm_torino,ibm_fez,ibm_marrakesh --msg 010011001010 --shots 4096 --layout best_readout --mitigate_readout --save_json

backend: ibm_torino  job_id: d694fhhv6o8c73d7dle0
raw exact_match_rate: 0.939209  raw BER: 0.005168
mitigated exact_match_rate: 0.972900  mitigated BER: 0.002340

backend: ibm_fez  job_id: d694gbhv6o8c73d7dmi0
raw exact_match_rate: 0.934082  raw BER: 0.005595
mitigated exact_match_rate: 0.972656  mitigated BER: 0.002380

backend: ibm_marrakesh  job_id: d694hdlbujdc73d1p2o0
raw exact_match_rate: 0.967285  raw BER: 0.002808
mitigated exact_match_rate: 0.991943  mitigated BER: 0.000753

=== SUMMARY ===
ibm_torino      exact=0.9729  BER=0.0023  target=010100110010
ibm_fez         exact=0.9727  BER=0.0024  target=010100110010
ibm_marrakesh   exact=0.9919  BER=0.0008  target=010100110010
```

---

## Interpretation

### Layout Matters

Using --layout best_readout selects the 12 qubits with lowest readout error on each backend. 
This significantly improves raw fidelity compared to default layout.

### Readout Mitigation is Highly Effective

Applying independent per-qubit readout calibration:
- Reduces BER by ~50–70%
- Pushes exact match above 97% on Torino and Fez
- Pushes exact match above 99% on Marrakesh

### Backend Comparison

ibm_marrakesh exhibited the highest effective channel stability in this test. This demonstrates that:
- Backend calibration state strongly influences experiment outcomes.
- Hardware-aware compilation is critical.
- Readout error dominates shallow classical circuits.

---

## Empirical Contribution

These experiments collectively demonstrate:
- Amplification-first strategies are robust under NISQ noise.
- Structural invariants are more stable than raw replication.
- Hardware-aware layout selection is critical.
- Readout mitigation significantly improves effective fidelity.
- Hybrid architectures (core + relations) are viable in real hardware.

---

## Relevance to Current Quantum Landscape

In the NISQ regime:
- Multi-controlled gates are costly.
- State replication propagates noise.
- Backend calibration matters.
- Readout errors dominate shallow experiments.

These results show:
- Coherence can be localized and amplified.
- Structural projection is robust.
- Hardware-aware compilation is essential.
- Physical channel characterization should precede algorithmic claims.

This aligns with current research directions in:
- Noise-aware compilation
- Invariant-based validation
- Readout mitigation strategies
- Backend-aware architecture design

---

## Files Included

qIBM_V3.7.py
qIBM_V3.7_2.py
qIBM12D-MENSAJE-V3.py
results_qIBM_v3_7_*.json
results_qIBM_v3_7_2_*.json
results_qIBM12D_MENSAJE_ibm_*.json

---

## Scope and Limitations

These experiments:
- Do not claim quantum speedup.
- Do not demonstrate fault tolerance.
- Operate within NISQ constraints.
- Use shallow circuits for physical benchmarking.
- They are architectural and hardware-validation experiments.

---

## Summary

IBM-QUANTUM provides hardware validation of:
- Core amplification
- Delayed structural propagation
- Invariant robustness
- Backend-aware layout optimization
- Readout mitigation effects

The results confirm that:
- Amplifying a small coherent nucleus before propagation improves robustness.
- Structural relations remain stable under realistic noise.
- Layout selection and readout mitigation dramatically improve effective 12D channel fidelity.
- Hardware-level benchmarking is essential before structural algorithm design.
This establishes a rigorous experimental baseline for further structural and multidimensional architecture exploration.
