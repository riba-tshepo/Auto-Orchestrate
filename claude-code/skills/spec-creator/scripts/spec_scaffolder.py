#!/usr/bin/env python3
"""
Specification document scaffolder.

Generates a skeleton specification document with all required sections
and helpful prompts for each section.

Usage:
    python spec_scaffolder.py <topic_name> [output_file.md]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add shared library to path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer0 import EXIT_SUCCESS, EXIT_ERROR  # noqa: E402
from layer1 import emit_error, emit_warning, emit_info  # noqa: E402

SPEC_TEMPLATE = """# Technical Specification: {topic}

**Author:** [Your Name]
**Date:** {date}
**Status:** Draft

---

## Overview

*Provide a high-level summary of this specification in 2-3 sentences.*

- **Purpose:** [What problem does this solve?]
- **Scope:** [What systems/components are affected?]
- **Target Audience:** [Who should read this spec?]

---

## Problem Statement

*Describe the problem this specification addresses.*

**Current State:**
- [What exists today?]
- [What are the pain points?]

**Desired State:**
- [What should exist after implementation?]
- [What benefits will this provide?]

---

## Goals

*List the measurable objectives this specification aims to achieve.*

1. [Primary goal with success metric]
2. [Secondary goal with success metric]
3. [Additional goals...]

---

## Functional Requirements

*List the features and capabilities that must be implemented.*

### FR-1: [Requirement Title]
**Description:** [What must the system do?]
**Priority:** [Critical / High / Medium / Low]
**User Story:** As a [role], I want to [action] so that [benefit].

### FR-2: [Requirement Title]
**Description:** [What must the system do?]
**Priority:** [Critical / High / Medium / Low]
**User Story:** As a [role], I want to [action] so that [benefit].

---

## Non-Functional Requirements

*List quality attributes, constraints, and performance requirements.*

### NFR-1: Performance
- [Specific performance metrics]

### NFR-2: Scalability
- [Scaling requirements and limits]

### NFR-3: Security
- [Security requirements and constraints]

### NFR-4: Maintainability
- [Code quality and maintenance requirements]

---

## Acceptance Criteria

*Define testable conditions that must be met for completion.*

- [ ] [Specific, measurable criterion]
- [ ] [Specific, measurable criterion]
- [ ] [Specific, measurable criterion]
- [ ] [All tests pass]
- [ ] [Documentation updated]

---

## Dependencies

*List external systems, libraries, and prerequisites.*

### External Dependencies
- **System/Library:** [Version] — [Purpose]
- **System/Library:** [Version] — [Purpose]

### Internal Dependencies
- **Component/Module:** [What does it provide?]
- **Component/Module:** [What does it provide?]

### Team Dependencies
- **Team/Person:** [What do they need to provide?]

---

## Out of Scope

*Explicitly state what this specification does NOT cover.*

- [Feature or capability not included]
- [Future enhancement to be addressed separately]
- [Related work that is handled elsewhere]

---

## Implementation Notes

*Optional: Add technical details, architecture notes, or implementation guidance.*

### Architecture Overview
[Diagram or description]

### Key Components
- **Component 1:** [Purpose and responsibilities]
- **Component 2:** [Purpose and responsibilities]

### Data Model
[Schema or data structure notes]

### API Design
[Endpoint definitions or interface descriptions]

---

## Risks and Mitigations

*Identify potential risks and mitigation strategies.*

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | Low/Med/High | Low/Med/High | [How to mitigate] |

---

## Open Questions

*List unresolved questions that need answers before implementation.*

1. [Question requiring decision or clarification?]
2. [Technical uncertainty to investigate?]

---

## References

*Link to related documents, prior art, or research.*

- [Related specification]
- [Design document]
- [External documentation]

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| {date} | [Author] | Initial draft |

"""


def scaffold_spec(topic: str, output_path: Path) -> bool:
    """Generate specification scaffold."""
    try:
        content = SPEC_TEMPLATE.format(topic=topic, date=datetime.now().strftime("%Y-%m-%d"))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        print(f"✅ Created specification scaffold: {output_path}")
        print("\nNext steps:")
        print(f"  1. Open {output_path} in your editor")
        print("  2. Replace [placeholders] with actual content")
        print("  3. Remove sections that don't apply (optional)")
        print(f"  4. Validate with: spec-analyzer/scripts/spec_validator.py {output_path}")

        return True
    except Exception as e:
        emit_error(f"Error creating specification: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate specification document scaffold")
    parser.add_argument("topic", help="Topic/feature name for the specification")
    parser.add_argument(
        "output", nargs="?", type=Path, help="Output file path (default: SPEC-<topic>.md)"
    )
    args = parser.parse_args()

    # Generate default output filename if not provided
    if args.output is None:
        safe_topic = args.topic.lower().replace(" ", "-").replace("_", "-")
        args.output = Path(f"SPEC-{safe_topic}.md")

    # Check if file already exists
    if args.output.exists():
        response = input(f"{args.output} already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            sys.exit(EXIT_SUCCESS)

    success = scaffold_spec(args.topic, args.output)
    sys.exit(EXIT_SUCCESS if success else EXIT_ERROR)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
