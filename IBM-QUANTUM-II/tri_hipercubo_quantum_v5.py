#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


ONE_HOT = {"0001","0010","0100","1000"}
TWO_HOT = {"1100","0011","1010","0101","1001","0110"}


# -------------------------------------------------
# Oracle helper
# -------------------------------------------------

def phase_flip(qc, qubits, pattern):

    for i,bit in enumerate(pattern):
        if bit=="0":
            qc.x(qubits[i])

    qc.h(qubits[-1])
    qc.mcx(qubits[:-1],qubits[-1])
    qc.h(qubits[-1])

    for i,bit in enumerate(pattern):
        if bit=="0":
            qc.x(qubits[i])


def oracle(qc,A,patterns):

    for p in patterns:
        phase_flip(qc,A,p)


def diffusion(qc,qubits):

    qc.h(qubits)
    qc.x(qubits)

    qc.h(qubits[-1])
    qc.mcx(qubits[:-1],qubits[-1])
    qc.h(qubits[-1])

    qc.x(qubits)
    qc.h(qubits)


# -------------------------------------------------
# Circuit builder
# -------------------------------------------------

def build_circuit(patterns):

    qc=QuantumCircuit(12,12)

    A=[0,1,2,3]
    B=[4,5,6,7]
    C=[8,9,10,11]

    qc.h(A)
    qc.h(B)

    oracle(qc,A,patterns)
    diffusion(qc,A)

    for i in range(4):
        qc.cx(A[i],C[i])
        qc.cx(B[i],C[i])

    qc.measure(range(12),range(12))

    return qc


# -------------------------------------------------
# Metrics
# -------------------------------------------------

def extract_counts(pub):

    data=pub.data

    if hasattr(data,"meas"):
        return data.meas.get_counts()

    if hasattr(data,"c"):
        return data.c.get_counts()

    for name in dir(data):
        obj=getattr(data,name)
        if hasattr(obj,"get_counts"):
            return obj.get_counts()

    raise RuntimeError("counts not found")


def metrics(counts,goodA):

    shots=sum(counts.values())

    coherent=0
    axis=0
    good=0
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

        axis+=axis_ok*c

        is_coherent=(axis_ok==4)
        is_good=(A_str in goodA)

        if is_coherent:
            coherent+=c

        if is_good:
            good+=c

        if is_coherent and is_good:
            joint+=c

    return {
        "coherent_rate":coherent/shots,
        "axis_consistency":axis/(shots*4),
        "A_good_rate":good/shots,
        "joint_rate":joint/shots
    }


# -------------------------------------------------
# Runner
# -------------------------------------------------

def run_case(name,patterns,backend):

    qc=build_circuit(patterns)

    service=QiskitRuntimeService()
    backend=service.backend(backend)

    pm=generate_preset_pass_manager(backend=backend,optimization_level=1)
    isa=pm.run(qc)

    sampler=Sampler(mode=backend)

    job=sampler.run([isa],shots=4096)

    res=job.result()

    counts=extract_counts(res[0])

    m=metrics(counts,patterns)

    print("\n",name)
    print("job:",job.job_id())
    print(m)

    return m


# -------------------------------------------------

def main():

    backend="ibm_marrakesh"

    print("\nTri-Hipercubo: one-hot vs two-hot")

    one=run_case("one_hot",ONE_HOT,backend)
    two=run_case("two_hot",TWO_HOT,backend)

    out={
        "backend":backend,
        "one_hot":one,
        "two_hot":two
    }

    fname=f"tri_hypercube_onehot_vs_twohot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(fname,"w") as f:
        json.dump(out,f,indent=2)

    print("\nSaved:",fname)


if __name__=="__main__":
    main()
