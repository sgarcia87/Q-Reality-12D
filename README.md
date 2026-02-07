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

## 🌍 English

### Overview

This repository contains a collection of Python scripts implementing several variants of **Grover’s quantum search algorithm**, directly inspired by the philosophical and mathematical framework developed in the book **“La Realidad”** by Sergi G. M. (included in this repository).

Rather than using Grover as a classical search tool, the project explores it as a **mechanism for amplifying structural coherence**, where quantum states representing fractal symmetries, dualities (±), and multidimensional alignments are selectively enhanced.

The guiding mathematical structure is:

±[((-1, +1)⁴)³]

---

### Installation

```bash
pip install qiskit qiskit-aer
```

---

### License

MIT License.
