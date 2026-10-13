"""
CLI for Quantum Teleportation Protocol.
Provides commands for teleportation simulation, verification, and state analysis.
"""
import argparse
import cmath
import math
import sys

from quantum_teleportation.engine import (
    teleport, verify_teleportation, state_tomography,
    bell_state, prepare_bell_pair, describe_circuit,
    fidelity, state_probabilities,
)


def cmd_teleport(args):
    """Execute quantum teleportation."""
    # Parse alpha and beta
    if args.state == '|0⟩':
        alpha, beta = complex(1, 0), complex(0, 0)
    elif args.state == '|1⟩':
        alpha, beta = complex(0, 0), complex(1, 0)
    elif args.state == '|+⟩':
        alpha, beta = complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))
    elif args.state == '|-⟩':
        alpha, beta = complex(1 / math.sqrt(2)), complex(-1 / math.sqrt(2))
    elif args.state == '|i+⟩':
        alpha, beta = complex(1 / math.sqrt(2)), complex(0, 1 / math.sqrt(2))
    else:
        # Parse custom state
        parts = args.state.split(',')
        alpha = complex(parts[0])
        beta = complex(parts[1])
    
    result = teleport(alpha, beta, seed=args.seed)
    
    print(f"Quantum Teleportation:")
    print(f"  Target state: α={result['alpha']:.6f}, β={result['beta']:.6f}")
    print(f"  Bell measurement: |{['Φ+', 'Ψ+', 'Φ-', 'Ψ-'][result['bell_measurement']]}⟩ "
          f"(classical bits: {result['bell_measurement_binary']})")
    print(f"  Bell probabilities: {[f'{p:.4f}' for p in result['bell_probabilities']]}")
    print(f"  Correction gate: {result['correction_gate']}")
    print(f"  Bob's state: {result['bob_state_after_correction']}")
    print(f"  Fidelity: {result['fidelity']:.10f}")
    print(f"  Success: {result['success']}")
    
    if args.tomography:
        print(f"\n  State Tomography (Bob's qubit):")
        tomo = state_tomography(result['bob_state_after_correction'])
        bx, by, bz = tomo['bloch_vector']
        print(f"    Bloch vector: ({bx:.6f}, {by:.6f}, {bz:.6f})")
        print(f"    Purity: {tomo['purity']:.6f}")
        print(f"    Trace: {tomo['trace']:.6f}")
    return 0


def cmd_verify(args):
    """Verify teleportation fidelity over many trials."""
    if args.state == '|+⟩':
        alpha, beta = complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))
    elif args.state == '|0⟩':
        alpha, beta = complex(1, 0), complex(0, 0)
    elif args.state == '|1⟩':
        alpha, beta = complex(0, 0), complex(1, 0)
    elif args.state == '|-⟩':
        alpha, beta = complex(1 / math.sqrt(2)), complex(-1 / math.sqrt(2))
    elif args.state == '|i+⟩':
        alpha, beta = complex(1 / math.sqrt(2)), complex(0, 1 / math.sqrt(2))
    else:
        parts = args.state.split(',')
        if len(parts) != 2:
            raise ValueError("Specify a supported state or two comma-separated complex amplitudes")
        alpha = complex(parts[0])
        beta = complex(parts[1])

    result = verify_teleportation(alpha, beta, n_trials=args.trials, seed=args.seed)
    
    print(f"Teleportation Verification ({result['n_trials']} trials):")
    print(f"  Average fidelity: {result['average_fidelity']:.10f}")
    print(f"  Min fidelity:     {result['min_fidelity']:.10f}")
    print(f"  Max fidelity:     {result['max_fidelity']:.10f}")
    print(f"  All fidelities > 0.99: {result['all_fidelities_above_099']}")
    print(f"\n  Bell measurement outcome distribution:")
    for outcome, prob in result['outcome_distribution'].items():
        names = ['|Φ+⟩', '|Ψ+⟩', '|Φ-⟩', '|Ψ-⟩']
        print(f"    {names[outcome]}: {prob:.4f}")
    return 0


def cmd_bell(args):
    """Display Bell states."""
    print("Bell States:")
    names = ['|Φ+⟩', '|Φ-⟩', '|Ψ+⟩', '|Ψ-⟩']
    formulas = [
        '1/√2(|00⟩ + |11⟩)',
        '1/√2(|00⟩ - |11⟩)',
        '1/√2(|01⟩ + |10⟩)',
        '1/√2(|01⟩ - |10⟩)',
    ]
    for i in range(4):
        state = bell_state(i)
        probs = state_probabilities(state)
        print(f"  {names[i]} = {formulas[i]}")
        print(f"    Amplitudes: {[f'{a:.4f}' for a in state]}")
        print(f"    Probabilities: {[f'{p:.4f}' for p in probs]}")
        print()
    
    # Verify Bell pair preparation
    prepared = prepare_bell_pair()
    expected = bell_state(0)
    fid = fidelity(expected, prepared)
    print(f"  Bell pair preparation fidelity: {fid:.10f}")
    return 0


def cmd_circuit(args):
    """Display the teleportation circuit description."""
    print(describe_circuit())
    return 0


def cmd_tomography(args):
    """Perform state tomography on a qubit state."""
    if args.state == '|0⟩':
        state = [complex(1, 0), complex(0, 0)]
    elif args.state == '|1⟩':
        state = [complex(0, 0), complex(1, 0)]
    elif args.state == '|+⟩':
        state = [complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))]
    elif args.state == '|-⟩':
        state = [complex(1 / math.sqrt(2)), complex(-1 / math.sqrt(2))]
    else:
        parts = args.state.split(',')
        state = [complex(parts[0]), complex(parts[1])]
    
    tomo = state_tomography(state)
    print(f"State Tomography:")
    print(f"  State: [{state[0]:.6f}, {state[1]:.6f}]")
    print(f"  Density matrix:")
    for row in tomo['density_matrix']:
        print(f"    [{row[0].real:+.6f}{row[0].imag:+.6f}i  {row[1].real:+.6f}{row[1].imag:+.6f}i]")
    bx, by, bz = tomo['bloch_vector']
    print(f"  Bloch vector: ({bx:.6f}, {by:.6f}, {bz:.6f})")
    print(f"  Purity: {tomo['purity']:.6f}")
    print(f"  Trace: {tomo['trace']:.6f}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="quantum-teleportation-protocol",
        description="Quantum Teleportation Protocol — real quantum state simulation"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # teleport
    p = sub.add_parser("teleport", help="Execute teleportation protocol")
    p.add_argument("--state", type=str, default="|+⟩",
                   help="State to teleport: |0⟩, |1⟩, |+⟩, |-⟩, |i+⟩, or α,β")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--tomography", action="store_true", help="Show state tomography")

    # verify
    p = sub.add_parser("verify", help="Verify teleportation over many trials")
    p.add_argument("--state", type=str, default="|+⟩", help="State to teleport")
    p.add_argument("--trials", type=int, default=1000, help="Number of trials")
    p.add_argument("--seed", type=int, default=42, help="Random seed")

    # bell
    sub.add_parser("bell", help="Display Bell states")

    # circuit
    sub.add_parser("circuit", help="Display circuit description")

    # tomography
    p = sub.add_parser("tomography", help="State tomography analysis")
    p.add_argument("--state", type=str, default="|+⟩", help="State to analyze")

    args = parser.parse_args(argv)
    handlers = {
        'teleport': cmd_teleport,
        'verify': cmd_verify,
        'bell': cmd_bell,
        'circuit': cmd_circuit,
        'tomography': cmd_tomography,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
