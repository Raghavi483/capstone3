"""
Controller: Reports & Operational Analytics API Endpoints (specs/reports_spec.md).
Enforces NFR-04 role boundaries (only INSURER or ADMIN permitted).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from src.repositories.database import get_db
from src.services.reports_service import ReportsService

router = APIRouter(prefix="/api/v1/reports", tags=["Reports & Analytics"])


def verify_analytics_access(x_user_role: Optional[str] = Header(None, alias="X-User-Role")):
    """Ensure caller has INSURER or ADMIN role."""
    if not x_user_role or x_user_role.upper() not in {"INSURER", "ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: INSURER or ADMIN role required to access operational reports."
        )


@router.get("/analytics")
def get_comprehensive_analytics(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    hospital_id: Optional[str] = None,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    verify_analytics_access(x_user_role)
    service = ReportsService(db)
    return service.get_operational_analytics_dto(
        from_date=from_date,
        to_date=to_date,
        hospital_id=hospital_id
    )


@router.get("/turnaround-time")
def get_turnaround_time_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    hospital_id: Optional[str] = None,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    verify_analytics_access(x_user_role)
    service = ReportsService(db)
    return service.get_turnaround_time_metrics(
        from_date=from_date,
        to_date=to_date,
        hospital_id=hospital_id
    )


@router.get("/query-rates")
def get_query_rate_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    verify_analytics_access(x_user_role)
    service = ReportsService(db)
    return service.get_query_rate_metrics(
        from_date=from_date,
        to_date=to_date
    )


@router.get("/settlement-summary")
def get_settlement_summary_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    verify_analytics_access(x_user_role)
    service = ReportsService(db)
    return service.get_settlement_metrics(
        from_date=from_date,
        to_date=to_date
    )
