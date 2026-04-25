---
name: test-writer-pytest
description: |
  Python test writing skill using pytest framework.
  Use when user says "write tests", "create pytest tests", "add unit tests",
  "python tests", "test coverage", "write test cases", "integration tests",
  "create tests", "pytest", "test module".
triggers:
  - write tests
  - create pytest tests
  - add unit tests
  - python tests
  - test coverage
---

# Test Writer (Pytest) Skill

You are a test writer. Your role is to create comprehensive tests using the pytest framework following the project's test infrastructure.

## Capabilities

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test module interactions
3. **Fixtures** - Use conftest.py fixtures for test isolation
4. **Parametrized Tests** - Data-driven testing with multiple inputs

---

## Helper Scripts

The following scripts in `scripts/` provide automated test generation:

| Script | Purpose | CLI Example |
|--------|---------|-------------|
| `test_template_generator.py` | Generate pytest test files from function discovery | `python scripts/test_template_generator.py funcs.json --output tests/` |

### Usage

```bash
# First, discover functions using hierarchy-unifier
python ~/.claude/skills/hierarchy-unifier/scripts/function_discoverer.py lib/ -o json > funcs.json

# Generate test templates
python scripts/test_template_generator.py funcs.json --output-dir tests/

# Generate with parametrized tests
python scripts/test_template_generator.py funcs.json --parametrize --output-dir tests/

# Dry run (preview without writing files)
python scripts/test_template_generator.py funcs.json --dry-run -o json
```

---

## Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── fixtures/
│   ├── __init__.py
│   └── setup.py                 # Test utilities
├── test_layer0/                 # Layer 0 tests
│   ├── __init__.py
│   ├── test_exit_codes.py
│   ├── test_colors.py
│   └── test_constants.py
├── test_layer1/                 # Layer 1 tests
│   ├── __init__.py
│   ├── test_logging.py
│   ├── test_config.py
│   └── test_file_ops.py
├── test_layer2/                 # Layer 2 tests
│   ├── __init__.py
│   ├── test_validation.py
│   └── test_task_ops.py
└── test_layer3/                 # Layer 3 tests
    ├── __init__.py
    ├── test_migrate.py
    └── test_backup.py
```

---

## Available Fixtures

The project provides these fixtures in `tests/conftest.py`:

| Fixture | Purpose | Scope |
|---------|---------|-------|
| `tmp_project_dir` | Isolated temp directory for file operations | function |
| `mock_xdg_dirs` | Mock XDG directory environment variables | function |
| `isolated_env` | Clean environment without user config | function |
| `sample_config` | Pre-populated test configuration | function |
| `sample_tasks` | Test task data with known states | function |

### Using Fixtures

```python
def test_file_operation(tmp_project_dir):
    """Test that uses isolated temporary directory."""
    test_file = tmp_project_dir / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
    # tmp_project_dir is automatically cleaned up


def test_with_config(sample_config):
    """Test that needs pre-populated config."""
    assert sample_config.exists()
    # Use sample_config for testing


def test_clean_environment(isolated_env, monkeypatch):
    """Test in clean environment."""
    # isolated_env ensures no user config interference
    pass
```

---

## Test File Template

```python
"""
tests/test_layer{N}/test_{module_name}.py - Tests for {module_name} module.

Run with:
    pytest tests/test_layer{N}/test_{module_name}.py -v
    pytest tests/test_layer{N}/test_{module_name}.py -k "test_function_name"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from lib.layer{N}.{module_name} import (
    function_name,
    ClassName,
    SpecificError,
)


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Provide sample test data."""
    return {
        "key": "value",
        "number": 42,
    }


@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path


# ==============================================================================
# UNIT TESTS - function_name
# ==============================================================================


class TestFunctionName:
    """Tests for function_name."""

    def test_returns_success_with_valid_input(self):
        """Test that function returns success with valid input."""
        # Arrange
        input_value = "valid input"

        # Act
        result = function_name(input_value)

        # Assert
        assert result.success is True
        assert "completed" in result.message.lower()

    def test_raises_value_error_on_empty_input(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            function_name("")

    def test_handles_optional_arg(self):
        """Test that optional argument is processed correctly."""
        result = function_name("input", optional_arg=42)

        assert result.success is True
        assert result.data is not None

    @pytest.mark.parametrize(
        "input_value,expected_success",
        [
            ("valid", True),
            ("also valid", True),
            ("another valid", True),
        ],
    )
    def test_various_valid_inputs(self, input_value: str, expected_success: bool):
        """Test function with various valid inputs."""
        result = function_name(input_value)
        assert result.success == expected_success


# ==============================================================================
# UNIT TESTS - ClassName
# ==============================================================================


class TestClassName:
    """Tests for ClassName."""

    def test_initialization(self):
        """Test that class initializes correctly."""
        obj = ClassName("test value")

        assert obj.attribute_one == "test value"
        assert obj.attribute_two == 0

    def test_do_something_returns_true(self):
        """Test that do_something returns True."""
        obj = ClassName("value")

        result = obj.do_something()

        assert result is True


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_handles_file_not_found(self, tmp_path: Path):
        """Test graceful handling of missing files."""
        nonexistent = tmp_path / "does_not_exist.txt"

        # Function should handle gracefully, not crash
        # Adjust based on actual function behavior

    def test_raises_specific_error_on_invalid_state(self):
        """Test that SpecificError is raised appropriately."""
        with pytest.raises(SpecificError):
            # Trigger the specific error condition
            pass


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================


class TestIntegration:
    """Integration tests for module interactions."""

    def test_full_workflow(self, tmp_project_dir: Path):
        """Test complete workflow from start to finish."""
        # Arrange - set up initial state

        # Act - perform the workflow

        # Assert - verify final state
        pass

    def test_interacts_with_file_system(self, tmp_path: Path):
        """Test file system interactions."""
        test_file = tmp_path / "output.txt"

        # Perform operation that writes file

        assert test_file.exists()
```

---

## Test Patterns

### Arrange-Act-Assert (AAA)

```python
def test_with_aaa_pattern():
    """Clear structure with Arrange-Act-Assert."""
    # Arrange - set up test conditions
    input_data = {"key": "value"}
    expected_result = "processed"

    # Act - execute the code under test
    result = process_data(input_data)

    # Assert - verify the outcome
    assert result == expected_result
```

### Parametrized Tests

```python
@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("hello", "HELLO"),
        ("World", "WORLD"),
        ("pytest", "PYTEST"),
    ],
    ids=["lowercase", "mixed_case", "all_lower"],
)
def test_uppercase_conversion(input_value: str, expected: str):
    """Test uppercase conversion with various inputs."""
    assert input_value.upper() == expected
```

### Exception Testing

```python
def test_raises_exception_with_context():
    """Test that correct exception is raised with message."""
    with pytest.raises(ValueError) as exc_info:
        function_that_raises("")

    assert "cannot be empty" in str(exc_info.value)


def test_exception_attributes():
    """Test exception has correct attributes."""
    with pytest.raises(CustomError) as exc_info:
        function_that_raises_custom()

    assert exc_info.value.error_code == 42
```

### Fixture-Based Testing

```python
@pytest.fixture
def database_connection():
    """Provide database connection with cleanup."""
    conn = create_connection()
    yield conn
    conn.close()


def test_database_query(database_connection):
    """Test using database fixture."""
    result = database_connection.query("SELECT 1")
    assert result == 1
```

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific layer tests
pytest tests/test_layer0/ -v
pytest tests/ -k "layer0" -v

# Run specific test file
pytest tests/test_layer1/test_config.py -v

# Run specific test function
pytest tests/test_layer1/test_config.py::test_load_config -v

# Run tests matching pattern
pytest tests/ -k "test_valid" -v

# Run with coverage
pytest tests/ --cov=lib --cov-report=term-missing

# Run via project runner (recommended)
python dev/run_all_tests.py
```

---

## Task System Integration

@_shared/templates/skill-boilerplate.md#task-integration

### Execution Sequence

1. Get task details via `TaskGet`
2. Set focus via `TaskUpdate` (status: in_progress) - skip if orchestrator already set
3. Identify module to test and its layer
4. Create test file in appropriate tests/test_layer{N}/ directory
5. Run tests: `pytest tests/test_layer{N}/test_{module}.py -v`
6. Verify all tests pass
7. Append manifest entry to `{{MANIFEST_PATH}}`
8. Complete task via `TaskUpdate` (status: completed)
9. Return summary message only

---

## Subagent Protocol

@_shared/templates/skill-boilerplate.md#subagent-protocol

### Output Requirements

1. MUST create test file in appropriate tests/test_layer{N}/ directory
2. MUST use fixtures for test isolation
3. MUST include both happy path and error case tests
4. MUST run tests and verify they pass
5. MUST append ONE line to: `{{MANIFEST_PATH}}`
6. MUST return ONLY: "Tests complete. See MANIFEST.jsonl for summary."
7. MUST NOT return full test content in response

### Manifest Entry Format

@_shared/templates/skill-boilerplate.md#manifest-entry

Test-specific fields:

```json
{"id":"tests-{{MODULE}}-{{DATE}}","file":"{{DATE}}_tests-{{MODULE}}.md","title":"Tests: {{MODULE}}","date":"{{DATE}}","status":"complete","topics":["tests","pytest","layer{{N}}","{{DOMAIN}}"],"key_findings":["Created {{N}} tests: {{X}} unit, {{Y}} integration, {{Z}} error cases","All tests pass","Coverage: {{LIST_OF_SCENARIOS}}","Fixtures used: {{FIXTURE_LIST}}"],"actionable":false,"needs_followup":[],"linked_tasks":["{{TASK_ID}}"]}
```

---

## Completion Checklist

@_shared/templates/skill-boilerplate.md#completion-checklist

### Test-Specific Checks

- [ ] Test file created in correct tests/test_layer{N}/ directory
- [ ] Tests use fixtures for isolation (no global state)
- [ ] Happy path tests included
- [ ] Error handling tests included
- [ ] Edge case tests included (empty input, None, etc.)
- [ ] All tests pass when run
- [ ] Type hints in test code

---

## Anti-Patterns

@_shared/templates/anti-patterns.md#testing-anti-patterns

### Pytest-Specific Anti-Patterns

**DO NOT**:
- Use `unittest.TestCase` style (use plain functions/classes)
- Create tests that depend on execution order
- Skip cleanup (use fixtures with yield)
- Use `assert x == True` (use `assert x is True`)
- Ignore test isolation (each test must be independent)
- Use `time.sleep()` for async operations (use proper waiting)
- Hard-code paths (use `tmp_path` fixture)
- Test implementation details instead of behavior

---

## Skill Chaining

@_shared/protocols/skill-chain-contracts.md

### Produces

| Output | Format | Description |
|--------|--------|-------------|
| `test-files` | Python files | pytest test modules with tests |
| `test-report` | Markdown | Summary of tests created and coverage |

### Consumes

| Input | From Skill | Description |
|-------|------------|-------------|
| `gaps-list` | `test-gap-analyzer` | Prioritized list of functions needing tests |
| `test-stubs` | `test-gap-analyzer` | Generated test file skeletons |

### Chain Relationships

| Direction | Skills | Pattern |
|-----------|--------|---------|
| Chains from | `test-gap-analyzer` | analyzer-executor |
| Chains to | `validator` | quality-gate |

The test-writer-pytest consumes analysis from test-gap-analyzer and creates tests that validator can verify.
