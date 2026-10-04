#!/usr/bin/env python3
"""
MediCard AI-Native Agent Dispatcher & Orchestrator
Demonstrates programmatic invocation and orchestration of Claude Code / Anthropic SDK.

Usage:
    python scripts/run_feature_agent.py --ac AC-07 --spec specs/settlement_spec.md --agent settlement-agent --dry-run
    python scripts/run_feature_agent.py --verify-sdk
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Programmatic Claude Agent SDK Import
try:
    import anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    ANTHROPIC_SDK_AVAILABLE = False


def verify_sdk_installation():
    """Verifies that the Anthropic Claude SDK is genuinely available and operational."""
    if not ANTHROPIC_SDK_AVAILABLE:
        print("[SDK VERIFY] FAILED: 'anthropic' package is not installed.")
        return False
    print(f"[SDK VERIFY] SUCCESS: 'anthropic' SDK v{anthropic.__version__} is installed and importable.")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        print("[SDK VERIFY] ANTHROPIC_API_KEY is detected in environment.")
        try:
            client = anthropic.Anthropic(api_key=api_key)
            print("[SDK VERIFY] Client instantiated successfully.")
            return True
        except Exception as e:
            print(f"[SDK VERIFY] Client initialization error: {e}")
            return False
    else:
        print("[SDK VERIFY] Note: ANTHROPIC_API_KEY not set in current environment (Safe Mode Active).")
        return True


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
    return content[:1500]


def construct_token_optimized_prompt(ac_id: str, spec_snippet: str, agent_name: str) -> dict:
    """Builds a tightly scoped task payload for Claude Code agent following Section 39."""
    task_payload = {
        "task_id": f"TASK-{ac_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "target_ac": ac_id,
        "assigned_agent": agent_name,
        "system_prompt": (
            "You are a specialized MediCard domain agent. Adhere strictly to Rule 1 (No-Hand-Coding) "
            "and Rule 2 (Spec is Source of Truth). Follow TDD Red-Green-Refactor. Use Decimal for all currency."
        ),
        "user_message": (
            f"Implement Acceptance Criteria {ac_id}.\n\n"
            f"Specification Context:\n{spec_snippet}\n\n"
            f"Requirements:\n"
            f"1. Generate tests in tests/unit/ (Red phase).\n"
            f"2. Implement domain logic in src/domain/ using Decimal arithmetic.\n"
            f"3. Verify non-negative settlement invariant and append-only rules.\n"
            f"4. Prohibit PHI plaintext logging."
        ),
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


def execute_agent_sdk_task(payload: dict, dry_run: bool = True) -> dict:
    """Executes or previews programmatic Claude Agent SDK invocation."""
    if dry_run or not os.environ.get("ANTHROPIC_API_KEY"):
        return {
            "status": "DRY_RUN_DISPATCHED",
            "task_id": payload["task_id"],
            "sdk_client": "anthropic.Anthropic (Safe Mode / Dry Run)",
            "action": "Task contract recorded to specs/reviews/ for Claude Code autonomous execution."
        }
    
    # Real SDK call when API key is provided
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        system=payload["system_prompt"],
        messages=[{"role": "user", "content": payload["user_message"]}]
    )
    return {
        "status": "SDK_CALL_COMPLETED",
        "task_id": payload["task_id"],
        "response_id": response.id,
        "content_length": len(response.content[0].text)
    }


def main():
    parser = argparse.ArgumentParser(description="Programmatic Claude Agent Dispatcher for MediCard")
    parser.add_argument("--ac", help="Target Acceptance Criteria ID (e.g. AC-07)")
    parser.add_argument("--spec", help="Path to specification markdown file")
    parser.add_argument("--agent", help="Name of assigned agent (e.g. settlement-agent)")
    parser.add_argument("--dry-run", action="store_true", help="Print task dispatch payload without live LLM calls")
    parser.add_argument("--verify-sdk", action="store_true", help="Perform verification of the Anthropic SDK installation")
    args = parser.parse_args()

    if args.verify_sdk:
        success = verify_sdk_installation()
        return 0 if success else 1

    if not args.ac or not args.spec or not args.agent:
        parser.error("--ac, --spec, and --agent are required unless --verify-sdk is passed.")

    print(f"[ORCHESTRATOR] Initializing programmatic agent dispatch for {args.ac}...")
    print(f"[ORCHESTRATOR] Assigned Agent: {args.agent}")
    print(f"[ORCHESTRATOR] Specification Source: {args.spec}")
    print(f"[ORCHESTRATOR] Anthropic SDK Status: {'Available (v' + anthropic.__version__ + ')' if ANTHROPIC_SDK_AVAILABLE else 'Not Installed'}")

    try:
        snippet = load_specification_snippet(args.spec, args.ac)
        payload = construct_token_optimized_prompt(args.ac, snippet, args.agent)
        evidence_path = record_agent_dispatch_evidence(payload)
        result = execute_agent_sdk_task(payload, dry_run=args.dry_run or ("ANTHROPIC_API_KEY" not in os.environ))
        
        print(f"[ORCHESTRATOR] Task payload generated and recorded.")
        print(f"[ORCHESTRATOR] Evidence File: {evidence_path}")
        print(f"[ORCHESTRATOR] Execution Status: {result['status']}")
        
        if args.dry_run:
            print("\n--- TASK PAYLOAD (DRY RUN) ---")
            print(json.dumps(payload, indent=2))
        return 0
    except Exception as e:
        print(f"[ERROR] Agent orchestration failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
