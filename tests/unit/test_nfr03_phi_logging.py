"""
Test Suite: NFR-03 Structured JSON Logging & PHI Redaction
Requirements:
- Prohibits diagnosis, procedure, medical history from plaintext logs
- Verifies correlation_id and case_id presence
- Validates network hospital domain rule
"""

import json
import logging
from src.utils.logger import redact_phi, StructuredJsonFormatter
from src.domain.network_hospital_rule import NetworkHospitalRule


def test_nfr03_phi_redaction_masks_sensitive_medical_keys():
    """NFR-03: Confirms all PHI keys are masked with [REDACTED_PHI]."""
    raw_payload = {
        "member_id": "MEM-1001",
        "diagnosis": "ACUTE_APPENDICITIS",
        "procedure": "Laparoscopic Appendectomy",
        "medical_history": "Hypertension, Type 2 Diabetes",
        "treatment": "IV Antibiotics",
        "icd10": "K35.80",
        "nested": {
            "condition": "Severe Acute Abdomen",
            "clinical_notes": "Patient presented with lower right quadrant pain"
        }
    }
    redacted = redact_phi(raw_payload)
    assert redacted["member_id"] == "MEM-1001"
    assert redacted["diagnosis"] == "[REDACTED_PHI]"
    assert redacted["procedure"] == "[REDACTED_PHI]"
    assert redacted["medical_history"] == "[REDACTED_PHI]"
    assert redacted["treatment"] == "[REDACTED_PHI]"
    assert redacted["icd10"] == "[REDACTED_PHI]"
    assert redacted["nested"]["condition"] == "[REDACTED_PHI]"
    assert redacted["nested"]["clinical_notes"] == "[REDACTED_PHI]"


def test_nfr03_structured_json_formatter_fields():
    """NFR-03: Formatter injects correlation_id, case_id, timestamp, and redacts extra data."""
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Pre-authorization decision processed",
        args=(),
        exc_info=None
    )
    record.correlation_id = "CORR-9988-77"
    record.case_id = "CLM-3001"
    record.extra_payload = {
        "diagnosis": "Cholecystitis",
        "estimated_cost": "45000.00"
    }

    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    
    assert parsed["level"] == "INFO"
    assert parsed["correlation_id"] == "CORR-9988-77"
    assert parsed["case_id"] == "CLM-3001"
    assert parsed["data"]["diagnosis"] == "[REDACTED_PHI]"
    assert parsed["data"]["estimated_cost"] == "45000.00"


def test_network_hospital_rule_evaluation():
    """Domain Rule: Validates in-network vs out-of-network check."""
    network = ["HOSP-001", "HOSP-002", "HOSP-003"]
    assert NetworkHospitalRule.is_hospital_in_network("HOSP-001", network) is True
    assert NetworkHospitalRule.is_hospital_in_network("HOSP-999", network) is False
    assert NetworkHospitalRule.is_hospital_in_network("", network) is False
    assert NetworkHospitalRule.is_hospital_in_network("HOSP-001", []) is False
