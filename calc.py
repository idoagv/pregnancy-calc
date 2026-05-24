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


# Standard Israeli prenatal ultrasound screening windows, LMP-anchored.
# Each entry: (i18n_key, (start_week, start_day), (end_week, end_day)) — inclusive bounds.
SCREENING_WINDOWS = [
    ("screening_nuchal", (11, 0), (13, 6)),
    ("screening_early", (14, 0), (16, 6)),
    ("screening_second", (20, 0), (24, 6)),
    ("screening_third", (30, 0), (32, 0)),
]


@dataclass
class ScreeningWindow:
    key: str          # i18n key for the test name
    start: date       # inclusive
    end: date         # inclusive
    status: str       # "passed" | "current" | "upcoming"


def screening_windows(lmp: date, today: date) -> list["ScreeningWindow"]:
    """For each standard screening, compute its date window and current status.

    Cycle length is intentionally not applied — Israeli clinical practice
    anchors these windows to LMP directly.
    """
    out: list[ScreeningWindow] = []
    for key, (sw, sd), (ew, ed) in SCREENING_WINDOWS:
        start = lmp + timedelta(days=sw * 7 + sd)
        end = lmp + timedelta(days=ew * 7 + ed)
        if today < start:
            st = "upcoming"
        elif today > end:
            st = "passed"
        else:
            st = "current"
        out.append(ScreeningWindow(key=key, start=start, end=end, status=st))
    return out


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
