from datetime import date

import pytest

from calc import edd_from_lmp, lmp_from_gestational_age, status


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
