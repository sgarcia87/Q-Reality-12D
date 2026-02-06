#!/usr/bin/env python3
"""
quant_v10_4axes_full_vertices_sign.py

Alineado con 'La Realidad.pdf': teseracto completo (16 vértices por patrón 4D), 
alineación en 4 ejes (4 dims), ^3 como repetición fractal en 3 planos, 
± como simetría par/impar en los 4 ejes (XOR q0-3).
Sin wt=2 para todos los vértices duales.

Requisitos: pip install qiskit qiskit-aer
"""

from __future__ import annotations

import itertools
import math
from typing import List, Tuple

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

# Configuración del ± global
SIGN = +1  # +1: XOR(q0,q1,q2,q3)=1; -1: =0

def compute_eq_three(qc: QuantumCircuit, qa, qb, qcbit, eq, t1, t2):
    qc.cx(qa, t1)
    qc.cx(qb, t1)
    qc.cx(qb, t2)
    qc.cx(qcbit, t2)
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

# Coherencia (marco físico): alineación 4 ejes, sin wt=2
def axis_sign_bit(s_phys: str) -> int:
    b0 = 1 if s_phys[0] == "1" else 0
    b1 = 1 if s_phys[1] == "1" else 0
    b2 = 1 if s_phys[2] == "1" else 0
    b3 = 1 if s_phys[3] == "1" else 0
    return b0 ^ b1 ^ b2 ^ b3

def coherent_string_phys(s_phys: str) -> bool:
    if len(s_phys) != 12:
        return False
    axis0_ok = (s_phys[0] == s_phys[4] == s_phys[8])
    axis1_ok = (s_phys[1] == s_phys[5] == s_phys[9])
    axis2_ok = (s_phys[2] == s_phys[6] == s_phys[10])
    axis3_ok = (s_phys[3] == s_phys[7] == s_phys[11])
    signbit = axis_sign_bit(s_phys)
    sign_ok = (signbit == 1) if SIGN == +1 else (signbit == 0)
    return axis0_ok and axis1_ok and axis2_ok and axis3_ok and sign_ok

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

def list_good_states() -> List[str]:
    goods = []
    for bits in itertools.product("01", repeat=12):
        s = "".join(bits)
        if coherent_string_phys(s):
            goods.append(s)
    return goods

# Circuito: oracle con 4 ejes + axis-sign ±
def build_circuit(iterations: int) -> QuantumCircuit:
    data = QuantumRegister(12, "q")
    eq0 = QuantumRegister(1, "eq0")
    eq1 = QuantumRegister(1, "eq1")
    eq2 = QuantumRegister(1, "eq2")
    eq3 = QuantumRegister(1, "eq3")
    t = QuantumRegister(9, "t")  # 2 por eje (8) + 1 para sign
    ph = QuantumRegister(1, "ph")
    c = ClassicalRegister(12, "c")

    qc = QuantumCircuit(data, eq0, eq1, eq2, eq3, t, ph, c)

    q = data

    qc.h(q)
    qc.x(ph[0])
    qc.h(ph[0])

    for _ in range(iterations):
        # Compute alineaciones (sin wt=2)
        compute_eq_three(qc, q[0], q[4], q[8], eq0[0], t[0], t[1])
        compute_eq_three(qc, q[1], q[5], q[9], eq1[0], t[2], t[3])
        compute_eq_three(qc, q[2], q[6], q[10], eq2[0], t[4], t[5])
        compute_eq_three(qc, q[3], q[7], q[11], eq3[0], t[6], t[7])

        # Compute axis-sign en t[8] = XOR(q0,q1,q2,q3)
        qc.cx(q[0], t[8])
        qc.cx(q[1], t[8])
        qc.cx(q[2], t[8])
        qc.cx(q[3], t[8])

        if SIGN == -1:
            qc.x(t[8])

        # Oracle: mcx con 4 eq + sign
        qc.mcx([eq0[0], eq1[0], eq2[0], eq3[0], t[8]], ph[0])

        # Uncompute sign
        if SIGN == -1:
            qc.x(t[8])
        qc.cx(q[3], t[8])
        qc.cx(q[2], t[8])
        qc.cx(q[1], t[8])
        qc.cx(q[0], t[8])

        # Uncompute alineaciones
        uncompute_eq_three(qc, q[3], q[7], q[11], eq3[0], t[6], t[7])
        uncompute_eq_three(qc, q[2], q[6], q[10], eq2[0], t[4], t[5])
        uncompute_eq_three(qc, q[1], q[5], q[9], eq1[0], t[2], t[3])
        uncompute_eq_three(qc, q[0], q[4], q[8], eq0[0], t[0], t[1])

        grover_diffusion(qc, list(q))

    qc.measure(q, c)
    return qc

def run(shots: int = 4096, iterations: int | None = None, opt_level: int = 1) -> None:
    N = 2 ** 12
    M = count_good_states()
    k_suggested = suggested_grover_iterations(N, M)

    if iterations is None:
        iterations = k_suggested

    sign_label = "+" if SIGN == +1 else "-"
    want = "XOR(q0-3)=1" if SIGN == +1 else "XOR(q0-3)=0"
    print(f"SIGN={sign_label} (axis-sign: {want})")
    print(f"N={N}  M={M}  M/N={M/N:.6f}  k_sugerido≈{k_suggested}  k_usado={iterations}")

    goods = list_good_states()
    print("Estados coherentes (fisico):", len(goods))
    for g in goods:
        print(g, "pattern=", g[0:4], "axis_sign=", axis_sign_bit(g))

    qc = build_circuit(iterations=iterations)

    sim = AerSimulator()
    tqc = transpile(qc, sim, optimization_level=opt_level)
    res = sim.run(tqc, shots=shots).result()
    counts = res.get_counts()

    top10: List[Tuple[str, int]] = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("TOP10:", top10)

    good_shots = sum(v for k, v in counts.items() if coherent_string_measured(k))
    print(f"Shots coherentes: {good_shots} / {shots} = {good_shots/shots:.6f}")

    for s, c in top10:
        s_phys = s[::-1]
        ok = coherent_string_phys(s_phys)
        print(s, c, "phys=", s_phys, "ok=", ok,
              "axis_sign=", axis_sign_bit(s_phys),
              "pattern=", s_phys[0:4])

if __name__ == "__main__":
    SHOTS = 4096
    ITERATIONS = None
    run(shots=SHOTS, iterations=ITERATIONS, opt_level=1)
