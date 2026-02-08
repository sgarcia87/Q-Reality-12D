#!/usr/bin/env python3
"""
quant_v10_4axes_full_vertices_sign_exact_k18.py

Exact amplitude amplification (estilo "Exact Grover"):
- (k-1) iteraciones estándar (pi, pi)
- última iteración con fases (phi_last, varphi_last) ajustadas para P(good)~1

Con M/N=8/4096, k=17 NO puede clavar 1 en este esquema.
Con k=18 sí (en simulación ideal).
"""

from __future__ import annotations

import itertools
import math
import cmath
from typing import List, Tuple, Dict

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

# -----------------------------
# Configuración
# -----------------------------
SIGN = +1
K_FIXED = 18          # <-- clave: 18, no 17
SHOTS = 4096
OPT_LEVEL = 1


# -----------------------------
# Coherencia / estados buenos
# -----------------------------
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

def list_good_states() -> List[str]:
    goods = []
    for bits in itertools.product("01", repeat=12):
        s = "".join(bits)
        if coherent_string_phys(s):
            goods.append(s)
    return goods


# -----------------------------
# eq_three: eq=1 si qa==qb==qcbit
# -----------------------------
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


# -----------------------------
# Oracle con fase: e^{i phi} a good
# -----------------------------
def apply_oracle_phased(qc: QuantumCircuit, controls, ph_qubit, phi_oracle: float):
    qc.mcp(phi_oracle, controls, ph_qubit)


# -----------------------------
# Difusión con fase
# -----------------------------
def grover_diffusion_phased(qc: QuantumCircuit, qubits, phi_diff: float):
    qc.h(qubits)
    qc.x(qubits)
    qc.mcp(phi_diff, qubits[:-1], qubits[-1])
    qc.x(qubits)
    qc.h(qubits)


# ============================================================
# Solver 2D exacto para la ÚLTIMA iteración
# ============================================================
def _matmul2(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
    ]

def _matvec2(A, v):
    return [A[0][0]*v[0] + A[0][1]*v[1], A[1][0]*v[0] + A[1][1]*v[1]]

def Q_matrix(a: float, phi_oracle: float, phi_diff: float):
    s = math.sqrt(a)
    c = math.sqrt(1.0 - a)
    eD = cmath.exp(1j * phi_diff)
    eO = cmath.exp(1j * phi_oracle)

    # |s><s|
    ss00, ss01 = s*s, s*c
    ss10, ss11 = s*c, c*c

    # D(phi_diff) = I + (e^{i phi_diff}-1) |s><s|
    lam = (eD - 1.0)
    D = [
        [1.0 + lam*ss00,      lam*ss01],
        [     lam*ss10, 1.0 + lam*ss11],
    ]

    # O(phi_oracle) = diag(e^{i phi_oracle}, 1)
    O = [
        [eO, 0.0],
        [0.0, 1.0],
    ]

    # Iteración: Q = D * O
    return _matmul2(D, O)

def evolve(a: float, steps: int, phi_oracle: float, phi_diff: float):
    s = math.sqrt(a); c = math.sqrt(1.0 - a)
    v = [s, c]
    Q = Q_matrix(a, phi_oracle, phi_diff)
    for _ in range(steps):
        v = _matvec2(Q, v)
    return v

def find_last_step_phases(a: float, k_fixed: int) -> Tuple[float, float, float, float]:
    """
    (k_fixed-1) iteraciones estándar (pi,pi) y última iteración con (phi_last,varphi_last)
    minimizando |bad|.
    """
    v_pre = evolve(a, k_fixed - 1, math.pi, math.pi)

    two_pi = 2.0 * math.pi
    best_err = None
    best_phi = 0.0
    best_var = 0.0
    best_vf = None

    GRID = 360
    for i in range(GRID):
        phi = two_pi * i / GRID
        for j in range(GRID):
            var = two_pi * j / GRID
            Q = Q_matrix(a, phi, var)
            vf = _matvec2(Q, v_pre)
            err = abs(vf[1])
            if best_err is None or err < best_err:
                best_err, best_phi, best_var, best_vf = err, phi, var, vf

    step = 0.05
    for _ in range(80):
        improved = False
        for dphi in (0.0, step, -step):
            for dvar in (0.0, step, -step):
                phi = (best_phi + dphi) % two_pi
                var = (best_var + dvar) % two_pi
                Q = Q_matrix(a, phi, var)
                vf = _matvec2(Q, v_pre)
                err = abs(vf[1])
                if err < best_err:
                    best_err, best_phi, best_var, best_vf = err, phi, var, vf
                    improved = True
        if not improved:
            step *= 0.5
            if step < 1e-12:
                break

    p_good = abs(best_vf[0])**2
    return best_phi, best_var, float(p_good), float(best_err)


# -----------------------------
# Circuito: (k-1) estándar + última ajustada
# -----------------------------
def build_circuit_exact(iterations: int, phi_oracle_last: float, phi_diff_last: float) -> QuantumCircuit:
    data = QuantumRegister(12, "q")
    eq0 = QuantumRegister(1, "eq0")
    eq1 = QuantumRegister(1, "eq1")
    eq2 = QuantumRegister(1, "eq2")
    eq3 = QuantumRegister(1, "eq3")
    t = QuantumRegister(9, "t")
    ph = QuantumRegister(1, "ph")
    c = ClassicalRegister(12, "c")

    qc = QuantumCircuit(data, eq0, eq1, eq2, eq3, t, ph, c)
    q = data

    qc.h(q)
    qc.x(ph[0])  # ph = |1>

    for it in range(iterations):
        if it == iterations - 1:
            phi_o = phi_oracle_last
            phi_d = phi_diff_last
        else:
            phi_o = math.pi
            phi_d = math.pi

        compute_eq_three(qc, q[0], q[4], q[8],  eq0[0], t[0], t[1])
        compute_eq_three(qc, q[1], q[5], q[9],  eq1[0], t[2], t[3])
        compute_eq_three(qc, q[2], q[6], q[10], eq2[0], t[4], t[5])
        compute_eq_three(qc, q[3], q[7], q[11], eq3[0], t[6], t[7])

        qc.cx(q[0], t[8])
        qc.cx(q[1], t[8])
        qc.cx(q[2], t[8])
        qc.cx(q[3], t[8])

        if SIGN == -1:
            qc.x(t[8])

        apply_oracle_phased(qc, [eq0[0], eq1[0], eq2[0], eq3[0], t[8]], ph[0], phi_o)

        if SIGN == -1:
            qc.x(t[8])
        qc.cx(q[3], t[8])
        qc.cx(q[2], t[8])
        qc.cx(q[1], t[8])
        qc.cx(q[0], t[8])

        uncompute_eq_three(qc, q[3], q[7], q[11], eq3[0], t[6], t[7])
        uncompute_eq_three(qc, q[2], q[6], q[10], eq2[0], t[4], t[5])
        uncompute_eq_three(qc, q[1], q[5], q[9],  eq1[0], t[2], t[3])
        uncompute_eq_three(qc, q[0], q[4], q[8],  eq0[0], t[0], t[1])

        grover_diffusion_phased(qc, list(q), phi_d)

    qc.measure(q, c)
    return qc


def run():
    N = 2**12
    M = count_good_states()
    a = M / N

    print(f"SIGN={'+' if SIGN==1 else '-'}  N={N}  M={M}  a={a:.12f}  k_fijo={K_FIXED}")

    phi_last, var_last, p_theory, bad_theory = find_last_step_phases(a, K_FIXED)
    print("\n[Exact last-step phases]")
    print(f"phi_oracle_last = {phi_last:.12f} rad")
    print(f"phi_diff_last   = {var_last:.12f} rad")
    print(f"P_theory(k={K_FIXED}) ≈ {p_theory:.15f}")
    print(f"|bad|_theory      ≈ {bad_theory:.3e}")

    qc = build_circuit_exact(K_FIXED, phi_last, var_last)
    sim = AerSimulator()
    tqc = transpile(qc, sim, optimization_level=OPT_LEVEL)
    res = sim.run(tqc, shots=SHOTS).result()
    counts = res.get_counts()

    good_shots = sum(v for k, v in counts.items() if coherent_string_measured(k))
    print(f"\nShots coherentes: {good_shots} / {SHOTS} = {good_shots/SHOTS:.6f}")

    bads = {k: v for k, v in counts.items() if not coherent_string_measured(k)}
    if bads:
        print("MALOS:", sorted(bads.items(), key=lambda x: x[1], reverse=True)[:10])
    else:
        print("MALOS: ninguno (100% coherentes en estos shots).")


if __name__ == "__main__":
    run()
