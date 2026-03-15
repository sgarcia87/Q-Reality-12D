#!/usr/bin/env python3
"""
Structured Coherence Certificate v0.1

Runs a lightweight structural benchmark based on the tri-hypercube constraint:
C_i = A_i XOR B_i
"""

import argparse
import json
from datetime import datetime

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

ONE_HOT = {"0001","0010","0100","1000"}
TWO_HOT = {"1100","0011","1010","0101","1001","0110"}


def phase_flip(qc, qubits, pattern):
    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(qubits[i])
    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])
    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(qubits[i])


def oracle(qc, A, patterns):
    for p in patterns:
        phase_flip(qc, A, p)


def diffusion(qc, qubits):
    qc.h(qubits)
    qc.x(qubits)
    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])
    qc.x(qubits)
    qc.h(qubits)


def build_circuit(patterns=None):
    qc = QuantumCircuit(12, 12)
    A = [0,1,2,3]
    B = [4,5,6,7]
    C = [8,9,10,11]

    qc.h(A)
    qc.h(B)

    if patterns:
        oracle(qc, A, patterns)
        diffusion(qc, A)

    for i in range(4):
        qc.cx(A[i], C[i])
        qc.cx(B[i], C[i])

    qc.measure(range(12), range(12))
    return qc


def extract_counts(pub):
    data = pub.data
    if hasattr(data, "meas"):
        return data.meas.get_counts()
    if hasattr(data, "c"):
        return data.c.get_counts()
    for name in dir(data):
        obj = getattr(data, name)
        if hasattr(obj, "get_counts"):
            return obj.get_counts()
    raise RuntimeError("Counts not found")


def compute_metrics(counts, goodA):
    shots = sum(counts.values())
    coherent = 0
    axis_correct = 0
    A_good = 0
    joint = 0

    for s, c in counts.items():
        s = s[::-1]
        A = [int(x) for x in s[0:4]]
        B = [int(x) for x in s[4:8]]
        C = [int(x) for x in s[8:12]]
        A_str = "".join(str(x) for x in A)

        axis_ok = 0
        for i in range(4):
            if (A[i] ^ B[i]) == C[i]:
                axis_ok += 1

        axis_correct += axis_ok * c
        is_coherent = axis_ok == 4
        is_A_good = A_str in goodA

        if is_coherent:
            coherent += c
        if is_A_good:
            A_good += c
        if is_coherent and is_A_good:
            joint += c

    coherent_rate = coherent / shots
    axis_consistency = axis_correct / (shots * 4)
    A_good_rate = A_good / shots
    joint_rate = joint / shots

    baseline_A = len(goodA) / 16
    gain_A = A_good_rate / baseline_A if baseline_A else 0
    baseline_joint = coherent_rate * baseline_A

    P_coherent_given_A = (joint_rate / A_good_rate) if A_good_rate else 0
    P_A_given_coherent = (joint_rate / coherent_rate) if coherent_rate else 0

    return {
        "shots": shots,
        "coherent_rate": coherent_rate,
        "axis_consistency": axis_consistency,
        "A_good_rate": A_good_rate,
        "joint_rate": joint_rate,
        "gain_A": gain_A,
        "P_coherent_given_A": P_coherent_given_A,
        "P_A_given_coherent": P_A_given_coherent,
        "baseline_A": baseline_A,
        "baseline_joint": baseline_joint
    }


def coherence_score(metrics):
    score = (
        0.4 * metrics["coherent_rate"]
        + 0.3 * metrics["axis_consistency"]
        + 0.3 * min(metrics["gain_A"] / 2.0, 1.0)
    )
    return round(score * 100, 2)


def run_case(name, patterns, backend_name):
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)

    qc = build_circuit(patterns)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa = pm.run(qc)

    sampler = Sampler(mode=backend)
    job = sampler.run([isa], shots=4096)
    result = job.result()

    counts = extract_counts(result[0])
    metrics = compute_metrics(counts, patterns if patterns else ONE_HOT)
    score = coherence_score(metrics)

    print(f"\n{name}")
    print("job:", job.job_id())
    print("score:", score)
    print(metrics)

    return {
        "job_id": job.job_id(),
        "metrics": metrics,
        "coherence_score": score
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--cases", default="v1,onehot,twohot")
    args = parser.parse_args()

    cases = args.cases.split(",")
    results = {}

    for c in cases:
        if c == "v1":
            patterns = None
            label = "baseline_uniform"
        elif c == "onehot":
            patterns = ONE_HOT
            label = "grover_one_hot"
        elif c == "twohot":
            patterns = TWO_HOT
            label = "grover_two_hot"
        else:
            continue

        results[label] = run_case(label, patterns, args.backend)

    out = {
        "backend": args.backend,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    fname = f"structured_coherence_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2)

    print("\nSaved:", fname)


if __name__ == "__main__":
    main()
