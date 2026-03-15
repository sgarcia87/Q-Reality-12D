# Structured Coherence Certificate v0.1

A lightweight benchmark for measuring **triadic structural coherence** in NISQ quantum devices.

Core constraint tested:

C_i = A_i XOR B_i

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

Optional:

```
--cases v1,onehot,twohot
```

## Output

Produces a JSON certificate with a coherence score (0–100).
