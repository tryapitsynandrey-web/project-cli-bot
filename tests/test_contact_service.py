import pytest


def test_add_contact_persists_new_contact(fake_contact_repository):
    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)
    contact = svc.add_contact(
        name="Zed",
        phone_numbers=["+353830000005"],
        tags=["xx"],
    )

    assert contact.name == "Zed"
    assert fake_contact_repository.save_calls == 1
    assert any(
        saved_contact.contact_id == contact.contact_id
        for saved_contact in fake_contact_repository._contacts
    )


def test_get_contact_raises_when_missing(fake_contact_repository):
    from assistant_bot.domain.exceptions import ContactNotFoundError
    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)

    with pytest.raises(ContactNotFoundError):
        svc.get_contact("no-such-id")


def test_get_all_contacts_sorted_and_search(fake_contact_repository):
    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)
    svc.add_contact("Bob", ["+353830000006"])
    svc.add_contact("alice", ["+353830000007"])

    names = [contact.name for contact in svc.get_all_contacts()]
    assert names == ["alice", "Bob"]

    results = svc.search_contacts("Alice")
    assert len(results) == 1
    assert results[0].name == "alice"


def test_get_contacts_by_tag_normalization(fake_contact_repository):
    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)
    contact = svc.add_contact(
        "TagGuy",
        ["+353830000020"],
        tags=["Work"],
    )

    results = svc.get_contacts_by_tag("work")

    assert any(result.contact_id == contact.contact_id for result in results)


def test_update_and_delete_contact(fake_contact_repository):
    from assistant_bot.domain.exceptions import ContactNotFoundError
    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)
    contact = svc.add_contact("Tom", ["+353830000008"], tags=["aa"])

    svc.update_contact(contact.contact_id, name="Tommy", tags=["bb"])
    updated = svc.get_contact(contact.contact_id)

    assert updated.name == "Tommy"
    assert updated.tags == ["bb"]

    svc.delete_contact(contact.contact_id)

    with pytest.raises(ContactNotFoundError):
        svc.get_contact(contact.contact_id)


def test_get_contacts_with_birthdays_sorted(fake_contact_repository):
    from datetime import date, timedelta

    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)
    today = date.today()

    d1 = today + timedelta(days=2)
    d2 = today + timedelta(days=1)

    birthday_1 = d1.replace(year=today.year - 30).isoformat()
    birthday_2 = d2.replace(year=today.year - 30).isoformat()

    contact_1 = svc.add_contact("Soon", ["+353830000030"], birthday=birthday_1)
    contact_2 = svc.add_contact("Sooner", ["+353830000031"], birthday=birthday_2)

    upcoming = svc.get_contacts_with_birthday_in_days(7)

    assert len(upcoming) >= 2
    assert upcoming[0][0].contact_id == contact_2.contact_id
    assert upcoming[1][0].contact_id == contact_1.contact_id


def test_tag_operations(fake_contact_repository):
    from assistant_bot.services.contact_service import ContactService

    svc = ContactService(fake_contact_repository)
    contact = svc.add_contact("Tagger", ["+353830000009"], tags=["one"])

    svc.add_tag_to_contact(contact.contact_id, "two")
    assert "two" in svc.get_contact(contact.contact_id).tags

    svc.edit_contact_tag(contact.contact_id, "two", "TWO")
    assert "two" in svc.get_contact(contact.contact_id).tags

    svc.delete_tag_from_contact(contact.contact_id, "one")

    tags = svc.get_all_contact_tags()
    assert isinstance(tags, set)
    assert "one" not in tags