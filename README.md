# Quantum Fractal Simulator

## 🌌 Español

### Descripción general

Este repositorio contiene una serie de scripts en Python que implementan distintas variantes del algoritmo de búsqueda cuántica de **Grover**, inspiradas directamente en los conceptos filosóficos, geométricos y matemáticos desarrollados en el libro **“La Realidad”** de Sergi G. M. (incluido en este repositorio).

El objetivo principal del proyecto es **amplificar estados cuánticos altamente estructurados**, que representan simetrías fractales, dualidades (±), alineaciones multidimensionales y la geometría del **teseracto (hipercubo 4D)**, utilizando simulación cuántica con **Qiskit**.

La idea central no es “buscar un elemento” en el sentido clásico, sino **observar** cómo Grover actúa como un **mecanismo de amplificación de coherencia estructural**, donde el observador (el algoritmo) selecciona y refuerza estados que cumplen una geometría interna muy precisa.

La estructura matemática que guía el proyecto es:

±[((-1, +1)⁴)³]

---

### Características principales

- **Repetición fractal (^3)**  
  Un mismo patrón de 4 bits se replica en tres planos, reflejando la estructura fractal descrita en el libro.

- **Dualidad (±)**  
  Implementada mediante una paridad global (XOR) sobre los ejes, dividiendo el espacio de estados en dos ramas simétricas y complementarias.

- **Teseracto completo**  
  Las versiones más avanzadas incluyen los **16 vértices completos del hipercubo 4D**, sin restricciones artificiales de peso de Hamming.

- **Simulación cuántica**  
  Ejecutado con `Qiskit AerSimulator`, ideal para estudiar algoritmos cuánticos estructurados en la era NISQ.

- **Grover estándar y Phase-Matched Grover**  
  Se incluyen variantes donde Grover alcanza su límite teórico (<100%) y versiones avanzadas con **phase-matching** capaces de “clavar” probabilidad 1 en simulación ideal.

---

### Instalación

```bash
pip install qiskit qiskit-aer
```
---


## quant_v5_3axes.py

### 🔹 Descripción conceptual
Este experimento implementa un algoritmo de amplificación de amplitud (estilo Grover) sobre un sistema de 12 qubits, introduciendo restricciones explícitas de coherencia estructural.
Los qubits se organizan en tres planos de 4 qubits, y un estado se considera coherente únicamente si cumple simultáneamente:

**- Equilibrio interno**: Cada bloque de 4 qubits debe tener peso exactamente igual a 2.
**- Alineación entre planos**: Determinados qubits deben ser idénticos a lo largo de los tres planos, definiendo tres ejes de coherencia interplanar.
Estas condiciones reducen el espacio válido de 4096 estados posibles a únicamente 6 estados coherentes.

### 🔹 Resultado principal
El algoritmo de Grover concentra el 100% de la probabilidad de medición en estos estados coherentes:
```bash
python3 quant_v5_3axes.py
N=4096  M=6  M/N=0.001465  k_sugerido≈20  k_usado=20
TOP10: [('100110011001', 701), ('001100110011', 697), ('011001100110', 690), ('010101010101', 686), ('101010101010', 683), ('110011001100', 639)]
**Shots coherentes: 4096 / 4096 = 1.000000**
100110011001 701 phys= 100110011001 ok= True blocks= ['1001', '1001', '1001']
001100110011 697 phys= 110011001100 ok= True blocks= ['1100', '1100', '1100']
011001100110 690 phys= 011001100110 ok= True blocks= ['0110', '0110', '0110']
010101010101 686 phys= 101010101010 ok= True blocks= ['1010', '1010', '1010']
101010101010 683 phys= 010101010101 ok= True blocks= ['0101', '0101', '0101']
110011001100 639 phys= 001100110011 ok= True blocks= ['0011', '0011', '0011']
```

### 🔹 Interpretación
Este resultado muestra que, cuando un sistema cuántico está sujeto a restricciones geométricas de coherencia (equilibrio + alineación), el espacio de soluciones colapsa de forma determinista hacia un conjunto extremadamente reducido de configuraciones altamente estructuradas.
El experimento busca demostrar cómo la coherencia emerge de la geometría interna del sistema, sin necesidad de aprendizaje, optimización externa ni reglas heurísticas.

---
## quant_v8_3axes_parity_pm.py

### 🔹 Descripción conceptual
Este experimento implementa amplificación de amplitud (Grover) sobre un registro de 12 qubits organizado en tres planos de 4 qubits, imponiendo coherencia estructural en dos niveles:

**- Coherencia geométrica local e interplano**
- Cada plano debe tener peso exactamente 2 (wt=2).
- Tres ejes quedan alineados entre planos (q0=q4=q8, q1=q5=q9, q2=q6=q10).

**± global como propiedad del TODO**
En lugar de fijar un “signo” en un eje local, el ± se implementa como paridad global del estado completo:
- SIGN=+ selecciona paridad PAR (XOR total de los 12 bits = 0).
- SIGN=- selecciona paridad IMPAR (XOR total de los 12 bits = 1).
Esto hace que el ± actúe como una condición global de lectura del sistema.

### 🔹 Resultado principal
Con N=4096 estados posibles, solo M=6 cumplen simultáneamente (estructura + paridad). Tras ~20 iteraciones, Grover concentra el 100% de la probabilidad de medida en esos estados:

```bash
python3 quant_v8_3axes_parity_pm.py
SIGN=+ (paridad PAR)
N=4096  M=6  M/N=0.001465  k_sugerido≈20  k_usado=20
TOP10: [('010101010101', 710), ('100110011001', 705), ('011001100110', 687), ('110011001100', 668), ('001100110011', 667), ('101010101010', 659)]
**Shots coherentes (según C en físico): 4096 / 4096 = 1.000000**
010101010101 710 phys= 101010101010 ok= True parity= 0 blocks= ['1010', '1010', '1010']
100110011001 705 phys= 100110011001 ok= True parity= 0 blocks= ['1001', '1001', '1001']
011001100110 687 phys= 011001100110 ok= True parity= 0 blocks= ['0110', '0110', '0110']
110011001100 668 phys= 001100110011 ok= True parity= 0 blocks= ['0011', '0011', '0011']
001100110011 667 phys= 110011001100 ok= True parity= 0 blocks= ['1100', '1100', '1100']
101010101010 659 phys= 010101010101 ok= True parity= 0 blocks= ['0101', '0101', '0101']
```
Los estados dominantes corresponden a patrones equilibrados repetidos en los tres planos (p.ej. 1010|1010|1010, 1001|1001|1001) y todos satisfacen la paridad global exigida.

### 🔹 Qué intenta demostrar 
Esta versión intenta demostrar que el signo ± no pertenece a ningún eje ni a ningún plano local, sino que es una propiedad global del sistema completo.

Al imponer:
- equilibrio interno en cada plano.
- alineación geométrica entre planos (ejes compartidos).
- una condición de paridad global sobre el estado completo.

El experimento muestra que la coherencia no depende de fijar bits concretos, sino de cómo el todo es leído como una unidad.
En este marco, el ± actúa como un criterio de observación global (paridad total), no como una variable interna del espacio. El sistema no “contiene” el signo: el signo emerge al evaluar el conjunto completo.
El resultado confirma que, cuando la estructura geométrica es coherente, introducir una lectura global (±) no rompe el orden ni introduce ruido: el espacio de estados colapsa de forma determinista hacia un conjunto mínimo de configuraciones altamente estructuradas.

En términos conceptuales, el experimento ilustra lo siguiente:
- la coherencia nace de la geometría
- el equilibrio es local
- la alineación es interdimensional
- el ± pertenece al marco de lectura del todo, análogo al observador en un modelo hipercúbico de la realidad.

---
## quant_v10_12sign_product_pm.py
### 🔹 Descripción conceptual
Este experimento implementa amplificación de amplitud (Grover) sobre un registro de 12 qubits, organizados conceptualmente como tres planos de 4 qubits, manteniendo la misma base geométrica que las versiones anteriores:
- Cada plano representa una proyección del mismo patrón
- Los planos están alineados entre sí
- Solo ciertos estados altamente estructurados son aceptados como coherentes.

La diferencia clave de esta versión es la forma en que se define el signo ±. Aquí, el signo no se define por un eje, ni por una paridad simple, sino por el producto global de los 12 bits, implementado como una condición sobre el popcount total (número de bits a 1):
- **SIGN = +** → popcount PAR
- **SIGN = −** → popcount IMPAR

Es decir, el signo emerge del conjunto completo de los 12 qubits, no de ninguna parte local del sistema. Así entonces el ± deja de ser una restricción geométrica y pasa a ser una propiedad algebraica global del estado completo.

### Resultados principales

**Rama SIGN = +**

```bash
python3 quant_v10_12sign_product_pm.py
SIGN=+ (12-sign product; bits: popcount PAR)
N=4096  M=6  M/N=0.001465  k_sugerido≈20  k_usado=20
Estados coherentes (fisico): 6
001100110011 ['0011', '0011', '0011'] popcount= 6 Sbit= 1
010101010101 ['0101', '0101', '0101'] popcount= 6 Sbit= 1
011001100110 ['0110', '0110', '0110'] popcount= 6 Sbit= 1
100110011001 ['1001', '1001', '1001'] popcount= 6 Sbit= 1
101010101010 ['1010', '1010', '1010'] popcount= 6 Sbit= 1
110011001100 ['1100', '1100', '1100'] popcount= 6 Sbit= 1
TOP10: [('110011001100', 717), ('100110011001', 696), ('010101010101', 693), ('001100110011', 676), ('101010101010', 671), ('011001100110', 643)]
Shots coherentes (según C en físico): 4096 / 4096 = 1.000000
110011001100 717 phys= 001100110011 ok= True popcount= 6 Sbit= 1 blocks= ['0011', '0011', '0011']
100110011001 696 phys= 100110011001 ok= True popcount= 6 Sbit= 1 blocks= ['1001', '1001', '1001']
010101010101 693 phys= 101010101010 ok= True popcount= 6 Sbit= 1 blocks= ['1010', '1010', '1010']
001100110011 676 phys= 110011001100 ok= True popcount= 6 Sbit= 1 blocks= ['1100', '1100', '1100']
101010101010 671 phys= 010101010101 ok= True popcount= 6 Sbit= 1 blocks= ['0101', '0101', '0101']
011001100110 643 phys= 011001100110 ok= True popcount= 6 Sbit= 1 blocks= ['0110', '0110', '0110']
```

Solo 6 estados cumplen simultáneamente:
- Equilibrio interno por plano
- Alineación entre planos
- Popcount total PAR

Grover concentra el 100% de la probabilidad exclusivamente en esos 6 estados.

Todos los estados coherentes presentan:
- Patrones equilibrados repetidos en los tres planos
- Popcount total = 6
- Signo global consistente (Sbit = 1)

El sistema no genera ningún estado incoherente.

**Rama SIGN = −**
```bash
python3 quant_v10_12sign_product_pm.py
SIGN=- (12-sign product; bits: popcount IMPAR)
N=4096  M=0  M/N=0.000000  k_sugerido≈0  k_usado=0
Estados coherentes (fisico): 0
TOP10: [('100010011111', 6), ('000011110101', 5), ('000110000011', 5), ('100010100011', 5), ('000110111111', 5), ('101000010010', 5), ('100000011010', 5), ('000000000110', 5), ('011010001111', 5), ('110111100010', 5)]
Shots coherentes (según C en físico): 0 / 4096 = 0.000000
100010011111 6 phys= 111110010001 ok= False popcount= 7 Sbit= 0 blocks= ['1111', '1001', '0001']
000011110101 5 phys= 101011110000 ok= False popcount= 6 Sbit= 1 blocks= ['1010', '1111', '0000']
000110000011 5 phys= 110000011000 ok= False popcount= 4 Sbit= 1 blocks= ['1100', '0001', '1000']
100010100011 5 phys= 110001010001 ok= False popcount= 5 Sbit= 0 blocks= ['1100', '0101', '0001']
000110111111 5 phys= 111111011000 ok= False popcount= 8 Sbit= 1 blocks= ['1111', '1101', '1000']
101000010010 5 phys= 010010000101 ok= False popcount= 4 Sbit= 1 blocks= ['0100', '1000', '0101']
100000011010 5 phys= 010110000001 ok= False popcount= 4 Sbit= 1 blocks= ['0101', '1000', '0001']
000000000110 5 phys= 011000000000 ok= False popcount= 2 Sbit= 1 blocks= ['0110', '0000', '0000']
011010001111 5 phys= 111100010110 ok= False popcount= 7 Sbit= 0 blocks= ['1111', '0001', '0110']
110111100010 5 phys= 010001111011 ok= False popcount= 7 Sbit= 0 blocks= ['0100', '0111', '1011']
```
No existe ningún estado que cumpla la estructura geométrica y tenga popcount IMPAR.
El espacio de estados coherentes queda vacío.
Grover no puede amplificar nada porque no hay soluciones estructuralmente compatibles.

### 🔹 Qué intenta demostrar
Esta versión intenta demostrar que no todas las ramas ± son siempre posibles.
Cuando el signo se define como un producto global de todas las dimensiones, la propia geometría del sistema puede permitir una rama y prohibir la otra.
En este caso:
- La rama + es estructuralmente consistente con el equilibrio y la alineación
- La rama − es incompatible y desaparece por completo (M = 0)

Conceptualmente, esto refleja la idea central del libro:
- El ± no es una simetría garantizada
- Es una propiedad emergente del conjunto completo de dimensiones

El experimento muestra que:
- El signo no se puede imponer arbitrariamente
- El observador (o marco de lectura) solo puede “leer” aquellas ramas que la estructura global permite
- Ciertas configuraciones del todo no admiten dualidad completa, sino una única rama coherente

Desde esta perspectiva, el resultado ilustra cómo la geometría profunda del sistema decide qué realidades son posibles y cuáles no, incluso antes de cualquier medición.

---

### **🔹 Relevancia**
Este enfoque puede interpretarse como un modelo mínimo de:
- coherencia estructural
- reducción de grados de libertad
- emergencia de orden a partir de simetría y alineación dimensional

Futuro intento de posibles conexiones conceptuales con modelos geométricos del significado, sistemas cognitivos estructurados y arquitecturas no estadísticas de inferencia :)
