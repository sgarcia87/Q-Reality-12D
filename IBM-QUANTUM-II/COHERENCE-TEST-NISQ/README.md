# Structured Coherence Certificate v0.1

A lightweight benchmark for measuring **triadic structural coherence** in NISQ quantum devices.
Core constraint tested:
```
C_i = A_i XOR B_i
```

## Metrics
- coherent_rate
- axis_consistency
- A_good_rate
- joint_rate
- gain_A
- P(coherent | A_good)
- P(A_good | coherent)

## Run
```
python3 structured_coherence_certificate_v0_1.py --backend ibm_marrakesh
```

## Optional:
```
--cases v1,onehot,twohot
```

## Output
Produces a JSON certificate with a coherence score (0–100).

## Objective
The final component of the repository is a lightweight benchmarking tool designed to evaluate how well a quantum device preserves triadic structural coherence.
The certificate builds directly on the experimental results obtained in the previous sections.

## Files:
```
structured_coherence_certificate_v0_1.py
STRUCTURED_COHERENCE_CERTIFICATE_README.md
structured_coherence_certificate_*.json
```

## Motivation

The previous experiments established several key properties:
```
Experiment	Demonstration
v1	        The tri-hypercube constraint survives realistic hardware noise
v2        	Structural subsets can be amplified using Grover
v3	        Statistical metrics reveal interaction between selection and coherence
v4	        Grover amplification dynamics follow the expected theoretical pattern
v5        	The geometry of the selected subset affects structural stability
```
Together these results suggest that the tri-hypercube model can serve as a probe of structural coherence in NISQ devices.

The certificate is designed to summarize these properties in a single reproducible benchmark.

## Benchmark Idea

Instead of measuring only raw circuit fidelity, the certificate measures how well a device preserves structured parity relations of the form:
```
A_i XOR B_i XOR C_i = 0
```
These relations define the coherent subspace explored in the previous experiments.
The benchmark therefore evaluates the ability of the hardware to:
```
prepare
maintain
and manipulate
```
states inside this constrained structural subspace.

## Metrics Used

The certificate aggregates several structural metrics.

### coherent_rate
Fraction of shots where all structural constraints hold simultaneously.
```
coherent_rate =
shots satisfying all parity constraints
---------------------------------------
total shots
```

### axis_consistency
Average fraction of axes where the relation
```
A_i XOR B_i XOR C_i = 0
```
is satisfied.
This metric captures local structural stability.

### A_good_rate
Probability that register A belongs to the selected structural subset.
For example in the one-hot experiment:
```
{0001,0010,0100,1000}
```

### joint_rate
Fraction of shots satisfying both:
```
A in selected subset
AND
structural constraints satisfied
```
This measures successful structural amplification.

### gain_A
Amplification factor of the selected subset relative to its baseline probability.
Example:
```
baseline probability ≈ 0.25
observed probability ≈ 0.69
gain ≈ 2.8
```

### Conditional metrics
Two conditional probabilities provide deeper insight:
```
P(coherent | A_good)
P(A_good | coherent)
```
These reveal whether Grover amplification and structural coherence reinforce or interfere with each other.

## Coherence Score

All metrics are combined into a simple coherence score (0–100) that summarizes backend performance.
Example result on IBM Marrakesh:
```
Test            	Score
baseline_uniform	~79
grover_one_hot	  ~87
grover_two_hot  	~83
```
Higher scores indicate that the hardware preserves structural relations more reliably.

## How to Run the Certificate

Install dependencies:
```
pip install qiskit qiskit-ibm-runtime
```

Run the benchmark:
```
python structured_coherence_certificate_v0_1.py --backend ibm_marrakesh --cases v1,onehot,twohot
```

The program generates a JSON certificate containing all metrics and the coherence score.

Example output file:
```
structured_coherence_certificate_20260315_003254.json
```

## What This Benchmark Measures

The certificate does not measure raw fidelity alone.
Instead it evaluates whether the device can:
- preserve structural parity relations
- propagate them through circuits
- amplify structured subsets

This makes it a complementary benchmark to existing NISQ metrics such as:
```
quantum volume
random circuit sampling
mirror circuits
```

## Interpretation

A high score indicates that the backend is capable of maintaining coherent parity structures under noise, which is relevant for:
- parity-based quantum codes
- stabilizer circuits
- structured search algorithms
- constraint-based quantum simulations

## Status

The Structured Coherence Certificate is currently an experimental benchmark prototype developed within the Q-Reality-12D project.
Its purpose is to explore whether structured subspace benchmarks can complement existing NISQ performance metrics.

Future versions may include:
- error mitigation techniques
- multi-backend comparison
- graphical reports
- integration with Qiskit Runtime workflows

## Final Note

The repository therefore progresses through three stages:
```
classical structural model
→ quantum experiments
→ structural coherence benchmark
```
```

providing a reproducible framework for studying how structured quantum states behave on real hardware.
