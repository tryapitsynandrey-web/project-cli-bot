import pytest
from datetime import date

from assistant_bot.domain.contacts import Contact


class TestContactCreation:
    """Tests for contact creation and initialization."""

    def test_create_contact_with_required_fields_only(self):
        """Should create contact with minimum required fields."""
        contact = Contact.create(
            name="Alice Baker",
            phone_numbers=["+353830000001"]
        )
        assert contact.name == "Alice Baker"
        # Phone number is normalized by phonenumbers library stub
        assert len(contact.phone_numbers) == 1
        assert contact.phone_numbers[0].startswith("+1")
        assert contact.email is None
        assert contact.address is None
        assert contact.birthday is None
        assert contact.note is None
        assert contact.tags == []

    def test_create_contact_with_all_fields(self):
        """Should create contact with all fields populated."""
        data = {
            "name": "Bob Smith",
            "phone_numbers": ["+353830000002"],
            "email": "bob@gmail.com",
            "address": "1 Road Lane",
            "birthday": "1990-01-01",
            "note": "some note",
            "tags": ["Work", "important"],
        }
        contact = Contact.create(**data)
        assert contact.name == "Bob Smith"
        assert contact.email == "bob@gmail.com"
        assert contact.address == "1 Road Lane"
        assert contact.birthday == "1990-01-01"
        assert contact.note == "some note"
        # Tags should be normalized (lowercase)
        assert "work" in contact.tags
        assert "important" in contact.tags

    def test_create_contact_generates_id(self):
        """Should generate contact_id if not provided."""
        contact = Contact.create(
            name="Charlie Dane",
            phone_numbers=["+353830000003"]
        )
        assert contact.contact_id
        assert len(contact.contact_id) > 0

    def test_create_contact_sets_created_at(self):
        """Should set created_at timestamp."""
        contact = Contact.create(
            name="Diana Evans",
            phone_numbers=["+353830000004"]
        )
        assert contact.created_at
        assert "T" in contact.created_at  # Should be ISO format

    def test_create_contact_requires_phone_numbers(self):
        """Should require at least one phone number."""
        with pytest.raises(ValueError):
            Contact.create(name="No Phone", phone_numbers=[])

    def test_create_contact_filters_empty_phone_numbers(self):
        """Should filter out empty phone strings."""
        contact = Contact.create(
            name="Frank Green",
            phone_numbers=["", "+353830000005", "", "+353830000006"]
        )
        # Empty strings should be filtered out, remaining normalized by stub
        assert len(contact.phone_numbers) == 2
        assert all(p == "+10000000000" for p in contact.phone_numbers)

    def test_create_contact_with_empty_optional_string(self):
        """Should treat empty strings as None for optional fields."""
        contact = Contact.create(
            name="Gail Harper",
            phone_numbers=["+353830000007"],
            email="",
            address="",
            note=""
        )
        assert contact.email is None
        assert contact.address is None
        assert contact.note is None

    def test_create_contact_with_multiple_phones(self):
        """Should handle multiple phone numbers."""
        phones = ["+353830000008", "+353830000009", "+353830000010"]
        contact = Contact.create(
            name="Hector Ivans",
            phone_numbers=phones
        )
        # All phones normalized to stub format
        assert len(contact.phone_numbers) == 3
        assert all(p == "+10000000000" for p in contact.phone_numbers)


class TestContactSerialization:
    """Tests for to_dict and from_dict methods."""

    def test_to_dict_contains_all_fields(self):
        """to_dict should include all contact fields."""
        contact = Contact.create(
            name="Iris Jackson",
            phone_numbers=["+353830000011"],
            email="iris@test.co.uk",
            tags=["personal"]
        )
        d = contact.to_dict()
        assert "contact_id" in d
        assert "name" in d
        assert "phone_numbers" in d
        assert "email" in d
        assert "address" in d
        assert "birthday" in d
        assert "note" in d
        assert "tags" in d
        assert "created_at" in d

    def test_from_dict_restores_all_fields(self):
        """Should restore contact from dict with all values."""
        original_data = {
            "contact_id": "test-id-123",
            "name": "James King",
            "phone_numbers": ["+10000000000"],
            "email": "james@test.co.uk",
            "address": "10 Main St",
            "birthday": "1985-05-15",
            "note": "Important client",
            "tags": ["vip"],
            "created_at": "2024-01-01T12:00:00"
        }
        contact = Contact.from_dict(original_data)
        assert contact.contact_id == "test-id-123"
        assert contact.name == "James King"
        assert contact.email == "james@test.co.uk"
        assert contact.address == "10 Main St"
        assert contact.birthday == "1985-05-15"
        assert contact.note == "Important client"
        assert "vip" in contact.tags
        assert contact.created_at == "2024-01-01T12:00:00"

    def test_roundtrip_create_to_dict_from_dict(self):
        """Data should round-trip through to_dict and from_dict."""
        contact = Contact.create(
            name="Karen Loren",
            phone_numbers=["+353830000013", "+353830000014"],
            email="karen@test.co.uk",
            address="20 Oak Ave",
            birthday="1988-03-20",
            note="Team lead",
            tags=["work", "manager"]
        )
        original_id = contact.contact_id
        original_created = contact.created_at

        # Serialize and deserialize
        dict_repr = contact.to_dict()
        restored = Contact.from_dict(dict_repr)

        assert restored.name == contact.name
        assert restored.phone_numbers == contact.phone_numbers
        assert restored.email == contact.email
        assert restored.address == contact.address
        assert restored.birthday == contact.birthday
        assert restored.note == contact.note
        assert set(restored.tags) == set(contact.tags)
        assert restored.contact_id == original_id
        assert restored.created_at == original_created

    def test_from_dict_requires_valid_phones(self):
        """from_dict should fail if no valid phone numbers."""
        data = {
            "name": "No Phone",
            "phone_numbers": [],
            "contact_id": "test"
        }
        with pytest.raises(ValueError):
            Contact.from_dict(data)

    def test_from_dict_filters_empty_phones(self):
        """from_dict should filter out empty phone strings."""
        data = {
            "name": "Leo Martin",
            "phone_numbers": ["", "+353830000015", "", "+353830000016"],
            "contact_id": "test-leo"
        }
        contact = Contact.from_dict(data)
        assert len(contact.phone_numbers) == 2

    def test_from_dict_with_missing_optional_fields(self):
        """Should handle from_dict with minimal data."""
        data = {
            "name": "Maud Nelson",
            "phone_numbers": ["+353830000017"]
        }
        contact = Contact.from_dict(data)
        assert contact.name == "Maud Nelson"
        assert contact.email is None
        assert contact.address is None
        assert contact.birthday is None
        assert contact.note is None
        assert contact.tags == []


class TestTagManipulation:
    """Tests for tag operations."""

    def test_create_contact_with_tags(self):
        """Tags should be normalized and stored."""
        contact = Contact.create(
            name="Oscar Paul",
            phone_numbers=["+353830000018"],
            tags=["Work", "Client", "PRIORITY"]
        )
        assert "work" in contact.tags
        assert "client" in contact.tags
        assert "priority" in contact.tags

    def test_add_tag_single(self):
        """Should add a single tag."""
        contact = Contact.create(
            name="Paula Quinn",
            phone_numbers=["+353830000019"],
            tags=["existing"]
        )
        contact.add_tag("New")
        assert "new" in contact.tags

    def test_add_tag_avoids_duplicates(self):
        """Should not add duplicate tags."""
        contact = Contact.create(
            name="Quincy Ray",
            phone_numbers=["+353830000020"],
            tags=["unique"]
        )
        contact.add_tag("unique")
        assert contact.tags.count("unique") == 1

    def test_add_tag_preserves_order(self):
        """Tags should maintain insertion order."""
        contact = Contact.create(
            name="Riley Strong",
            phone_numbers=["+353830000021"]
        )
        contact.add_tag("first")
        contact.add_tag("second")
        contact.add_tag("third")
        assert contact.tags == ["first", "second", "third"]

    def test_edit_tag_replaces_existing(self):
        """Should replace one tag with another."""
        contact = Contact.create(
            name="Sam Turner",
            phone_numbers=["+353830000022"],
            tags=["oldtag"]
        )
        contact.edit_tag("oldtag", "newtag")
        assert "oldtag" not in contact.tags
        assert "newtag" in contact.tags

    def test_edit_tag_nonexistent_is_noop(self):
        """Editing nonexistent tag should be safe."""
        contact = Contact.create(
            name="Uma Valley",
            phone_numbers=["+353830000023"],
            tags=["existing"]
        )
        contact.edit_tag("nonexistent", "newname")
        assert contact.tags == ["existing"]

    def test_remove_tag_single(self):
        """Should remove a tag."""
        contact = Contact.create(
            name="Victor Walsh",
            phone_numbers=["+353830000024"],
            tags=["first", "second", "third"]
        )
        contact.remove_tag("second")
        assert "second" not in contact.tags
        assert contact.tags == ["first", "third"]

    def test_remove_tag_nonexistent_is_noop(self):
        """Removing nonexistent tag should be safe."""
        contact = Contact.create(
            name="Wendy Xander",
            phone_numbers=["+353830000025"],
            tags=["only"]
        )
        contact.remove_tag("missing")
        assert contact.tags == ["only"]

    def test_tags_deduplication(self):
        """Should deduplicate tags on creation."""
        contact = Contact.create(
            name="Xavier Young",
            phone_numbers=["+353830000026"],
            tags=["tag", "TAG", "Tag", "other"]
        )
        # All should be normalized to "tag", deduplicated
        assert contact.tags.count("tag") == 1
        assert "other" in contact.tags

    def test_tags_empty_list(self):
        """Should handle empty tag list."""
        contact = Contact.create(
            name="Yara Zeller",
            phone_numbers=["+353830000027"],
            tags=[]
        )
        assert contact.tags == []


class TestContactUpdate:
    """Tests for updating contact fields."""

    def test_update_name(self):
        """Should update name field."""
        contact = Contact.create(
            name="Original Name",
            phone_numbers=["+353830000028"]
        )
        contact.update(name="Updated Name")
        assert contact.name == "Updated Name"

    def test_update_email(self):
        """Should update email field."""
        contact = Contact.create(
            name="Aaron Brady",
            phone_numbers=["+353830000029"]
        )
        contact.update(email="aaron@test.co.uk")
        assert contact.email == "aaron@test.co.uk"

    def test_update_phone_numbers(self):
        """Should update phone numbers."""
        contact = Contact.create(
            name="Bella Coleman",
            phone_numbers=["+353830000030"]
        )
        contact.update(phone_numbers=["+353830000031", "+353830000032"])
        # Phone numbers normalized by stub
        assert len(contact.phone_numbers) >= 1
        assert all(p.startswith("+1") for p in contact.phone_numbers)

    def test_update_phone_numbers_requires_at_least_one(self):
        """Should not allow removing all phone numbers."""
        contact = Contact.create(
            name="Caleb Davis",
            phone_numbers=["+353830000033"]
        )
        with pytest.raises(ValueError):
            contact.update(phone_numbers=[])

    def test_update_multiple_fields(self):
        """Should update multiple fields in one call."""
        contact = Contact.create(
            name="Diana Elliot",
            phone_numbers=["+353830000034"],
            email="old@test.co.uk"
        )
        contact.update(
            name="Diana Elliott",
            email="new@test.co.uk",
            address="123 New St"
        )
        assert contact.name == "Diana Elliott"
        assert contact.email == "new@test.co.uk"
        assert contact.address == "123 New St"

    def test_update_with_none_leaves_unchanged(self):
        """Passing None to update should skip that field."""
        contact = Contact.create(
            name="Evan Foster",
            phone_numbers=["+353830000035"],
            email="evan@test.co.uk"
        )
        contact.update(name="Evan Fraser", email=None)
        assert contact.name == "Evan Fraser"
        assert contact.email == "evan@test.co.uk"

    def test_update_note(self):
        """Should update note field."""
        contact = Contact.create(
            name="Fiona Grant",
            phone_numbers=["+353830000036"]
        )
        contact.update(note="Important contact")
        assert contact.note == "Important contact"

    def test_update_birthday(self):
        """Should update birthday field."""
        contact = Contact.create(
            name="George Harris",
            phone_numbers=["+353830000037"]
        )
        contact.update(birthday="2000-06-15")
        assert contact.birthday == "2000-06-15"

    def test_update_tags(self):
        """Should update tags list."""
        contact = Contact.create(
            name="Helen Ivory",
            phone_numbers=["+353830000038"],
            tags=["old"]
        )
        contact.update(tags=["new", "updated"])
        assert "old" not in contact.tags
        assert "new" in contact.tags
        assert "updated" in contact.tags


class TestContactSearch:
    """Tests for search functionality."""

    def test_search_matches_name(self):
        """Should find contact by name."""
        contact = Contact.create(
            name="Iris Jenkins",
            phone_numbers=["+353830000039"]
        )
        assert contact.matches_search("iris")
        assert contact.matches_search("jenkins")
        assert contact.matches_search("iris jenkins")

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        contact = Contact.create(
            name="Jack Kennedy",
            phone_numbers=["+353830000040"]
        )
        assert contact.matches_search("JACK")
        assert contact.matches_search("JaCk")
        assert contact.matches_search("jack KENNEDY")

    def test_search_matches_email(self):
        """Should find contact by email."""
        contact = Contact.create(
            name="Kathy Lewis",
            phone_numbers=["+353830000041"],
            email="kathy@test.co.uk"
        )
        assert contact.matches_search("kathy@")
        assert contact.matches_search("test.co")

    def test_search_matches_address(self):
        """Should find contact by address."""
        contact = Contact.create(
            name="Leo Martin",
            phone_numbers=["+353830000042"],
            address="123 Main Street"
        )
        assert contact.matches_search("main")
        assert contact.matches_search("street")

    def test_search_matches_phone_substring(self):
        """Should find contact by phone number substring."""
        contact = Contact.create(
            name="Molly Nelson",
            phone_numbers=["+353830000043"]
        )
        # Test partial phone match
        phone_sub = contact.phone_numbers[0][1:7]
        assert contact.matches_search(phone_sub)

    def test_search_matches_note(self):
        """Should find contact by note."""
        contact = Contact.create(
            name="Nathan Oliver",
            phone_numbers=["+353830000044"],
            note="Very important client"
        )
        assert contact.matches_search("important")
        assert contact.matches_search("client")

    def test_search_matches_tags(self):
        """Should find contact by tags."""
        contact = Contact.create(
            name="Olivia Peterson",
            phone_numbers=["+353830000045"],
            tags=["vip", "priority"]
        )
        assert contact.matches_search("vip")
        assert contact.matches_search("priority")

    def test_search_empty_query_returns_false(self):
        """Empty search query should return False."""
        contact = Contact.create(
            name="Patricia Quinn",
            phone_numbers=["+353830000046"]
        )
        assert not contact.matches_search("")
        assert not contact.matches_search("   ")

    def test_search_no_match_returns_false(self):
        """Non-matching query should return False."""
        contact = Contact.create(
            name="Quinn Roberts",
            phone_numbers=["+353830000047"]
        )
        assert not contact.matches_search("xyz")
        assert not contact.matches_search("nonexistent")

    def test_search_partial_matches(self):
        """Should match partial field values."""
        contact = Contact.create(
            name="Robert Summers",
            phone_numbers=["+353830000048"]
        )
        assert contact.matches_search("ober")  # Partial name
        assert contact.matches_search("mmer")  # Partial surname
