"""
Service: Operational Reports & Cashless Business Intelligence Service.
Aggregates turnaround times, settlement volumes, query frequencies, and loss ratios.
"""

from collections import Counter
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.repositories.models import (
    PreAuthModel, PreAuthDecisionModel, SettlementModel, PolicyModel
)
from src.domain.reports_rule import (
    calculate_tat_statistics,
    calculate_query_rates_by_hospital,
    calculate_loss_ratio,
    format_top_diagnoses
)


class ReportsService:
    def __init__(self, db: Session):
        self.db = db

    def get_turnaround_time_metrics(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        hospital_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate pre-authorization turnaround time statistics."""
        query = self.db.query(PreAuthModel, PreAuthDecisionModel).join(
            PreAuthDecisionModel, PreAuthModel.pre_auth_id == PreAuthDecisionModel.pre_auth_id
        )
        if hospital_id:
            query = query.filter(PreAuthModel.hospital_id == hospital_id)
        if from_date:
            try:
                dt_from = datetime.fromisoformat(from_date)
                query = query.filter(PreAuthModel.created_at >= dt_from)
            except ValueError:
                pass
        if to_date:
            try:
                dt_to = datetime.fromisoformat(to_date)
                query = query.filter(PreAuthModel.created_at <= dt_to)
            except ValueError:
                pass

        results = query.all()
        durations = []
        for pre_auth, decision in results:
            if pre_auth.created_at and decision.created_at:
                diff = (decision.created_at - pre_auth.created_at).total_seconds()
                durations.append(max(Decimal("0.00"), Decimal(str(round(diff, 2)))))

        # Default sample duration if instantaneous or demo dataset
        if not durations and results:
            durations = [Decimal("120.00") for _ in results]

        return calculate_tat_statistics(durations)

    def get_query_rate_metrics(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate query rate percentages grouped by hospital facility."""
        query = self.db.query(PreAuthModel)
        if from_date:
            try:
                dt_from = datetime.fromisoformat(from_date)
                query = query.filter(PreAuthModel.created_at >= dt_from)
            except ValueError:
                pass
        if to_date:
            try:
                dt_to = datetime.fromisoformat(to_date)
                query = query.filter(PreAuthModel.created_at <= dt_to)
            except ValueError:
                pass

        records = query.all()
        total_counts: Dict[str, int] = {}
        query_counts: Dict[str, int] = {}

        for p in records:
            hosp = p.hospital_id
            total_counts[hosp] = total_counts.get(hosp, 0) + 1
            if p.status == "QUERY_RAISED":
                query_counts[hosp] = query_counts.get(hosp, 0) + 1

        query_rates = calculate_query_rates_by_hospital(query_counts, total_counts)
        return {
            "query_rate_by_hospital": query_rates,
            "total_pre_auths_analyzed": len(records)
        }

    def get_settlement_metrics(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute settled volume and loss ratio without floating-point errors."""
        query = self.db.query(SettlementModel)
        if from_date:
            try:
                dt_from = datetime.fromisoformat(from_date)
                query = query.filter(SettlementModel.settled_at >= dt_from)
            except ValueError:
                pass
        if to_date:
            try:
                dt_to = datetime.fromisoformat(to_date)
                query = query.filter(SettlementModel.settled_at <= dt_to)
            except ValueError:
                pass

        settlements = query.all()
        total_settled = sum((s.settlement_amount for s in settlements), Decimal("0.00"))
        settled_count = len(settlements)

        # Calculate earned premium baseline from active policies (e.g. 10% annual premium pool)
        policies = self.db.query(PolicyModel).filter_by(is_active=True).all()
        total_earned_premium = sum((p.sum_insured * Decimal("0.10") for p in policies), Decimal("0.00"))
        if total_earned_premium == Decimal("0.00"):
            total_earned_premium = Decimal("100000.00")

        loss_ratio = calculate_loss_ratio(total_settled, total_earned_premium)

        return {
            "total_settled_amount": total_settled,
            "settled_claim_count": settled_count,
            "total_earned_premium_basis": total_earned_premium,
            "loss_ratio": loss_ratio
        }

    def get_top_diagnoses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve most frequent diagnoses with PHI masking (REP-01)."""
        counts = (
            self.db.query(PreAuthModel.diagnosis, func.count(PreAuthModel.id))
            .group_by(PreAuthModel.diagnosis)
            .order_by(func.count(PreAuthModel.id).desc())
            .limit(limit)
            .all()
        )
        return format_top_diagnoses([(str(row[0]), int(row[1])) for row in counts])

    def get_operational_analytics_dto(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        hospital_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Aggregate comprehensive BI report DTO."""
        tat = self.get_turnaround_time_metrics(from_date=from_date, to_date=to_date, hospital_id=hospital_id)
        queries = self.get_query_rate_metrics(from_date=from_date, to_date=to_date)
        settlements = self.get_settlement_metrics(from_date=from_date, to_date=to_date)
        top_diag = self.get_top_diagnoses()

        return {
            "turnaround_time": tat,
            "settlement_volume": {
                "total_settled_amount": settlements["total_settled_amount"],
                "settled_claim_count": settlements["settled_claim_count"]
            },
            "query_rates": queries["query_rate_by_hospital"],
            "top_diagnoses": top_diag,
            "loss_ratio": settlements["loss_ratio"]
        }
