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
# Helpers
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
# Circuits
# =========================================================

def circuit_v1():

    qc=QuantumCircuit(12,12)

    A=[0,1,2,3]
    B=[4,5,6,7]
    C=[8,9,10,11]

    qc.h(A)
    qc.h(B)

    for i in range(4):
        qc.cx(A[i],C[i])
        qc.cx(B[i],C[i])

    qc.measure(range(12),range(12))

    return qc


def circuit_v2():

    qc=QuantumCircuit(12,12)

    A=[0,1,2,3]
    B=[4,5,6,7]
    C=[8,9,10,11]

    qc.h(A)
    qc.h(B)

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
        "shots":shots,
        "coherent_rate":coherent_rate,
        "axis_consistency":axis_consistency,
        "A_good_rate":A_good_rate,
        "joint_rate":joint_rate
    }


# =========================================================
# Run case
# =========================================================

def run_case(name,qc,backend_name):

    service=QiskitRuntimeService()
    backend=service.backend(backend_name)

    pm=generate_preset_pass_manager(backend=backend,optimization_level=1)
    isa=pm.run(qc)

    sampler=Sampler(mode=backend)

    job=sampler.run([isa],shots=4096)

    result=job.result()

    counts=extract_counts(result[0])

    m=metrics(counts)

    print("\n",name)
    print("job:",job.job_id())
    print(m)

    return m


# =========================================================
# Main
# =========================================================

def main():

    backend="ibm_marrakesh"

    print("\nTri-Hipercubo Benchmark v1 vs v2")

    v1=run_case("v1",circuit_v1(),backend)
    v2=run_case("v2",circuit_v2(),backend)

    baseline_A=0.25

    gain_A=v2["A_good_rate"]/baseline_A

    baseline_joint=v1["coherent_rate"]*baseline_A

    P_coherent_given_A=v2["joint_rate"]/v2["A_good_rate"]
    P_A_given_coherent=v2["joint_rate"]/v2["coherent_rate"]

    print("\n==============================")
    print("Derived metrics")
    print("==============================")

    print("baseline_A =",baseline_A)
    print("gain_A =",gain_A)

    print("baseline_joint =",baseline_joint)

    print("P(coherent|A_good) =",P_coherent_given_A)
    print("P(A_good|coherent) =",P_A_given_coherent)

    out={
        "backend":backend,
        "v1":v1,
        "v2":v2,
        "baseline_A":baseline_A,
        "gain_A":gain_A,
        "baseline_joint":baseline_joint,
        "P_coherent_given_A":P_coherent_given_A,
        "P_A_given_coherent":P_A_given_coherent
    }

    fname=f"tri_hypercube_v1_v2_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(fname,"w") as f:
        json.dump(out,f,indent=2)

    print("\nSaved:",fname)


if __name__=="__main__":
    main()
