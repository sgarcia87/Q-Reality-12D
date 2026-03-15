#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


# =========================================================
# Construcción del circuito del tri-hipercubo
# =========================================================

def build_tri_hypercube():

    qc = QuantumCircuit(12,12)

    A = [0,1,2,3]
    B = [4,5,6,7]
    C = [8,9,10,11]

    # Superposición uniforme
    qc.h(A)
    qc.h(B)

    # C_i = A_i XOR B_i
    for i in range(4):
        qc.cx(A[i],C[i])
        qc.cx(B[i],C[i])

    qc.measure(range(12),range(12))

    return qc


# =========================================================
# Extraer counts
# =========================================================

def extract_counts(pub_result):

    data = pub_result.data

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
# Métrica del modelo
# =========================================================

def coherence_metrics(counts):

    shots=sum(counts.values())

    coherent=0
    axis_correct=0

    for s,c in counts.items():

        s=s[::-1]

        A=[int(x) for x in s[0:4]]
        B=[int(x) for x in s[4:8]]
        C=[int(x) for x in s[8:12]]

        axis_ok=0

        for i in range(4):

            if (A[i]^B[i])==C[i]:
                axis_ok+=1

        axis_correct+=axis_ok*c

        if axis_ok==4:
            coherent+=c

    return {

        "shots":shots,
        "coherent_rate":coherent/shots,
        "axis_consistency":axis_correct/(shots*4)

    }


# =========================================================
# Runner
# =========================================================

def run(backend_name="ibm_marrakesh",shots=4096):

    qc=build_tri_hypercube()

    service=QiskitRuntimeService()

    backend=service.backend(backend_name)

    pm=generate_preset_pass_manager(
        backend=backend,
        optimization_level=1
    )

    isa=pm.run(qc)

    sampler=Sampler(mode=backend)

    job=sampler.run([isa],shots=shots)

    result=job.result()

    counts=extract_counts(result[0])

    metrics=coherence_metrics(counts)

    print("\nTri-Hipercubo Quantum Test")
    print("backend:",backend_name)
    print("job:",job.job_id())
    print(metrics)

    out={
        "backend":backend_name,
        "job_id":job.job_id(),
        "metrics":metrics,
        "counts":counts
    }

    fname=f"tri_hypercube_quantum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(fname,"w") as f:
        json.dump(out,f,indent=2)

    print("\nSaved:",fname)


# =========================================================

if __name__=="__main__":

    run()
