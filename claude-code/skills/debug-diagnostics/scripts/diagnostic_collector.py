#!/usr/bin/env python3
"""Collect diagnostic data for a given error category.

Usage:
    python3 diagnostic_collector.py --category docker --root /path/to/project
    python3 diagnostic_collector.py --category runtime --root .
    python3 diagnostic_collector.py --help

Output: JSON object with collected diagnostic data, secrets redacted.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"))
from layer0 import EXIT_SUCCESS, EXIT_ERROR, EXIT_INVALID_ARGS, EXIT_VALIDATION_ERROR
from layer1 import emit_error, emit_warning, emit_info


SECRET_PATTERNS = re.compile(
    r"(PASSWORD|PASS|SECRET|TOKEN|API_KEY|PRIVATE_KEY|AUTH|CREDENTIAL)(\s*[=:]\s*)\S+",
    re.IGNORECASE,
)


def redact(text: str) -> str:
    """Redact sensitive values from text."""
    return SECRET_PATTERNS.sub(r"\1\2***REDACTED***", text)


def run_cmd(cmd: str, timeout: int = 10) -> Optional[str]:
    """Run a shell command, return stdout or None on failure."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr.strip():
            output = (output + "\n" + result.stderr.strip()).strip()
        return redact(output) if output else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def find_files(root: Path, patterns: list[str], max_results: int = 20) -> list[str]:
    """Find files matching patterns under root, respecting .gitignore."""
    found = []
    gitignore_patterns: set[str] = set()
    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    gitignore_patterns.add(line)

    for pattern in patterns:
        for path in root.rglob(pattern):
            if len(found) >= max_results:
                break
            rel = str(path.relative_to(root))
            # Skip common sensitive/ignored paths
            if any(
                part in rel
                for part in (".git", "node_modules", "__pycache__", ".venv", "venv")
            ):
                continue
            found.append(rel)
    return found[:max_results]


def read_file_safe(path: str, max_lines: int = 30) -> Optional[str]:
    """Read first N lines of a file, redacting secrets."""
    try:
        with open(path) as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"... ({i} more lines)")
                    break
                lines.append(line.rstrip())
            return redact("\n".join(lines))
    except (OSError, UnicodeDecodeError):
        return None


def collect_universal(root: Path) -> dict:
    """Collect universal diagnostic data."""
    data = {}

    # Language versions
    versions = {}
    for cmd, name in [
        ("python3 --version", "python"),
        ("node --version", "node"),
        ("go version", "go"),
        ("rustc --version", "rust"),
        ("java --version 2>&1 | head -1", "java"),
    ]:
        v = run_cmd(cmd)
        if v:
            versions[name] = v
    data["language_versions"] = versions

    # Dependency manifests
    manifests = {}
    for fname in [
        "requirements.txt", "Pipfile", "pyproject.toml", "setup.py",
        "package.json", "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
    ]:
        fpath = root / fname
        if fpath.exists():
            content = read_file_safe(str(fpath))
            if content:
                manifests[fname] = content
    data["dependency_manifests"] = manifests

    # Working directory
    data["cwd"] = str(root.resolve())

    return data


def collect_docker(root: Path) -> dict:
    """Collect Docker-specific diagnostics."""
    data = {}
    data["compose_ps"] = run_cmd("docker compose ps --format json")
    data["compose_logs"] = run_cmd("docker compose logs --tail=50 2>&1", timeout=15)
    data["docker_version"] = run_cmd("docker --version")
    data["compose_version"] = run_cmd("docker compose version")

    # Container details
    container_ids = run_cmd("docker compose ps -q 2>/dev/null")
    if container_ids:
        states = []
        for cid in container_ids.strip().splitlines():
            cid = cid.strip()
            if cid:
                state = run_cmd(f"docker inspect {cid} --format '{{{{json .State}}}}'")
                name = run_cmd(f"docker inspect {cid} --format '{{{{.Name}}}}'")
                health = run_cmd(
                    f"docker inspect {cid} --format '{{{{json .State.Health}}}}'"
                )
                ports = run_cmd(
                    f"docker inspect {cid} --format '{{{{json .NetworkSettings.Ports}}}}'"
                )
                states.append({
                    "id": cid[:12],
                    "name": name,
                    "state": state,
                    "health": health,
                    "ports": ports,
                })
        data["containers"] = states

    # Resource usage
    data["stats"] = run_cmd(
        'docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}"',
        timeout=15,
    )

    # Compose and Dockerfile content
    for fname in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        fpath = root / fname
        if fpath.exists():
            data["compose_file"] = read_file_safe(str(fpath), max_lines=50)
            data["compose_file_name"] = fname
            break

    dockerfiles = find_files(root, ["Dockerfile", "Dockerfile.*", "*.dockerfile"], max_results=5)
    if dockerfiles:
        data["dockerfiles"] = {f: read_file_safe(str(root / f), max_lines=50) for f in dockerfiles}

    # Port conflicts
    data["port_conflicts"] = run_cmd(
        "ss -tlnp 2>/dev/null | grep -E ':(80|443|3000|5000|5432|6379|8080|8443|27017)'"
    )

    return data


def collect_runtime(_root: Path) -> dict:
    """Collect runtime error diagnostics."""
    data = {}
    data["memory"] = run_cmd("free -h 2>/dev/null")
    data["disk"] = run_cmd("df -h . 2>/dev/null")
    data["core_dumps"] = run_cmd("ls -la /tmp/core* 2>/dev/null")
    data["ulimits"] = run_cmd("ulimit -a 2>/dev/null")
    return data


def collect_configuration(root: Path) -> dict:
    """Collect configuration diagnostics."""
    data = {}

    # Environment variables (redacted)
    env_output = run_cmd(
        "env | grep -iE '(DATABASE|REDIS|API|APP|PORT|HOST|SECRET|KEY|TOKEN|URL|CONFIG|ENV|MODE|DEBUG)' | sort"
    )
    data["env_vars"] = env_output

    # Config files
    config_files = find_files(
        root,
        ["*.env", ".env.*", "*.conf", "*.cfg", "*.ini", "*.toml", "*.yaml", "*.yml"],
    )
    data["config_files_found"] = config_files

    # Read .env files
    env_files = {}
    for f in config_files:
        if ".env" in f:
            content = read_file_safe(str(root / f), max_lines=20)
            if content:
                env_files[f] = content
    data["env_file_contents"] = env_files

    return data


def collect_dependency(root: Path) -> dict:
    """Collect dependency diagnostics."""
    data = {}
    data["pip_list"] = run_cmd("pip list 2>/dev/null")
    data["npm_ls"] = run_cmd("npm ls --depth=0 2>/dev/null")
    data["lock_files"] = run_cmd(f"ls -la {root}/*lock* 2>/dev/null")
    data["virtual_env"] = os.environ.get("VIRTUAL_ENV", "not set")
    data["node_modules_exists"] = (root / "node_modules").exists()
    return data


def collect_network(_root: Path) -> dict:
    """Collect network diagnostics."""
    data = {}
    data["listening_ports"] = run_cmd("ss -tlnp 2>/dev/null")
    data["dns_resolv"] = read_file_safe("/etc/resolv.conf", max_lines=10)
    return data


def collect_database(root: Path) -> dict:
    """Collect database diagnostics."""
    data = {}

    # Connection info (redacted)
    data["db_env_vars"] = run_cmd(
        "env | grep -iE '(DATABASE_URL|DB_HOST|DB_PORT|DB_NAME|POSTGRES|MYSQL|MONGO|REDIS)' | sort"
    )

    # Migration status
    data["django_migrations"] = run_cmd("python3 manage.py showmigrations 2>/dev/null")
    data["alembic_current"] = run_cmd("alembic current 2>/dev/null")
    data["prisma_status"] = run_cmd("npx prisma migrate status 2>/dev/null")

    # DB readiness
    data["pg_isready"] = run_cmd("pg_isready 2>/dev/null")
    data["mysql_ping"] = run_cmd("mysqladmin ping 2>/dev/null")

    # Migration files
    migration_files = find_files(root, ["*/migrations/*.py", "*/migration*/*.sql"], max_results=10)
    data["migration_files"] = migration_files

    return data


def collect_permission(_root: Path) -> dict:
    """Collect permission diagnostics."""
    data = {}
    data["current_user"] = run_cmd("id")
    data["cwd_permissions"] = run_cmd("ls -la .")
    return data


COLLECTORS = {
    "docker": collect_docker,
    "runtime": collect_runtime,
    "configuration": collect_configuration,
    "dependency": collect_dependency,
    "network": collect_network,
    "database": collect_database,
    "permission": collect_permission,
    "syntax": lambda root: {},  # Syntax errors need file content, not system state
}


def main():
    parser = argparse.ArgumentParser(description="Collect diagnostic data for an error category")
    parser.add_argument(
        "--category", "-c", required=True,
        choices=list(COLLECTORS.keys()),
        help="Error category to collect diagnostics for",
    )
    parser.add_argument("--root", "-r", default=".", help="Project root directory (default: .)")
    parser.add_argument("--docker", "-d", action="store_true", help="Also collect Docker diagnostics")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        emit_error(f"Root directory not found: {root}")
        sys.exit(EXIT_INVALID_ARGS)

    result = {
        "category": args.category,
        "project_root": str(root),
        "universal": collect_universal(root),
    }

    # Category-specific collection
    collector = COLLECTORS.get(args.category)
    if collector:
        result["category_data"] = collector(root)

    # Optionally include Docker data
    if args.docker and args.category != "docker":
        result["docker_data"] = collect_docker(root)

    # Remove None values for cleaner output
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [clean(i) for i in obj]
        return obj

    print(json.dumps(clean(result), indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
