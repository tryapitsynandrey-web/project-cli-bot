import pytest

from assistant_bot.cli.command_registry import CommandRegistry
from assistant_bot.cli.parser import Command


def _dummy_handler(command: Command) -> bool:
    return True


def _false_handler(command: Command) -> bool:
    return False


def test_register_and_get_command():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    handler = registry.get("help")

    assert handler is _dummy_handler


def test_registered_handler_can_be_called():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    command = Command(name="help", args=[])
    handler = registry.get("help")

    assert handler is not None
    assert handler(command) is True


def test_register_normalizes_command_name():
    registry = CommandRegistry()
    registry.register("  HeLp  ", _dummy_handler)

    assert registry.get("help") is _dummy_handler
    assert registry.get("HELP") is _dummy_handler
    assert registry.get("  help  ") is _dummy_handler


def test_get_normalizes_command_name_with_spaces():
    registry = CommandRegistry()
    registry.register("search-contact", _dummy_handler)

    assert registry.get("  search-contact  ") is _dummy_handler


def test_has_normalizes_command_name_with_spaces_and_case():
    registry = CommandRegistry()
    registry.register("list-notes", _dummy_handler)

    assert registry.has("list-notes") is True
    assert registry.has("LIST-NOTES") is True
    assert registry.has("  list-notes  ") is True


def test_register_empty_command_raises_value_error():
    registry = CommandRegistry()

    with pytest.raises(ValueError, match="Command name cannot be empty."):
        registry.register("   ", _dummy_handler)


def test_register_duplicate_command_raises_value_error():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("help", _dummy_handler)


def test_register_duplicate_command_is_case_insensitive():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("HELP", _false_handler)


def test_get_returns_none_for_unknown_command():
    registry = CommandRegistry()

    assert registry.get("missing") is None


def test_has_returns_true_for_registered_command():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    assert registry.has("help") is True
    assert registry.has("HELP") is True


def test_has_returns_false_for_unknown_command():
    registry = CommandRegistry()

    assert registry.has("missing") is False


def test_names_returns_sorted_command_names():
    registry = CommandRegistry()
    registry.register("search-contact", _dummy_handler)
    registry.register("help", _dummy_handler)
    registry.register("add-contact", _dummy_handler)

    assert registry.names() == ["add-contact", "help", "search-contact"]


def test_names_returns_empty_list_for_empty_registry():
    registry = CommandRegistry()

    assert registry.names() == []


def test_as_dict_returns_copy_of_registry_mapping():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    mapping = registry.as_dict()
    mapping["other"] = _dummy_handler

    assert registry.get("other") is None
    assert registry.get("help") is _dummy_handler


def test_as_dict_contains_all_registered_commands():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)
    registry.register("exit", _false_handler)

    mapping = registry.as_dict()

    assert set(mapping.keys()) == {"help", "exit"}
    assert mapping["help"] is _dummy_handler
    assert mapping["exit"] is _false_handler


def test_as_dict_returns_independent_mapping_object():
    registry = CommandRegistry()
    registry.register("help", _dummy_handler)

    mapping_one = registry.as_dict()
    mapping_two = registry.as_dict()

    assert mapping_one is not mapping_two
    assert mapping_one == mapping_two