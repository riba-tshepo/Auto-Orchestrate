"""Tests enforcing the forward-only layer import architecture.

Uses AST parsing to detect import statements in each module and validates
that Layer N only imports from Layers 0 through N-1.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Base path to the Python library
LIB_ROOT = Path(__file__).resolve().parent.parent

# Layer names in order (index = layer number)
LAYER_NAMES = ["layer0", "layer1", "layer2", "layer3"]

# Map of layer name to allowed import sources (layer names)
ALLOWED_IMPORTS: dict[str, set[str]] = {
    "layer0": set(),
    "layer1": {"layer0"},
    "layer2": {"layer0", "layer1"},
    "layer3": {"layer0", "layer1", "layer2"},
}

# New modules added to the library
NEW_MODULES = [
    ("layer1", "heartbeat.py"),
    ("layer1", "memory.py"),
    ("layer2", "hooks.py"),
    ("layer2", "messaging.py"),
    ("layer2", "token_budget.py"),
    ("layer2", "webhooks.py"),
]


def _get_imports(filepath: Path) -> list[str]:
    """Parse a Python file and return all import module names."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def _get_layer_modules(layer_name: str) -> list[Path]:
    """Get all .py files in a layer directory (excluding __init__.py)."""
    layer_dir = LIB_ROOT / layer_name
    if not layer_dir.is_dir():
        return []
    return [f for f in sorted(layer_dir.glob("*.py")) if f.name != "__init__.py"]


def _check_layer_violations(module_path: Path, layer_name: str) -> list[str]:
    """Check if a module imports from forbidden layers.

    Same-layer peer imports (e.g. layer2.webhooks importing from layer2.hooks)
    are allowed and not flagged as violations.
    """
    allowed = ALLOWED_IMPORTS[layer_name]
    imports = _get_imports(module_path)
    violations: list[str] = []
    for imp in imports:
        for other_layer in LAYER_NAMES:
            # Same-layer peer imports are permitted
            if other_layer == layer_name:
                continue
            if (
                (imp.startswith(other_layer + ".") or imp == other_layer)
                and other_layer not in allowed
            ):
                violations.append(
                    f"{module_path.name}: imports '{imp}' from {other_layer} "
                    f"(allowed: {sorted(allowed) if allowed else 'none'})"
                )
    return violations


# ---------------------------------------------------------------------------
# Parametrized: validate every layer respects forward-only imports
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("layer_name", LAYER_NAMES)
def test_no_upward_imports(layer_name: str) -> None:
    """Verify that no module in the layer imports from a higher layer."""
    modules = _get_layer_modules(layer_name)
    all_violations: list[str] = []
    for mod_path in modules:
        violations = _check_layer_violations(mod_path, layer_name)
        all_violations.extend(violations)
    assert not all_violations, (
        f"Import violations in {layer_name}:\n" + "\n".join(all_violations)
    )


# ---------------------------------------------------------------------------
# Per-layer explicit tests
# ---------------------------------------------------------------------------


def test_layer0_imports_nothing_from_other_layers() -> None:
    """Layer0 modules must not import from any other layer."""
    modules = _get_layer_modules("layer0")
    assert modules, "layer0 has no modules"
    all_violations: list[str] = []
    for mod_path in modules:
        violations = _check_layer_violations(mod_path, "layer0")
        all_violations.extend(violations)
    assert not all_violations, (
        "layer0 import violations:\n" + "\n".join(all_violations)
    )


def test_layer1_imports_only_from_layer0() -> None:
    """Layer1 modules (including heartbeat.py, memory.py) may only import from layer0."""
    modules = _get_layer_modules("layer1")
    assert modules, "layer1 has no modules"
    all_violations: list[str] = []
    for mod_path in modules:
        violations = _check_layer_violations(mod_path, "layer1")
        all_violations.extend(violations)
    assert not all_violations, (
        "layer1 import violations:\n" + "\n".join(all_violations)
    )


def test_layer2_imports_only_from_layer0_and_layer1() -> None:
    """Layer2 modules (including hooks, messaging, token_budget, webhooks) may only import from layer0 and layer1."""
    modules = _get_layer_modules("layer2")
    assert modules, "layer2 has no modules"
    all_violations: list[str] = []
    for mod_path in modules:
        violations = _check_layer_violations(mod_path, "layer2")
        all_violations.extend(violations)
    assert not all_violations, (
        "layer2 import violations:\n" + "\n".join(all_violations)
    )


def test_layer3_imports_only_from_lower_layers() -> None:
    """Layer3 modules may only import from layer0, layer1, and layer2."""
    modules = _get_layer_modules("layer3")
    assert modules, "layer3 has no modules"
    all_violations: list[str] = []
    for mod_path in modules:
        violations = _check_layer_violations(mod_path, "layer3")
        all_violations.extend(violations)
    assert not all_violations, (
        "layer3 import violations:\n" + "\n".join(all_violations)
    )


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("layer_name", LAYER_NAMES)
def test_all_layers_have_modules(layer_name: str) -> None:
    """Every layer directory must exist and contain at least one .py module."""
    layer_dir = LIB_ROOT / layer_name
    assert layer_dir.is_dir(), f"{layer_name}/ directory does not exist"
    modules = _get_layer_modules(layer_name)
    assert modules, f"{layer_name}/ has no .py modules (excluding __init__.py)"


@pytest.mark.parametrize("layer,filename", NEW_MODULES)
def test_new_modules_exist(layer: str, filename: str) -> None:
    """Verify that all six new modules exist at their expected paths."""
    module_path = LIB_ROOT / layer / filename
    assert module_path.exists(), f"{layer}/{filename} not found at {module_path}"


# ---------------------------------------------------------------------------
# New-module-specific import compliance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("layer,filename", NEW_MODULES)
def test_new_module_import_compliance(layer: str, filename: str) -> None:
    """Verify each new module follows layer import rules."""
    module_path = LIB_ROOT / layer / filename
    assert module_path.exists(), f"{layer}/{filename} not found"
    violations = _check_layer_violations(module_path, layer)
    assert not violations, (
        f"Import violations in {layer}/{filename}:\n" + "\n".join(violations)
    )
