#!/usr/bin/env python3
# mezcla entre el 3.3 y el 3.6
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
# Relaciones XOR (v3.6)
# =========================================================
def write_xor(qc: QuantumCircuit, a: int, b: int, target: int):
    qc.cx(a, target)
    qc.cx(b, target)


def compute_relations(qc: QuantumCircuit, base, rel1, rel2):
    b0, b1, b2, b3 = base
    r10, r11, r12, r13 = rel1
    r20, r21, r22, r23 = rel2

    # rel1 vecinos
    write_xor(qc, b0, b1, r10)
    write_xor(qc, b1, b2, r11)
    write_xor(qc, b2, b3, r12)
    write_xor(qc, b3, b0, r13)

    # rel2 cruzados
    write_xor(qc, b0, b2, r20)
    write_xor(qc, b1, b3, r21)
    write_xor(qc, b0, b3, r22)
    write_xor(qc, b1, b2, r23)


# =========================================================
# Circuito v3.7 (12 qubits)
# q0..q3  : base (núcleo)
# q4..q7  : bit_copy (copia bit a bit del núcleo)
# q8..q11 : relations (XORs desde el núcleo)
# =========================================================
def make_circuit(sign: int, grover_iters: int) -> QuantumCircuit:
    qc = QuantumCircuit(12, 12)

    base = [0, 1, 2, 3]
    bitcopy = [4, 5, 6, 7]
    rel1 = [8, 9, 10, 11]   # usamos solo 4 qubits para rel1 (vecinos)
    # Nota: para no añadir más qubits, en v3.7 solo guardamos rel1 (4 relaciones).
    # Si quieres rel1+rel2 como en v3.6, necesitaríamos 16 qubits. Aquí priorizamos 12.

    qc.h(base)

    # Grover en núcleo
    for _ in range(grover_iters):
        apply_oracle(qc, base, sign)
        diffusion(qc, base)

    # Propagar después:
    # 1) copia bit a bit
    for i in range(4):
        qc.cx(base[i], bitcopy[i])

    # 2) relaciones (vecinos)
    b0, b1, b2, b3 = base
    r0, r1q, r2q, r3q = rel1
    write_xor(qc, b0, b1, r0)
    write_xor(qc, b1, b2, r1q)
    write_xor(qc, b2, b3, r2q)
    write_xor(qc, b3, b0, r3q)

    qc.measure(range(12), range(12))
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
# Métricas
# - P_good_base: base en good-set
# - bit-copy coherence: exact_axes y parity_axes entre base y copia (2 bloques)
# - relation consistency: rel bits coinciden con XOR(base) (4 relaciones)
# Robustez a inversión global: probamos s y s[::-1] y elegimos mejor.
# =========================================================
def _bits_to_int(ch: str) -> int:
    return 1 if ch == "1" else 0


def _eval_orientation(s: str, sign: int) -> Tuple[float, float, float, int]:
    """
    Devuelve:
      (bit_exact_axes, bit_parity_axes, rel_consistency, good_base_flag)
    """
    if len(s) != 12:
        return (0.0, 0.0, 0.0, 0)

    base = s[0:4]
    copy = s[4:8]
    rel = s[8:12]

    b = [_bits_to_int(x) for x in base]
    c = [_bits_to_int(x) for x in copy]
    r = [_bits_to_int(x) for x in rel]

    # bit-copy exact axes: % i donde base[i]==copy[i]
    exact = sum(1 for i in range(4) if base[i] == copy[i]) / 4.0

    # bit-copy parity axes: % i donde XOR(base[i],copy[i])==0 (equivalente a igualdad)
    parity = sum(1 for i in range(4) if ((b[i] ^ c[i]) == 0)) / 4.0

    # relaciones esperadas (vecinos)
    rel_exp = [b[0]^b[1], b[1]^b[2], b[2]^b[3], b[3]^b[0]]
    relc = sum(1 for i in range(4) if r[i] == rel_exp[i]) / 4.0

    good = 1 if base in good_patterns(sign) else 0
    return (exact, parity, relc, good)


def analyze_counts(counts: Dict[str, int], sign: int) -> Dict[str, float]:
    shots = sum(counts.values()) or 1
    sum_exact = 0.0
    sum_parity = 0.0
    sum_rel = 0.0
    sum_good = 0

    for bs, c in counts.items():
        a = _eval_orientation(bs, sign)
        b = _eval_orientation(bs[::-1], sign)

        # elegimos orientación que maximiza rel_consistency; si empata, maximiza exact; luego good
        (ex1, pa1, rc1, g1) = a
        (ex2, pa2, rc2, g2) = b
        if (rc2 > rc1) or (rc2 == rc1 and ex2 > ex1) or (rc2 == rc1 and ex2 == ex1 and g2 > g1):
            ex, pa, rc, g = ex2, pa2, rc2, g2
        else:
            ex, pa, rc, g = ex1, pa1, rc1, g1

        sum_exact += ex * c
        sum_parity += pa * c
        sum_rel += rc * c
        sum_good += g * c

    return {
        "shots": shots,
        "P_good_base": sum_good / shots,
        "avg_bit_exact": sum_exact / shots,
        "avg_bit_parity": sum_parity / shots,
        "avg_rel_consistency": sum_rel / shots,
    }


# =========================================================
# Runner v3.7 (4 casos: sign± × k=0/1)
# =========================================================
def run_v37(
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
        "variant": "v3.7 (amplify nucleus + propagate bit-copy + propagate relations)",
        "cases": [],
    }

    print("Backend:", backend.name)
    print(f"shots={shots}  opt_level={optimization_level}")
    print("Total casos: 4 (sign± × k=0/1)")

    for sign in (+1, -1):
        for k in (0, 1):
            label = f"sign={sign:+d} | hybrid(bits+relations) | k={k}"
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
                f"rel={m['avg_rel_consistency']:.4f}"
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
    print("RESUMEN (v3.7)")
    print("#" * 72)
    for c in out["cases"]:
        m = c["metrics"]
        print(f"{c['label']:<34} | "
              f"P_good_base={m['P_good_base']:.4f} | "
              f"bit_exact={m['avg_bit_exact']:.4f} | "
              f"rel={m['avg_rel_consistency']:.4f} | "
              f"depth={c['compiled']['depth']}")

    filename = f"results_qIBM_v3_7_{backend.name}_{ts}.json"
    if save_json:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print("\nGuardado:", filename)

    return filename


if __name__ == "__main__":
    run_v37(
        backend_name="ibm_torino",
        shots=4096,
        optimization_level=1,
        save_json=True,
    )
