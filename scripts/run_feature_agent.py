#!/usr/bin/env python3
"""
MediCard AI-Native Agent Dispatcher & Orchestrator (Section 10, Priority 6).
Demonstrates programmatic invocation and orchestration of Claude Code / Anthropic SDK.

Usage:
    # Explicit Dry Run (contract generation and schema verification):
    python scripts/run_feature_agent.py --ac AC-07 --spec specs/settlement_spec.md --agent settlement-agent --dry-run

    # Real Programmatic SDK Agent Execution (requires ANTHROPIC_API_KEY):
    python scripts/run_feature_agent.py --ac AC-07 --spec specs/settlement_spec.md --agent settlement-agent --execute

    # Verify SDK Installation and Environment Readiness:
    python scripts/run_feature_agent.py --verify-sdk
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Programmatic Claude Agent SDK Import
try:
    import anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_SDK_AVAILABLE = False


# Controlled Tools schema exposed to the Claude Agent
AGENT_CONTROLLED_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "read_specification_section",
        "description": "Reads a specific Acceptance Criteria section from a MediCard markdown specification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spec_path": {"type": "string", "description": "Relative path to spec markdown file"},
                "ac_id": {"type": "string", "description": "Target AC identifier, e.g. AC-07"}
            },
            "required": ["spec_path", "ac_id"]
        }
    },
    {
        "name": "run_pytest_suite",
        "description": "Executes pytest for the target AC tests to verify Red-Green-Refactor progression.",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_path": {"type": "string", "description": "Path to test file to execute"}
            },
            "required": ["test_path"]
        }
    },
    {
        "name": "record_audit_evidence",
        "description": "Appends an immutable audit event for agent code generation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "details": {"type": "string"}
            },
            "required": ["event_type", "details"]
        }
    }
]


def verify_sdk_installation() -> bool:
    """Verifies that the Anthropic Claude SDK is genuinely available and operational."""
    if not ANTHROPIC_SDK_AVAILABLE:
        print("[SDK VERIFY] FAILED: 'anthropic' package is not installed in current Python environment.")
        return False
    print(f"[SDK VERIFY] SUCCESS: 'anthropic' SDK v{anthropic.__version__} is installed and importable.")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"[SDK VERIFY] ANTHROPIC_API_KEY detected: {masked_key}")
        try:
            client = anthropic.Anthropic(api_key=api_key)
            print("[SDK VERIFY] Anthropic client instantiated successfully.")
            return True
        except Exception as e:
            print(f"[SDK VERIFY] Client initialization error: {e}")
            return False
    else:
        print("[SDK VERIFY] Note: ANTHROPIC_API_KEY is not set in current environment.")
        print("[SDK VERIFY] Ready for Safe Mode / Dry-Run dispatch; live execution requires export ANTHROPIC_API_KEY.")
        return True


def load_specification_snippet(spec_path: str, ac_id: str) -> str:
    """Extracts relevant Acceptance Criteria section from specification."""
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if ac_id in content:
        lines = content.splitlines()
        extracted = []
        capture = False
        for line in lines:
            if ac_id in line:
                capture = True
            elif capture and (line.startswith("### AC-") or line.startswith("## AC-")) and ac_id not in line:
                break
            if capture:
                extracted.append(line)
        if extracted:
            return "\n".join(extracted)
    return content[:1500]


def construct_token_optimized_prompt(ac_id: str, spec_snippet: str, agent_name: str) -> Dict[str, Any]:
    """Builds a tightly scoped task payload for Claude Code agent following Section 39."""
    task_payload = {
        "task_id": f"TASK-{ac_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "target_ac": ac_id,
        "assigned_agent": agent_name,
        "system_prompt": (
            "You are a specialized MediCard domain agent. Adhere strictly to Rule 1 (No-Hand-Coding) "
            "and Rule 2 (Spec is Source of Truth). Follow TDD Red-Green-Refactor. Use Decimal for all currency. "
            "Enforce append-only ledger immutability and mask all PHI from logs."
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
        "tools": AGENT_CONTROLLED_TOOLS,
        "validation_command": f"pytest tests/unit/test_{ac_id.lower()}*.py -v",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return task_payload


def record_agent_dispatch_evidence(payload: Dict[str, Any], output_dir: str = "specs/reviews") -> Path:
    """Records programmatic agent task dispatch to evidence directory."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    evidence_file = out_path / f"dispatch_{payload['target_ac'].lower()}.json"
    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return evidence_file


def execute_agent_sdk_task(payload: Dict[str, Any], execute_mode: bool = False) -> Dict[str, Any]:
    """
    Executes or previews programmatic Claude Agent SDK invocation.
    Strictly distinguishes between DRY RUN and REAL AGENT EXECUTION.
    """
    if not execute_mode:
        print("\n========================================================")
        print("[MODE: DRY RUN] No live Anthropic API call requested.")
        print("========================================================")
        return {
            "mode": "DRY_RUN",
            "status": "DRY_RUN_DISPATCHED",
            "task_id": payload["task_id"],
            "sdk_client": f"anthropic.Anthropic (v{anthropic.__version__ if ANTHROPIC_SDK_AVAILABLE else 'N/A'}) - Dry Run Simulation",
            "tools_registered": len(payload["tools"]),
            "action": "Task contract recorded to specs/reviews/ for Claude Code autonomous execution."
        }
    
    # Real execution requested
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n========================================================")
        print("[MODE: REAL AGENT EXECUTION] BLOCKED")
        print("========================================================")
        print("[REAL AGENT EXECUTION] Reason: ANTHROPIC_API_KEY environment variable is NOT set.")
        print("[REAL AGENT EXECUTION] User Action Required: Export a valid ANTHROPIC_API_KEY to proceed with live execution.")
        raise PermissionError("ANTHROPIC_API_KEY is required for real agent execution.")

    if not ANTHROPIC_SDK_AVAILABLE:
        raise ImportError("'anthropic' package must be installed for real execution.")

    print("\n========================================================")
    print("[MODE: REAL AGENT EXECUTION] Calling Anthropic API via Claude Agent SDK...")
    print("========================================================")
    
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        system=payload["system_prompt"],
        tools=payload["tools"],
        messages=[{"role": "user", "content": payload["user_message"]}]
    )
    
    # Parse agent response and tool calls
    tool_calls_requested = []
    text_content = ""
    for block in response.content:
        if block.type == "text":
            text_content += block.text
        elif block.type == "tool_use":
            tool_calls_requested.append({"tool": block.name, "input": block.input})

    result = {
        "mode": "REAL_AGENT_EXECUTION",
        "status": "SDK_CALL_COMPLETED",
        "task_id": payload["task_id"],
        "response_id": response.id,
        "model": response.model,
        "stop_reason": response.stop_reason,
        "tool_calls_count": len(tool_calls_requested),
        "tool_calls": tool_calls_requested,
        "content_length": len(text_content),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }

    # Record real execution transcript
    transcript_file = Path("specs/reviews") / f"real_agent_execution_{payload['target_ac'].lower()}.json"
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(description="Programmatic Claude Agent Dispatcher for MediCard")
    parser.add_argument("--ac", help="Target Acceptance Criteria ID (e.g. AC-07, AC-NET-01)")
    parser.add_argument("--spec", help="Path to specification markdown file")
    parser.add_argument("--agent", help="Name of assigned agent (e.g. settlement-agent, eligibility-agent)")
    parser.add_argument("--dry-run", action="store_true", help="Explicit dry run mode (generates contract without live LLM calls)")
    parser.add_argument("--execute", action="store_true", help="Execute task against real Claude Agent SDK (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--verify-sdk", action="store_true", help="Perform verification of the Anthropic SDK installation")
    args = parser.parse_args()

    if args.verify_sdk:
        success = verify_sdk_installation()
        return 0 if success else 1

    if not args.ac or not args.spec or not args.agent:
        parser.error("--ac, --spec, and --agent are required unless --verify-sdk is passed.")

    # Determine execution mode: default to dry-run unless --execute is explicitly passed
    execute_mode = args.execute and not args.dry_run

    print(f"[ORCHESTRATOR] Initializing agent dispatch for {args.ac}...")
    print(f"[ORCHESTRATOR] Assigned Agent: {args.agent}")
    print(f"[ORCHESTRATOR] Specification Source: {args.spec}")
    print(f"[ORCHESTRATOR] Execution Mode: {'REAL AGENT EXECUTION' if execute_mode else 'DRY RUN'}")

    try:
        snippet = load_specification_snippet(args.spec, args.ac)
        payload = construct_token_optimized_prompt(args.ac, snippet, args.agent)
        evidence_path = record_agent_dispatch_evidence(payload)
        
        result = execute_agent_sdk_task(payload, execute_mode=execute_mode)
        
        print(f"[ORCHESTRATOR] Task payload recorded at: {evidence_path}")
        print(f"[ORCHESTRATOR] Result Status: {result['status']}")
        
        if result["mode"] == "DRY_RUN":
            print("\n--- TASK DISPATCH CONTRACT (DRY RUN) ---")
            print(json.dumps(payload, indent=2))
        else:
            print("\n--- REAL AGENT EXECUTION SUMMARY ---")
            print(json.dumps(result, indent=2))

        return 0
    except PermissionError as pe:
        print(f"\n[BLOCKED] {pe}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"[ERROR] Agent orchestration failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
