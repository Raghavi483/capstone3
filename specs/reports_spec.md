# Feature Specification: Reports & Cashless Analytics
**Feature**: Operational Reports & Business Intelligence  
**Specification File**: `specs/reports_spec.md`  
**Version**: 1.0.0  

---

## 1. Purpose
Defines operational reports, business metrics, and analytical endpoints for pre-auth turnaround times, settlement volumes, query rates by hospital, top admission diagnoses, and average loss ratio computations.

---

## 2. Actors
- **Insurer Administrator**: Reviews operational metrics and provider compliance.
- **Claims Operations Manager**: Analyzes pre-auth turnaround times and query frequency.

---

## 3. Inputs
- Report Filter Query: `from_date`, `to_date`, `hospital_id` (optional), `metric_type`.

---

## 4. Outputs
- Operational Analytics DTO:
  - `pre_auth_turnaround_time_seconds`: Average, median, and 95th percentile TAT.
  - `settlement_volumes`: Total payout amount (Decimal) and count of settled claims.
  - `query_rate_by_hospital`: Dictionary of `{hospital_id: query_percentage}`.
  - `top_diagnoses`: Frequency table of pre-auth clinical diagnoses.
  - `average_loss_ratio`: Ratio of total claims settled to total earned premium.

---

## 5. Domain Rules
1. **Rule REP-01 (Privacy in Analytics)**: Aggregate reports must never expose patient identities or member names.
2. **Rule REP-02 (Monetary Precision)**: Financial metrics (total settlement volumes, average claim payout) must be formatted in fixed-point decimal arithmetic.

---

## 6. Security Rules
- Only users with role `INSURER` or `ADMIN` can access analytics and reporting endpoints.

---

## 7. Acceptance Criteria
- **AC-REP-01**: Admin can retrieve average pre-authorization turnaround time across all network hospitals.
- **AC-REP-02**: Admin can retrieve query rate breakdown by hospital facility.
- **AC-REP-03**: System calculates total settled payout volume and loss ratio without floating-point errors.
