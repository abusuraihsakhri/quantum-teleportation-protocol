# Quantum Teleportation Protocol

> **Domain:** Quantum Information & Post-Quantum Cryptography
> **Standards:** Bennett et al. 1993 Quantum Teleportation Protocol

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)

</div>

---

## 📖 What It Does

A Python implementation of the quantum teleportation protocol (Bennett et al., 1993) using state vector simulation. The project simulates the teleportation of an arbitrary qubit state from Alice to Bob using a shared Bell pair and classical communication.

The project also includes an enterprise agent framework with PHI (Protected Health Information) guardrails, HMAC-SHA256 audit trails, and a FastAPI REST API server.

---

## ⚙️ Key Features

- **Quantum Teleportation Engine**: Full state vector simulation of the 3-qubit teleportation protocol
- **Bell State Measurement**: Complete Bell state analysis and tomography
- **State Tomography**: Density matrix reconstruction and Bloch sphere coordinates
- **Statistical Verification**: Multi-trial fidelity verification
- **PHI Guard**: Outbound data inspection blocking sensitive identifiers (MRN, SSN, phone, email)
- **HMAC-SHA256 Audit Trail**: Cryptographically chained, tamper-evident logging
- **FastAPI REST API**: REST endpoints for audit and chat operations
- **CLI Interface**: Command-line tools for teleportation simulation and analysis

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/quantum-teleportation-protocol.git
cd quantum-teleportation-protocol

# Install dependencies (stdlib-only core, optional FastAPI for web server)
pip install -e .

# Optional: Install FastAPI dependencies for the REST server
pip install fastapi uvicorn pydantic
```

---

## 🚀 Usage

### Quantum Teleportation CLI

```bash
# Run teleportation with default |+⟩ state
python cli.py teleport

# Teleport a specific state
python cli.py teleport --state "|0⟩" --seed 42
python cli.py teleport --state "|1⟩" --seed 42
python cli.py teleport --state "|-⟩" --seed 42

# Teleport with state tomography
python cli.py teleport --state "|+⟩" --seed 42 --tomography

# Verify teleportation fidelity over many trials
python cli.py verify --state "|+⟩" --trials 1000 --seed 42

# Display Bell states
python cli.py bell

# Show circuit description
python cli.py circuit

# Perform state tomography
python cli.py tomography --state "|+⟩"
```

### Enterprise Agent CLI

```bash
# Run a single audit task
python -m quantum_teleportation.cli audit --task-id "TASK-001" --primary 29.4 --secondary 15.1

# Batch process CSV records
python -m quantum_teleportation.cli batch -i sample.csv -o results.csv

# Launch FastAPI REST server
python -m quantum_teleportation.cli serve --host 127.0.0.1 --port 8000
```

### REST API Endpoints

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus-style metrics |
| `/api/audit` | POST | Process a task payload |
| `/api/chat` | POST | Query the supervisory chat |
| `/api/audit/logs` | GET | Retrieve audit trail |

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=quantum_teleportation --cov=agents
```

---

## 📁 Project Structure

```
quantum-teleportation-protocol/
├── cli.py                          # Root CLI (teleportation commands)
├── quantum_teleportation/
│   ├── engine.py                   # Core quantum teleportation engine
│   ├── cli.py                      # Enterprise agent CLI
│   ├── agents.py                   # Agent coordination
│   ├── models.py                   # Data models
│   └── server.py                   # FastAPI server
├── agents/
│   ├── base.py                     # PHI guard, audit trail
│   ├── models.py                   # Pydantic schemas
│   ├── workers.py                  # Specialized workers
│   ├── supervisor.py               # Supervisor orchestrator
│   ├── api.py                      # FastAPI endpoints
│   ├── llm_factory.py              # LLM provider factory
│   ├── learning.py                 # Bayesian calibration
│   ├── metrics.py                  # Prometheus metrics
│   └── streamer.py                 # WebSocket telemetry
├── tests/
│   ├── test_quantum_teleportation.py
│   ├── test_quantum_teleportation_protocol.py
│   └── test_enrichment.py
├── web/
│   └── index.html                  # Operations console
├── enrichment.py                   # Enrichment feature engines
├── simulator.py                    # High-throughput simulator
├── pyproject.toml                  # Project configuration
└── README.md
```

---

## 🔒 Security

- **PHI Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **Audit Trail**: HMAC-SHA256 chained, tamper-evident logging
- **Path Traversal Protection**: Input/output file paths validated against current working directory
- **Ephemeral Key Generation**: Random audit key generated if `AUDIT_SECRET_KEY` env var not set

---

## 🐳 Docker

```bash
docker build -t quantum-teleportation-protocol .
docker run -p 8000:8000 quantum-teleportation-protocol
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
