"""
Tests for Quantum Teleportation Protocol Engine.
Real quantum teleportation verification.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import cmath
import pytest
from quantum_teleportation.engine import (
    zero_state, basis_state, state_probabilities, normalize_state,
    fidelity, inner_product, tensor_product,
    apply_single_qubit_gate, apply_two_qubit_gate,
    bell_state, prepare_bell_pair,
    create_teleportation_state, bell_measurement, get_correction_gate,
    teleport, extract_bob_state, state_tomography,
    verify_teleportation, describe_circuit,
    I_MATRIX, X_MATRIX, Z_MATRIX, ZX_MATRIX, H_MATRIX, CNOT_MATRIX,
)


# ─── Gate Tests ──────────────────────────────────────────────────────────────

class TestGates:
    def test_x_gate_flips(self):
        state = [complex(1, 0), complex(0, 0)]
        result = apply_single_qubit_gate(state, X_MATRIX, 0, 1)
        assert abs(result[0]) < 1e-10
        assert abs(result[1] - 1.0) < 1e-10

    def test_z_gate_phase(self):
        state = [complex(0, 0), complex(1, 0)]
        result = apply_single_qubit_gate(state, Z_MATRIX, 0, 1)
        assert abs(result[0]) < 1e-10
        assert abs(result[1] + 1.0) < 1e-10

    def test_zx_gate(self):
        # ZX|0⟩ = Z|1⟩ = -|1⟩
        state = [complex(1, 0), complex(0, 0)]
        result = apply_single_qubit_gate(state, ZX_MATRIX, 0, 1)
        assert abs(result[0]) < 1e-10
        assert abs(result[1] + 1.0) < 1e-10

    def test_cnot_matrix(self):
        # CNOT|10⟩ = |11⟩
        state = basis_state(2, 2)  # |10⟩
        result = apply_two_qubit_gate(state, CNOT_MATRIX, 0, 1, 2)
        assert abs(result[3] - 1.0) < 1e-10

    def test_cnot_control_zero(self):
        # CNOT|01⟩ = |01⟩ (control=0, no flip)
        state = basis_state(2, 1)  # |01⟩
        result = apply_two_qubit_gate(state, CNOT_MATRIX, 0, 1, 2)
        assert abs(result[1] - 1.0) < 1e-10

    def test_hadamard_on_zero(self):
        state = [complex(1, 0), complex(0, 0)]
        result = apply_single_qubit_gate(state, H_MATRIX, 0, 1)
        assert abs(result[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[1] - 1 / math.sqrt(2)) < 1e-10


# ─── Bell States ─────────────────────────────────────────────────────────────

class TestBellStates:
    def test_bell_phi_plus(self):
        state = bell_state(0)
        assert abs(state[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(state[3] - 1 / math.sqrt(2)) < 1e-10
        assert abs(state[1]) < 1e-10
        assert abs(state[2]) < 1e-10

    def test_bell_phi_minus(self):
        state = bell_state(1)
        assert abs(state[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(state[3] + 1 / math.sqrt(2)) < 1e-10

    def test_bell_psi_plus(self):
        state = bell_state(2)
        assert abs(state[1] - 1 / math.sqrt(2)) < 1e-10
        assert abs(state[2] - 1 / math.sqrt(2)) < 1e-10

    def test_bell_psi_minus(self):
        state = bell_state(3)
        assert abs(state[1] - 1 / math.sqrt(2)) < 1e-10
        assert abs(state[2] + 1 / math.sqrt(2)) < 1e-10

    def test_bell_states_normalized(self):
        for i in range(4):
            state = bell_state(i)
            norm_sq = sum(abs(a) ** 2 for a in state)
            assert abs(norm_sq - 1.0) < 1e-10

    def test_bell_states_orthogonal(self):
        for i in range(4):
            for j in range(4):
                ip = inner_product(bell_state(i), bell_state(j))
                expected = 1.0 if i == j else 0.0
                assert abs(ip - expected) < 1e-10

    def test_prepare_bell_pair(self):
        prepared = prepare_bell_pair()
        expected = bell_state(0)
        assert fidelity(expected, prepared) > 1 - 1e-10

    def test_invalid_bell_index(self):
        with pytest.raises(ValueError):
            bell_state(4)


# ─── Tensor Product ──────────────────────────────────────────────────────────

class TestTensorProduct:
    def test_tensor_product_basic(self):
        s1 = [complex(1, 0), complex(0, 0)]
        s2 = [complex(1, 0), complex(0, 0)]
        result = tensor_product(s1, s2)
        assert len(result) == 4
        assert abs(result[0] - 1.0) < 1e-10

    def test_tensor_product_superposition(self):
        s1 = [complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))]
        s2 = [complex(1, 0), complex(0, 0)]
        result = tensor_product(s1, s2)
        assert abs(result[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[2] - 1 / math.sqrt(2)) < 1e-10


# ─── Teleportation State Creation ────────────────────────────────────────────

class TestTeleportationState:
    def test_create_state_normalized(self):
        state = create_teleportation_state(0.6, 0.8)
        norm_sq = sum(abs(a) ** 2 for a in state)
        assert abs(norm_sq - 1.0) < 1e-10

    def test_create_state_length(self):
        state = create_teleportation_state(1, 0)
        assert len(state) == 8  # 3 qubits

    def test_create_state_zero_state(self):
        state = create_teleportation_state(1, 0)
        # |0⟩ ⊗ |Φ+⟩ = 1/√2(|000⟩ + |011⟩)
        assert abs(abs(state[0]) ** 2 - 0.5) < 1e-10
        assert abs(abs(state[3]) ** 2 - 0.5) < 1e-10


# ─── Bell Measurement ───────────────────────────────────────────────────────

class TestBellMeasurement:
    def test_bell_measurement_probabilities_sum(self):
        state = create_teleportation_state(0.6, 0.8)
        # Apply CNOT and H (Alice's operations)
        state = apply_two_qubit_gate(state, CNOT_MATRIX, 0, 1, 3)
        state = apply_single_qubit_gate(state, H_MATRIX, 0, 3)
        _, probs = bell_measurement(state)
        assert abs(sum(probs) - 1.0) < 1e-10

    def test_bell_measurement_uniform_for_basis(self):
        # For |0⟩ state, all Bell outcomes should be equally likely
        state = create_teleportation_state(1, 0)
        state = apply_two_qubit_gate(state, CNOT_MATRIX, 0, 1, 3)
        state = apply_single_qubit_gate(state, H_MATRIX, 0, 3)
        _, probs = bell_measurement(state)
        for p in probs:
            assert abs(p - 0.25) < 1e-10


# ─── Correction Gates ────────────────────────────────────────────────────────

class TestCorrectionGates:
    def test_correction_gate_0_is_identity(self):
        gate = get_correction_gate(0)
        for i in range(2):
            for j in range(2):
                expected = 1.0 if i == j else 0.0
                assert abs(gate[i][j] - expected) < 1e-10

    def test_correction_gate_1_is_x(self):
        gate = get_correction_gate(1)
        assert abs(gate[0][1] - 1.0) < 1e-10
        assert abs(gate[1][0] - 1.0) < 1e-10

    def test_correction_gate_2_is_z(self):
        gate = get_correction_gate(2)
        assert abs(gate[1][1] + 1.0) < 1e-10

    def test_correction_gate_3_is_zx(self):
        gate = get_correction_gate(3)
        assert abs(gate[0][1] - 1.0) < 1e-10
        assert abs(gate[1][0] + 1.0) < 1e-10

    def test_invalid_correction(self):
        with pytest.raises(ValueError):
            get_correction_gate(5)


# ─── Full Teleportation ─────────────────────────────────────────────────────

class TestTeleportation:
    def test_teleport_zero_state(self):
        result = teleport(1, 0, seed=42)
        assert result['fidelity'] > 0.99

    def test_teleport_one_state(self):
        result = teleport(0, 1, seed=42)
        assert result['fidelity'] > 0.99

    def test_teleport_plus_state(self):
        result = teleport(1 / math.sqrt(2), 1 / math.sqrt(2), seed=42)
        assert result['fidelity'] > 0.99

    def test_teleport_minus_state(self):
        result = teleport(1 / math.sqrt(2), -1 / math.sqrt(2), seed=42)
        assert result['fidelity'] > 0.99

    def test_teleport_custom_state(self):
        result = teleport(0.6, 0.8, seed=42)
        assert result['fidelity'] > 0.99

    def test_teleport_complex_state(self):
        result = teleport(complex(0.6, 0.2), complex(0.3, -0.7), seed=42)
        assert result['fidelity'] > 0.99

    def test_teleport_returns_all_fields(self):
        result = teleport(0.6, 0.8, seed=42)
        required = ['target_state', 'alpha', 'beta', 'bell_measurement',
                     'bell_measurement_binary', 'bell_probabilities',
                     'correction_gate', 'bob_state_after_correction', 'fidelity', 'success']
        for key in required:
            assert key in result

    def test_teleport_classical_bits_format(self):
        result = teleport(0.6, 0.8, seed=42)
        assert len(result['bell_measurement_binary']) == 2
        assert all(c in '01' for c in result['bell_measurement_binary'])

    def test_teleport_correction_gate_valid(self):
        result = teleport(0.6, 0.8, seed=42)
        assert result['correction_gate'] in ['I', 'Z', 'X', 'ZX']


# ─── Statistical Verification ────────────────────────────────────────────────

class TestVerification:
    def test_verify_teleportation_high_fidelity(self):
        result = verify_teleportation(0.6, 0.8, n_trials=500, seed=42)
        assert result['average_fidelity'] > 0.99
        assert result['all_fidelities_above_099']

    def test_verify_outcome_distribution(self):
        result = verify_teleportation(0.6, 0.8, n_trials=1000, seed=42)
        # Each outcome should occur roughly 25% of the time
        for outcome, prob in result['outcome_distribution'].items():
            assert 0.15 < prob < 0.35

    def test_verify_different_states(self):
        for alpha, beta in [(1, 0), (0, 1), (0.6, 0.8)]:
            result = verify_teleportation(alpha, beta, n_trials=200, seed=42)
            assert result['average_fidelity'] > 0.99


# ─── State Tomography ────────────────────────────────────────────────────────

class TestTomography:
    def test_tomography_zero_state(self):
        tomo = state_tomography([complex(1, 0), complex(0, 0)])
        _, _, bz = tomo['bloch_vector']
        assert abs(bz - 1.0) < 1e-10

    def test_tomography_one_state(self):
        tomo = state_tomography([complex(0, 0), complex(1, 0)])
        _, _, bz = tomo['bloch_vector']
        assert abs(bz + 1.0) < 1e-10

    def test_tomography_plus_state(self):
        tomo = state_tomography([complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))])
        bx, _, _ = tomo['bloch_vector']
        assert abs(bx - 1.0) < 1e-10

    def test_tomography_trace_one(self):
        tomo = state_tomography([complex(0.6), complex(0.8)])
        assert abs(tomo['trace'] - 1.0) < 1e-10

    def test_tomography_purity(self):
        # Pure state has purity 1
        tomo = state_tomography([complex(0.6), complex(0.8)])
        assert abs(tomo['purity'] - 1.0) < 1e-10

    def test_tomography_invalid_state(self):
        with pytest.raises(ValueError):
            state_tomography([complex(1, 0), complex(0, 0), complex(0, 0)])


# ─── Circuit Description ────────────────────────────────────────────────────

class TestCircuit:
    def test_describe_circuit(self):
        desc = describe_circuit()
        assert 'Bell' in desc
        assert 'CNOT' in desc
        assert 'correction' in desc.lower()


# ─── CLI Tests ───────────────────────────────────────────────────────────────

class TestCLI:
    def test_teleport_command(self):
        from cli import main
        assert main(["teleport", "--state", "|+⟩", "--seed", "42"]) == 0

    def test_teleport_tomography(self):
        from cli import main
        assert main(["teleport", "--state", "|0⟩", "--seed", "42", "--tomography"]) == 0

    def test_verify_command(self):
        from cli import main
        assert main(["verify", "--state", "|+⟩", "--trials", "100", "--seed", "42"]) == 0

    def test_bell_command(self):
        from cli import main
        assert main(["bell"]) == 0

    def test_circuit_command(self):
        from cli import main
        assert main(["circuit"]) == 0

    def test_tomography_command(self):
        from cli import main
        assert main(["tomography", "--state", "|+⟩"]) == 0
