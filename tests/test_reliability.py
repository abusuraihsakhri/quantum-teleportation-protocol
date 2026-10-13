"""Regression tests for mathematical correctness, API compatibility and audit integrity."""
import math
import random

import pytest

from agents.base import AuditTrail
from quantum_teleportation.engine import teleport, verify_teleportation, state_tomography


@pytest.mark.parametrize("alpha,beta", [
    (1, 0),
    (0, 1),
    (1, 1),
    (1, -1),
    (1, 1j),
    (0.6 + 0.2j, 0.3 - 0.7j),
])
@pytest.mark.parametrize("seed", [0, 1, 42, 1234])
def test_teleport_random_outcomes_preserve_state(alpha, beta, seed):
    result = teleport(alpha, beta, seed=seed)
    assert result["fidelity"] == pytest.approx(1.0, abs=1e-12)
    assert result["correction_gate"] == ["I", "X", "Z", "ZX"][result["bell_measurement"]]
    assert result["bell_measurement_binary"] == format(result["bell_measurement"], "02b")


def test_state_tomography_pauli_y_orientation():
    s = [1 / math.sqrt(2), 1j / math.sqrt(2)]
    assert state_tomography(s)["bloch_vector"] == pytest.approx((0, 1, 0), abs=1e-12)
    s = [1 / math.sqrt(2), -1j / math.sqrt(2)]
    assert state_tomography(s)["bloch_vector"] == pytest.approx((0, -1, 0), abs=1e-12)


@pytest.mark.parametrize("alpha,beta", [(0, 0), (float("nan"), 0), (float("inf"), 1)])
def test_invalid_amplitudes_raise_value_error(alpha, beta):
    with pytest.raises(ValueError):
        teleport(alpha, beta)


@pytest.mark.parametrize("trials", [0, -1, 1.5])
def test_invalid_trials_raise_value_error(trials):
    with pytest.raises(ValueError):
        verify_teleportation(1, 0, n_trials=trials)


def test_rng_does_not_change_global_state():
    random.seed(987654)
    previous_state = random.getstate()
    first = teleport(1, 1, seed=41)
    second = teleport(1, 1, seed=41)
    assert first["bell_measurement"] == second["bell_measurement"]
    assert random.getstate() == previous_state
    verify_teleportation(1, 0, n_trials=15, seed=42)
    assert random.getstate() == previous_state


def test_audit_rejects_modified_signature():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("worker", "tier", "event", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[0]["current_hash"] = "f" * 64
    assert not trail.verify_integrity()


def test_audit_rejects_tampered_fields_even_with_consistent_chain():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("worker", "tier", "event", {"status": "OK"})
    trail.log("worker", "tier", "other", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "altered"
    assert not trail.verify_integrity()


def test_audit_log_api_returns_defensive_copies():
    trail = AuditTrail(secret_key="test-only-key")
    entry = trail.log("worker", "tier", "event", {"status": "OK"})
    entry["event_type"] = "altered"
    exposed = trail.get_trail()
    exposed[0]["event_type"] = "altered"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["event_type"] == "event"


def test_legacy_coordinator_and_cli_importable(capsys):
    from quantum_teleportation.cli import main
    assert main(["audit", "--task-id", "TEST-001", "--primary", "29"]) == 0
    assert "TEST-001" in capsys.readouterr().out
