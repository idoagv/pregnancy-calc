from datetime import date, timedelta

import pytest

from calc import (
    SCREENING_WINDOWS,
    edd_from_lmp,
    lmp_from_gestational_age,
    screening_windows,
    status,
)


def test_naegele_basic():
    # LMP 2026-01-01, 28-day cycle → +280 days = 2026-10-08
    assert edd_from_lmp(date(2026, 1, 1)) == date(2026, 10, 8)


def test_cycle_length_longer():
    # 35-day cycle adds 7 days to the EDD
    assert edd_from_lmp(date(2026, 1, 1), 35) == date(2026, 10, 15)


def test_cycle_length_shorter():
    assert edd_from_lmp(date(2026, 1, 1), 25) == date(2026, 10, 5)


def test_cycle_length_out_of_range():
    with pytest.raises(ValueError):
        edd_from_lmp(date(2026, 1, 1), 10)


def test_gestational_age_inverts_to_lmp():
    lmp = date(2026, 1, 1)
    on_date = date(2026, 5, 1)
    elapsed = (on_date - lmp).days  # 120
    weeks, days = divmod(elapsed, 7)  # 17w 1d
    assert lmp_from_gestational_age(weeks, days, on_date) == lmp


def test_gestational_age_with_cycle_length():
    # If cycle is 35 days, "17w 1d on May 1" implies LMP shifted 7 days earlier
    lmp = lmp_from_gestational_age(17, 1, date(2026, 5, 1), 35)
    # EDD from this LMP @ cycle 35 should equal May 1 + (40w - 17w1d) of remaining
    edd = edd_from_lmp(lmp, 35)
    assert (edd - date(2026, 5, 1)).days == 280 - (17 * 7 + 1)


def test_gestational_age_days_range():
    with pytest.raises(ValueError):
        lmp_from_gestational_age(10, 7, date(2026, 5, 1))


def test_status_trimesters():
    assert status(date(2026, 4, 1), date(2026, 5, 1)).trimester == 1   # ~4w
    assert status(date(2025, 12, 1), date(2026, 5, 1)).trimester == 2  # ~21w
    assert status(date(2025, 9, 1), date(2026, 5, 1)).trimester == 3   # ~34w


def test_status_weeks_and_days():
    s = status(date(2026, 1, 1), date(2026, 1, 15))
    assert s.weeks == 2 and s.days == 0


def test_status_days_remaining():
    lmp = date(2026, 1, 1)
    today = date(2026, 1, 8)
    s = status(lmp, today)
    assert s.days_remaining == 280 - 7


def test_leap_year_boundary():
    # LMP in a leap year, EDD crosses into next year
    edd = edd_from_lmp(date(2024, 6, 1))
    assert edd == date(2025, 3, 8)


def test_year_boundary():
    edd = edd_from_lmp(date(2025, 12, 31))
    assert edd == date(2026, 10, 7)


def test_screening_windows_count():
    ws = screening_windows(date(2026, 1, 1), date(2026, 1, 1))
    assert len(ws) == 4
    assert [w.key for w in ws] == [k for k, _, _ in SCREENING_WINDOWS]


def test_screening_nuchal_dates():
    # LMP 2026-01-01: nuchal 11w0d..13w6d = +77 days..+97 days
    ws = screening_windows(date(2026, 1, 1), date(2026, 1, 1))
    nuchal = ws[0]
    assert nuchal.key == "screening_nuchal"
    assert nuchal.start == date(2026, 1, 1) + timedelta(days=77)
    assert nuchal.end == date(2026, 1, 1) + timedelta(days=97)


def test_screening_third_endpoint():
    # 32+0 = 30*7 + 0 + 14 = 224 days from LMP
    ws = screening_windows(date(2026, 1, 1), date(2026, 1, 1))
    third = ws[3]
    assert third.key == "screening_third"
    assert (third.end - date(2026, 1, 1)).days == 30 * 7 + 14


def test_screening_status_upcoming():
    # today = LMP itself → everything is upcoming
    ws = screening_windows(date(2026, 1, 1), date(2026, 1, 1))
    assert all(w.status == "upcoming" for w in ws)


def test_screening_status_current():
    # today inside the second-scan window (20+0..24+6 → days 140..174)
    lmp = date(2026, 1, 1)
    today = lmp + timedelta(days=150)
    ws = screening_windows(lmp, today)
    statuses = {w.key: w.status for w in ws}
    assert statuses["screening_nuchal"] == "passed"
    assert statuses["screening_early"] == "passed"
    assert statuses["screening_second"] == "current"
    assert statuses["screening_third"] == "upcoming"


def test_screening_status_passed():
    lmp = date(2026, 1, 1)
    today = lmp + timedelta(days=300)
    ws = screening_windows(lmp, today)
    assert all(w.status == "passed" for w in ws)
