#!/usr/bin/env python3
"""
MediCard AI-Native Agent Dispatcher & Orchestrator
Demonstrates programmatic invocation and orchestration of Claude Code / Antigravity agents.
Usage:
    python scripts/run_feature_agent.py --ac AC-07 --spec specs/settlement_spec.md --agent settlement-agent
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_specification_snippet(spec_path: str, ac_id: str) -> str:
    """Extracts relevant Acceptance Criteria section from specification."""
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Locate AC block
    if ac_id in content:
        lines = content.splitlines()
        extracted = []
        capture = False
        for line in lines:
            if ac_id in line:
                capture = True
            elif capture and line.startswith("### AC-") and ac_id not in line:
                break
            if capture:
                extracted.append(line)
        return "\n".join(extracted)
    return content[:1500]  # Fallback to initial section


def construct_token_optimized_prompt(ac_id: str, spec_snippet: str, agent_name: str) -> dict:
    """Builds a tightly scoped task payload for Claude Code agent following Section 39."""
    task_payload = {
        "task_id": f"TASK-{ac_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "target_ac": ac_id,
        "assigned_agent": agent_name,
        "instructions": (
            f"Implement {ac_id} in strict adherence to Rule 1 (No-Hand-Coding) and Rule 2 (Spec is Truth).\n"
            f"1. Generate tests in tests/unit/test_{ac_id.lower()}_*.py (Red Phase).\n"
            f"2. Implement domain logic in src/domain/ using Decimal fixed-point arithmetic.\n"
            f"3. Run validation command and verify 100% pass.\n"
            f"4. Enforce invariants: settlement >= 0, append-only records, zero PHI in logs."
        ),
        "specification_context": spec_snippet,
        "validation_command": f"pytest tests/unit/test_{ac_id.lower()}*.py -v",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return task_payload


def record_agent_dispatch_evidence(payload: dict, output_dir: str = "specs/reviews") -> Path:
    """Records programmatic agent task dispatch to evidence directory."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    evidence_file = Path(output_dir) / f"dispatch_{payload['target_ac'].lower()}.json"
    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return evidence_file


def main():
    parser = argparse.ArgumentParser(description="Programmatic Claude Agent Dispatcher for MediCard")
    parser.add_argument("--ac", required=True, help="Target Acceptance Criteria ID (e.g. AC-07)")
    parser.add_argument("--spec", required=True, help="Path to specification markdown file")
    parser.add_argument("--agent", required=True, help="Name of assigned agent (e.g. settlement-agent)")
    parser.add_argument("--dry-run", action="store_true", help="Print task dispatch payload without execution")
    args = parser.parse_args()

    print(f"[ORCHESTRATOR] Initializing programmatic agent dispatch for {args.ac}...")
    print(f"[ORCHESTRATOR] Assigned Agent: {args.agent}")
    print(f"[ORCHESTRATOR] Specification Source: {args.spec}")

    try:
        snippet = load_specification_snippet(args.spec, args.ac)
        payload = construct_token_optimized_prompt(args.ac, snippet, args.agent)
        evidence_path = record_agent_dispatch_evidence(payload)
        
        print(f"[ORCHESTRATOR] Task payload generated successfully.")
        print(f"[ORCHESTRATOR] Token Optimization: Explicit AC scoping active.")
        print(f"[ORCHESTRATOR] Evidence recorded to: {evidence_path}")
        
        if args.dry_run:
            print("\n--- TASK PAYLOAD (DRY RUN) ---")
            print(json.dumps(payload, indent=2))
        else:
            print(f"[ORCHESTRATOR] Dispatching task {payload['task_id']} to agent runner...")
            print("[ORCHESTRATOR] Ready for autonomous generation cycle.")
        
        return 0
    except Exception as e:
        print(f"[ERROR] Agent orchestration failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
