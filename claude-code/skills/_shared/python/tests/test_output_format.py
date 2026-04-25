"""
Tests for layer1.output_format module.

Tests output formatting utilities including output, format_human, format_table,
and CLIOutput.
"""

import json
from io import StringIO

from layer1.output_format import (
    CLIOutput,
    OutputFormat,
    format_human,
    format_table,
    output,
)


def test_output_json_format():
    """Test output() with JSON format."""
    data = {"key": "value", "count": 42}
    buffer = StringIO()

    output(data, format_type=OutputFormat.JSON, file=buffer)

    result = buffer.getvalue()
    parsed = json.loads(result)
    assert parsed == data


def test_output_human_format():
    """Test output() with HUMAN format."""
    data = {"name": "test", "value": 123}
    buffer = StringIO()

    output(data, format_type=OutputFormat.HUMAN, file=buffer)

    result = buffer.getvalue()
    assert "name: test" in result
    assert "value: 123" in result


def test_output_table_format():
    """Test output() with TABLE format."""
    data = {"items": [{"id": 1, "name": "test"}]}
    buffer = StringIO()

    output(data, format_type=OutputFormat.TABLE, file=buffer)

    result = buffer.getvalue()
    assert "id" in result
    assert "name" in result


def test_format_human_simple_dict():
    """Test format_human() with simple dictionary."""
    data = {"key1": "value1", "key2": "value2"}

    result = format_human(data)

    assert "key1: value1" in result
    assert "key2: value2" in result


def test_format_human_nested_dict():
    """Test format_human() with nested dictionary."""
    data = {"parent": {"child1": "value1", "child2": "value2"}}

    result = format_human(data)

    assert "parent:" in result
    assert "child1: value1" in result
    assert "child2: value2" in result


def test_format_human_with_list():
    """Test format_human() with list values."""
    data = {"items": ["item1", "item2", "item3"]}

    result = format_human(data)

    assert "items:" in result
    assert "- item1" in result
    assert "- item2" in result
    assert "- item3" in result


def test_format_human_with_dict_list():
    """Test format_human() with list of dictionaries."""
    data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}

    result = format_human(data)

    assert "users:" in result
    assert "name: Alice" in result
    assert "name: Bob" in result


def test_format_table_simple_items():
    """Test format_table() with simple items."""
    data = {"items": [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]}

    result = format_table(data)

    assert "id" in result
    assert "name" in result
    assert "test1" in result
    assert "test2" in result
    assert "|" in result  # Table separator


def test_format_table_with_headers():
    """Test format_table() with custom headers."""
    data = {"items": [{"a": 1, "b": 2, "c": 3}]}

    result = format_table(data, headers=["a", "b"])

    assert "a" in result
    assert "b" in result
    # c should not be in result since headers specifies only a and b


def test_format_table_empty_items():
    """Test format_table() with no items."""
    data = {"items": []}

    result = format_table(data)

    assert result == "(no items)"


def test_format_table_custom_key():
    """Test format_table() with custom key."""
    data = {"results": [{"value": 1}, {"value": 2}]}

    result = format_table(data, key="results")

    assert "value" in result
    assert "1" in result
    assert "2" in result


def test_cli_output_success():
    """Test CLIOutput with success case."""
    output = CLIOutput(success=True, data={"result": "completed"}, message="Operation successful")

    result_dict = output.to_dict()

    assert result_dict["success"] is True
    assert result_dict["data"] == {"result": "completed"}
    assert result_dict["message"] == "Operation successful"
    assert result_dict.get("errors", []) == []


def test_cli_output_with_errors():
    """Test CLIOutput with errors."""
    output = CLIOutput(success=False, data={}, errors=["Error 1", "Error 2"])

    result_dict = output.to_dict()

    assert result_dict["success"] is False
    assert result_dict["errors"] == ["Error 1", "Error 2"]


def test_cli_output_default_values():
    """Test CLIOutput with default values."""
    output = CLIOutput(success=True, data={})

    result_dict = output.to_dict()

    assert result_dict["success"] is True
    assert result_dict["data"] == {}
    assert "message" not in result_dict  # Empty message should be omitted
    assert "errors" not in result_dict  # Empty errors should be omitted
