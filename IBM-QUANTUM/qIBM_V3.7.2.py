#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Tuple, Any
from collections import Counter
import itertools

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


# =========================================================
# Good set (peso completo, como v3.3)
# =========================================================
def good_patterns(sign: int):
    goods = []
    for bits in itertools.product("01", repeat=4):
        s = "".join(bits)
        wt = s.count("1")
        if sign == +1 and wt == 1:
            goods.append(s)
        if sign == -1 and wt == 3:
            goods.append(s)
    return set(goods)


# =========================================================
# Grover en 4 qubits base (MCZ via H + MCX + H)
# =========================================================
def phase_flip_on_pattern(qc: QuantumCircuit, base, pattern: str):
    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(base[i])

    qc.h(base[3])
    qc.mcx(base[:3], base[3])
    qc.h(base[3])

    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(base[i])


def apply_oracle(qc: QuantumCircuit, base, sign: int):
    for pat in good_patterns(sign):
        phase_flip_on_pattern(qc, base, pat)


def diffusion(qc: QuantumCircuit, base):
    qc.h(base)
    qc.x(base)
    qc.h(base[3])
    qc.mcx(base[:3], base[3])
    qc.h(base[3])
    qc.x(base)
    qc.h(base)


# =========================================================
# Relaciones XOR
# =========================================================
def write_xor(qc: QuantumCircuit, a: int, b: int, target: int):
    qc.cx(a, target)
    qc.cx(b, target)


def compute_rel1_neighbors(qc: QuantumCircuit, base, rel1):
    b0, b1, b2, b3 = base
    r0, r1, r2, r3 = rel1
    write_xor(qc, b0, b1, r0)  # q0^q1
    write_xor(qc, b1, b2, r1)  # q1^q2
    write_xor(qc, b2, b3, r2)  # q2^q3
    write_xor(qc, b3, b0, r3)  # q3^q0


def compute_rel2_cross(qc: QuantumCircuit, base, rel2):
    b0, b1, b2, b3 = base
    r0, r1, r2, r3 = rel2
    write_xor(qc, b0, b2, r0)  # q0^q2
    write_xor(qc, b1, b3, r1)  # q1^q3
    write_xor(qc, b0, b3, r2)  # q0^q3
    write_xor(qc, b1, b2, r3)  # q1^q2


# =========================================================
# Circuito v3.7 full (16 qubits)
# q0..q3   : base
# q4..q7   : bitcopy
# q8..q11  : rel1 (vecinos)
# q12..q15 : rel2 (cruzados)
# =========================================================
def make_circuit(sign: int, grover_iters: int) -> QuantumCircuit:
    qc = QuantumCircuit(16, 16)

    base = [0, 1, 2, 3]
    bitcopy = [4, 5, 6, 7]
    rel1 = [8, 9, 10, 11]
    rel2 = [12, 13, 14, 15]

    qc.h(base)

    for _ in range(grover_iters):
        apply_oracle(qc, base, sign)
        diffusion(qc, base)

    # Propagación al final (copy_after)
    for i in range(4):
        qc.cx(base[i], bitcopy[i])

    compute_rel1_neighbors(qc, base, rel1)
    compute_rel2_cross(qc, base, rel2)

    qc.measure(range(16), range(16))
    return qc


# =========================================================
# Lectura counts (BitArray)
# =========================================================
def bitarray_to_counts(bitarr) -> Dict[str, int]:
    if hasattr(bitarr, "get_counts"):
        return bitarr.get_counts()
    if hasattr(bitarr, "get_bitstrings"):
        return dict(Counter(bitarr.get_bitstrings()))
    raise RuntimeError("No sé extraer counts del BitArray")


# =========================================================
# Métricas (robusto a inversión global)
# =========================================================
def _b(ch: str) -> int:
    return 1 if ch == "1" else 0


def _eval_orientation(s: str, sign: int) -> Tuple[float, float, float, float, int]:
    """
    Devuelve:
      (bit_exact, rel1_cons, rel2_cons, rel_avg, good_flag)
    """
    if len(s) != 16:
        return (0.0, 0.0, 0.0, 0.0, 0)

    base = s[0:4]
    copy = s[4:8]
    rel1 = s[8:12]
    rel2 = s[12:16]

    b = [_b(x) for x in base]
    r1 = [_b(x) for x in rel1]
    r2 = [_b(x) for x in rel2]

    bit_exact = sum(1 for i in range(4) if base[i] == copy[i]) / 4.0

    rel1_exp = [b[0]^b[1], b[1]^b[2], b[2]^b[3], b[3]^b[0]]
    rel2_exp = [b[0]^b[2], b[1]^b[3], b[0]^b[3], b[1]^b[2]]

    rel1_cons = sum(1 for i in range(4) if r1[i] == rel1_exp[i]) / 4.0
    rel2_cons = sum(1 for i in range(4) if r2[i] == rel2_exp[i]) / 4.0
    rel_avg = 0.5 * (rel1_cons + rel2_cons)

    good = 1 if base in good_patterns(sign) else 0
    return (bit_exact, rel1_cons, rel2_cons, rel_avg, good)


def analyze_counts(counts: Dict[str, int], sign: int) -> Dict[str, float]:
    shots = sum(counts.values()) or 1
    sum_bit = 0.0
    sum_r1 = 0.0
    sum_r2 = 0.0
    sum_ra = 0.0
    sum_good = 0

    for bs, c in counts.items():
        a = _eval_orientation(bs, sign)
        b = _eval_orientation(bs[::-1], sign)

        # Elegimos orientación que maximiza rel_avg; si empata, maximiza bit_exact; luego good
        (be1, r11, r21, ra1, g1) = a
        (be2, r12, r22, ra2, g2) = b
        if (ra2 > ra1) or (ra2 == ra1 and be2 > be1) or (ra2 == ra1 and be2 == be1 and g2 > g1):
            be, r1c, r2c, rac, g = be2, r12, r22, ra2, g2
        else:
            be, r1c, r2c, rac, g = be1, r11, r21, ra1, g1

        sum_bit += be * c
        sum_r1 += r1c * c
        sum_r2 += r2c * c
        sum_ra += rac * c
        sum_good += g * c

    return {
        "shots": shots,
        "P_good_base": sum_good / shots,
        "avg_bit_exact": sum_bit / shots,
        "avg_rel1_consistency": sum_r1 / shots,
        "avg_rel2_consistency": sum_r2 / shots,
        "avg_rel_consistency": sum_ra / shots,
    }


# =========================================================
# Runner v3.7 full (4 casos: sign± × k=0/1)
# =========================================================
def run_v37_full(
    backend_name: str = "ibm_torino",
    shots: int = 4096,
    optimization_level: int = 1,
    save_json: bool = True,
) -> str:
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    sampler = Sampler(mode=backend)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out: Dict[str, Any] = {
        "timestamp": ts,
        "backend": backend.name,
        "shots": shots,
        "optimization_level": optimization_level,
        "variant": "v3.7 full (16q): nucleus + bitcopy + rel1 + rel2",
        "cases": [],
    }

    print("Backend:", backend.name)
    print(f"shots={shots}  opt_level={optimization_level}")
    print("Total casos: 4 (sign± × k=0/1)")

    for sign in (+1, -1):
        for k in (0, 1):
            label = f"sign={sign:+d} | v3.7_full | k={k}"
            qc = make_circuit(sign=sign, grover_iters=k)

            pm = generate_preset_pass_manager(backend=backend, optimization_level=optimization_level)
            isa = pm.run(qc)

            print("\n" + "=" * 60)
            print(label)
            print("Depth:", isa.depth(), "Ops:", isa.count_ops())

            job = sampler.run([isa], shots=shots)
            res = job.result()
            counts = bitarray_to_counts(res[0].data.c)
            m = analyze_counts(counts, sign)

            print(
                f"job={job.job_id()}  "
                f"P_good_base={m['P_good_base']:.4f}  "
                f"bit_exact={m['avg_bit_exact']:.4f}  "
                f"rel1={m['avg_rel1_consistency']:.4f}  "
                f"rel2={m['avg_rel2_consistency']:.4f}  "
                f"rel_avg={m['avg_rel_consistency']:.4f}"
            )

            out["cases"].append({
                "label": label,
                "sign": sign,
                "k": k,
                "compiled": {
                    "depth": isa.depth(),
                    "ops": {str(op): int(n) for op, n in isa.count_ops().items()},
                },
                "job_id": job.job_id(),
                "metrics": m,
            })

    print("\n" + "#" * 72)
    print("RESUMEN (v3.7 full)")
    print("#" * 72)
    for c in out["cases"]:
        m = c["metrics"]
        print(f"{c['label']:<22} | "
              f"P_good_base={m['P_good_base']:.4f} | "
              f"bit_exact={m['avg_bit_exact']:.4f} | "
              f"rel_avg={m['avg_rel_consistency']:.4f} "
              f"(rel1={m['avg_rel1_consistency']:.4f}, rel2={m['avg_rel2_consistency']:.4f}) | "
              f"depth={c['compiled']['depth']}")

    filename = f"results_qIBM_v3_7_full_{backend.name}_{ts}.json"
    if save_json:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print("\nGuardado:", filename)

    return filename


if __name__ == "__main__":
    run_v37_full(
        backend_name="ibm_torino",
        shots=4096,
        optimization_level=1,
        save_json=True,
    )
