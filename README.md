# Quantum Teleportation Protocol

Real implementation of quantum teleportation (Bennett et al., 1993) using state vector simulation in pure Python (stdlib only).

## What This Actually Does

- **Bell state preparation** — |Φ+⟩ = 1/√2(|00⟩ + |11⟩) via H + CNOT
- **Bell measurement** — projective measurement in Bell basis on sender's qubits
- **Classical communication** — 2 bits encoding measurement outcome
- **Correction operations** — I, X, Z, or ZX applied by receiver
- **Fidelity calculation** — |⟨ψ_target|ψ_received⟩|²
- **State tomography** — density matrix and Bloch sphere coordinates
- **Statistical verification** — multi-trial fidelity testing

### Protocol Steps

1. Alice and Bob share Bell pair |Φ+⟩
2. Alice has unknown state |ψ⟩ = α|0⟩ + β|1⟩
3. Alice performs Bell measurement on her qubit + Bell half
4. Alice sends 2 classical bits to Bob
5. Bob applies correction → recovers |ψ⟩

### Correction Table

| Bell Measurement | Classical Bits | Bob's Correction |
|:---:|:---:|:---:|
| \|Φ+⟩ | 00 | I (none) |
| \|Φ-⟩ | 01 | Z |
| \|Ψ+⟩ | 10 | X |
| \|Ψ-⟩ | 11 | ZX |

## Usage

```bash
# Teleport |+⟩ state
python cli.py teleport --state "|+⟩" --tomography

# Teleport custom state α|0⟩ + β|1⟩
python cli.py teleport --state "0.6,0.8"

# Verify teleportation over 1000 trials
python cli.py verify --state "|+⟩" --trials 1000

# Display Bell states
python cli.py bell

# Show circuit description
python cli.py circuit

# State tomography
python cli.py tomography --state "|+⟩"
```

## API

```python
from quantum_teleportation.engine import teleport, verify_teleportation, state_tomography

# Single teleportation
result = teleport(alpha=1/math.sqrt(2), beta=1/math.sqrt(2), seed=42)
print(f"Fidelity: {result['fidelity']}")

# Statistical verification
stats = verify_teleportation(alpha=0.6, beta=0.8, n_trials=1000)
print(f"Average fidelity: {stats['average_fidelity']}")
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Limitations

- Ideal simulation only — no noise or decoherence
- Bell measurement is projective (not LOCC-based)
- Single-qubit teleportation only
