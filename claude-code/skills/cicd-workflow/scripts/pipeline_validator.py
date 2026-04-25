#!/usr/bin/env python3
"""
CI/CD pipeline YAML validator.

Validates GitHub Actions and GitLab CI pipeline configurations for:
- Valid YAML syntax
- Required fields
- Common anti-patterns
- Security issues

Usage:
    python pipeline_validator.py <pipeline_file.yml>
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# Add shared library to path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer0 import EXIT_SUCCESS, EXIT_ERROR, EXIT_DEPENDENCY_ERROR, EXIT_VALIDATION_ERROR  # noqa: E402
from layer1 import emit_error, emit_warning, emit_info  # noqa: E402

try:
    import yaml
except ImportError:
    emit_error("PyYAML required. Install with: pip install pyyaml")
    sys.exit(EXIT_DEPENDENCY_ERROR)


class PipelineValidator:
    """Validates CI/CD pipeline configurations."""

    def __init__(self, pipeline_path: Path):
        self.path = pipeline_path
        self.config: dict[str, Any] = {}
        self.issues: list[tuple] = []  # (severity, message)
        self.platform = self._detect_platform()

    def _detect_platform(self) -> str:
        """Detect pipeline platform from path."""
        path_str = str(self.path)
        if ".github/workflows" in path_str:
            return "github"
        elif ".gitlab-ci" in self.path.name:
            return "gitlab"
        else:
            return "unknown"

    def load(self) -> bool:
        """Load and parse YAML file."""
        try:
            with open(self.path, encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            return True
        except yaml.YAMLError as e:
            emit_error(f"YAML syntax error: {e}")
            return False
        except Exception as e:
            emit_error(f"Error reading file: {e}")
            return False

    def check_github_actions(self):
        """Validate GitHub Actions workflow."""
        # Check for name
        if "name" not in self.config:
            self.issues.append(("INFO", "Missing workflow name"))

        # Check for on triggers
        if "on" not in self.config:
            self.issues.append(("CRITICAL", 'Missing "on" triggers'))

        # Check for jobs
        if "jobs" not in self.config:
            self.issues.append(("CRITICAL", 'Missing "jobs" section'))
            return

        jobs = self.config["jobs"]
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue

            # Check for runs-on
            if "runs-on" not in job_config:
                self.issues.append(("CRITICAL", f'Job "{job_name}" missing runs-on'))

            # Check for steps
            if "steps" not in job_config:
                self.issues.append(("WARNING", f'Job "{job_name}" has no steps'))
            else:
                # Check for checkout action
                steps = job_config["steps"]
                has_checkout = any(
                    isinstance(step, dict) and step.get("uses", "").startswith("actions/checkout")
                    for step in steps
                )
                if not has_checkout:
                    self.issues.append(("WARNING", f'Job "{job_name}" missing checkout action'))

    def check_gitlab_ci(self):
        """Validate GitLab CI configuration."""
        # Check for stages
        if "stages" in self.config:
            stages = self.config["stages"]
            if not isinstance(stages, list) or len(stages) == 0:
                self.issues.append(("WARNING", "Empty or invalid stages"))

        # Check jobs
        job_count = 0
        for key, value in self.config.items():
            if key.startswith(".") or key in ["stages", "variables", "default"]:
                continue

            if isinstance(value, dict):
                job_count += 1

                # Check for script
                if "script" not in value:
                    self.issues.append(("WARNING", f'Job "{key}" missing script'))

        if job_count == 0:
            self.issues.append(("CRITICAL", "No jobs defined"))

    def check_secrets(self):
        """Check for hardcoded secrets."""
        yaml_str = str(self.config)

        secret_patterns = [
            ("password", "Potential password"),
            ("api_key", "Potential API key"),
            ("token", "Potential token"),
            ("secret", "Potential secret"),
        ]

        for pattern, message in secret_patterns:
            if pattern in yaml_str.lower() and "${{" not in yaml_str:
                self.issues.append(("WARNING", f"{message} detected (use secrets instead)"))

    def check_caching(self):
        """Check for caching configuration."""
        yaml_str = str(self.config).lower()

        if self.platform == "github":
            if "cache" not in yaml_str and "setup-" in yaml_str:
                self.issues.append(("INFO", "Consider adding caching for dependencies"))
        elif self.platform == "gitlab" and "cache" not in self.config:
            self.issues.append(("INFO", "Consider adding cache configuration"))

    def validate(self) -> bool:
        """Run all validation checks."""
        if not self.load():
            return False

        if self.platform == "github":
            self.check_github_actions()
        elif self.platform == "gitlab":
            self.check_gitlab_ci()
        else:
            self.issues.append(
                ("WARNING", "Unknown platform (expected GitHub Actions or GitLab CI)")
            )

        self.check_secrets()
        self.check_caching()

        return True

    def print_report(self):
        """Print validation report."""
        platform_name = {
            "github": "GitHub Actions",
            "gitlab": "GitLab CI",
            "unknown": "Unknown Platform",
        }[self.platform]

        if not self.issues:
            print(f"✅ {self.path.name} ({platform_name}): Valid!")
            return

        print(f"\n{self.path.name} ({platform_name}) — {len(self.issues)} issue(s):\n")

        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        sorted_issues = sorted(self.issues, key=lambda x: severity_order[x[0]])

        for severity, message in sorted_issues:
            icon = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "ℹ️"}[severity]
            print(f"  {icon} [{severity}] {message}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate CI/CD pipeline YAML")
    parser.add_argument("pipeline", type=Path, help="Path to pipeline YAML file")
    args = parser.parse_args()

    if not args.pipeline.exists():
        emit_error(f"{args.pipeline} not found")
        sys.exit(EXIT_ERROR)

    validator = PipelineValidator(args.pipeline)
    if not validator.validate():
        sys.exit(EXIT_ERROR)

    validator.print_report()

    # Exit with error if critical issues found
    has_critical = any(sev == "CRITICAL" for sev, _ in validator.issues)
    sys.exit(EXIT_VALIDATION_ERROR if has_critical else EXIT_SUCCESS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
