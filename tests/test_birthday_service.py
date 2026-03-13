from datetime import date


def test_get_upcoming_birthdays_returns_matching_contact(contact_service):
    from assistant_bot.services.birthday_service import BirthdayService

    today = date.today().isoformat()
    contact = contact_service.add_contact(
        "Bday",
        ["+353830000010"],
        birthday=today,
    )

    birthday_service = BirthdayService(contact_service)
    upcoming = birthday_service.get_upcoming_birthdays(1)

    assert len(upcoming) >= 1
    assert any(item["contact_id"] == contact.contact_id for item in upcoming)
    assert any(item["name"] == "Bday" for item in upcoming)


def test_get_upcoming_birthdays_returns_empty_list_when_no_matches(contact_service):
    from assistant_bot.services.birthday_service import BirthdayService

    birthday_service = BirthdayService(contact_service)
    upcoming = birthday_service.get_upcoming_birthdays(1)

    assert upcoming == []


def test_days_parameter_default_used_when_zero_passed(contact_service):
    from assistant_bot.services.birthday_service import BirthdayService

    birthday_service = BirthdayService(contact_service)
    result = birthday_service.get_upcoming_birthdays(0)

    assert isinstance(result, list)


def test_days_parameter_default_used_when_negative_passed(contact_service):
    from assistant_bot.services.birthday_service import BirthdayService

    birthday_service = BirthdayService(contact_service)
    result = birthday_service.get_upcoming_birthdays(-5)

    assert isinstance(result, list)