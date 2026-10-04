"""
Test Suite: AC-09 Stubbed Notifications & Case Timeline
Acceptance Criteria:
    Every state transition produces a stubbed notification.
    Customer and hospital can view the complete chronological case timeline.
"""

from datetime import datetime, timezone
import pytest
from src.domain.notification_rule import (
    NotificationEvent,
    build_lifecycle_notification,
    CaseTimelineEventItem
)


def test_ac09_notification_generation_for_state_transition():
    """AC-09: Generates formatted notification for both CUSTOMER and HOSPITAL."""
    notifications = build_lifecycle_notification(
        claim_id="CLM-3001",
        from_state="ADMITTED",
        to_state="DISCHARGED",
        member_id="MEM-1001",
        hospital_id="HOSP-001"
    )
    assert len(notifications) == 2
    recipients = {n.recipient_type: n for n in notifications}
    
    assert "CUSTOMER" in recipients
    assert recipients["CUSTOMER"].recipient_id == "MEM-1001"
    assert "discharged" in recipients["CUSTOMER"].message.lower()

    assert "HOSPITAL" in recipients
    assert recipients["HOSPITAL"].recipient_id == "HOSP-001"
    assert "CLM-3001" in recipients["HOSPITAL"].message


def test_ac09_timeline_chronological_structure():
    """AC-09: Validates case timeline entry structure."""
    event = CaseTimelineEventItem(
        claim_id="CLM-3001",
        event_type="DISCHARGED",
        description="Patient discharged; final bill submitted",
        actor_role="HOSPITAL",
        actor_id="HOSP-001",
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    assert event.claim_id == "CLM-3001"
    assert event.event_type == "DISCHARGED"
    assert event.actor_role == "HOSPITAL"
