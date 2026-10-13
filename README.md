# Quantum Teleportation Protocol

An ideal, noiseless implementation of the **Bennett et al. (1993) three-qubit quantum teleportation protocol**. The Python state-vector simulator uses only the standard library. A separate, static browser simulator is available in [docs/index.html](docs/index.html); it uses native JavaScript and does not require a server.

## Features

- Teleport a normalized qubit with real or complex amplitudes through a three-qubit state vector.
- Prepare Bell states; perform Alice's two-bit measurement and Bob's conditional Pauli correction.
- Calculate pure-state fidelity, density matrices and Bloch coordinates; verify outcome frequencies over repeated trials.
- Run a dependency-free browser visualization with Bloch-angle presets, seeded measurements, verification and JSON export.
- Optional **separate** threshold-audit CLI and FastAPI server with heuristic identifier checks and an HMAC-chained, in-memory log.

The threshold-audit workflows are generic diagnostics, **not** tests of quantum protocol compliance. Auxiliary `enrichment.py` classes are threshold evaluators; they do not simulate GHZ-state or continuous-variable teleportation. This repository is not an implementation of NIST post-quantum cryptographic algorithms.

## Browser application

Open `docs/index.html` in a modern browser, or serve `docs/` as static files. The browser simulator does not use Pyodide; a small JavaScript implementation avoids the runtime and download overhead of loading Python for a three-qubit circuit. No input data is uploaded, and no external services or local storage are required. Results can be exported as JSON.

GitHub Pages publication is configured by [the Pages workflow](.github/workflows/pages.yml) to deploy `docs/` from `master` **when the repository's Pages settings permit Actions deployment**. The live URL will be added here once it has been verified.

## Python installation

Python 3.9 or later:

```bash
python -m pip install -e .
quantum-teleportation-protocol teleport --state "|+⟩" --seed 42
quantum-teleportation-protocol teleport --state "|i+⟩" --tomography
quantum-teleportation-protocol verify --state "|+⟩" --trials 1000
quantum-teleportation-protocol bell
quantum-teleportation-protocol circuit
```

You can also run `python cli.py teleport` without installing the package. Custom qubits are entered as two comma-separated Python complex numbers, e.g. `--state "0.6+0.2j,0.3-0.7j"`. Input amplitudes are normalized before teleportation. The simulator reports fidelity and Alice's sampled measurement outcome.

## Optional audit API and CLI

Install the additional server dependencies:

```bash
python -m pip install -e ".[server]"
python -m quantum_teleportation.cli audit --task-id TEST-01 --primary 29.4 --secondary 15.1
python -m quantum_teleportation.cli batch -i sample.csv -o results.csv
python -m quantum_teleportation.cli serve --host 127.0.0.1 --port 8000
```

The legacy server offers `GET /health`, `POST /api/audit` and `POST /api/chat`. An alternate agent-based API with `/metrics` and `/api/audit/logs` is available with `uvicorn agents.api:app --host 127.0.0.1 --port 8000`. The backend operations console (`web/index.html`) requires a running API on the **same origin**; unlike the static browser simulator, it does not work as a standalone GitHub Pages app.

To run the legacy server using Docker, use `docker build -t quantum-teleportation-protocol .` and `docker run -p 8000:8000 quantum-teleportation-protocol`. For Compose, generate a random private `AUDIT_SECRET_KEY` and provide it in a local `.env` file (see `.env.example`). Do not commit or publish this key.

## Tests

```bash
python -m pip install -e ".[server,test]"
pytest -q
node --test tests/test_browser_simulator.cjs
```

CI exercises Python 3.10–3.12 and the browser simulation's Node tests. Both the Python simulator and the static web app are intended to work in modern desktop and mobile browsers / supported Python versions respectively. The small JavaScript interface does not require a build step.

## Security and limitations

The audit API uses a heuristic regular-expression identifier filter, **not certified PHI de-identification or HIPAA compliance**. The audit log includes HMAC-SHA256 signatures and chain verification, but is held only in process memory. The server generates a random ephemeral audit key if `AUDIT_SECRET_KEY` is absent; persistent verification across restarts requires a securely supplied persistent key **and independent log persistence**, which this implementation does not provide. Run the API behind appropriate authentication and access controls before any network exposure; these are not implemented by this project.

Quantum teleportation here is a software model of an ideal single-qubit channel, not a physical quantum-network or production cryptographic device. The browser and Python simulators use pseudorandom sampling, not hardware quantum randomness.

## License

MIT; see [LICENSE](LICENSE).
