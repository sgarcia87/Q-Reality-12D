# quant_v3.py
# Observador (opción A): oracle reversible + Grover diffusion
# Coherencia C(x):
#   (1) cada plano de 4 qubits tiene peso de Hamming == 2
#   (2) alineación de eje: q0 == q4 == q8
#
# Requisitos: qiskit, qiskit-aer

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator


# ---------------------------
# Utilidades: patrones peso=2
# ---------------------------

def mark_pattern(qc: QuantumCircuit, qubits4, flag, pattern_bits):
    """
    Marca flag (XOR) si qubits4 coincide EXACTAMENTE con pattern_bits (lista de 4 bits 0/1).
    Reversible: X en ceros -> mcx -> deshacer X.
    """
    for qb, b in zip(qubits4, pattern_bits):
        if b == 0:
            qc.x(qb)
    qc.mcx(qubits4, flag)
    for qb, b in zip(qubits4, pattern_bits):
        if b == 0:
            qc.x(qb)


def weight_eq_2_flag(qc: QuantumCircuit, qubits4, flag):
    """
    Escribe en flag (XOR) si el bloque de 4 tiene exactamente dos '1'.
    Nota: flag debe empezar en |0>.
    """
    patterns = [
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 1],
    ]
    for p in patterns:
        mark_pattern(qc, qubits4, flag, p)


def uncompute_weight_eq_2_flag(qc: QuantumCircuit, qubits4, flag):
    """
    Inverso exacto de weight_eq_2_flag (repetimos en orden inverso).
    """
    patterns = [
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 1],
    ]
    for p in reversed(patterns):
        mark_pattern(qc, qubits4, flag, p)


# ---------------------------
# eq = (q0==q4==q8) limpio
# ---------------------------

def compute_eq_three(qc: QuantumCircuit, q0, q4, q8, eq, t1, t2):
    """
    eq = 1 <=> (q0 == q4 == q8) usando ancillas t1,t2 (XORs).
    Reversible y limpio.
    """
    # t1 = q0 XOR q4
    qc.cx(q0, t1)
    qc.cx(q4, t1)

    # t2 = q4 XOR q8
    qc.cx(q4, t2)
    qc.cx(q8, t2)

    # eq = AND(~t1, ~t2)
    qc.x(t1)
    qc.x(t2)
    qc.mcx([t1, t2], eq)
    qc.x(t1)
    qc.x(t2)


def uncompute_eq_three(qc: QuantumCircuit, q0, q4, q8, eq, t1, t2):
    """
    Deshace compute_eq_three dejando eq,t1,t2 en |0>.
    """
    # deshacer eq = AND(~t1, ~t2)
    qc.x(t1)
    qc.x(t2)
    qc.mcx([t1, t2], eq)
    qc.x(t1)
    qc.x(t2)

    # deshacer t2
    qc.cx(q8, t2)
    qc.cx(q4, t2)

    # deshacer t1
    qc.cx(q4, t1)
    qc.cx(q0, t1)


# ---------------------------
# Grover diffusion
# ---------------------------

def grover_diffusion(qc: QuantumCircuit, qubits):
    """
    Difusión estándar de Grover sobre 'qubits' (lista).
    """
    qc.h(qubits)
    qc.x(qubits)
    qc.h(qubits[-1])
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(qubits[-1])
    qc.x(qubits)
    qc.h(qubits)


# ---------------------------
# Circuito completo
# ---------------------------

def build_circuit(iterations=9):

    data = QuantumRegister(12, "q")

    # flags de peso
    w0 = QuantumRegister(1, "w0")
    w1 = QuantumRegister(1, "w1")
    w2 = QuantumRegister(1, "w2")

    # flags de ejes
    eq0 = QuantumRegister(1, "eq0")   # q0 == q4 == q8
    eq1 = QuantumRegister(1, "eq1")   # q1 == q5 == q9

    # ancillas XOR
    t = QuantumRegister(4, "t")       # t[0],t[1] para eq0; t[2],t[3] para eq1

    # qubit de fase (oracle)
    ph = QuantumRegister(1, "ph")

    # registro clásico
    c = ClassicalRegister(12, "c")

    # 🔹 AHORA sí: crear el circuito
    qc = QuantumCircuit(data, w0, w1, w2, eq0, eq1, t, ph, c)

    q = data

    # 3 planos de 4 qubits
    b0 = [q[0], q[1], q[2], q[3]]
    b1 = [q[4], q[5], q[6], q[7]]
    b2 = [q[8], q[9], q[10], q[11]]

    # Superposición hipercubo 12D
    qc.h(q)

    # Preparar qubit de fase en |->
    qc.x(ph[0])
    qc.h(ph[0])

    for _ in range(iterations):
        # ---- OBSERVADOR (compute) ----
        weight_eq_2_flag(qc, b0, w0[0])
        weight_eq_2_flag(qc, b1, w1[0])
        weight_eq_2_flag(qc, b2, w2[0])

        # eje 0
        compute_eq_three(qc, q[0], q[4], q[8], eq0[0], t[0], t[1])
        # eje 1
        compute_eq_three(qc, q[1], q[5], q[9], eq1[0], t[2], t[3])

        # oracle: ahora exige 2 ejes alineados
        qc.mcx([w0[0], w1[0], w2[0], eq0[0], eq1[0]], ph[0])

        # uncompute en orden inverso (buena práctica)
        uncompute_eq_three(qc, q[1], q[5], q[9], eq1[0], t[2], t[3])
        uncompute_eq_three(qc, q[0], q[4], q[8], eq0[0], t[0], t[1])

        uncompute_weight_eq_2_flag(qc, b2, w2[0])
        uncompute_weight_eq_2_flag(qc, b1, w1[0])
        uncompute_weight_eq_2_flag(qc, b0, w0[0])

        # ---- Difusión Grover ----
        grover_diffusion(qc, list(q))

    qc.measure(q, c)
    return qc


# ---------------------------
# Verificador (para tus top10)
# ---------------------------

def coherent_string(s: str):
    """
    Comprueba C(x) en un string de 12 bits usando el mismo criterio:
    - wt de cada bloque de 4 == 2
    - s[0]==s[4]==s[8]
    """
    def wt(x): return sum(int(b) for b in x)
    b0, b1, b2 = s[0:4], s[4:8], s[8:12]
    return (wt(b0) == 2 and wt(b1) == 2 and wt(b2) == 2
            and (s[0] == s[4] == s[8])
            and (s[1] == s[5] == s[9]))



# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    iterations = 9
    shots = 4096

    qc = build_circuit(iterations=iterations)

    sim = AerSimulator()
    tqc = transpile(qc, sim, optimization_level=1)
    res = sim.run(tqc, shots=shots).result()
    counts = res.get_counts()

    top10 = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("TOP10:", top10)

    def coherent_phys(bitstring: str) -> bool:
        # marco físico = reverse
        return coherent_string(bitstring[::-1])

    good_shots = sum(v for k, v in counts.items() if coherent_phys(k))
    print("Shots coherentes:", good_shots, "/", shots, "=", good_shots / shots)

    for s, c in top10:
        s_phys = s[::-1]
        ok = coherent_string(s_phys)
        print(s, c, "phys=", s_phys, "ok=", ok,
              "blocks=", [s_phys[0:4], s_phys[4:8], s_phys[8:12]])

