# Pytest Test Suite for Shared Python Libraries

This directory contains comprehensive pytest tests for all layer modules in the shared Python library.

## Test Files

### Infrastructure
- `__init__.py` — Test package initialization
- `conftest.py` — Shared fixtures (temp_dir, sample_json_data, sample_task_id)

### Layer 0 Tests
- `test_exit_codes.py` — Exit code constants and message conversion (6 tests)
- `test_colors.py` — ANSI color utilities (6 tests)
- `test_constants.py` — Application constants validation (6 tests)

### Layer 1 Tests
- `test_error_json.py` — Structured JSON error output (5 tests)
- `test_config.py` — Configuration management (8 tests)

### Layer 2 Tests
- `test_task_ops.py` — Task ID parsing and validation (13 tests)

### Layer 3 Tests
- `test_doctor.py` — System diagnostics (8 tests)
- `test_hierarchy_unified.py` — Task hierarchy operations (13 tests)

## Running Tests

```bash
# Run all tests
cd /home/tshepo/projects/plugins-ai/claude-code/skills/_shared/python
pytest tests/

# Run specific test file
pytest tests/test_colors.py

# Run with coverage
pytest --cov=layer0 --cov=layer1 --cov=layer2 --cov=layer3 tests/

# Run with verbose output
pytest -v tests/
```

## Test Coverage

Each test file covers:
- **Happy path**: Normal operation with valid inputs
- **Edge cases**: Empty inputs, None values, boundary conditions
- **Error conditions**: Invalid inputs, exceptions, error handling

## Test Count Summary

- **Total test files**: 8
- **Total test functions**: ~65 tests
- **Layers covered**: All (layer0, layer1, layer2, layer3)

## Dependencies

Required packages:
- `pytest>=7.0.0`
- Python 3.10+

Install test dependencies:
```bash
pip install pytest pytest-cov
```

## Notes

- Tests use shared fixtures from `conftest.py` for consistency
- Tests do not require actual `~/.claude/` directory (uses temp_dir fixture)
- All tests pass syntax validation via `python3 -m py_compile`
