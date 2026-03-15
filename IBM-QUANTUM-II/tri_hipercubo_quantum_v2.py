#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


GOOD_A = {"0001", "0010", "0100", "1000"}


# =========================================================
# Helpers
# =========================================================

def phase_flip_on_pattern(qc: QuantumCircuit, qubits, pattern: str):
    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(qubits[i])

    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])

    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(qubits[i])


def oracle_A_onehot(qc: QuantumCircuit, A):
    for p in GOOD_A:
        phase_flip_on_pattern(qc, A, p)


def diffusion(qc: QuantumCircuit, qubits):
    qc.h(qubits)
    qc.x(qubits)

    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])

    qc.x(qubits)
    qc.h(qubits)


# =========================================================
# Circuit builder
# =========================================================

def build_tri_hypercube_v2():
    qc = QuantumCircuit(12, 12)

    A = [0, 1, 2, 3]
    B = [4, 5, 6, 7]
    C = [8, 9, 10, 11]

    # Superposición uniforme en A y B
    qc.h(A)
    qc.h(B)

    # Una iteración Grover SOLO sobre A
    oracle_A_onehot(qc, A)
    diffusion(qc, A)

    # C = A XOR B
    for i in range(4):
        qc.cx(A[i], C[i])
        qc.cx(B[i], C[i])

    qc.measure(range(12), range(12))
    return qc


# =========================================================
# Counts extraction
# =========================================================

def extract_counts(pub_result):
    data = pub_result.data

    if hasattr(data, "meas"):
        return data.meas.get_counts()

    if hasattr(data, "c"):
        return data.c.get_counts()

    for name in dir(data):
        if name.startswith("_"):
            continue
        obj = getattr(data, name)
        if hasattr(obj, "get_counts"):
            return obj.get_counts()

    raise RuntimeError("No counts found")


# =========================================================
# Metrics
# =========================================================

def metrics_v2(counts):
    shots = sum(counts.values())

    coherent = 0
    axis_ok_total = 0
    a_good = 0
    joint = 0

    for s, c in counts.items():
        # orden lógico: invertimos para leer q0..q11
        s = s[::-1]

        A = [int(x) for x in s[0:4]]
        B = [int(x) for x in s[4:8]]
        C = [int(x) for x in s[8:12]]

        A_str = "".join(str(x) for x in A)

        axis_ok = 0
        for i in range(4):
            if (A[i] ^ B[i]) == C[i]:
                axis_ok += 1

        axis_ok_total += axis_ok * c

        is_coherent = (axis_ok == 4)
        is_A_good = (A_str in GOOD_A)

        if is_coherent:
            coherent += c
        if is_A_good:
            a_good += c
        if is_coherent and is_A_good:
            joint += c

    return {
        "shots": shots,
        "coherent_rate": coherent / shots,
        "axis_consistency": axis_ok_total / (shots * 4),
        "A_good_rate": a_good / shots,
        "joint_rate": joint / shots,
    }


# =========================================================
# Runner
# =========================================================

def run(backend_name="ibm_marrakesh", shots=4096, opt_level=1):
    qc = build_tri_hypercube_v2()

    service = QiskitRuntimeService()
    backend = service.backend(backend_name)

    pm = generate_preset_pass_manager(
        backend=backend,
        optimization_level=opt_level
    )
    isa = pm.run(qc)

    sampler = Sampler(mode=backend)
    job = sampler.run([isa], shots=shots)
    result = job.result()

    counts = extract_counts(result[0])
    metrics = metrics_v2(counts)

    print("\nTri-Hipercubo Quantum v2")
    print("backend:", backend_name)
    print("job:", job.job_id())
    print("Depth ISA:", isa.depth())
    print("Ops ISA:", isa.count_ops())
    print(metrics)

    out = {
        "backend": backend_name,
        "job_id": job.job_id(),
        "depth_isa": isa.depth(),
        "ops_isa": {str(k): int(v) for k, v in isa.count_ops().items()},
        "metrics": metrics,
        "counts": counts,
    }

    fname = f"tri_hypercube_quantum_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("\nSaved:", fname)


if __name__ == "__main__":
    run()
