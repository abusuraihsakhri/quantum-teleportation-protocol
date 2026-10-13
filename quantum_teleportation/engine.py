"""
Quantum Teleportation Protocol Engine
Real implementation using state vector simulation with Python stdlib only.

Protocol (Bennett et al., 1993):
1. Alice and Bob share Bell state |Φ+⟩ = 1/√2(|00⟩ + |11⟩)
2. Alice has unknown state |ψ⟩ = α|0⟩ + β|1⟩ to teleport
3. Alice performs Bell measurement on her qubit + half of Bell pair
4. Alice sends 2 classical bits to Bob
5. Bob applies correction (I, X, Z, or ZX) based on Alice's measurement
6. Bob's qubit is now in state |ψ⟩

Fidelity: F = |⟨ψ_target|ψ_received⟩|²
"""
import cmath
import math
import random
from typing import List, Tuple, Dict, Optional


# ─── Gate Matrices ───────────────────────────────────────────────────────────

SQRT2_INV = 1.0 / math.sqrt(2.0)

I_MATRIX = [
    [complex(1, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0)],
]

X_MATRIX = [
    [complex(0, 0), complex(1, 0)],
    [complex(1, 0), complex(0, 0)],
]

Z_MATRIX = [
    [complex(1, 0), complex(0, 0)],
    [complex(0, 0), complex(-1, 0)],
]

H_MATRIX = [
    [complex(SQRT2_INV, 0), complex(SQRT2_INV, 0)],
    [complex(SQRT2_INV, 0), complex(-SQRT2_INV, 0)],
]

# ZX = Z @ X
ZX_MATRIX = [
    [complex(0, 0), complex(1, 0)],
    [complex(-1, 0), complex(0, 0)],
]

# CNOT matrix (4×4): control=qubit 0, target=qubit 1
CNOT_MATRIX = [
    [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0)],
    [complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0)],
    [complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0)],
]


# ─── State Vector Operations ────────────────────────────────────────────────

def zero_state(n: int) -> List[complex]:
    """|0...0⟩ state for n qubits."""
    N = 2 ** n
    state = [complex(0, 0)] * N
    state[0] = complex(1, 0)
    return state


def basis_state(n: int, index: int) -> List[complex]:
    """|index⟩ computational basis state."""
    N = 2 ** n
    state = [complex(0, 0)] * N
    state[index] = complex(1, 0)
    return state


def state_probabilities(state: List[complex]) -> List[float]:
    """|α_i|² for each basis state."""
    return [abs(a) ** 2 for a in state]


def normalize_state(state: List[complex]) -> List[complex]:
    """Normalize to unit length."""
    norm = math.sqrt(sum(abs(a) ** 2 for a in state))
    if norm < 1e-15:
        raise ValueError("Cannot normalize zero vector")
    return [a / norm for a in state]


def fidelity(state1: List[complex], state2: List[complex]) -> float:
    """F = |⟨ψ1|ψ2⟩|²."""
    inner = sum(a.conjugate() * b for a, b in zip(state1, state2))
    return abs(inner) ** 2


def inner_product(state1: List[complex], state2: List[complex]) -> complex:
    """⟨ψ1|ψ2⟩."""
    return sum(a.conjugate() * b for a, b in zip(state1, state2))


def tensor_product(state1: List[complex], state2: List[complex]) -> List[complex]:
    """|ψ1⟩ ⊗ |ψ2⟩."""
    result = []
    for a in state1:
        for b in state2:
            result.append(a * b)
    return result


def apply_single_qubit_gate(state: List[complex], gate: List[List[complex]],
                             target: int, n_qubits: int) -> List[complex]:
    """Apply single-qubit gate to target qubit."""
    N = 2 ** n_qubits
    new_state = [complex(0, 0)] * N
    t_shift = n_qubits - 1 - target
    t_mask = 1 << t_shift
    for i in range(N):
        bit = (i >> t_shift) & 1
        for new_bit in range(2):
            coeff = gate[new_bit][bit]
            if abs(coeff) < 1e-15:
                continue
            j = (i & ~t_mask) | (new_bit << t_shift)
            new_state[j] += coeff * state[i]
    return new_state


def apply_two_qubit_gate(state: List[complex], gate4: List[List[complex]],
                          qubit0: int, qubit1: int, n_qubits: int) -> List[complex]:
    """Apply 4×4 two-qubit gate to qubits qubit0 and qubit1."""
    N = 2 ** n_qubits
    new_state = [complex(0, 0)] * N
    s0 = n_qubits - 1 - qubit0
    s1 = n_qubits - 1 - qubit1
    for i in range(N):
        b0 = (i >> s0) & 1
        b1 = (i >> s1) & 1
        in_idx = b0 * 2 + b1
        for out_idx in range(4):
            coeff = gate4[out_idx][in_idx]
            if abs(coeff) < 1e-15:
                continue
            new_b0 = out_idx >> 1
            new_b1 = out_idx & 1
            j = i
            j = (j & ~(1 << s0)) | (new_b0 << s0)
            j = (j & ~(1 << s1)) | (new_b1 << s1)
            new_state[j] += coeff * state[i]
    return new_state


# ─── Bell States ─────────────────────────────────────────────────────────────

def bell_state(bell_index: int) -> List[complex]:
    """
    Create Bell states (2 qubits):
    0: |Φ+⟩ = 1/√2(|00⟩ + |11⟩)
    1: |Φ-⟩ = 1/√2(|00⟩ - |11⟩)
    2: |Ψ+⟩ = 1/√2(|01⟩ + |10⟩)
    3: |Ψ-⟩ = 1/√2(|01⟩ - |10⟩)
    """
    state = [complex(0, 0)] * 4
    if bell_index == 0:  # |Φ+⟩
        state[0] = complex(SQRT2_INV, 0)
        state[3] = complex(SQRT2_INV, 0)
    elif bell_index == 1:  # |Φ-⟩
        state[0] = complex(SQRT2_INV, 0)
        state[3] = complex(-SQRT2_INV, 0)
    elif bell_index == 2:  # |Ψ+⟩
        state[1] = complex(SQRT2_INV, 0)
        state[2] = complex(SQRT2_INV, 0)
    elif bell_index == 3:  # |Ψ-⟩
        state[1] = complex(SQRT2_INV, 0)
        state[2] = complex(-SQRT2_INV, 0)
    else:
        raise ValueError(f"Bell index must be 0-3, got {bell_index}")
    return state


def prepare_bell_pair() -> List[complex]:
    """Prepare |Φ+⟩ = 1/√2(|00⟩ + |11⟩) using H then CNOT."""
    state = zero_state(2)  # |00⟩
    state = apply_single_qubit_gate(state, H_MATRIX, 0, 2)  # |+0⟩
    state = apply_two_qubit_gate(state, CNOT_MATRIX, 0, 1, 2)  # |Φ+⟩
    return state


# ─── Teleportation Protocol ─────────────────────────────────────────────────

def create_teleportation_state(alpha: complex, beta: complex) -> List[complex]:
    """
    Create the 3-qubit initial state for teleportation:
    |ψ⟩_Alice ⊗ |Φ+⟩_AB
    
    Qubit layout: [q0=Alice's state, q1=Alice's Bell half, q2=Bob's Bell half]
    """
    # Normalize alpha, beta
    norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    if norm < 1e-15:
        raise ValueError("State cannot be zero")
    alpha_n = alpha / norm
    beta_n = beta / norm
    
    # |ψ⟩ = α|0⟩ + β|1⟩
    psi = [alpha_n, beta_n]
    
    # |Φ+⟩
    bell = bell_state(0)
    
    # |ψ⟩ ⊗ |Φ+⟩
    state = tensor_product(psi, bell)
    return state


def bell_measurement(state: List[complex]) -> Tuple[int, List[float]]:
    """
    Perform Bell measurement on qubits 0 and 1.
    
    Projects onto Bell basis:
    |Φ+⟩ = 1/√2(|00⟩ + |11⟩)
    |Φ-⟩ = 1/√2(|00⟩ - |11⟩)
    |Ψ+⟩ = 1/√2(|01⟩ + |10⟩)
    |Ψ-⟩ = 1/√2(|01⟩ - |10⟩)
    
    Returns (measurement outcome 0-3, probabilities for each Bell state).
    """
    n = 3  # total qubits
    N = 8
    bell_probs = [0.0, 0.0, 0.0, 0.0]
    
    # For each Bell state, compute probability by projecting qubits 0,1
    for bell_idx in range(4):
        bell_vec = bell_state(bell_idx)
        prob = 0.0
        for q2 in range(2):  # Bob's qubit state
            amplitude = complex(0, 0)
            for b01 in range(4):  # qubits 0,1 basis states
                # Full state index: b01 * 2 + q2
                full_idx = b01 * 2 + q2
                # Bell state amplitude for b01
                amplitude += bell_vec[b01].conjugate() * state[full_idx]
            prob += abs(amplitude) ** 2
        bell_probs[bell_idx] = prob
    
    # Choose measurement outcome based on probabilities
    r = random.random()
    cumulative = 0.0
    outcome = 3
    for i in range(4):
        cumulative += bell_probs[i]
        if r < cumulative:
            outcome = i
            break
    
    return outcome, bell_probs


def get_correction_gate(bell_measurement: int) -> List[List[complex]]:
    """
    Get Bob's correction gate based on Alice's measurement outcome.
    
    Measurement outcome → Correction:
    0 (00) → I (no correction needed)
    1 (01) → X (bit flip)
    2 (10) → Z (phase flip)
    3 (11) → ZX (bit + phase flip)
    """
    if bell_measurement == 0:
        return I_MATRIX
    elif bell_measurement == 1:
        return X_MATRIX
    elif bell_measurement == 2:
        return Z_MATRIX
    elif bell_measurement == 3:
        return ZX_MATRIX
    else:
        raise ValueError(f"Invalid measurement outcome: {bell_measurement}")


def teleport(alpha: complex, beta: complex, seed: Optional[int] = None) -> dict:
    """
    Execute the full quantum teleportation protocol.
    
    Uses computational basis measurement (standard approach):
    1. Prepare |ψ⟩ ⊗ |Φ+⟩
    2. Alice applies CNOT(q0,q1) then H(q0)
    3. Alice measures q0 and q1 in computational basis
    4. Bob applies correction based on 2-bit outcome
    
    Args:
        alpha: amplitude of |0⟩ in state to teleport
        beta: amplitude of |1⟩ in state to teleport
        seed: random seed for reproducibility
    
    Returns dict with protocol results.
    """
    rng = random.Random(seed)
    
    # Normalize input state; invalid amplitudes must not yield NaN fidelities.
    norm = math.hypot(abs(alpha), abs(beta))
    if not math.isfinite(norm) or norm < 1e-15:
        raise ValueError("Amplitudes must be finite and not both zero")
    alpha_n = alpha / norm
    beta_n = beta / norm
    target_state = [alpha_n, beta_n]
    
    # Step 1: Create 3-qubit state |ψ⟩ ⊗ |Φ+⟩
    state3 = create_teleportation_state(alpha, beta)
    
    # Step 2: Alice applies CNOT (q0 control, q1 target) then H on q0
    state3 = apply_two_qubit_gate(state3, CNOT_MATRIX, 0, 1, 3)
    state3 = apply_single_qubit_gate(state3, H_MATRIX, 0, 3)
    
    # Step 3: Measure qubits 0 and 1 in computational basis
    # After Alice's operations, the state is:
    # 1/2[|00⟩(α|0⟩+β|1⟩) + |01⟩(α|1⟩+β|0⟩) + |10⟩(α|0⟩-β|1⟩) + |11⟩(α|1⟩-β|0⟩)]
    # Each outcome has probability 1/4
    
    # Compute probabilities for each computational basis outcome on qubits 0,1
    outcome_probs = [0.0] * 4
    for q01 in range(4):
        prob = 0.0
        for q2 in range(2):
            idx = q01 * 2 + q2
            prob += abs(state3[idx]) ** 2
        outcome_probs[q01] = prob
    
    # Choose measurement outcome
    r = rng.random()
    cumulative = 0.0
    outcome = 3
    for i in range(4):
        cumulative += outcome_probs[i]
        if r < cumulative:
            outcome = i
            break
    
    # Step 4: Extract Bob's qubit state after measurement
    bob_state = extract_bob_state_computational(state3, outcome)
    
    # Step 5: Bob applies correction
    correction = get_correction_gate(outcome)
    bob_corrected = apply_single_qubit_gate(bob_state, correction, 0, 1)
    
    # Step 6: Calculate fidelity
    fid = fidelity(target_state, bob_corrected)
    
    # Classical bits sent
    classical_bits = format(outcome, '02b')
    
    return {
        'target_state': target_state,
        'alpha': alpha_n,
        'beta': beta_n,
        'bell_measurement': outcome,
        'bell_measurement_binary': classical_bits,
        'bell_probabilities': outcome_probs,
        'correction_gate': ['I', 'X', 'Z', 'ZX'][outcome],
        'bob_state_before_correction': bob_state,
        'bob_state_after_correction': bob_corrected,
        'fidelity': fid,
        'success': fid > 0.99,
    }


def extract_bob_state(state3: List[complex], bell_outcome: int) -> List[complex]:
    """
    Extract Bob's qubit state after Alice's Bell measurement.
    
    Given the 3-qubit state and Alice's measurement outcome,
    project onto the Bell state and extract Bob's qubit.
    """
    bell_vec = bell_state(bell_outcome)
    bob_state = [complex(0, 0), complex(0, 0)]
    
    for q2 in range(2):
        amplitude = complex(0, 0)
        for b01 in range(4):
            full_idx = b01 * 2 + q2
            amplitude += bell_vec[b01].conjugate() * state3[full_idx]
        bob_state[q2] = amplitude
    
    # Normalize
    norm = math.sqrt(sum(abs(a) ** 2 for a in bob_state))
    if norm > 1e-15:
        bob_state = [a / norm for a in bob_state]
    
    return bob_state


def extract_bob_state_computational(state3: List[complex], outcome: int) -> List[complex]:
    """
    Extract Bob's qubit state after computational basis measurement on qubits 0,1.
    
    outcome: 2-bit value (0-3) from measuring qubits 0 and 1
    Returns Bob's qubit state (qubit 2).
    """
    bob_state = [complex(0, 0), complex(0, 0)]
    
    for q2 in range(2):
        idx = outcome * 2 + q2
        bob_state[q2] = state3[idx]
    
    # Normalize
    norm = math.sqrt(sum(abs(a) ** 2 for a in bob_state))
    if norm > 1e-15:
        bob_state = [a / norm for a in bob_state]
    
    return bob_state


# ─── State Tomography ────────────────────────────────────────────────────────

def state_tomography(state: List[complex]) -> dict:
    """
    Perform single-qubit state tomography.
    Returns density matrix components and Bloch sphere coordinates.
    """
    if len(state) != 2:
        raise ValueError("State tomography requires a single-qubit state")
    
    alpha = state[0]
    beta = state[1]
    
    # Density matrix ρ = |ψ⟩⟨ψ|
    rho = [
        [alpha * alpha.conjugate(), alpha * beta.conjugate()],
        [beta * alpha.conjugate(), beta * beta.conjugate()],
    ]
    
    # Bloch sphere coordinates
    # ρ = (I + r·σ)/2
    # r_x = 2 Re(α*β)
    # r_y = 2 Im(conjugate(α) β), using the Pauli-Y convention
    # r_z = |α|² - |β|²
    r_x = 2 * (alpha.conjugate() * beta).real
    r_y = 2 * (alpha.conjugate() * beta).imag
    r_z = abs(alpha) ** 2 - abs(beta) ** 2
    
    return {
        'density_matrix': rho,
        'bloch_vector': (r_x, r_y, r_z),
        'purity': sum(rho[i][i].real ** 2 + rho[i][i].imag ** 2 for i in range(2)) +
                  sum(abs(rho[i][j]) ** 2 for i in range(2) for j in range(2) if i != j),
        'trace': (rho[0][0] + rho[1][1]).real,
    }


def verify_teleportation(alpha: complex, beta: complex, n_trials: int = 1000,
                          seed: int = 42) -> dict:
    """
    Run teleportation multiple times and verify average fidelity.
    """
    if not isinstance(n_trials, int) or n_trials < 1:
        raise ValueError("n_trials must be a positive integer")
    rng = random.Random(seed)
    fidelities = []
    outcomes = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for _ in range(n_trials):
        result = teleport(alpha, beta, seed=rng.randrange(2 ** 63))
        fidelities.append(result['fidelity'])
        outcomes[result['bell_measurement']] += 1
    
    avg_fid = sum(fidelities) / len(fidelities)
    
    return {
        'n_trials': n_trials,
        'average_fidelity': avg_fid,
        'min_fidelity': min(fidelities),
        'max_fidelity': max(fidelities),
        'outcome_distribution': {k: v / n_trials for k, v in outcomes.items()},
        'all_fidelities_above_099': all(f > 0.99 for f in fidelities),
    }


# ─── Circuit Description ────────────────────────────────────────────────────

def describe_circuit() -> str:
    """Return a human-readable description of the teleportation circuit."""
    return """Quantum Teleportation Circuit (3 qubits):
Qubit layout: [q0=Alice's state, q1=Alice's Bell half, q2=Bob's Bell half]

Step 1: Prepare Bell pair
  - H on q1: |0⟩ → |+⟩
  - CNOT(q1, q2): |+0⟩ → |Φ+⟩ = 1/√2(|00⟩ + |11⟩)

Step 2: Alice's operations
  - CNOT(q0, q1): entangle Alice's state with her Bell half
  - H on q0: prepare for Bell measurement

Step 3: Alice measures q0 and q1
  - 4 possible outcomes (2 classical bits):
    00 → Bob applies I
    01 → Bob applies X
    10 → Bob applies Z
    11 → Bob applies ZX

Step 4: Bob applies correction
  - Based on 2 classical bits from Alice
  - Bob's qubit is now in state |ψ⟩ = α|0⟩ + β|1⟩

Computational-basis measurement after CNOT(q0,q1) and H(q0):
  00 → I  (no change)
  01 → X  (bit flip)
  10 → Z  (phase flip)
  11 → ZX (bit + phase flip)
"""
