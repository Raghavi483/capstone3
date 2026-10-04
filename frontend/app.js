/**
 * MediCard Frontend Application Logic
 * Integrates with FastAPI REST endpoints at /api/v1/...
 */

const API_BASE = "/api/v1";

document.addEventListener("DOMContentLoaded", () => {
  checkApiHealth();
  setInterval(checkApiHealth, 15000);
  loadPreAuthQueue();
  loadSettlementsReport();
});

// Persona Navigation
function switchPortal(portalName) {
  document.querySelectorAll(".nav-tab").forEach(tab => tab.classList.remove("active"));
  document.querySelectorAll(".portal-panel").forEach(panel => panel.classList.remove("active"));

  const targetTab = document.getElementById(`tab-btn-${portalName}`);
  const targetPanel = document.getElementById(`portal-${portalName}`);

  if (targetTab && targetPanel) {
    targetTab.classList.add("active");
    targetPanel.classList.add("active");
  }

  if (portalName === "insurer") {
    loadPreAuthQueue();
  } else if (portalName === "admin") {
    loadAdminHospitals();
  } else if (portalName === "reports") {
    loadAnalyticsDashboard();
    loadSettlementsReport();
  }
}

// System Health Check (NFR-07)
async function checkApiHealth() {
  const dot = document.getElementById("api-health-dot");
  const text = document.getElementById("api-health-text");
  const latencySpan = document.getElementById("api-latency");

  const start = performance.now();
  try {
    const res = await fetch("/health");
    const duration = Math.round(performance.now() - start);
    if (res.ok) {
      dot.className = "status-indicator live";
      text.innerHTML = `API Online (<span id="api-latency">${duration}ms</span>)`;
    } else {
      dot.className = "status-indicator";
      dot.style.background = "#f43f5e";
      text.innerText = "API Degraded";
    }
  } catch (err) {
    dot.className = "status-indicator";
    dot.style.background = "#f43f5e";
    text.innerText = "API Offline";
  }
}

// 1. Customer Registration (AC-01)
async function handleCustomerRegistration(e) {
  e.preventDefault();
  const payload = {
    member_id: document.getElementById("reg-member-id").value.trim(),
    name: document.getElementById("reg-name").value.trim(),
    email: document.getElementById("reg-email").value.trim(),
    phone: document.getElementById("reg-phone").value.trim(),
    policy_id: document.getElementById("reg-policy-id").value.trim(),
    product_name: document.getElementById("reg-product-name").value.trim(),
    sum_insured: document.getElementById("reg-sum-insured").value.trim(),
    exclusions: document.getElementById("reg-exclusions").value.split(",").map(s => s.trim()).filter(Boolean)
  };

  try {
    const res = await fetch(`${API_BASE}/customers/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      alert(`Customer registered successfully! Linked to policy ${data.coverage.policy_id}.`);
      document.getElementById("lookup-member-id").value = payload.member_id;
      document.getElementById("lookup-policy-id").value = payload.policy_id;
      fetchCoverage();
    } else {
      alert(`Registration error: ${data.detail || "Unknown error"}`);
    }
  } catch (err) {
    alert(`Failed to register: ${err.message}`);
  }
}

// 2. Fetch Coverage Details (AC-01)
async function fetchCoverage() {
  const memberId = document.getElementById("lookup-member-id").value.trim();
  const policyId = document.getElementById("lookup-policy-id").value.trim();
  const card = document.getElementById("coverage-card");

  try {
    const res = await fetch(`${API_BASE}/customers/${memberId}/policies/${policyId}/coverage`);
    if (!res.ok) {
      alert("Policy coverage record not found.");
      card.style.display = "none";
      return;
    }
    const data = await res.json();
    document.getElementById("cov-sum-insured").innerText = `₹${parseFloat(data.sum_insured).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("cov-remaining-balance").innerText = `₹${parseFloat(data.remaining_balance).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("cov-status").innerText = data.is_active ? "ACTIVE" : "INACTIVE";

    const exList = document.getElementById("cov-exclusions-list");
    exList.innerHTML = (data.exclusions || []).map(e => `<span class="badge badge-danger">${e}</span>`).join(" ") || "<span class='badge badge-secondary'>None</span>";

    const hospList = document.getElementById("cov-hospitals-list");
    hospList.innerHTML = (data.network_hospitals || []).map(h => `<span class="badge badge-cyan">${h}</span>`).join(" ") || "<span class='badge badge-secondary'>All Network Facilities</span>";

    card.style.display = "block";
  } catch (err) {
    alert(`Failed to fetch coverage: ${err.message}`);
  }
}

// 3. Hospital Eligibility Check (AC-02)
async function handleEligibilityCheck(e) {
  e.preventDefault();
  const banner = document.getElementById("eligibility-result-banner");
  const payload = {
    member_id: document.getElementById("check-member-id").value.trim(),
    policy_id: document.getElementById("check-policy-id").value.trim(),
    hospital_id: document.getElementById("check-hospital-id").value.trim()
  };

  try {
    const res = await fetch(`${API_BASE}/eligibility/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    banner.style.display = "block";

    const statusTitle = document.getElementById("elig-status-text");
    const balanceElem = document.getElementById("elig-balance");
    const reasonsContainer = document.getElementById("elig-reasons-container");

    statusTitle.innerText = data.status;
    balanceElem.innerText = `₹${parseFloat(data.available_balance).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

    if (data.is_eligible) {
      banner.className = "status-banner";
      statusTitle.style.color = "var(--accent-emerald)";
      reasonsContainer.innerHTML = "<span class='badge badge-success'>In-Network Cashless Eligible</span>";
    } else {
      banner.className = "status-banner error";
      statusTitle.style.color = "var(--accent-rose)";
      reasonsContainer.innerHTML = (data.reason_codes || []).map(r => `<span class="badge badge-danger">${r}</span>`).join(" ");
    }
  } catch (err) {
    alert(`Eligibility check failed: ${err.message}`);
  }
}

// 4. Pre-Auth Submission (AC-03, AC-05)
async function handlePreAuthSubmit(e) {
  e.preventDefault();
  const banner = document.getElementById("preauth-decision-banner");
  const payload = {
    member_id: document.getElementById("pa-member-id").value.trim(),
    policy_id: document.getElementById("pa-policy-id").value.trim(),
    hospital_id: document.getElementById("pa-hospital-id").value.trim(),
    diagnosis: document.getElementById("pa-diagnosis").value.trim(),
    estimated_cost: document.getElementById("pa-estimated-cost").value.trim(),
    expected_admission_date: document.getElementById("pa-admission-date").value.trim()
  };

  try {
    const res = await fetch(`${API_BASE}/preauth/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    banner.style.display = "block";

    document.getElementById("pa-decision-status").innerText = data.status;
    document.getElementById("pa-res-id").innerText = data.pre_auth_id;
    document.getElementById("pa-res-claim-id").innerText = data.claim_id;
    document.getElementById("pa-res-amount").innerText = `₹${parseFloat(data.approved_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

    const reasonsElem = document.getElementById("pa-res-reasons");
    reasonsElem.innerHTML = (data.reason_codes || []).map(r => `<span class="badge badge-cyan">${r}</span>`).join(" ");

    if (data.status === "APPROVED") {
      banner.className = "status-banner";
    } else if (data.status === "REJECTED") {
      banner.className = "status-banner error";
    } else {
      banner.className = "status-banner warning";
    }

    // Auto populate admission form with generated claim_id
    document.getElementById("admit-claim-id").value = data.claim_id;
    document.getElementById("dis-claim-id").value = data.claim_id;
    document.getElementById("calc-claim-id").value = data.claim_id;
  } catch (err) {
    alert(`Pre-Auth submission failed: ${err.message}`);
  }
}

// 5. Patient Admission (AC-06, AC-08)
async function handleAdmitPatient(e) {
  e.preventDefault();
  const claimId = document.getElementById("admit-claim-id").value.trim();
  const payload = {
    admission_date: document.getElementById("admit-date").value,
    hospital_id: document.getElementById("admit-hospital-id").value.trim()
  };

  const feedback = document.getElementById("admit-feedback");
  try {
    const res = await fetch(`${API_BASE}/claims/${claimId}/admit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    feedback.style.display = "block";
    if (res.ok) {
      feedback.className = "status-banner";
      feedback.innerHTML = `<strong>Admission Confirmed</strong>: Patient checked in. Claim is now <code>${data.status}</code>.`;
    } else {
      feedback.className = "status-banner error";
      feedback.innerHTML = `<strong>Admission Blocked</strong>: ${data.detail || "Validation Error"}`;
    }
  } catch (err) {
    alert(`Admission failed: ${err.message}`);
  }
}

// 6. Discharge & Final Bill (AC-06)
async function handleDischargePatient(e) {
  e.preventDefault();
  const claimId = document.getElementById("dis-claim-id").value.trim();
  const procCode = document.getElementById("dis-proc-code").value.trim();
  const procDesc = document.getElementById("dis-proc-desc").value.trim();
  const procCost = document.getElementById("dis-proc-cost").value.trim();

  const payload = {
    discharge_date: document.getElementById("dis-date").value,
    final_bill: document.getElementById("dis-final-bill").value.trim(),
    hospital_id: document.getElementById("dis-hospital-id").value.trim(),
    procedures: [
      { procedure_code: procCode, description: procDesc, cost: procCost }
    ]
  };

  const feedback = document.getElementById("discharge-feedback");
  try {
    const res = await fetch(`${API_BASE}/claims/${claimId}/discharge`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    feedback.style.display = "block";
    if (res.ok) {
      feedback.className = "status-banner";
      feedback.innerHTML = `<strong>Discharge Complete</strong>: Final Bill ₹${data.final_bill} within Cap ₹${data.bill_cap}. Claim is now <code>${data.status}</code>.`;
    } else {
      feedback.className = "status-banner error";
      feedback.innerHTML = `<strong>Bill Exceeds Cap</strong>: ${data.detail || "Buffer Error"}`;
    }
  } catch (err) {
    alert(`Discharge failed: ${err.message}`);
  }
}

// 7. Administrator Override (AC-10)
async function handleAdminOverride(e) {
  e.preventDefault();
  const payload = {
    pre_auth_id: document.getElementById("ov-preauth-id").value.trim(),
    override_decision: document.getElementById("ov-decision").value,
    override_amount: document.getElementById("ov-amount").value.trim(),
    reason: document.getElementById("ov-reason").value.trim(),
    actor_id: document.getElementById("ov-actor-id").value.trim()
  };

  const roleHeader = document.getElementById("ov-role-header").value;
  const banner = document.getElementById("override-result-banner");

  try {
    const res = await fetch(`${API_BASE}/admin/preauth/override`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": roleHeader
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    banner.style.display = "block";
    if (res.ok) {
      banner.className = "status-banner";
      banner.innerHTML = `<strong>Override Success</strong>: ${data.pre_auth_id} status updated to <code>${data.status}</code> for ₹${data.approved_amount}.`;
      loadPreAuthQueue();
    } else {
      banner.className = "status-banner error";
      banner.innerHTML = `<strong>Override Rejected (${res.status})</strong>: ${data.detail}`;
    }
  } catch (err) {
    alert(`Override failed: ${err.message}`);
  }
}

// 8. Claim Settlement Calculation (AC-07)
async function handleClaimSettlement(e) {
  e.preventDefault();
  const claimId = document.getElementById("calc-claim-id").value.trim();
  const payload = {
    deductible: document.getElementById("calc-deductible").value.trim() || "0.00",
    co_pay: document.getElementById("calc-copay").value.trim() || "0.00",
    actor_id: "fin_adjudicator_01"
  };

  const feedback = document.getElementById("calc-settlement-feedback");
  try {
    const res = await fetch(`${API_BASE}/claims/${claimId}/settle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    feedback.style.display = "block";
    if (res.ok) {
      feedback.className = "status-banner";
      feedback.innerHTML = `<strong>Settlement Finalized</strong>: Insurer Payout: ₹${data.settlement_amount}, Patient Responsibility: ₹${data.patient_responsibility}.`;
      loadSettlementsReport();
    } else {
      feedback.className = "status-banner error";
      feedback.innerHTML = `<strong>Settlement Error</strong>: ${data.detail}`;
    }
  } catch (err) {
    alert(`Settlement failed: ${err.message}`);
  }
}

// 9. Timeline Fetch (AC-09)
async function fetchClaimTimeline() {
  const claimId = document.getElementById("timeline-claim-id").value.trim();
  const container = document.getElementById("timeline-events-container");

  try {
    const res = await fetch(`${API_BASE}/claims/${claimId}/timeline`);
    const events = await res.json();
    if (!events || events.length === 0) {
      container.innerHTML = "<p class='empty-state'>No timeline events found for this claim.</p>";
      return;
    }
    container.innerHTML = events.map(e => `
      <div class="timeline-item">
        <div class="time">${e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : 'N/A'}</div>
        <div class="desc">
          <strong>${e.event_type}</strong> (${e.actor_role})<br>
          <span>${e.description}</span>
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<p class="text-danger">Error loading timeline: ${err.message}</p>`;
  }
}

// 10. Settlement Details Fetch (AC-07)
async function fetchSettlementDetails() {
  const claimId = document.getElementById("settlement-claim-id").value.trim();
  const panel = document.getElementById("settlement-details-card");

  try {
    const res = await fetch(`${API_BASE}/claims/${claimId}/settlement`);
    if (!res.ok) {
      panel.style.display = "none";
      alert("No settlement record found for this claim.");
      return;
    }
    const data = await res.json();
    document.getElementById("set-final-bill").innerText = `₹${parseFloat(data.final_bill).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("set-pre-auth").innerText = `₹${parseFloat(data.pre_auth_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("set-buffer-pct").innerText = `${parseFloat(data.buffer_percentage) * 100}%`;
    document.getElementById("set-bill-cap").innerText = `₹${parseFloat(data.bill_cap).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("set-deductible").innerText = `₹${parseFloat(data.deductible).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("set-copay").innerText = `₹${parseFloat(data.co_pay).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("set-insurer-payout").innerText = `₹${parseFloat(data.settlement_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("set-patient-resp").innerText = `₹${parseFloat(data.patient_responsibility).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    panel.style.display = "block";
  } catch (err) {
    alert(`Failed to fetch settlement: ${err.message}`);
  }
}

// 11. Load Pre-Auth Queue
async function loadPreAuthQueue() {
  const tbody = document.getElementById("preauth-queue-tbody");
  try {
    const res = await fetch(`${API_BASE}/preauth`);
    const items = await res.json();
    if (!items || items.length === 0) {
      tbody.innerHTML = "<tr><td colspan='6' class='text-center'>No pre-authorizations recorded.</td></tr>";
      return;
    }
    tbody.innerHTML = items.map(item => `
      <tr>
        <td><code>${item.pre_auth_id}</code></td>
        <td><code>${item.claim_id}</code></td>
        <td>${item.member_id}</td>
        <td>₹${parseFloat(item.estimated_cost).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td>${item.expected_admission_date}</td>
        <td><span class="badge ${getStatusBadgeClass(item.status)}">${item.status}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan='6' class='text-danger'>Failed to load queue: ${err.message}</td></tr>`;
  }
}

// 12. Load Settlements Report
async function loadSettlementsReport() {
  const tbody = document.getElementById("settlements-report-tbody");
  try {
    const res = await fetch(`${API_BASE}/settlements`);
    const items = await res.json();
    if (!items || items.length === 0) {
      tbody.innerHTML = "<tr><td colspan='6' class='text-center'>No settlements recorded.</td></tr>";
      return;
    }
    tbody.innerHTML = items.map(s => `
      <tr>
        <td><code>${s.settlement_id}</code></td>
        <td><code>${s.claim_id}</code></td>
        <td>₹${parseFloat(s.final_bill).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td class="text-success">₹${parseFloat(s.settlement_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td class="text-warning">₹${parseFloat(s.patient_responsibility).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td><span class="badge badge-success">${s.status}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan='6' class='text-danger'>Failed to load reports: ${err.message}</td></tr>`;
  }
}

function getStatusBadgeClass(status) {
  switch (status) {
    case "APPROVED": return "badge-success";
    case "REJECTED": return "badge-danger";
    case "PARTIALLY_APPROVED": return "badge-cyan";
    default: return "badge-secondary";
  }
}

// 13. Network Admin: Onboard Hospital (AC-NET-01)
async function handleOnboardHospital(e) {
  e.preventDefault();
  const feedback = document.getElementById("onboard-feedback");
  feedback.style.display = "none";

  const payload = {
    hospital_id: document.getElementById("onboard-hospital-id").value.trim(),
    name: document.getElementById("onboard-hospital-name").value.trim(),
    city: document.getElementById("onboard-city").value.trim(),
    state: document.getElementById("onboard-state") ? document.getElementById("onboard-state").value.trim() : "Karnataka",
    tier: document.getElementById("onboard-tier").value
  };

  try {
    const res = await fetch(`${API_BASE}/admin/hospitals/onboard`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": "ADMIN",
        "X-User-Id": "admin_portal_user"
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      feedback.className = "status-banner success mt-2";
      feedback.innerText = `Hospital ${data.hospital_id} successfully onboarded into ${data.tier}!`;
      feedback.style.display = "block";
      loadAdminHospitals();
    } else {
      feedback.className = "status-banner error mt-2";
      feedback.innerText = `Onboarding failed: ${data.detail || "Error"}`;
      feedback.style.display = "block";
    }
  } catch (err) {
    feedback.className = "status-banner error mt-2";
    feedback.innerText = `Network error: ${err.message}`;
    feedback.style.display = "block";
  }
}

// 14. Network Admin: Configure Policy (AC-NET-02)
async function handleConfigurePolicy(e) {
  e.preventDefault();
  const feedback = document.getElementById("policy-config-feedback");
  feedback.style.display = "none";

  const whitelist = document.getElementById("cfg-whitelist").value.split(",").map(s => s.trim()).filter(Boolean);
  const payload = {
    product_name: document.getElementById("cfg-product-name").value.trim(),
    auto_approval_threshold: document.getElementById("cfg-auto-threshold").value.trim(),
    diagnosis_whitelist: whitelist,
    policy_cap: document.getElementById("cfg-policy-cap").value.trim(),
    buffer_percentage: document.getElementById("cfg-buffer-pct").value.trim()
  };

  try {
    const res = await fetch(`${API_BASE}/admin/policies/configure`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": "ADMIN",
        "X-User-Id": "admin_portal_user"
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      feedback.className = "status-banner success mt-2";
      feedback.innerText = `Policy configuration saved for ${data.product_name}!`;
      feedback.style.display = "block";
    } else {
      feedback.className = "status-banner error mt-2";
      feedback.innerText = `Configuration failed: ${data.detail || "Error"}`;
      feedback.style.display = "block";
    }
  } catch (err) {
    feedback.className = "status-banner error mt-2";
    feedback.innerText = `Network error: ${err.message}`;
    feedback.style.display = "block";
  }
}

// 15. Load Admin Hospitals Directory (AC-NET-03)
async function loadAdminHospitals() {
  const tbody = document.getElementById("admin-hospitals-tbody");
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE}/admin/hospitals`, {
      headers: {
        "X-User-Role": "ADMIN",
        "X-User-Id": "admin_portal_user"
      }
    });
    if (!res.ok) return;
    const items = await res.json();
    if (!items || items.length === 0) {
      tbody.innerHTML = "<tr><td colspan='6' class='text-center'>No hospitals registered.</td></tr>";
      return;
    }
    tbody.innerHTML = items.map(h => `
      <tr>
        <td><code>${h.hospital_id}</code></td>
        <td>${h.name}</td>
        <td>${h.city}</td>
        <td><span class="badge ${h.tier === 'TIER_1' ? 'badge-success' : 'badge-cyan'}">${h.tier}</span></td>
        <td><span class="badge ${h.is_active ? 'badge-success' : 'badge-danger'}">${h.is_active ? 'In-Network' : 'Inactive'}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="toggleHospitalStatus('${h.hospital_id}', ${h.is_active})">
            ${h.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan='6' class='text-danger'>Failed to load hospitals: ${err.message}</td></tr>`;
  }
}

// 16. Toggle Hospital Network Status (AC-NET-01)
async function toggleHospitalStatus(hospId, isCurrentlyActive) {
  try {
    const res = await fetch(`${API_BASE}/admin/hospitals/${hospId}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": "ADMIN",
        "X-User-Id": "admin_portal_user"
      },
      body: JSON.stringify({ is_active: !isCurrentlyActive })
    });
    if (res.ok) {
      loadAdminHospitals();
    } else {
      const err = await res.json();
      alert(`Status toggle failed: ${err.detail || "Error"}`);
    }
  } catch (err) {
    alert(`Request error: ${err.message}`);
  }
}

// 17. Load Operational Analytics Dashboard (AC-REP-01, AC-REP-02, AC-REP-03)
async function loadAnalyticsDashboard() {
  try {
    const res = await fetch(`${API_BASE}/reports/analytics`, {
      headers: {
        "X-User-Role": "INSURER",
        "X-User-Id": "insurer_analyst_01"
      }
    });
    if (!res.ok) return;
    const data = await res.json();

    // Render KPIs
    const tat = data.turnaround_time;
    if (tat) {
      document.getElementById("rep-mean-tat").innerText = `${parseFloat(tat.mean_seconds).toFixed(2)} s`;
      document.getElementById("rep-median-tat").innerText = `Median: ${parseFloat(tat.median_seconds).toFixed(2)} s (P95: ${parseFloat(tat.p95_seconds).toFixed(2)} s)`;
      document.getElementById("rep-auto-approval-rate").innerText = `${(parseFloat(tat.auto_approval_ratio) * 100).toFixed(1)}%`;
      document.getElementById("rep-auto-approval-count").innerText = `${tat.auto_approved_count} auto / ${tat.total_evaluations} total`;
    }

    const setSum = data.settlement_summary;
    if (setSum) {
      document.getElementById("rep-total-settlement-vol").innerText = `₹${parseFloat(setSum.total_settled_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
      document.getElementById("rep-settlement-count").innerText = `${setSum.total_claims_settled} settled claims`;
      document.getElementById("rep-loss-ratio").innerText = `${(parseFloat(setSum.loss_ratio) * 100).toFixed(1)}%`;
    }

    // Render Hospital Query Rates
    const qTbody = document.getElementById("tbody-hospital-query-rates");
    if (qTbody && data.query_rates_by_hospital) {
      if (data.query_rates_by_hospital.length === 0) {
        qTbody.innerHTML = "<tr><td colspan='5' class='text-center'>No query data.</td></tr>";
      } else {
        qTbody.innerHTML = data.query_rates_by_hospital.map(q => `
          <tr>
            <td><code>${q.hospital_id}</code></td>
            <td>${q.hospital_name}</td>
            <td>${q.total_claims}</td>
            <td>${q.query_count}</td>
            <td><span class="badge ${parseFloat(q.query_rate) > 0.2 ? 'badge-danger' : 'badge-success'}">${(parseFloat(q.query_rate) * 100).toFixed(1)}%</span></td>
          </tr>
        `).join("");
      }
    }

    // Render Top Diagnoses
    const diagTbody = document.getElementById("tbody-top-diagnoses");
    if (diagTbody && data.top_diagnoses) {
      if (data.top_diagnoses.length === 0) {
        diagTbody.innerHTML = "<tr><td colspan='3' class='text-center'>No diagnosis data.</td></tr>";
      } else {
        diagTbody.innerHTML = data.top_diagnoses.map(d => `
          <tr>
            <td><code>${d.diagnosis}</code></td>
            <td>${d.frequency}</td>
            <td class="text-emerald">₹${parseFloat(d.total_payout).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
          </tr>
        `).join("");
      }
    }
  } catch (err) {
    console.error("Failed to load analytics dashboard:", err);
  }
}
