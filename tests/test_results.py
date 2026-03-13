import pytest

from assistant_bot.cli.results import CommandResult


class TestCommandResultConstructors:
    """Tests for CommandResult factory methods."""

    def test_success_with_message_and_data(self):
        """Success result should store message and data."""
        data = {"id": 123, "name": "test"}
        result = CommandResult.success("Operation completed", data=data)
        assert result.status == "success"
        assert result.message == "Operation completed"
        assert result.data == data
        assert result.details == []

    def test_success_with_none_message(self):
        """Success result allows None message."""
        result = CommandResult.success()
        assert result.status == "success"
        assert result.message is None
        assert result.data is None
        assert result.details == []

    def test_success_with_details(self):
        """Success result should store details list."""
        details = ["Step 1 complete", "Step 2 complete"]
        result = CommandResult.success("Done", details=details)
        assert result.status == "success"
        assert result.details == details
        assert len(result.details) == 2

    def test_error_with_message(self):
        """Error result should require message."""
        result = CommandResult.error("Operation failed")
        assert result.status == "error"
        assert result.message == "Operation failed"
        assert result.data is None
        assert result.details == []

    def test_error_with_data_and_details(self):
        """Error result can include diagnostic data and details."""
        details = ["Reason 1", "Reason 2", "Reason 3"]
        data = {"error_code": 500, "trace": "exception trace"}
        result = CommandResult.error(
            "Failed to process", data=data, details=details
        )
        assert result.status == "error"
        assert result.message == "Failed to process"
        assert result.data == data
        assert result.details == details
        assert len(result.details) == 3

    def test_info_result(self):
        """Info result should work as expected."""
        result = CommandResult.info("For your information")
        assert result.status == "info"
        assert result.message == "For your information"
        assert result.data is None
        assert result.details == []

    def test_info_with_all_fields(self):
        """Info result can have all fields populated."""
        data = {"timestamp": "2024-01-01"}
        details = ["Detail A", "Detail B"]
        result = CommandResult.info("FYI", data=data, details=details)
        assert result.status == "info"
        assert result.message == "FYI"
        assert result.data == data
        assert result.details == details

    def test_warning_result(self):
        """Warning result should work as expected."""
        result = CommandResult.warning("Caution required")
        assert result.status == "warning"
        assert result.message == "Caution required"
        assert result.data is None
        assert result.details == []

    def test_warning_with_details(self):
        """Warning result should include details."""
        details = ["Check this", "Review that"]
        result = CommandResult.warning("Be careful", details=details)
        assert result.status == "warning"
        assert result.details == details

    def test_details_default_to_empty_list(self):
        """Details field should default to empty list."""
        s = CommandResult.success("msg")
        e = CommandResult.error("msg")
        i = CommandResult.info("msg")
        w = CommandResult.warning("msg")
        assert s.details == []
        assert e.details == []
        assert i.details == []
        assert w.details == []

    def test_details_not_shared_between_instances(self):
        """Each instance should have independent details list."""
        r1 = CommandResult.success("msg1")
        r2 = CommandResult.success("msg2")
        r1.details.append("item1")
        assert r1.details == ["item1"]
        assert r2.details == []  # Should not be shared


class TestCommandResultFields:
    """Tests for field values and types."""

    @pytest.mark.parametrize("status", ["success", "error", "info", "warning"])
    def test_all_statuses_valid(self, status):
        """All status types should be valid."""
        if status == "success":
            result = CommandResult.success("msg")
        elif status == "error":
            result = CommandResult.error("msg")
        elif status == "info":
            result = CommandResult.info("msg")
        else:  # warning
            result = CommandResult.warning("msg")
        assert result.status == status

    def test_data_can_be_various_types(self):
        """Data field should accept various types."""
        # List
        result_list = CommandResult.success(data=[1, 2, 3])
        assert result_list.data == [1, 2, 3]

        # Dict
        result_dict = CommandResult.success(data={"key": "value"})
        assert result_dict.data == {"key": "value"}

        # String
        result_str = CommandResult.success(data="string data")
        assert result_str.data == "string data"

        # Integer
        result_int = CommandResult.success(data=42)
        assert result_int.data == 42

        # None
        result_none = CommandResult.success()
        assert result_none.data is None

    def test_empty_details_list_behavior(self):
        """Empty details list should behave correctly."""
        result = CommandResult.success(details=[])
        assert len(result.details) == 0
        assert isinstance(result.details, list)

    def test_large_details_list(self):
        """Should handle large details lists."""
        large_details = [f"Detail {i}" for i in range(100)]
        result = CommandResult.success(details=large_details)
        assert len(result.details) == 100
        assert result.details[-1] == "Detail 99"


class TestCommandResultEquality:
    """Tests for instance equality and semantics."""

    def test_identical_results_are_equal(self):
        """Identical results should be equal (dataclass default)."""
        r1 = CommandResult.success("msg")
        r2 = CommandResult.success("msg")
        assert r1 == r2

    def test_different_messages_not_equal(self):
        """Different messages should create different results."""
        r1 = CommandResult.success("msg1")
        r2 = CommandResult.success("msg2")
        assert r1 != r2

    def test_different_statuses_not_equal(self):
        """Different statuses should not be equal."""
        s = CommandResult.success("msg")
        e = CommandResult.error("msg")
        assert s != e

    def test_different_data_not_equal(self):
        """Different data should create different results."""
        r1 = CommandResult.success("msg", data=[1, 2])
        r2 = CommandResult.success("msg", data=[1, 3])
        assert r1 != r2

    def test_different_details_not_equal(self):
        """Different details should create different results."""
        r1 = CommandResult.success("msg", details=["a"])
        r2 = CommandResult.success("msg", details=["b"])
        assert r1 != r2


class TestCommandResultRepresentation:
    """Tests for dataclass behavior."""

    def test_result_has_string_representation(self):
        """Result should have a string representation."""
        result = CommandResult.success("test message", data={"key": "value"})
        repr_str = repr(result)
        assert "CommandResult" in repr_str
        assert "success" in repr_str


class TestCommandResultEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_empty_string_message(self):
        """Should handle empty string messages."""
        result = CommandResult.success("")
        assert result.message == ""
        assert result.status == "success"

    def test_very_long_message(self):
        """Should handle very long messages."""
        long_msg = "x" * 10000
        result = CommandResult.error(long_msg)
        assert result.message == long_msg
        assert len(result.message) == 10000

    def test_unicode_in_message(self):
        """Should handle unicode characters."""
        result = CommandResult.success("Hello 世界 🌍")
        assert "世界" in result.message
        assert "🌍" in result.message

    def test_unicode_in_details(self):
        """Should handle unicode in details."""
        result = CommandResult.success(details=["Élève", "Café", "Москва"])
        assert "Élève" in result.details
        assert "Москва" in result.details

    def test_none_values_handled(self):
        """Should handle None values in data and details."""
        result = CommandResult.success(data=None, details=None)
        assert result.data is None
        # details None should be converted to []
        assert result.details == []
