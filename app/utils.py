import calendar
from datetime import date, timedelta

from app.models import BillingCycle


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def period_end_for_cycle(start: date, cycle: BillingCycle) -> date:
    """Computes the end of a billing period given its start and cycle."""
    if cycle == BillingCycle.MONTHLY:
        return _add_months(start, 1)
    if cycle == BillingCycle.QUARTERLY:
        return _add_months(start, 3)
    if cycle == BillingCycle.YEARLY:
        return _add_months(start, 12)
    return start + timedelta(days=30)  # CUSTOM — default to a 30-day period
