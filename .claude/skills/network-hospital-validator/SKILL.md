---
name: network-hospital-validator
description: Validates hospital affiliation, tiering, and active network status
---

# Skill: network-hospital-validator

## Purpose
Validates whether a hospital facility is currently recognized as an in-network provider for cashless hospitalization.

## Inputs
- `hospital_id` (string): Facility identifier

## Execution Logic & Rules
1. Query hospital registry by `hospital_id`.
2. Check `active_status == True`.
3. If active, return provider profile, tier, and affiliation status.
4. If missing or suspended, return `is_network: False` with code `HOSP_OUT_OF_NETWORK`.

## Outputs
- `is_network`: boolean
- `tier`: string (`TIER_1` | `TIER_2` | `TIER_3`)
- `status_code`: string
