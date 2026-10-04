"""
Domain Layer: Notification Stubs & Timeline Models (AC-09)
Generates multi-party lifecycle notifications and timeline events.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass
class NotificationEvent:
    """Stubbed notification contract."""
    recipient_type: str  # CUSTOMER, HOSPITAL, INSURER
    recipient_id: str
    channel: str
    message: str
    timestamp: str


@dataclass
class CaseTimelineEventItem:
    """Timeline milestone contract."""
    claim_id: str
    event_type: str
    description: str
    actor_role: str
    actor_id: str
    timestamp: str


def build_lifecycle_notification(
    claim_id: str,
    from_state: str,
    to_state: str,
    member_id: str,
    hospital_id: str
) -> List[NotificationEvent]:
    """AC-09: Constructs stubbed notifications for Customer and Hospital upon state change."""
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Customer message
    cust_msg = (
        f"Your cashless hospitalization claim {claim_id} has transitioned from "
        f"{from_state} to {to_state}."
    )
    if to_state == "ADMITTED":
        cust_msg = f"Your admission for claim {claim_id} has been confirmed. Cashless coverage is active."
    elif to_state == "DISCHARGED":
        cust_msg = f"You have been discharged for claim {claim_id}. Final settlement is under review."
    elif to_state == "SETTLED":
        cust_msg = f"Claim {claim_id} has been successfully settled. View your breakdown online."

    # Hospital message
    hosp_msg = f"Claim {claim_id} updated: {from_state} -> {to_state}."

    return [
        NotificationEvent(
            recipient_type="CUSTOMER",
            recipient_id=member_id,
            channel="SMS_AND_IN_APP",
            message=cust_msg,
            timestamp=now_iso
        ),
        NotificationEvent(
            recipient_type="HOSPITAL",
            recipient_id=hospital_id,
            channel="PORTAL_ALERT",
            message=hosp_msg,
            timestamp=now_iso
        )
    ]
