#!/usr/bin/env python3
"""Discover Docker services from compose files and check their running state.

Usage:
    python3 service_discovery.py --compose docker-compose.yml
    python3 service_discovery.py --compose docker-compose.yml --root /path/to/project
    python3 service_discovery.py --help

Output: JSON with service definitions, running state, health, and port accessibility.
"""

import argparse
import json
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add shared library to path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer0 import EXIT_SUCCESS, EXIT_ERROR  # noqa: E402
from layer1 import emit_error, emit_warning, emit_info  # noqa: E402


# Known service ports for health check inference
KNOWN_SERVICES = {
    "postgres": {"port": 5432, "type": "database"},
    "postgresql": {"port": 5432, "type": "database"},
    "mysql": {"port": 3306, "type": "database"},
    "mariadb": {"port": 3306, "type": "database"},
    "mongo": {"port": 27017, "type": "database"},
    "mongodb": {"port": 27017, "type": "database"},
    "redis": {"port": 6379, "type": "cache"},
    "memcached": {"port": 11211, "type": "cache"},
    "rabbitmq": {"port": 5672, "type": "broker"},
    "kafka": {"port": 9092, "type": "broker"},
    "elasticsearch": {"port": 9200, "type": "search"},
    "nginx": {"port": 80, "type": "proxy"},
    "traefik": {"port": 80, "type": "proxy"},
    "minio": {"port": 9000, "type": "storage"},
}


def run_cmd(cmd: str, timeout: int = 10) -> Optional[str]:
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a TCP port is accessible."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def check_http(url: str, timeout: int = 5) -> Optional[int]:
    """Check HTTP endpoint and return status code."""
    result = run_cmd(
        f'curl -sf -o /dev/null -w "%{{http_code}}" "{url}" 2>/dev/null',
        timeout=timeout,
    )
    if result and result.isdigit():
        return int(result)
    return None


def parse_compose(compose_path: str) -> list[dict]:
    """Parse docker-compose.yml to extract service definitions."""
    try:
        import yaml
        with open(compose_path) as f:
            data = yaml.safe_load(f)
    except ImportError:
        # Fallback: use basic regex parsing
        return parse_compose_basic(compose_path)
    except Exception as e:
        return [{"error": str(e)}]

    services = []
    svc_dict = data.get("services", {})

    for name, config in svc_dict.items():
        if not isinstance(config, dict):
            continue

        # Extract ports
        ports = []
        for port_def in config.get("ports", []):
            port_str = str(port_def)
            # Parse "8080:80", "5432:5432/tcp", "127.0.0.1:3000:3000"
            m = re.search(r"(\d+):(\d+)", port_str)
            if m:
                ports.append({
                    "host": int(m.group(1)),
                    "container": int(m.group(2)),
                })

        # Infer service type from name/image
        svc_type = "application"
        image = config.get("image", "")
        for known_name, info in KNOWN_SERVICES.items():
            if known_name in name.lower() or known_name in image.lower():
                svc_type = info["type"]
                # Add default port if none defined
                if not ports:
                    ports.append({"host": info["port"], "container": info["port"]})
                break

        services.append({
            "name": name,
            "image": config.get("image", config.get("build", "custom-build")),
            "ports": ports,
            "healthcheck": config.get("healthcheck"),
            "depends_on": list(config.get("depends_on", {}).keys()) if isinstance(config.get("depends_on"), dict) else config.get("depends_on", []),
            "environment": list(config.get("environment", {}).keys()) if isinstance(config.get("environment"), dict) else [e.split("=")[0] for e in config.get("environment", []) if isinstance(e, str)],
            "volumes": [str(v) for v in config.get("volumes", [])],
            "type": svc_type,
        })

    return services


def parse_compose_basic(compose_path: str) -> list[dict]:
    """Basic compose file parsing without YAML library."""
    try:
        with open(compose_path) as f:
            content = f.read()
    except OSError:
        return []

    services = []
    # Simple regex-based service extraction
    in_services = False
    current_service = None
    indent_level = 0

    for line in content.splitlines():
        stripped = line.strip()

        if stripped == "services:":
            in_services = True
            continue

        if in_services:
            # Detect service name (2-space indent, no leading -)
            m = re.match(r"^  (\w[\w-]*):\s*$", line)
            if m:
                if current_service:
                    services.append(current_service)
                current_service = {
                    "name": m.group(1),
                    "image": "",
                    "ports": [],
                    "healthcheck": None,
                    "depends_on": [],
                    "environment": [],
                    "volumes": [],
                    "type": "application",
                }
                # Check known services
                for known_name, info in KNOWN_SERVICES.items():
                    if known_name in m.group(1).lower():
                        current_service["type"] = info["type"]
                        break
                continue

            if current_service:
                if "image:" in stripped:
                    current_service["image"] = stripped.split("image:")[-1].strip().strip('"\'')
                elif re.match(r'^- ["\']?\d+:\d+', stripped):
                    m = re.search(r"(\d+):(\d+)", stripped)
                    if m:
                        current_service["ports"].append({
                            "host": int(m.group(1)),
                            "container": int(m.group(2)),
                        })

    if current_service:
        services.append(current_service)

    return services


def check_running_containers() -> dict:
    """Get running container state from docker compose."""
    output = run_cmd("docker compose ps --format json 2>/dev/null")
    if not output:
        return {}

    containers = {}
    for line in output.strip().splitlines():
        try:
            data = json.loads(line)
            name = data.get("Service") or data.get("Name", "")
            containers[name.lower()] = {
                "name": data.get("Name", ""),
                "state": data.get("State", ""),
                "status": data.get("Status", ""),
                "health": data.get("Health", ""),
            }
        except json.JSONDecodeError:
            continue

    return containers


def check_container_health(service_name: str) -> Optional[str]:
    """Check container health via docker inspect."""
    output = run_cmd(
        f"docker compose ps -q {service_name} 2>/dev/null"
    )
    if not output:
        return None

    container_id = output.strip().splitlines()[0]
    health = run_cmd(
        f"docker inspect {container_id} --format '{{{{json .State.Health}}}}' 2>/dev/null"
    )
    if health and health != "null" and health != "<nil>":
        try:
            data = json.loads(health)
            return data.get("Status", "unknown")
        except json.JSONDecodeError:
            pass
    return None


def discover_services(compose_path: str, project_root: str = ".") -> dict:
    """Full service discovery: parse compose, check state, test connectivity."""
    path = Path(compose_path)
    if not path.exists():
        # Try common alternatives
        for alt in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
            alt_path = Path(project_root) / alt
            if alt_path.exists():
                path = alt_path
                break
        else:
            return {
                "error": f"Compose file not found: {compose_path}",
                "services": [],
            }

    # Parse compose file
    defined_services = parse_compose(str(path))
    if not defined_services:
        return {
            "compose_path": str(path),
            "error": "No services found in compose file",
            "services": [],
        }

    # Get running containers
    running = check_running_containers()

    # Check each service
    results = []
    for svc in defined_services:
        if "error" in svc:
            continue

        name = svc["name"]
        container = running.get(name.lower(), {})

        # Determine running state
        is_running = container.get("state", "").lower() in ("running", "up")

        # Check health
        health_status = None
        if is_running:
            health_status = check_container_health(name) or container.get("health", "")

        # Check port connectivity
        port_checks = []
        for port_def in svc.get("ports", []):
            host_port = port_def["host"]
            accessible = check_port("localhost", host_port) if is_running else False

            # HTTP check for web-like ports
            http_status = None
            if accessible and host_port in range(3000, 10000) or host_port in (80, 443, 8080, 8443):
                http_status = check_http(f"http://localhost:{host_port}/health")
                if http_status is None:
                    http_status = check_http(f"http://localhost:{host_port}/")

            port_checks.append({
                "host_port": host_port,
                "container_port": port_def["container"],
                "accessible": accessible,
                "http_status": http_status,
            })

        # Determine overall service status
        if not is_running:
            status = "FAIL"
            details = f"Container not running (state: {container.get('state', 'not found')})"
        elif health_status and health_status.lower() not in ("healthy", ""):
            status = "FAIL"
            details = f"Container unhealthy (health: {health_status})"
        elif port_checks and not any(p["accessible"] for p in port_checks):
            status = "PARTIAL"
            details = "Container running but ports not accessible"
        elif port_checks and all(p["accessible"] for p in port_checks):
            status = "PASS"
            details = f"Running, healthy, {len(port_checks)} port(s) accessible"
        elif is_running:
            status = "PASS"
            details = "Running" + (f", health: {health_status}" if health_status else "")
        else:
            status = "MISSING"
            details = "Service not found in running containers"

        results.append({
            "id": f"SVC-{len(results) + 1:03d}",
            "name": name,
            "image": svc.get("image", ""),
            "type": svc.get("type", "application"),
            "status": status,
            "is_running": is_running,
            "health": health_status,
            "ports": port_checks,
            "depends_on": svc.get("depends_on", []),
            "details": details,
        })

    # Summary
    total = len(results)
    healthy = sum(1 for r in results if r["status"] == "PASS")
    unhealthy = total - healthy

    return {
        "compose_path": str(path),
        "total_services": total,
        "healthy": healthy,
        "unhealthy": unhealthy,
        "services": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Discover and check Docker services")
    parser.add_argument("--compose", "-c", default="docker-compose.yml", help="Path to compose file")
    parser.add_argument("--root", "-r", default=".", help="Project root directory")
    args = parser.parse_args()

    result = discover_services(args.compose, args.root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
