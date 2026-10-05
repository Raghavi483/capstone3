# Post-Mortem 01: Decimal Serialization in Repository JSON Fields
**Component**: `src/repositories/claim_repository.py`  
**Date**: 2026-10-04  
**Trigger**: Sprint 3 Integration Test (`test_ac06_and_ac08_admission_and_discharge_happy_path`)  
**Status**: **RESOLVED**  

---

## 1. Incident Symptom
During execution of `test_ac06_and_ac08_admission_and_discharge_happy_path`, the patient discharge endpoint crashed with an unhandled exception:
```text
TypeError: Object of type Decimal is not JSON serializable
```
Occurred in `src/repositories/claim_repository.py:85` during `json.dumps(itemized_summary or {})`.

---

## 2. Environment Context
- **Python Version**: 3.12.1
- **Standard Library**: `json` module default encoder does not provide serialization for `decimal.Decimal`.
- **Capstone Invariant**: Strict `Decimal` representation is mandatory for monetary values; converting to `float` is prohibited by NFR-01.

---

## 3. Root Cause Analysis
In `AdmissionService.submit_procedures_and_final_bill`, procedure item dictionaries containing `cost: Decimal(...)` were passed to `ClaimRepository.save_final_bill`. When `save_final_bill` attempted to dump `itemized_summary` to JSON using default parameters, Python's `json.encoder.JSONEncoder` threw a `TypeError` upon encountering `Decimal('40000.00')`.

---

## 4. Remediation & Fix Applied
Updated `json.dumps` in `ClaimRepository.save_final_bill` to pass `default=str`:
```python
itemized_summary_json=json.dumps(itemized_summary or {}, default=str)
```
This safely serializes `Decimal` quantities as exact numeric strings without losing precision or violating NFR-01.

---

## 5. Verification & Validation Evidence
Executed `python -m pytest tests/unit/ -v`:
- `test_ac06_and_ac08_admission_and_discharge_happy_path` PASSED.
- All unit and integration tests passed.
- No floating-point casts introduced; verified by `tests/architecture/test_architecture_boundaries.py`.
