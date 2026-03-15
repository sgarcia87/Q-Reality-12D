#!/usr/bin/env python3
from __future__ import annotations

import json
import itertools
from datetime import datetime

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


GOOD_A = {"0001","0010","0100","1000"}


# =========================================================
# Grover components
# =========================================================

def phase_flip_on_pattern(qc, qubits, pattern):

    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(qubits[i])

    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])

    for i, bit in enumerate(pattern):
        if bit == "0":
            qc.x(qubits[i])


def oracle_A_onehot(qc,A):

    for p in GOOD_A:
        phase_flip_on_pattern(qc,A,p)


def diffusion(qc,qubits):

    qc.h(qubits)
    qc.x(qubits)

    qc.h(qubits[-1])
    qc.mcx(qubits[:-1],qubits[-1])
    qc.h(qubits[-1])

    qc.x(qubits)
    qc.h(qubits)


# =========================================================
# Circuit builder
# =========================================================

def build_circuit(k):

    qc=QuantumCircuit(12,12)

    A=[0,1,2,3]
    B=[4,5,6,7]
    C=[8,9,10,11]

    qc.h(A)
    qc.h(B)

    for _ in range(k):
        oracle_A_onehot(qc,A)
        diffusion(qc,A)

    for i in range(4):
        qc.cx(A[i],C[i])
        qc.cx(B[i],C[i])

    qc.measure(range(12),range(12))

    return qc


# =========================================================
# Counts extraction
# =========================================================

def extract_counts(pub_result):

    data=pub_result.data

    if hasattr(data,"meas"):
        return data.meas.get_counts()

    if hasattr(data,"c"):
        return data.c.get_counts()

    for name in dir(data):
        obj=getattr(data,name)
        if hasattr(obj,"get_counts"):
            return obj.get_counts()

    raise RuntimeError("No counts found")


# =========================================================
# Metrics
# =========================================================

def metrics(counts):

    shots=sum(counts.values())

    coherent=0
    axis_correct=0
    A_good=0
    joint=0

    for s,c in counts.items():

        s=s[::-1]

        A=[int(x) for x in s[0:4]]
        B=[int(x) for x in s[4:8]]
        C=[int(x) for x in s[8:12]]

        A_str="".join(str(x) for x in A)

        axis_ok=0

        for i in range(4):
            if (A[i]^B[i])==C[i]:
                axis_ok+=1

        axis_correct+=axis_ok*c

        is_coherent=(axis_ok==4)
        is_A_good=(A_str in GOOD_A)

        if is_coherent:
            coherent+=c

        if is_A_good:
            A_good+=c

        if is_coherent and is_A_good:
            joint+=c

    coherent_rate=coherent/shots
    axis_consistency=axis_correct/(shots*4)
    A_good_rate=A_good/shots
    joint_rate=joint/shots

    return {
        "coherent_rate":coherent_rate,
        "axis_consistency":axis_consistency,
        "A_good_rate":A_good_rate,
        "joint_rate":joint_rate
    }


# =========================================================
# Runner
# =========================================================

def run_case(k,backend):

    qc=build_circuit(k)

    service=QiskitRuntimeService()
    backend=service.backend(backend)

    pm=generate_preset_pass_manager(
        backend=backend,
        optimization_level=1
    )

    isa=pm.run(qc)

    sampler=Sampler(mode=backend)

    job=sampler.run([isa],shots=4096)

    result=job.result()

    counts=extract_counts(result[0])

    m=metrics(counts)

    print("\nk =",k)
    print("job:",job.job_id())
    print(m)

    return {
        "k":k,
        "job_id":job.job_id(),
        "metrics":m
    }


# =========================================================
# Main
# =========================================================

def main():

    backend="ibm_marrakesh"

    print("\nTri-Hipercubo k-sweep experiment")

    results=[]

    for k in [0,1,2]:
        results.append(run_case(k,backend))

    out={
        "backend":backend,
        "results":results
    }

    fname=f"tri_hypercube_k_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(fname,"w") as f:
        json.dump(out,f,indent=2)

    print("\nSaved:",fname)


if __name__=="__main__":
    main()
