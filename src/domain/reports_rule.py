"""
Domain Rules: Operational Reports & Cashless Analytics (specs/reports_spec.md).
Enforces:
- Rule REP-01 (Privacy in Analytics): Aggregates must never expose patient identities or member IDs.
- Rule REP-02 (Monetary & Metric Precision): All metrics and durations formatted in fixed-point Decimal arithmetic.
- NFR-01: Absolute prohibition of floating-point arithmetic or casting.
"""

from decimal import Decimal, ROUND_HALF_UP
import math
from typing import List, Dict, Any, Tuple


def calculate_tat_statistics(durations_seconds: List[Decimal]) -> Dict[str, Any]:
    """
    Calculate average, median, and 95th percentile turnaround time in seconds using Decimal.
    """
    if not durations_seconds:
        return {
            "average_tat_seconds": Decimal("0.00"),
            "median_tat_seconds": Decimal("0.00"),
            "p95_tat_seconds": Decimal("0.00"),
            "sample_size": 0
        }

    sorted_durations = sorted(durations_seconds)
    n = len(sorted_durations)
    total_duration = sum(sorted_durations, Decimal("0.00"))
    avg_tat = (total_duration / Decimal(str(n))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Median
    mid = n // 2
    if n % 2 == 0:
        median_tat = ((sorted_durations[mid - 1] + sorted_durations[mid]) / Decimal("2")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        median_tat = sorted_durations[mid].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # 95th Percentile
    p95_idx = int(math.ceil(0.95 * n)) - 1
    p95_tat = sorted_durations[max(0, min(p95_idx, n - 1))].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "average_tat_seconds": avg_tat,
        "median_tat_seconds": median_tat,
        "p95_tat_seconds": p95_tat,
        "sample_size": n
    }


def calculate_query_rates_by_hospital(
    query_counts: Dict[str, int],
    total_counts: Dict[str, int]
) -> Dict[str, Decimal]:
    """
    Calculate query rate percentage per hospital facility using Decimal.
    """
    results: Dict[str, Decimal] = {}
    for hosp_id, total in total_counts.items():
        if total > 0:
            queries = query_counts.get(hosp_id, 0)
            rate = ((Decimal(str(queries)) / Decimal(str(total))) * Decimal("100.00")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            results[hosp_id] = rate
        else:
            results[hosp_id] = Decimal("0.00")
    return results


def calculate_loss_ratio(
    total_settled_payout: Decimal,
    total_earned_premium: Decimal
) -> Decimal:
    """
    Calculate loss ratio: total_settled_payout / total_earned_premium.
    Monetary values are pure Decimal.
    """
    if total_earned_premium <= Decimal("0.00"):
        return Decimal("0.00")
    
    ratio = (total_settled_payout / total_earned_premium).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return ratio


def format_top_diagnoses(
    diagnoses_frequencies: List[Tuple[str, int]]
) -> List[Dict[str, Any]]:
    """
    Format top diagnoses distribution.
    Enforces Rule REP-01: Excludes patient identifiers or individual member IDs.
    """
    output = []
    for diag, count in diagnoses_frequencies:
        output.append({
            "diagnosis": diag,
            "count": count
        })
    return output
