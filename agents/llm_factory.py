"""
Deterministic mock adapter with identifier screening; external LLM clients are not implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Quantum Teleportation Protocol"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} mock]: No model inference or external "
            "verification was performed. The query passed identifier screening."
        )


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Quantum Teleportation Protocol"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(
            f"Model provider '{provider}' is unavailable. Only the deterministic "
            "mock provider is implemented; no external model is contacted."
        )
