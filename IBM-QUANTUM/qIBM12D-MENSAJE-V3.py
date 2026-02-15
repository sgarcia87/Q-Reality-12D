#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error, ReadoutError

from qiskit_ibm_runtime import QiskitRuntimeService, Sampler


# ----------------------------
# Metrics
# ----------------------------
def hamming(a: str, b: str) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)

def compute_metrics(counts: Dict[str, int], msg: str) -> Dict[str, Any]:
    shots = sum(counts.values()) or 1

    # choose global orientation (msg vs msg[::-1]) that maximizes exact matches
    exact1 = counts.get(msg, 0)
    exact2 = counts.get(msg[::-1], 0)
    target = msg if exact1 >= exact2 else msg[::-1]

    exact = counts.get(target, 0)
    exact_match_rate = exact / shots

    total_hd = sum(hamming(k, target) * v for k, v in counts.items())
    ber = total_hd / (shots * 12.0)

    hist = defaultdict(int)
    for k, v in counts.items():
        hist[hamming(k, target)] += v
    hist = dict(sorted(hist.items(), key=lambda x: x[0]))

    top10 = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "shots": int(shots),
        "target_used_for_compare": target,
        "exact_match_rate": float(exact_match_rate),
        "bit_error_rate": float(ber),
        "hamming_histogram": hist,
        "top10": top10,
    }


# ----------------------------
# Circuit: encode 12-bit message
# ----------------------------
def build_message_circuit(msg: str) -> QuantumCircuit:
    if len(msg) != 12 or any(c not in "01" for c in msg):
        raise ValueError("msg must be a 12-bit string like 010011001010")

    qc = QuantumCircuit(12, 12)
    for i, bit in enumerate(msg):
        if bit == "1":
            qc.x(i)
    qc.measure(range(12), range(12))
    return qc


# ----------------------------
# Aer noise model
# ----------------------------
def build_noise_model(p_bitflip: float, p_phaseflip: float, p_readout: float) -> NoiseModel:
    nm = NoiseModel()

    if p_bitflip > 0 or p_phaseflip > 0:
        pI = max(0.0, 1.0 - p_bitflip - p_phaseflip)
        channel = [("I", pI)]
        if p_bitflip > 0:
            channel.append(("X", p_bitflip))
        if p_phaseflip > 0:
            channel.append(("Z", p_phaseflip))
        err = pauli_error(channel)
        nm.add_all_qubit_quantum_error(err, ["x"])

    if p_readout > 0:
        ro = ReadoutError([[1 - p_readout, p_readout],
                           [p_readout, 1 - p_readout]])
        nm.add_all_qubit_readout_error(ro)

    return nm


def run_aer(msg: str, shots: int, p_bitflip: float, p_phaseflip: float, p_readout: float) -> Tuple[Dict[str, int], Dict[str, Any]]:
    qc = build_message_circuit(msg)
    nm = build_noise_model(p_bitflip, p_phaseflip, p_readout)
    sim = AerSimulator(noise_model=nm)
    res = sim.run(qc, shots=shots).result()
    counts = res.get_counts()
    metrics = compute_metrics(counts, msg)

    meta = {
        "platform": "aer",
        "noise": {"bitflip": p_bitflip, "phaseflip": p_phaseflip, "readout": p_readout},
    }
    return counts, {"meta": meta, "metrics": metrics}


# ----------------------------
# IBM helpers
# ----------------------------
def _bitarray_to_counts(bitarr) -> Dict[str, int]:
    if hasattr(bitarr, "get_counts"):
        return bitarr.get_counts()
    if hasattr(bitarr, "get_bitstrings"):
        return dict(Counter(bitarr.get_bitstrings()))
    raise RuntimeError("Cannot extract counts from BitArray")

def _backend_readout_score(props, q: int) -> float:
    """
    Try to extract a readout error score for qubit q from backend properties.
    If unavailable, return inf.
    """
    try:
        qp = props.qubits[q]
        # Qiskit backend properties often include "readout_error"
        for item in qp:
            if getattr(item, "name", None) == "readout_error":
                return float(item.value)
        # Sometimes 'prob_meas0_prep1' / 'prob_meas1_prep0' exist
        e01 = e10 = None
        for item in qp:
            if getattr(item, "name", None) == "prob_meas1_prep0":
                e01 = float(item.value)
            if getattr(item, "name", None) == "prob_meas0_prep1":
                e10 = float(item.value)
        if e01 is not None and e10 is not None:
            return 0.5 * (e01 + e10)
    except Exception:
        pass
    return float("inf")

def choose_layout_best_readout(backend, n: int = 12) -> Optional[List[int]]:
    """
    Choose n physical qubits with best (lowest) readout score.
    Returns list of physical qubit indices, or None if properties missing.
    """
    try:
        props = backend.properties()
        scores = []
        for q in range(backend.num_qubits):
            s = _backend_readout_score(props, q)
            scores.append((s, q))
        scores.sort(key=lambda x: x[0])
        picked = [q for _, q in scores[:n]]
        # If all inf, properties didn't help
        if all(not np.isfinite(s) for s, _ in scores[:n]):
            return None
        return picked
    except Exception:
        return None


# ----------------------------
# Readout mitigation (independent per-qubit)
# ----------------------------
def _marginal_p1(counts: Dict[str, int], bit_index_from_right: int) -> float:
    """
    Given counts with keys like '0101...', compute marginal P(bit=1)
    where bit_index_from_right=0 refers to the rightmost char of the string.
    (This matches typical Qiskit bitstring conventions.)
    """
    shots = sum(counts.values()) or 1
    ones = 0
    for s, c in counts.items():
        if len(s) <= bit_index_from_right:
            continue
        if s[-1 - bit_index_from_right] == "1":
            ones += c
    return ones / shots

def build_readout_calibration(
    backend,
    sampler: Sampler,
    layout: Optional[List[int]],
    opt_level: int,
    shots: int,
) -> List[np.ndarray]:
    """
    Build per-qubit 2x2 readout confusion matrices A_i such that:
      p_meas = A_i @ p_true
    using two calibration circuits per qubit: prep 0 and prep 1.

    Returns list of 12 matrices (np.ndarray shape (2,2)).
    """
    mats: List[np.ndarray] = []

    for i in range(12):
        # prep |0...0> (no X)
        qc0 = QuantumCircuit(12, 12)
        qc0.measure(range(12), range(12))

        # prep |...1...> on logical qubit i
        qc1 = QuantumCircuit(12, 12)
        qc1.x(i)
        qc1.measure(range(12), range(12))

        tqc0 = transpile(qc0, backend=backend, optimization_level=opt_level, initial_layout=layout)
        tqc1 = transpile(qc1, backend=backend, optimization_level=opt_level, initial_layout=layout)

        job0 = sampler.run([tqc0], shots=shots)
        job1 = sampler.run([tqc1], shots=shots)

        r0 = job0.result()
        r1 = job1.result()
        c0 = _bitarray_to_counts(r0[0].data.c)
        c1 = _bitarray_to_counts(r1[0].data.c)

        # estimate readout flip probabilities for this bit position
        # e01 = P(meas=1 | prep=0), e10 = P(meas=0 | prep=1)
        p1_prep0 = _marginal_p1(c0, bit_index_from_right=i)
        p1_prep1 = _marginal_p1(c1, bit_index_from_right=i)
        e01 = p1_prep0
        e10 = 1.0 - p1_prep1

        # Forward matrix A
        # meas0 = (1-e01)*true0 + e10*true1
        # meas1 = e01*true0 + (1-e10)*true1
        A = np.array([[1.0 - e01, e10],
                      [e01, 1.0 - e10]], dtype=float)
        mats.append(A)

    return mats

def mitigate_counts_independent_readout(counts: Dict[str, int], mats: List[np.ndarray]) -> Dict[str, int]:
    """
    Apply independent per-qubit readout mitigation:
      p_true ≈ (A_0^-1 ⊗ ... ⊗ A_11^-1) p_meas
    where p_meas is derived from counts.

    Returns "corrected counts" as integers (renormalized to original shots).
    """
    shots = sum(counts.values()) or 1
    n = 12
    dim = 2 ** n

    # Build probability vector p_meas over all 12-bit strings
    p = np.zeros(dim, dtype=float)
    for s, c in counts.items():
        if len(s) != n:
            continue
        idx = int(s, 2)
        p[idx] += c / shots

    # reshape to tensor (2,)*n with axis order matching bitstring msb->lsb
    # Our idx=int(s,2) uses msb->lsb. We'll apply mitigation on axes in the same order.
    P = p.reshape([2] * n)

    # Apply inverse per axis
    for axis in range(n):
        A = mats[axis]
        try:
            Ainv = np.linalg.inv(A)
        except np.linalg.LinAlgError:
            Ainv = np.linalg.pinv(A)

        # tensordot applies on axis; keep dims
        P = np.tensordot(Ainv, P, axes=([1], [axis]))
        # tensordot brings new axis to front; move it back to original position
        P = np.moveaxis(P, 0, axis)

    p_true = P.reshape(dim)
    # clip small negatives due to inversion noise
    p_true = np.clip(p_true, 0.0, None)
    # renormalize
    ssum = p_true.sum()
    if ssum > 0:
        p_true /= ssum

    # back to counts
    corrected = {}
    for idx in range(dim):
        c = int(round(p_true[idx] * shots))
        if c > 0:
            corrected[format(idx, "012b")] = c

    # Fix total shots (rounding)
    diff = shots - sum(corrected.values())
    if diff != 0:
        # adjust the max bin
        if corrected:
            kmax = max(corrected.items(), key=lambda x: x[1])[0]
            corrected[kmax] = max(0, corrected[kmax] + diff)

    return corrected


# ----------------------------
# IBM run (optionally with best_readout layout + mitigation)
# ----------------------------
def run_ibm(
    msg: str,
    shots: int,
    backend_name: str,
    opt_level: int,
    layout_mode: str,
    mitigate_readout: bool,
    cal_shots: int,
) -> Tuple[Dict[str, int], Dict[str, Any]]:
    qc = build_message_circuit(msg)

    service = QiskitRuntimeService()
    backend = service.backend(backend_name)

    layout: Optional[List[int]] = None
    if layout_mode == "best_readout":
        layout = choose_layout_best_readout(backend, n=12)
    elif layout_mode not in ("none", ""):
        # parse "0,1,2,..."
        layout = [int(x.strip()) for x in layout_mode.split(",") if x.strip() != ""]

    sampler = Sampler(mode=backend)

    tqc = transpile(qc, backend=backend, optimization_level=opt_level, initial_layout=layout)
    job = sampler.run([tqc], shots=shots)
    result = job.result()
    counts = _bitarray_to_counts(result[0].data.c)

    raw_metrics = compute_metrics(counts, msg)

    meta = {
        "platform": "ibm",
        "backend": backend.name,
        "opt_level": opt_level,
        "layout_mode": layout_mode,
        "layout_used": layout,
        "job_id": job.job_id(),
    }

    if not mitigate_readout:
        return counts, {"meta": meta, "metrics": raw_metrics}

    # Calibration + mitigation
    mats = build_readout_calibration(
        backend=backend,
        sampler=sampler,
        layout=layout,
        opt_level=opt_level,
        shots=cal_shots,
    )
    corrected_counts = mitigate_counts_independent_readout(counts, mats)
    corrected_metrics = compute_metrics(corrected_counts, msg)

    meta["readout_mitigation"] = {
        "method": "independent_per_qubit_matrix_inversion",
        "cal_shots": cal_shots,
    }

    return corrected_counts, {"meta": meta, "metrics": corrected_metrics, "raw_metrics": raw_metrics}


# ----------------------------
# Main
# ----------------------------
def main():
    ap = argparse.ArgumentParser(description="12D message test on Aer (noise model) or IBM Quantum hardware.")
    ap.add_argument("--msg", required=True, help="12-bit string, e.g. 010011001010")
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--platform", choices=["aer", "ibm"], default="aer")

    # IBM options
    ap.add_argument("--backend", default="ibm_torino", help="IBM backend name (single)")
    ap.add_argument("--backends", default="", help="Comma-separated IBM backends (overrides --backend)")
    ap.add_argument("--opt_level", type=int, default=1)
    ap.add_argument("--layout", default="none", help="none | best_readout | '0,1,2,...'")

    ap.add_argument("--mitigate_readout", action="store_true")
    ap.add_argument("--cal_shots", type=int, default=2048, help="shots per calibration circuit (IBM)")

    # Aer noise
    ap.add_argument("--p_bitflip", type=float, default=0.0)
    ap.add_argument("--p_phaseflip", type=float, default=0.0)
    ap.add_argument("--p_readout", type=float, default=0.0)

    ap.add_argument("--save_json", action="store_true")

    args = ap.parse_args()

    msg = args.msg.strip()
    shots = args.shots

    if args.platform == "aer":
        counts, out = run_aer(msg, shots, args.p_bitflip, args.p_phaseflip, args.p_readout)
        meta = out["meta"]
        m = out["metrics"]
        print(f"msg: {msg}")
        print(f"shots: {shots}")
        n = meta["noise"]
        print(f"noise: bitflip={n['bitflip']} phaseflip={n['phaseflip']} readout={n['readout']}")
        print(f"target_used_for_compare: {m['target_used_for_compare']}")
        print(f"exact_match_rate: {m['exact_match_rate']:.6f}")
        print(f"bit_error_rate:   {m['bit_error_rate']:.6f}")
        print(f"hamming_histogram (dist->count): {m['hamming_histogram']}")
        print(f"top10: {m['top10']}")

        if args.save_json:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"results_qIBM12D_MENSAJE_aer_{ts}.json"
            payload = {"msg": msg, **meta, **m}
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            print(f"\nSaved: {fname}")
        return

    # IBM: maybe multiple backends
    bnames = []
    if args.backends.strip():
        bnames = [b.strip() for b in args.backends.split(",") if b.strip()]
    else:
        bnames = [args.backend]

    rows = []
    saved_files = []

    for bname in bnames:
        counts, out = run_ibm(
            msg=msg,
            shots=shots,
            backend_name=bname,
            opt_level=args.opt_level,
            layout_mode=args.layout,
            mitigate_readout=args.mitigate_readout,
            cal_shots=args.cal_shots,
        )
        meta = out["meta"]
        m = out["metrics"]

        print(f"\nbackend: {meta['backend']}  job_id: {meta['job_id']}")
        if "raw_metrics" in out:
            rm = out["raw_metrics"]
            print(f"raw exact_match_rate: {rm['exact_match_rate']:.6f}  raw BER: {rm['bit_error_rate']:.6f}")
            print(f"mitigated exact_match_rate: {m['exact_match_rate']:.6f}  mitigated BER: {m['bit_error_rate']:.6f}")
        else:
            print(f"exact_match_rate: {m['exact_match_rate']:.6f}  BER: {m['bit_error_rate']:.6f}")

        rows.append((meta["backend"], m["exact_match_rate"], m["bit_error_rate"], m["target_used_for_compare"]))

        if args.save_json:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"results_qIBM12D_MENSAJE_ibm_{meta['backend']}_{ts}.json"
            payload = {"msg": msg, **meta, **m}
            if "raw_metrics" in out:
                payload["raw_metrics"] = out["raw_metrics"]
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            saved_files.append(fname)

    # Summary table
    print("\n=== SUMMARY ===")
    for backend, ex, ber, tgt in rows:
        print(f"{backend:<14}  exact={ex:.4f}  BER={ber:.4f}  target={tgt}")

    if saved_files:
        print("\nSaved JSON:")
        for f in saved_files:
            print(f" - {f}")


if __name__ == "__main__":
    main()
