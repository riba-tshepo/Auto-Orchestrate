#!/usr/bin/env python3
"""Validate manifest.json against schema rules."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def validate_type(value: Any, expected_type: str, path: str, errors: list[str]) -> bool:
    """Validate that a value matches the expected type."""
    type_map = {
        "string": str,
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
    }

    if expected_type not in type_map:
        return True

    if not isinstance(value, type_map[expected_type]):
        errors.append(f"{path}: Expected {expected_type}, got {type(value).__name__}")
        return False

    return True


def validate_string_min_length(value: str, min_length: int, path: str, errors: list[str]) -> bool:
    """Validate that a string meets minimum length requirement."""
    if len(value) < min_length:
        errors.append(f"{path}: String length {len(value)} is less than minimum {min_length}")
        return False
    return True


def validate_integer_minimum(value: int, minimum: int, path: str, errors: list[str]) -> bool:
    """Validate that an integer meets minimum value requirement."""
    if value < minimum:
        errors.append(f"{path}: Integer value {value} is less than minimum {minimum}")
        return False
    return True


def validate_enum(value: str, allowed_values: list[str], path: str, errors: list[str]) -> bool:
    """Validate that a value is one of the allowed enum values."""
    if value not in allowed_values:
        errors.append(f"{path}: Value '{value}' not in allowed values {allowed_values}")
        return False
    return True


def validate_pattern(value: str, pattern: str, path: str, errors: list[str]) -> bool:
    """Validate that a string matches the expected pattern."""
    if not re.match(pattern, value):
        errors.append(f"{path}: String '{value}' does not match pattern '{pattern}'")
        return False
    return True


def validate_date_format(value: str, path: str, errors: list[str]) -> bool:
    """Validate that a string is a valid ISO 8601 date (YYYY-MM-DD)."""
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, value):
        errors.append(f"{path}: Date '{value}' is not in ISO 8601 format (YYYY-MM-DD)")
        return False
    return True


def validate_stats(stats: dict, path: str, errors: list[str]) -> None:
    """Validate the stats object."""
    required_fields = [
        "total_skills",
        "total_agents",
        "total_commands",
        "total_protocols",
        "total_templates",
        "total_style_guides",
    ]

    for field in required_fields:
        if field not in stats:
            errors.append(f"{path}.{field}: Required field missing")
            continue

        if not validate_type(stats[field], "integer", f"{path}.{field}", errors):
            continue

        validate_integer_minimum(stats[field], 0, f"{path}.{field}", errors)


def validate_agent(agent: dict, index: int, path: str, errors: list[str]) -> None:
    """Validate an agent object."""
    agent_path = f"{path}[{index}]"

    required_fields = [
        "name",
        "description",
        "model",
        "tools",
        "dispatch_triggers",
        "capabilities",
        "path",
    ]

    for field in required_fields:
        if field not in agent:
            errors.append(f"{agent_path}.{field}: Required field missing")

    if "name" in agent and validate_type(agent["name"], "string", f"{agent_path}.name", errors):
        validate_string_min_length(agent["name"], 1, f"{agent_path}.name", errors)

    if "description" in agent and validate_type(
        agent["description"], "string", f"{agent_path}.description", errors
    ):
        validate_string_min_length(agent["description"], 1, f"{agent_path}.description", errors)

    if "model" in agent and validate_type(agent["model"], "string", f"{agent_path}.model", errors):
        validate_enum(agent["model"], ["sonnet", "opus", "haiku"], f"{agent_path}.model", errors)

    if "tools" in agent and validate_type(agent["tools"], "array", f"{agent_path}.tools", errors):
        for i, tool in enumerate(agent["tools"]):
            if validate_type(tool, "string", f"{agent_path}.tools[{i}]", errors):
                validate_string_min_length(tool, 1, f"{agent_path}.tools[{i}]", errors)

    if "dispatch_triggers" in agent and validate_type(
        agent["dispatch_triggers"], "array", f"{agent_path}.dispatch_triggers", errors
    ):
        for i, trigger in enumerate(agent["dispatch_triggers"]):
            if validate_type(trigger, "string", f"{agent_path}.dispatch_triggers[{i}]", errors):
                validate_string_min_length(
                    trigger, 1, f"{agent_path}.dispatch_triggers[{i}]", errors
                )

    if "capabilities" in agent:
        validate_type(agent["capabilities"], "object", f"{agent_path}.capabilities", errors)

    if "path" in agent and validate_type(agent["path"], "string", f"{agent_path}.path", errors):
        validate_string_min_length(agent["path"], 1, f"{agent_path}.path", errors)


def validate_skill(skill: dict, index: int, path: str, errors: list[str]) -> None:
    """Validate a skill object."""
    skill_path = f"{path}[{index}]"

    required_fields = [
        "name",
        "description",
        "dispatch_triggers",
        "has_scripts",
        "has_references",
        "path",
    ]

    for field in required_fields:
        if field not in skill:
            errors.append(f"{skill_path}.{field}: Required field missing")

    if "name" in skill and validate_type(skill["name"], "string", f"{skill_path}.name", errors):
        validate_string_min_length(skill["name"], 1, f"{skill_path}.name", errors)

    if "description" in skill and validate_type(
        skill["description"], "string", f"{skill_path}.description", errors
    ):
        validate_string_min_length(skill["description"], 1, f"{skill_path}.description", errors)

    if "dispatch_triggers" in skill and validate_type(
        skill["dispatch_triggers"], "array", f"{skill_path}.dispatch_triggers", errors
    ):
        for i, trigger in enumerate(skill["dispatch_triggers"]):
            if validate_type(trigger, "string", f"{skill_path}.dispatch_triggers[{i}]", errors):
                validate_string_min_length(
                    trigger, 1, f"{skill_path}.dispatch_triggers[{i}]", errors
                )

    if "has_scripts" in skill:
        validate_type(skill["has_scripts"], "boolean", f"{skill_path}.has_scripts", errors)

    if "has_references" in skill:
        validate_type(skill["has_references"], "boolean", f"{skill_path}.has_references", errors)

    if "path" in skill and validate_type(skill["path"], "string", f"{skill_path}.path", errors):
        validate_string_min_length(skill["path"], 1, f"{skill_path}.path", errors)


def validate_command(command: dict, index: int, path: str, errors: list[str]) -> None:
    """Validate a command object."""
    command_path = f"{path}[{index}]"

    required_fields = ["name", "description", "path"]

    for field in required_fields:
        if field not in command:
            errors.append(f"{command_path}.{field}: Required field missing")

    if "name" in command and validate_type(
        command["name"], "string", f"{command_path}.name", errors
    ):
        validate_string_min_length(command["name"], 1, f"{command_path}.name", errors)

    if "description" in command and validate_type(
        command["description"], "string", f"{command_path}.description", errors
    ):
        validate_string_min_length(command["description"], 1, f"{command_path}.description", errors)

    if "path" in command and validate_type(
        command["path"], "string", f"{command_path}.path", errors
    ):
        validate_string_min_length(command["path"], 1, f"{command_path}.path", errors)


def validate_named_resource(resource: dict, index: int, path: str, errors: list[str]) -> None:
    """Validate a NamedResource object."""
    resource_path = f"{path}[{index}]"

    required_fields = ["name", "description", "path"]

    for field in required_fields:
        if field not in resource:
            errors.append(f"{resource_path}.{field}: Required field missing")

    if "name" in resource and validate_type(
        resource["name"], "string", f"{resource_path}.name", errors
    ):
        validate_string_min_length(resource["name"], 1, f"{resource_path}.name", errors)

    if "description" in resource and validate_type(
        resource["description"], "string", f"{resource_path}.description", errors
    ):
        validate_string_min_length(
            resource["description"], 1, f"{resource_path}.description", errors
        )

    if "path" in resource and validate_type(
        resource["path"], "string", f"{resource_path}.path", errors
    ):
        validate_string_min_length(resource["path"], 1, f"{resource_path}.path", errors)


def validate_reference(reference: dict, index: int, path: str, errors: list[str]) -> None:
    """Validate a Reference object."""
    reference_path = f"{path}[{index}]"

    required_fields = ["name", "path"]

    for field in required_fields:
        if field not in reference:
            errors.append(f"{reference_path}.{field}: Required field missing")

    if "name" in reference and validate_type(
        reference["name"], "string", f"{reference_path}.name", errors
    ):
        validate_string_min_length(reference["name"], 1, f"{reference_path}.name", errors)

    if "path" in reference and validate_type(
        reference["path"], "string", f"{reference_path}.path", errors
    ):
        validate_string_min_length(reference["path"], 1, f"{reference_path}.path", errors)


def validate_python_library(library: dict, path: str, errors: list[str]) -> None:
    """Validate a PythonLibrary object."""
    required_fields = ["base_path", "layers", "test_directory"]

    for field in required_fields:
        if field not in library:
            errors.append(f"{path}.{field}: Required field missing")

    if "base_path" in library and validate_type(
        library["base_path"], "string", f"{path}.base_path", errors
    ):
        validate_string_min_length(library["base_path"], 1, f"{path}.base_path", errors)

    if "layers" in library and validate_type(library["layers"], "array", f"{path}.layers", errors):
        for i, layer in enumerate(library["layers"]):
            if validate_type(layer, "string", f"{path}.layers[{i}]", errors):
                validate_string_min_length(layer, 1, f"{path}.layers[{i}]", errors)

    if "test_directory" in library and validate_type(
        library["test_directory"], "string", f"{path}.test_directory", errors
    ):
        validate_string_min_length(library["test_directory"], 1, f"{path}.test_directory", errors)


def validate_shared(shared: dict, path: str, errors: list[str]) -> None:
    """Validate the shared object."""
    required_fields = [
        "protocols",
        "templates",
        "style_guides",
        "tokens",
        "references",
        "python_library",
    ]

    for field in required_fields:
        if field not in shared:
            errors.append(f"{path}.{field}: Required field missing")

    if "protocols" in shared and validate_type(
        shared["protocols"], "array", f"{path}.protocols", errors
    ):
        for i, protocol in enumerate(shared["protocols"]):
            if validate_type(protocol, "object", f"{path}.protocols[{i}]", errors):
                validate_named_resource(protocol, i, f"{path}.protocols", errors)

    if "templates" in shared and validate_type(
        shared["templates"], "array", f"{path}.templates", errors
    ):
        for i, template in enumerate(shared["templates"]):
            if validate_type(template, "object", f"{path}.templates[{i}]", errors):
                validate_named_resource(template, i, f"{path}.templates", errors)

    if "style_guides" in shared and validate_type(
        shared["style_guides"], "array", f"{path}.style_guides", errors
    ):
        for i, guide in enumerate(shared["style_guides"]):
            if validate_type(guide, "object", f"{path}.style_guides[{i}]", errors):
                validate_named_resource(guide, i, f"{path}.style_guides", errors)

    if "tokens" in shared and validate_type(shared["tokens"], "array", f"{path}.tokens", errors):
        for i, token in enumerate(shared["tokens"]):
            if validate_type(token, "object", f"{path}.tokens[{i}]", errors):
                validate_named_resource(token, i, f"{path}.tokens", errors)

    if "references" in shared and validate_type(
        shared["references"], "array", f"{path}.references", errors
    ):
        for i, reference in enumerate(shared["references"]):
            if validate_type(reference, "object", f"{path}.references[{i}]", errors):
                validate_reference(reference, i, f"{path}.references", errors)

    if "python_library" in shared and validate_type(
        shared["python_library"], "object", f"{path}.python_library", errors
    ):
        validate_python_library(shared["python_library"], f"{path}.python_library", errors)


def validate_manifest(manifest_path: Path, verbose: bool = False) -> list[str]:
    """Validate manifest and return list of errors."""
    errors = []

    # Load manifest
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        errors.append(f"Manifest file not found: {manifest_path}")
        return errors
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if verbose:
        print(f"Loaded manifest from {manifest_path}")

    # Validate top-level required fields
    required_fields = [
        "schema_version",
        "name",
        "description",
        "updated_at",
        "stats",
        "agents",
        "skills",
        "commands",
        "shared",
    ]

    for field in required_fields:
        if field not in manifest:
            errors.append(f"Root.{field}: Required field missing")

    # Validate schema_version
    if "schema_version" in manifest and validate_type(
        manifest["schema_version"], "string", "Root.schema_version", errors
    ):
        validate_pattern(
            manifest["schema_version"], r"^\d+\.\d+\.\d+$", "Root.schema_version", errors
        )

    # Validate name
    if "name" in manifest and validate_type(manifest["name"], "string", "Root.name", errors):
        validate_string_min_length(manifest["name"], 1, "Root.name", errors)

    # Validate description
    if "description" in manifest and validate_type(
        manifest["description"], "string", "Root.description", errors
    ):
        validate_string_min_length(manifest["description"], 1, "Root.description", errors)

    # Validate updated_at
    if "updated_at" in manifest and validate_type(
        manifest["updated_at"], "string", "Root.updated_at", errors
    ):
        validate_date_format(manifest["updated_at"], "Root.updated_at", errors)

    # Validate stats
    if "stats" in manifest and validate_type(manifest["stats"], "object", "Root.stats", errors):
        validate_stats(manifest["stats"], "Root.stats", errors)

    # Validate agents
    if "agents" in manifest and validate_type(manifest["agents"], "array", "Root.agents", errors):
        for i, agent in enumerate(manifest["agents"]):
            if validate_type(agent, "object", f"Root.agents[{i}]", errors):
                validate_agent(agent, i, "Root.agents", errors)

    # Validate skills
    if "skills" in manifest and validate_type(manifest["skills"], "array", "Root.skills", errors):
        for i, skill in enumerate(manifest["skills"]):
            if validate_type(skill, "object", f"Root.skills[{i}]", errors):
                validate_skill(skill, i, "Root.skills", errors)

    # Validate commands
    if "commands" in manifest and validate_type(
        manifest["commands"], "array", "Root.commands", errors
    ):
        for i, command in enumerate(manifest["commands"]):
            if validate_type(command, "object", f"Root.commands[{i}]", errors):
                validate_command(command, i, "Root.commands", errors)

    # Validate shared
    if "shared" in manifest and validate_type(manifest["shared"], "object", "Root.shared", errors):
        validate_shared(manifest["shared"], "Root.shared", errors)

    return errors


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate manifest.json against schema rules")
    parser.add_argument(
        "manifest",
        nargs="?",
        default="claude-code/manifest.json",
        help="Path to manifest.json file (default: claude-code/manifest.json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    manifest_path = Path(args.manifest)

    # Make path absolute if relative
    if not manifest_path.is_absolute():
        manifest_path = Path.cwd() / manifest_path

    if args.verbose:
        print(f"Validating manifest: {manifest_path}")

    errors = validate_manifest(manifest_path, args.verbose)

    if errors:
        print("Validation failed with the following errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("Validation successful!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
