"""
Unit Tests for Claude Feature Agent SDK Orchestrator (Priority 6, Section 10).
Validates SDK verification, controlled tool schemas, dry-run contracts,
and live execution error guards.
"""

import os
import json
from unittest.mock import MagicMock, patch
import pytest
from scripts.run_feature_agent import (
    verify_sdk_installation,
    load_specification_snippet,
    construct_token_optimized_prompt,
    execute_agent_sdk_task,
    AGENT_CONTROLLED_TOOLS
)


def test_sdk_verify_installed():
    """Confirms Anthropic SDK is installed and reportable."""
    is_valid = verify_sdk_installation()
    assert is_valid is True


def test_construct_prompt_and_tools_schema():
    """Verifies that prompt generation includes controlled tools and required invariants."""
    snippet = "Rule NET-01: Only active hospitals are recognized."
    payload = construct_token_optimized_prompt("AC-NET-01", snippet, "network-admin-agent")
    
    assert payload["target_ac"] == "AC-NET-01"
    assert payload["assigned_agent"] == "network-admin-agent"
    assert "Decimal" in payload["system_prompt"]
    assert "tools" in payload
    assert len(payload["tools"]) == 3
    tool_names = [t["name"] for t in payload["tools"]]
    assert "read_specification_section" in tool_names
    assert "run_pytest_suite" in tool_names
    assert "record_audit_evidence" in tool_names


def test_dry_run_mode_dispatches_without_llm():
    """AC-SDK-01: Verifies dry-run mode returns DRY_RUN_DISPATCHED without calling API."""
    payload = construct_token_optimized_prompt("AC-07", "AC-07 Settlement Invariant", "settlement-agent")
    result = execute_agent_sdk_task(payload, execute_mode=False)
    
    assert result["mode"] == "DRY_RUN"
    assert result["status"] == "DRY_RUN_DISPATCHED"
    assert "Dry Run" in result["sdk_client"]


def test_execute_mode_without_api_key_raises_permission_error():
    """AC-SDK-02: Confirms --execute fails honestly if ANTHROPIC_API_KEY is missing."""
    payload = construct_token_optimized_prompt("AC-07", "AC-07 Settlement Invariant", "settlement-agent")
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(PermissionError) as exc_info:
            execute_agent_sdk_task(payload, execute_mode=True)
        assert "ANTHROPIC_API_KEY is required" in str(exc_info.value)


def test_execute_mode_with_mocked_client_records_transcript(tmp_path):
    """AC-SDK-03: Confirms real execution path processes message blocks and records usage."""
    payload = construct_token_optimized_prompt("AC-07", "AC-07 Settlement Invariant", "settlement-agent")
    
    # Mock Anthropic client and message response
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "Settlement calculation implemented using Decimal."
    
    mock_response = MagicMock()
    mock_response.id = "msg_test_mock_12345"
    mock_response.model = "claude-3-5-sonnet-20241022"
    mock_response.stop_reason = "end_turn"
    mock_response.content = [mock_block]
    mock_response.usage.input_tokens = 450
    mock_response.usage.output_tokens = 120

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-mock-key"}):
        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client_instance = MagicMock()
            mock_client_instance.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client_instance
            
            result = execute_agent_sdk_task(payload, execute_mode=True)
            
            assert result["mode"] == "REAL_AGENT_EXECUTION"
            assert result["status"] == "SDK_CALL_COMPLETED"
            assert result["response_id"] == "msg_test_mock_12345"
            assert result["usage"]["output_tokens"] == 120
            mock_client_instance.messages.create.assert_called_once()
