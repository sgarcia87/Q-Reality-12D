# Observador cuántico estructural sobre un espacio hipercúbico (12 qubits)
# Structural quantum observer over a hypercubic space (12 qubits)

> Español primero. English below.

---

## ES — Qué es este repositorio

Este repo nace de una pregunta simple:  
**¿se puede imponer coherencia en un sistema cuántico sin medirlo, solo “leyendo” estructura?**

Aquí no intento modelar partículas reales ni proponer una “nueva cuántica”. Lo que hago es más concreto:

- construyo un **espacio de estados** de 12 qubits (4096 estados posibles),
- defino una noción de **coherencia estructural** inspirada en un modelo hipercúbico,
- implemento un **observador reversible** (un *oracle* por fase) que detecta esa coherencia,
- y uso amplificación tipo Grover para que la probabilidad se concentre en el subespacio coherente,
  **sin colapso durante la observación**.

La idea madre, en notación simbólica, es:

\[
\pm\big((\{-1,+1\}^4)^3\big)
\]

- \(\{-1,+1\}\): dualidad mínima (dos polos, no “bits” en sentido filosófico)
- \(\cdot^4\): 4 ejes por plano
- \(\cdot^3\): 3 planos/lecturas del mismo esquema (12 ejes en total)
- \(\pm\): **marco global de lectura** (la parte delicada, y donde aparecen resultados distintos)

---

## ES — Qué significa “observador” aquí

En este repo, el observador NO es:

- un qubit extra que se mide,
- una dimensión adicional,
- ni una función que colapsa el estado.

El observador es un procedimiento reversible:

1. se conecta al sistema con ancillas,
2. evalúa condiciones estructurales (paridades, alineaciones, equilibrio),
3. marca por **fase** los estados coherentes,
4. se desconecta completamente (*uncompute*),
5. y deja que la interferencia haga el resto.

Esto es importante: el “acto de observar” aquí no destruye el estado. Solo introduce una asimetría de fase que luego se convierte en probabilidad al aplicar difusión (Grover).

---

## ES — La coherencia que estamos midiendo (la “C(x)”)

En la familia principal de scripts (v5–v10), la coherencia se define con dos capas:

### 1) Equilibrio local (por plano)
Divido los 12 qubits en 3 planos de 4 qubits:

- P0 = q0..q3
- P1 = q4..q7
- P2 = q8..q11

Cada plano debe tener **peso de Hamming = 2** (exactamente dos “1”).
Esto es una forma simple y controlable de representar “equilibrio” dentro de un plano de 4.

### 2) Coherencia transversal (ejes alineados)
Se alinean ejes entre planos (misma coordenada en cada plano):

- eje0: q0 = q4 = q8
- eje1: q1 = q5 = q9
- eje2: q2 = q6 = q10

Con 3 ejes alineados la estructura se vuelve extremadamente restrictiva.

---

## ES — Cómo correrlo

Requisitos:

```bash
pip install qiskit qiskit-aer
```

Ejemplos:

```bash
python3 quant_v9_3axes_axis_sign_pm.py
python3 quant_v10_12sign_product_pm.py
```

Notas prácticas:
- En mis pruebas, el “marco físico” sale como el **reverso** del bitstring medido (`s_phys = s_measured[::-1]`). Los scripts lo gestionan e imprimen `phys=` para que no haya dudas.

---

## ES — Qué demuestra cada versión (sin humo)

### `quant_v5_3axes.py`
**Qué hace:**  
Implementa coherencia fuerte: `wt==2` por plano + **3 ejes alineados**. No introduce ± explícito.

**Qué demuestra:**  
Que el observador reversible + Grover puede proyectar la probabilidad casi por completo (y a veces 100%) en un subespacio coherente muy pequeño.  
Aquí aparecen típicamente **6 estados coherentes**: patrones wt=2 repetidos en los 3 planos.

**Cuándo usarla:**  
Como base “estructural pura” sin discutir el ±.

---

### `quant_v6_3axes_plus.py`
**Qué hace:**  
Lo mismo que v5, pero añade una “polaridad +” de forma simple (por ejemplo, exigiendo q0=1 en marco físico).

**Qué demuestra:**  
Que puedes “romper simetría” de manera directa y forzar el sistema hacia un hemisferio del subespacio coherente.

**Limitación (importante):**  
Es útil como demostración técnica, pero conceptualmente el ± aquí está implementado como una condición local (un bit), no como un marco global. Por eso no es mi versión favorita para explicar el símbolo ±.

---

### `quant_v8_3axes_parity_pm.py`
**Qué hace:**  
Implementa ± como **paridad global de bits** (XOR total de los 12 qubits), con SIGN=+ (par) o SIGN=- (impar).

**Qué demuestra:**  
Algo muy útil: con `wt==2` en cada plano, el popcount total queda fijado (6) y la paridad global es siempre par.  
Resultado práctico:
- SIGN=+ funciona,
- SIGN=- da **M=0** (no existe ningún estado coherente impar bajo esa definición).

**Por qué importa:**  
Esto no es un bug; es una consecuencia matemática. Sirve para mostrar que algunas definiciones “globales” se vuelven redundantes o imposibles cuando impones equilibrio local fuerte.

---

### `quant_v9_3axes_axis_sign_pm.py`  ← **la versión que mejor encaja con “dos resultados posibles”**
**Qué hace:**  
Implementa ± como un **signo global derivado de los ejes** (no del popcount total), usando:

- axis-sign = XOR(q0, q1, q2) (en marco físico)
- SIGN=+ acepta axis-sign=1
- SIGN=- acepta axis-sign=0

Con esto, el subespacio coherente (6 estados) se divide en dos ramas reales:
- **3 estados** en la rama +
- **3 estados** en la rama −

**Qué demuestra:**  
Que el ± puede interpretarse como **marco de lectura** (dos orientaciones coherentes) sin colapsar una de las ramas por definición.

**Por qué la recomiendo:**  
Si en tu teoría hablas de dos resultados/lecturas posibles, esta versión es la que mejor lo representa de forma limpia: dos ramas, ambas coherentes, ambas alcanzables.

---

### `quant_v10_12sign_product_pm.py`
**Qué hace:**  
Implementa el ± más “literal” posible: como el **signo del producto de los 12 signos** (bit 1→+1, bit 0→-1). En bits termina siendo equivalente a paridad del popcount.

**Qué demuestra:**  
El límite estructural: con `wt==2` por plano, el popcount total es siempre 6 (par), así que:
- SIGN=+ mantiene los 6 estados coherentes,
- SIGN=- vuelve a dar **M=0**.

**Interpretación (no obligatoria, pero interesante):**  
Si mantienes un “equilibrio total” muy estricto, el sistema puede fijar automáticamente el signo global (solo “+” es compatible). Esto conecta con la idea de “camino unidireccional” si lo quieres leer así.

---

## ES — Qué conclusión razonable sale de todo esto

1) Un observador reversible puede actuar como “lector estructural” sin medir.  
2) La noción de coherencia que elijas importa más que la magia del circuito.  
3) El símbolo ± puede implementarse de varias formas; algunas degeneran por restricciones internas (v8, v10) y otras preservan dos lecturas coherentes (v9).

---

## ES — Archivos recomendados para empezar

- Si quieres entender el “cierre estructural”: **v5**
- Si quieres el ± con dos ramas reales: **v9**
- Si quieres ver por qué ciertas definiciones globales colapsan: **v8 y v10**

---

---

## EN — What this repository is

This repo starts from a simple question:  
**Can we enforce coherence in a quantum system without measuring it, purely by “reading” structure?**

This is not a physical particle model and not “new quantum mechanics”. It is a concrete experiment:

- build a **12‑qubit state space** (4096 basis states),
- define a notion of **structural coherence** inspired by a hypercubic model,
- implement an **observer as a reversible phase oracle**,
- use Grover‑style amplification so probability concentrates on the coherent subspace,
  **without collapse during observation**.

The symbolic inspiration is:

\[
\pm\big((\{-1,+1\}^4)^3\big)
\]

- \(\{-1,+1\}\): minimal duality (two poles)
- \(\cdot^4\): 4 axes per plane
- \(\cdot^3\): 3 planes / orthogonal readings (12 axes total)
- \(\pm\): a **global reading frame** (the tricky part)

---

## EN — What “observer” means here

The observer is NOT:

- an extra qubit that gets measured,
- an extra dimension,
- a collapse mechanism.

It is a reversible procedure:

1. couples ancillas to the system,
2. computes structural predicates,
3. marks coherent states by **phase**,
4. uncomputes everything (disconnects),
5. lets interference do the rest via Grover diffusion.

So: observation is implemented as a **reversible structural audit**, not measurement.

---

## EN — The coherence predicate C(x)

In the main scripts (v5–v10), coherence is defined in two layers:

### 1) Local equilibrium (per plane)
Split 12 qubits into 3 planes of 4:

- P0 = q0..q3
- P1 = q4..q7
- P2 = q8..q11

Each plane must have **Hamming weight = 2** (exactly two 1s).

### 2) Transversal coherence (aligned axes)
Align axes across planes:

- axis0: q0 = q4 = q8
- axis1: q1 = q5 = q9
- axis2: q2 = q6 = q10

With 3 aligned axes the subspace becomes extremely small.

---

## EN — Running

Requirements:

```bash
pip install qiskit qiskit-aer
```

Examples:

```bash
python3 quant_v9_3axes_axis_sign_pm.py
python3 quant_v10_12sign_product_pm.py
```

Practical note:
- In my runs the “physical frame” corresponds to reversing the measured bitstring (`s_phys = s_measured[::-1]`). The scripts print `phys=` to avoid confusion.

---

## EN — What each version demonstrates

### `quant_v5_3axes.py`
**What it does:**  
Strong coherence: `wt==2` per plane + **3 aligned axes**. No explicit ±.

**What it shows:**  
A reversible observer + Grover can concentrate probability almost entirely (sometimes 100%) on a tiny coherent subspace.  
Typically yields **6 coherent states**: one wt=2 pattern replicated across all three planes.

---

### `quant_v6_3axes_plus.py`
**What it does:**  
Same as v5, plus a simple “+ polarity” constraint (e.g. forcing q0=1 in the physical frame).

**What it shows:**  
You can break symmetry and push the system into one half of the coherent subspace.

**Important limitation:**  
Technically fine, but conceptually ± becomes a local bit constraint, not a global reading frame.

---

### `quant_v8_3axes_parity_pm.py`
**What it does:**  
Implements ± as **global bit parity** (XOR of all 12 bits): SIGN=+ (even) vs SIGN=- (odd).

**What it shows:**  
With `wt==2` in each plane, total popcount is fixed (6), so global parity is always even:
- SIGN=+ works,
- SIGN=- yields **M=0**.

This is a useful sanity check: some “global” definitions become redundant/impossible once local equilibrium is enforced.

---

### `quant_v9_3axes_axis_sign_pm.py`  ← **best match for “two possible outcomes”**
**What it does:**  
Implements ± as a global frame derived from the aligned axes:

- axis‑sign = XOR(q0, q1, q2) in the physical frame
- SIGN=+ accepts axis‑sign=1
- SIGN=- accepts axis‑sign=0

This splits the coherent subspace (6 states) into two real branches:
- **3 states** in +
- **3 states** in −

**What it shows:**  
± can be implemented as a true reading frame (two coherent orientations) without collapsing one branch by definition.

---

### `quant_v10_12sign_product_pm.py`
**What it does:**  
Implements the most literal ±: **product of all 12 signs** (bit 1→+1, bit 0→-1). In bits it reduces to popcount parity.

**What it shows:**  
A structural limit: with `wt==2` per plane, popcount is always 6 (even), so:
- SIGN=+ keeps the 6 coherent states,
- SIGN=- yields **M=0**.

---

## EN — Takeaways

1) A reversible observer can act as a structural reader without measurement.  
2) The coherence predicate matters more than the circuit “trick”.  
3) ± can be implemented in multiple ways; some degenerate under strong equilibrium (v8, v10) while others preserve two coherent frames (v9).

---

## EN — Where to start

- Structural closure baseline: **v5**
- Two real ± branches: **v9**
- Why some global signs collapse: **v8 and v10**
