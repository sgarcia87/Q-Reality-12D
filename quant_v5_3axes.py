#!/usr/bin/env python3
"""
quant_v5_3axes.py

Extiende quant_v4_2axes a 3 ejes alineados entre planos:

Coherencia C(x) (en marco físico):
  (1) cada plano de 4 qubits tiene wt==2
  (2) ejes alineados:
        eje0: q0 == q4 == q8
        eje1: q1 == q5 == q9
        eje2: q2 == q6 == q10

Esto suele reducir M respecto a 2 ejes y, por tanto, concentra aún más
(en menos soluciones) tras Grover.

Requisitos:
  pip install qiskit qiskit-aer
"""

from __future__ import annotations

import itertools
import math
from typing import List, Tuple

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


_PATTERNS_W2 = (
    (1, 1, 0, 0),
    (1, 0, 1, 0),
    (1, 0, 0, 1),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (0, 0, 1, 1),
)


def mark_pattern(qc: QuantumCircuit, qubits4, flag, pattern_bits):
    for qb, b in zip(qubits4, pattern_bits):
        if b == 0:
            qc.x(qb)
    qc.mcx(qubits4, flag)
    for qb, b in zip(qubits4, pattern_bits):
        if b == 0:
            qc.x(qb)


def weight_eq_2_flag(qc: QuantumCircuit, qubits4, flag):
    for p in _PATTERNS_W2:
        mark_pattern(qc, qubits4, flag, p)


def uncompute_weight_eq_2_flag(qc: QuantumCircuit, qubits4, flag):
    for p in reversed(_PATTERNS_W2):
        mark_pattern(qc, qubits4, flag, p)


def compute_eq_three(qc: QuantumCircuit, qa, qb, qcbit, eq, t1, t2):
    # t1 = qa XOR qb
    qc.cx(qa, t1)
    qc.cx(qb, t1)
    # t2 = qb XOR qcbit
    qc.cx(qb, t2)
    qc.cx(qcbit, t2)
    # eq ^= AND(~t1, ~t2)
    qc.x(t1); qc.x(t2)
    qc.mcx([t1, t2], eq)
    qc.x(t1); qc.x(t2)


def uncompute_eq_three(qc: QuantumCircuit, qa, qb, qcbit, eq, t1, t2):
    qc.x(t1); qc.x(t2)
    qc.mcx([t1, t2], eq)
    qc.x(t1); qc.x(t2)

    qc.cx(qcbit, t2)
    qc.cx(qb, t2)

    qc.cx(qb, t1)
    qc.cx(qa, t1)


def grover_diffusion(qc: QuantumCircuit, qubits):
    qc.h(qubits)
    qc.x(qubits)
    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])
    qc.x(qubits)
    qc.h(qubits)


def coherent_string_phys(s_phys: str) -> bool:
    def wt(x: str) -> int:
        return sum(1 for b in x if b == "1")

    if len(s_phys) != 12:
        return False

    b0, b1, b2 = s_phys[0:4], s_phys[4:8], s_phys[8:12]
    w_ok = (wt(b0) == 2 and wt(b1) == 2 and wt(b2) == 2)
    axis0_ok = (s_phys[0] == s_phys[4] == s_phys[8])
    axis1_ok = (s_phys[1] == s_phys[5] == s_phys[9])
    axis2_ok = (s_phys[2] == s_phys[6] == s_phys[10])
    return w_ok and axis0_ok and axis1_ok and axis2_ok


def coherent_string_measured(bitstring_measured: str) -> bool:
    return coherent_string_phys(bitstring_measured[::-1])


def count_good_states() -> int:
    good = 0
    for bits in itertools.product("01", repeat=12):
        s = "".join(bits)
        if coherent_string_phys(s):
            good += 1
    return good


def suggested_grover_iterations(n_states: int, m_good: int) -> int:
    if m_good <= 0 or m_good >= n_states:
        return 0
    theta = math.asin(math.sqrt(m_good / n_states))
    k = int((math.pi / (4 * theta)) - 0.5)
    return max(0, k)


def build_circuit(iterations: int) -> QuantumCircuit:
    data = QuantumRegister(12, "q")

    w0 = QuantumRegister(1, "w0")
    w1 = QuantumRegister(1, "w1")
    w2 = QuantumRegister(1, "w2")

    eq0 = QuantumRegister(1, "eq0")
    eq1 = QuantumRegister(1, "eq1")
    eq2 = QuantumRegister(1, "eq2")

    t = QuantumRegister(6, "t")   # 2 ancillas por eje (3 ejes)

    ph = QuantumRegister(1, "ph")
    c = ClassicalRegister(12, "c")

    qc = QuantumCircuit(data, w0, w1, w2, eq0, eq1, eq2, t, ph, c)

    q = data
    b0 = [q[0], q[1], q[2], q[3]]
    b1 = [q[4], q[5], q[6], q[7]]
    b2 = [q[8], q[9], q[10], q[11]]

    qc.h(q)

    qc.x(ph[0])
    qc.h(ph[0])

    for _ in range(iterations):
        weight_eq_2_flag(qc, b0, w0[0])
        weight_eq_2_flag(qc, b1, w1[0])
        weight_eq_2_flag(qc, b2, w2[0])

        compute_eq_three(qc, q[0], q[4], q[8],  eq0[0], t[0], t[1])
        compute_eq_three(qc, q[1], q[5], q[9],  eq1[0], t[2], t[3])
        compute_eq_three(qc, q[2], q[6], q[10], eq2[0], t[4], t[5])

        qc.mcx([w0[0], w1[0], w2[0], eq0[0], eq1[0], eq2[0]], ph[0])

        uncompute_eq_three(qc, q[2], q[6], q[10], eq2[0], t[4], t[5])
        uncompute_eq_three(qc, q[1], q[5], q[9],  eq1[0], t[2], t[3])
        uncompute_eq_three(qc, q[0], q[4], q[8],  eq0[0], t[0], t[1])

        uncompute_weight_eq_2_flag(qc, b2, w2[0])
        uncompute_weight_eq_2_flag(qc, b1, w1[0])
        uncompute_weight_eq_2_flag(qc, b0, w0[0])

        grover_diffusion(qc, list(q))

    qc.measure(q, c)
    return qc


def run(shots: int = 4096, iterations: int | None = None, opt_level: int = 1) -> None:
    N = 2 ** 12
    M = count_good_states()
    k_suggested = suggested_grover_iterations(N, M)

    if iterations is None:
        iterations = k_suggested

    print(f"N={N}  M={M}  M/N={M/N:.6f}  k_sugerido≈{k_suggested}  k_usado={iterations}")

    qc = build_circuit(iterations=iterations)

    sim = AerSimulator()
    tqc = transpile(qc, sim, optimization_level=opt_level)
    res = sim.run(tqc, shots=shots).result()
    counts = res.get_counts()

    top10: List[Tuple[str, int]] = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("TOP10:", top10)

    good_shots = sum(v for k, v in counts.items() if coherent_string_measured(k))
    print(f"Shots coherentes (según C en físico): {good_shots} / {shots} = {good_shots/shots:.6f}")

    for s, c in top10:
        s_phys = s[::-1]
        ok = coherent_string_phys(s_phys)
        print(s, c, "phys=", s_phys, "ok=", ok,
              "blocks=", [s_phys[0:4], s_phys[4:8], s_phys[8:12]])


if __name__ == "__main__":
    SHOTS = 4096
    ITERATIONS = None  # None -> usa k_sugerido automáticamente
    run(shots=SHOTS, iterations=ITERATIONS, opt_level=1)
