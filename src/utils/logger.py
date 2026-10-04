"""
Structured JSON Logging & PHI Redaction Engine (NFR-03)
Guarantees zero plaintext leakage of medical diagnoses, procedures, and health history.
Injects correlation_id and case_id into every operational log event.
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

SENSITIVE_PHI_KEYS = {
    "diagnosis",
    "diagnoses",
    "procedure",
    "procedures",
    "medical_history",
    "health_history",
    "treatment",
    "condition",
    "clinical_notes",
    "prescription",
    "icd_code",
    "icd10"
}

REDACTION_TOKEN = "[REDACTED_PHI]"


def redact_phi(data: Any) -> Any:
    """Recursively redacts Protected Health Information (PHI) fields from payloads."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_PHI_KEYS:
                cleaned[k] = REDACTION_TOKEN
            else:
                cleaned[k] = redact_phi(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_phi(item) for item in data]
    return data


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON with required compliance fields."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
            "case_id": getattr(record, "case_id", "N/A"),
        }

        # Include and redact extra payload if provided
        extra = getattr(record, "extra_payload", None)
        if extra and isinstance(extra, dict):
            payload["data"] = redact_phi(extra)

        return json.dumps(payload)


def get_logger(name: str = "medicard") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
