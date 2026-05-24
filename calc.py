"""Pregnancy date math. Pure functions on `date` objects — no I/O."""
from dataclasses import dataclass
from datetime import date, timedelta

GESTATION_DAYS = 280  # Naegele's rule: LMP + 40 weeks


def edd_from_lmp(lmp: date, cycle_length: int = 28) -> date:
    """Estimated due date from last menstrual period.

    For non-28-day cycles, shift by (cycle_length - 28) days.
    """
    if cycle_length < 20 or cycle_length > 45:
        raise ValueError("cycle_length must be between 20 and 45 days")
    return lmp + timedelta(days=GESTATION_DAYS + (cycle_length - 28))


def lmp_from_gestational_age(
    weeks: int, days: int, on_date: date, cycle_length: int = 28
) -> date:
    """Given "I am W weeks D days on date X", return the implied LMP."""
    if not (0 <= weeks <= 45):
        raise ValueError("weeks out of range")
    if not (0 <= days <= 6):
        raise ValueError("days must be 0-6")
    elapsed = weeks * 7 + days
    # cycle-length adjustment: longer cycles imply later ovulation, so the
    # "real" LMP is earlier than a naive 28-day calc would suggest.
    return on_date - timedelta(days=elapsed) - timedelta(days=cycle_length - 28)


@dataclass
class Status:
    edd: date
    weeks: int
    days: int
    trimester: int
    days_remaining: int


def status(lmp: date, today: date, cycle_length: int = 28) -> Status:
    """Snapshot of where the pregnancy is as of `today`."""
    edd = edd_from_lmp(lmp, cycle_length)
    elapsed = (today - lmp).days
    elapsed = max(elapsed, 0)
    weeks, days = divmod(elapsed, 7)
    if weeks < 14:
        trimester = 1
    elif weeks < 28:
        trimester = 2
    else:
        trimester = 3
    return Status(
        edd=edd,
        weeks=weeks,
        days=days,
        trimester=trimester,
        days_remaining=(edd - today).days,
    )
