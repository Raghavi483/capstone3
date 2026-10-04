# Architecture Blueprint: MediCard Cashless Hospitalization & Settlement Platform
**Document ID**: ARCH-BC-017  
**Version**: 1.0.0  
**Target Domain**: Insurance — Health Cashless  

---

## 1. Architectural Principles & Layered Architecture

MediCard implements a clean, layered architecture designed to enforce domain isolation, strict dependency direction, testability, and non-negotiable compliance rules.

```
       +-------------------------------------------------------+
       |                   Presentation Layer                  |
       |     (Responsive Web SPA / Customer, Hospital, Insurer) |
       +-------------------------------------------------------+
                                  |
                                  v
       +-------------------------------------------------------+
       |                   Controller Layer                    |
       |  (FastAPI REST Endpoints, Role Auth Boundaries, DTOs) |
       +-------------------------------------------------------+
                                  |
                                  v
       +-------------------------------------------------------+
       |                    Service Layer                      |
       | (Orchestration, Transaction Control, Notification Bus)|
       +-------------------------------------------------------+
                                  |
                                  v
       +-------------------------------------------------------+
       |                     Domain Layer                      |
       | (Business Rules, Invariants, State Machine, Entities) |
       |     * ZERO DEPENDENCIES ON OUTER LAYERS OR DB *       |
       +-------------------------------------------------------+
                                  |
                                  v
       +-------------------------------------------------------+
       |                  Repository Layer                     |
       |   (SQLAlchemy ORM Data Access, Append-Only Ledger)    |
       +-------------------------------------------------------+
                                  |
                                  v
       +-------------------------------------------------------+
       |                    Database Layer                     |
       |          (SQLite Engine / In-Memory Test DB)          |
       +-------------------------------------------------------+
```

### Layer Responsibilities & Strict Dependency Rules

1. **Presentation Layer (`frontend/`)**:
   - Multi-party responsive user interface serving Customer, Hospital, Adjudicator, and Admin personas.
   - Communicates exclusively with the Controller layer via typed REST APIs.
2. **Controller Layer (`src/controllers/`)**:
   - HTTP request parsing, input validation using Pydantic schemas, and serialization.
   - Enforces **NFR-04** Authentication & Role Boundaries (`CUSTOMER`, `HOSPITAL`, `INSURER`, `ADMIN`).
   - Generates structured JSON request context (`request_id`, `correlation_id`) for **NFR-06**.
   - Dependent *only* on the Service layer.
3. **Service Layer (`src/services/`)**:
   - Orchestrates domain rule execution, coordinates repositories, and publishes stubbed notifications (**AC-09**).
   - Manages database transaction boundaries and audit event dispatch.
   - Dependent on the Domain and Repository interfaces.
4. **Domain Layer (`src/domain/`)**:
   - **The core source of truth for business logic**. Contains pure business rules, entities, and state machines.
   - **Strict Rule**: Domain rules MUST NOT import or depend directly on controllers, services, database drivers, or HTTP frameworks.
   - Enforces **NFR-01** fixed-point decimal arithmetic, settlement cap invariants, and `InvalidClaimStateException`.
5. **Repository Layer (`src/repositories/`)**:
   - Encapsulates database queries, persistence models, and table mappings via SQLAlchemy.
   - Enforces **NFR-02** and **NFR-05** append-only persistence semantics for decisions, bills, overrides, and settlements.
6. **Database Layer**:
   - Relational store (SQLite) with versioned, forward-only schemas.

---

## 2. End-to-End Eligibility-to-Settlement Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Policyholder
    actor Hospital as Network Hospital
    actor Adjudicator as Insurer Adjudicator / Admin
    participant API as Controller Layer
    participant Service as Service Layer
    participant Domain as Domain Rules & State Machine
    participant Repo as Repository & Audit Ledger
    participant Notify as Notification Bus

    %% 1. Registration & Policy Linking
    Customer->>API: Register & Link Policy (AC-01)
    API->>Service: LinkPolicyCommand
    Service->>Repo: Persist Customer & Policy
    Repo-->>Service: Customer Registered
    Service-->>API: Return Coverage Details (Sum Insured, Exclusions, Networks)

    %% 2. Hospital Eligibility Verification
    Hospital->>API: Lookup Eligibility (member_id, policy_id) (AC-02)
    API->>Service: VerifyEligibilityQuery
    Service->>Domain: Evaluate Eligibility Rules (eligibility_rule.py)
    Domain-->>Service: ELIGIBLE / NOT_ELIGIBLE + Reason Codes
    Service-->>API: Return Status & Coverage Cap

    %% 3. Pre-Authorization Submission & Decisioning
    Hospital->>API: Submit Pre-Auth (Diagnosis, Est. Cost, Date) (AC-03)
    API->>Service: CreatePreAuthCommand
    Service->>Domain: Evaluate Auto-Approval Rules (pre_auth_rule.py) (AC-05)
    alt Cost <= Threshold AND Diagnosis Auto-Approved
        Domain-->>Service: Auto-Approved (up to Policy Cap)
        Service->>Repo: Append PreAuthDecision(APPROVED, reason="AUTO_APPROVED")
        Service->>Notify: Dispatch Transition Notification (AC-09)
    else Exceeds Threshold or Non-Auto Diagnosis
        Domain-->>Service: PENDING / QUERY_RAISED (AC-04)
        Service->>Repo: Append PreAuthDecision(PENDING)
        Adjudicator->>API: Manual Review / Override (AC-10)
        API->>Service: ExecuteOverrideCommand(reason, actor, timestamp)
        Service->>Domain: Validate Admin Authority (role_boundary_rule.py)
        Service->>Repo: Append AuditEntry(OVERRIDE_APPROVED)
    end

    %% 4. Admission Tracking
    Hospital->>API: Record Patient Admission (AC-08)
    API->>Service: TransitionClaimState(ADMITTED)
    Service->>Domain: Validate Transition (PRE_AUTH -> ADMITTED)
    Domain-->>Service: Valid Transition
    Service->>Repo: Update Claim State & Append Audit
    Service->>Notify: Notify Customer & Hospital

    %% 5. Final Bill Submission
    Hospital->>API: Submit Procedures & Final Bill (AC-06)
    API->>Service: SubmitFinalBillCommand(final_bill)
    Service->>Domain: Validate Bill Cap (final_bill <= pre_auth + buffer)
    Domain-->>Service: Valid Bill Cap
    Service->>Repo: Append FinalBillRecord

    %% 6. Settlement Calculation & Discharge
    Hospital->>API: Discharge & Request Settlement (AC-07, AC-08)
    API->>Service: CalculateSettlementCommand
    Service->>Domain: Calculate Settlement (settlement_rule.py)
    Note over Domain: settlement = min(bill, pre_auth + buffer) - deductible - co_pay<br/>Invariant: settlement >= 0 (Decimal)
    Domain-->>Service: Settlement Payout (Decimal)
    Service->>Repo: Append SettlementRecord & Transition State(SETTLED)
    Service->>Notify: Dispatch Final Settlement Summary to Customer & Hospital
    Service-->>API: Settlement Completed
```

---

## 3. Data Flow & Security Boundaries

```mermaid
flowchart TD
    subgraph External["External Actors"]
        C["Customer Portal (Role: CUSTOMER)"]
        H["Hospital Portal (Role: HOSPITAL)"]
        I["Insurer Desk (Role: INSURER / ADMIN)"]
    end

    subgraph SecurityBoundary["Security & Authentication Boundary (NFR-04)"]
        AuthMiddleware["FastAPI Role Verification & JWT Middleware"]
        TenancyGuard["Hospital Isolation Guard (Own cases only)"]
        PhiInterceptor["Structured Logging & PHI Masking Interceptor (NFR-03, NFR-06)"]
    end

    subgraph CorePlatform["Core Application Engine"]
        Controllers["API Controllers"]
        Services["Orchestration Services"]
        
        subgraph DomainEngine["Domain Logic (Pure Business Rules)"]
            EligibilityRules["eligibility_rule.py"]
            PreAuthRules["pre_auth_rule.py"]
            ClaimStateMachine["claim_state_rule.py (AC-08)"]
            SettlementCalculator["settlement_rule.py (Decimal / AC-07)"]
            RoleBoundaryRules["role_boundary_rule.py"]
        end
    end

    subgraph Persistence["Append-Only Persistence Layer (NFR-02)"]
        AppDB[(Operational State DB)]
        AuditLedger[(Immutable Audit Event Ledger)]
    end

    C --> AuthMiddleware
    H --> AuthMiddleware
    I --> AuthMiddleware

    AuthMiddleware --> TenancyGuard
    TenancyGuard --> PhiInterceptor
    PhiInterceptor --> Controllers

    Controllers --> Services
    Services --> DomainEngine
    Services --> Persistence
```

---

## 4. Key Architectural Safeguards & NFR Mapping

| Requirement | Architectural Mechanism | Verification Test |
| :--- | :--- | :--- |
| **NFR-01 (Fixed-Point Arithmetic)** | All monetary fields (`estimated_cost`, `final_bill`, `pre_auth_amount`, `deductible`, `co_pay`, `settlement_amount`) are declared as `decimal.Decimal`. Prohibit `float` casting in domain calculations. | `tests/unit/test_ac07_settlement.py` and hook `settlement-cap-check` |
| **NFR-02 (Append-Only Ledger)** | Tables `pre_auth_decisions`, `claim_bills`, `claim_settlements`, and `audit_logs` have INSERT-only access with database-level immutability constraints. | `tests/architecture/test_append_only_rules.py` |
| **NFR-03 (PHI Redaction)** | Logging filter scrubs diagnostic terms, ICD codes, and clinical procedure text, substituting SHA-256 hashes or redacting to `[REDACTED_PHI]`. | `tests/architecture/test_phi_redaction.py` and hook `phi-redaction-check` |
| **NFR-04 (Role & Tenant Isolation)** | Hospital ID claims are compared against route parameters; hospitals cannot query cases belonging to other facilities. Admin routes require `INSURER` or `ADMIN` roles. | `tests/unit/test_role_boundary.py` |
| **NFR-06 (Structured JSON Logs)** | Application logger outputs single-line JSON with `request_id`, `correlation_id`, `case_id`, `actor`, and `event`. | `tests/unit/test_logging.py` |
| **NFR-07 (Health Endpoint SLA)** | `/health` returns `{"status": "healthy", "database": "connected"}` in < 100ms. | API integration test |
| **NFR-08 (Architecture Rules as Tests)** | Automated tests under `tests/architecture/` verify that controllers are not imported by domain modules, settlement formulas are not duplicated, and settled claims cannot be modified. | `tests/architecture/test_layer_dependencies.py` |
