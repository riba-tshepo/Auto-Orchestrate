"""
Exit codes for CLI scripts.

These codes follow Unix conventions:
- 0: Success
- 1-127: Error conditions
- Specific ranges for different error categories
"""

# Success
EXIT_SUCCESS = 0

# General errors (1-10)
EXIT_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_TIMEOUT = 3

# File system errors (10-19)
EXIT_FILE_NOT_FOUND = 10
EXIT_PERMISSION_DENIED = 11

# Validation errors (20-29)
EXIT_VALIDATION_ERROR = 20

# Dependency errors (30-39)
EXIT_DEPENDENCY_ERROR = 30


def exit_code_to_message(code: int) -> str:
    """Convert exit code to human-readable message."""
    messages = {
        EXIT_SUCCESS: "Success",
        EXIT_ERROR: "General error",
        EXIT_INVALID_ARGS: "Invalid arguments",
        EXIT_TIMEOUT: "Operation timed out",
        EXIT_FILE_NOT_FOUND: "File not found",
        EXIT_PERMISSION_DENIED: "Permission denied",
        EXIT_VALIDATION_ERROR: "Validation failed",
        EXIT_DEPENDENCY_ERROR: "Dependency error",
    }
    return messages.get(code, f"Unknown error (code {code})")
