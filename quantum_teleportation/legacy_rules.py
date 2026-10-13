"""Compatibility threshold rules for the legacy audit CLI and coordinator.

These generic numerical checks are not quantum-state validation or
proof of compliance with the Bennett teleportation protocol.
"""


class FrontierDomainEngine:
    """Evaluate the existing threshold-based diagnostic workflow."""

    @staticmethod
    def evaluate_primary_parameter(value: float):
        if value > 25.0:
            return {
                "summary": "Primary Metric Threshold Exceeded",
                "details": f"Primary measurement {value:.2f} exceeds configured limit 25.00.",
                "remediation": "Review the configured limit and input measurement.",
            }
        return None

    @staticmethod
    def evaluate_secondary_kinetics(value: float, critical: bool):
        if critical or value > 12.0:
            return {
                "summary": "Secondary Metric or Critical Flag Triggered",
                "details": f"Secondary measurement {value:.2f}; critical flag {critical}.",
                "remediation": "Review the flagged record and configured thresholds.",
            }
        return None

    @staticmethod
    def audit_specification_conformance(descriptor: str, attributes: dict):
        if any(token in descriptor.upper() for token in
               ("DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT")):
            return {
                "summary": "Descriptor Indicates Discordance",
                "details": f"Descriptor '{descriptor}' matched an anomaly keyword.",
                "remediation": "Review the descriptor and associated metadata.",
            }
        return None
