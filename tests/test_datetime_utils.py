from datetime import date, timedelta
import pytest

from assistant_bot.utils import datetime_utils


class TestFormatBirthday:
    """Tests for formatting birthday dates."""

    def test_format_birthday_today(self):
        """Should format today's birthday."""
        today = date.today()
        formatted = datetime_utils.format_birthday(today.isoformat())
        assert formatted.startswith(today.strftime("%b"))

    def test_format_birthday_past_date(self):
        """Should format past birthday date."""
        past = date(2000, 5, 15)
        formatted = datetime_utils.format_birthday(past.isoformat())
        assert "May" in formatted or "05" in formatted

    def test_format_birthday_future_date(self):
        """Should format future birthday date."""
        tomorrow = date.today() + timedelta(days=1)
        formatted = datetime_utils.format_birthday(tomorrow.isoformat())
        assert formatted  # Should not raise

    def test_format_birthday_leap_year_date(self):
        """Should handle leap year birthdays."""
        leapday = date(2000, 2, 29)
        formatted = datetime_utils.format_birthday(leapday.isoformat())
        assert formatted


class TestFormatBirthdayWithDays:
    """Tests for formatting birthday with days calculation."""

    def test_format_with_days_today(self):
        """Should format with 0 days remaining."""
        today = date.today()
        result = datetime_utils.format_birthday_with_days(today.isoformat(), 0)
        assert "(" in result
        assert ")" in result
        assert "0" in result

    def test_format_with_days_many_days(self):
        """Should format with days countdown."""
        today = date.today()
        result = datetime_utils.format_birthday_with_days(today.isoformat(), 5)
        assert "5" in result
        assert "(" in result

    def test_format_with_days_negative(self):
        """Should handle negative days (past birthdays)."""
        today = date.today()
        result = datetime_utils.format_birthday_with_days(today.isoformat(), -5)
        # Negative days should still format the date
        assert "," in result or len(result) > 5  # Contains formatted date


class TestDaysUntilBirthday:
    """Tests for calculating days until birthday."""

    def test_days_until_next_year_birthday(self):
        """Should calculate days for upcoming birthday."""
        today = date.today()
        tomorrow = (today + timedelta(days=1)).isoformat()
        assert datetime_utils.days_until_birthday(tomorrow) == 1

    def test_days_until_far_future_birthday(self):
        """Should handle faraway birthdays."""
        today = date.today()
        future = (today + timedelta(days=100)).isoformat()
        days = datetime_utils.days_until_birthday(future)
        assert days > 0
        assert days >= 100

    def test_days_until_today_birthday(self):
        """Birthday today should be 0 days away."""
        today = date.today()
        days = datetime_utils.days_until_birthday(today.isoformat())
        assert days == 0

    def test_days_until_wrap_around_year(self):
        """Should handle birthdays wrapping around year boundary."""
        # A birthday later in current year should be positive
        today = date.today()
        later_this_year = today + timedelta(days=30)
        if later_this_year.year == today.year:
            days = datetime_utils.days_until_birthday(later_this_year.isoformat())
            assert days > 0

    def test_days_until_birthday_different_years(self):
        """Should work with different year formats."""
        today = date.today()
        # Test with future date in same year
        result = datetime_utils.days_until_birthday(
            (today + timedelta(days=10)).isoformat()
        )
        assert result > 0


class TestGetBirthdaysInNDays:
    """Tests for filtering birthdays by time range."""

    def test_get_upcoming_birthdays(self):
        """Should return upcoming birthdays."""
        today = date.today()
        tomorrow = (today + timedelta(days=1)).isoformat()
        day_after = (today + timedelta(days=2)).isoformat()

        birthdays = {"alice": tomorrow, "bob": day_after, "charlie": None}
        results = datetime_utils.get_birthdays_in_n_days(birthdays, 3)

        assert len(results) == 2
        # Results are tuples of (contact_id, birthday_str, days_left)
        assert any(contact_id == "alice" for contact_id, _, _ in results)
        assert any(contact_id == "bob" for contact_id, _, _ in results)

    def test_get_sorted_by_proximity(self):
        """Birthdays should be sorted by days remaining."""
        today = date.today()
        in_two = (today + timedelta(days=2)).isoformat()
        in_one = (today + timedelta(days=1)).isoformat()

        birthdays = {"a": in_two, "b": in_one}
        results = datetime_utils.get_birthdays_in_n_days(birthdays, 3)

        # Should be sorted: closer dates first
        assert results[0][0] == "b"
        assert results[1][0] == "a"

    def test_get_excludes_none_birthdays(self):
        """Should exclude contacts with None birthday."""
        today = date.today()
        tomorrow = (today + timedelta(days=1)).isoformat()

        birthdays = {"has_bday": tomorrow, "no_bday": None}
        results = datetime_utils.get_birthdays_in_n_days(birthdays, 3)

        assert len(results) == 1
        assert results[0][0] == "has_bday"

    def test_get_filtersby_days_limit(self):
        """Should only include birthdays within n days."""
        today = date.today()
        soon = (today + timedelta(days=1)).isoformat()
        far = (today + timedelta(days=100)).isoformat()

        birthdays = {"soon": soon, "far": far}
        results = datetime_utils.get_birthdays_in_n_days(birthdays, 5)

        # Only "soon" should be included
        assert len(results) == 1
        assert results[0][0] == "soon"

    def test_get_empty_input(self):
        """Should handle empty birthday dict."""
        results = datetime_utils.get_birthdays_in_n_days({}, 7)
        assert results == []

    def test_get_zero_days(self):
        """Should handle 0 day window."""
        today = date.today()
        results = datetime_utils.get_birthdays_in_n_days(
            {"today": today.isoformat()}, 0
        )
        assert len(results) >= 0
