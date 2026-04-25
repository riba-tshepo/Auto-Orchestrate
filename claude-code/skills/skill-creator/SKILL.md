---
name: skill-creator
description: >
  Guide for creating, updating, and packaging skills that extend Claude's capabilities
  with specialized knowledge, workflows, or tool integrations. Use when users want to
  create a new skill, update an existing skill, measure skill performance, or optimize
  a skill's description for better triggering accuracy.
triggers:
  - create a new skill
  - update an existing skill
  - skill creation
  - extend Claude capabilities
---

# Skill Creator

Guide for building effective skills — modular packages that transform Claude from a general-purpose agent into a specialized one by providing procedural knowledge, workflows, and tools.

## Before You Begin — Load Reference Docs

Read all of the following reference files before proceeding with any workflow step:

- Read `references/output-patterns.md` — Output format patterns and examples for skill-generated artifacts.
- Read `references/workflows.md` — Workflow patterns and lifecycle stages for skill creation and packaging.

## Core Principles

### Concise is Key

The context window is a shared resource. **Claude is already very smart** — only add what it doesn't already have. Challenge every paragraph: "Does this justify its token cost?" Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match specificity to fragility:

- **High freedom** (text instructions): Multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode/parameterized scripts): Preferred pattern exists, some variation acceptable
- **Low freedom** (exact scripts, few parameters): Fragile operations, consistency critical, specific sequence required

Think of it as path guidance: a narrow bridge needs guardrails (low freedom), an open field allows many routes (high freedom).

### Progressive Disclosure

Skills use three loading levels to manage context efficiently:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — loaded when skill triggers (<5k words, target <500 lines)
3. **Bundled resources** — loaded as needed (scripts can execute without reading into context)

---

## Skill Anatomy

```
skill-name/
├── SKILL.md              # Required: YAML frontmatter + markdown instructions
├── scripts/              # Optional: deterministic, reusable code
├── references/           # Optional: docs loaded into context as needed
└── assets/               # Optional: files used in output (templates, images, fonts)
```

### SKILL.md (required)

- **Frontmatter** (YAML): Only `name` and `description`. Description is the primary trigger mechanism — include both what the skill does and when to use it. All "when to use" info goes here, not in the body.
- **Body** (Markdown): Instructions and guidance, loaded only after triggering.

### Bundled Resources (optional)

| Directory | Purpose | When to Include | Example |
|-----------|---------|-----------------|---------|
| `scripts/` | Executable code for deterministic tasks | Same code rewritten repeatedly | `scripts/rotate_pdf.py` |
| `references/` | Docs loaded into context as needed | Claude needs domain knowledge while working | `references/schema.md` |
| `assets/` | Files used in output, not loaded into context | Output needs templates/images/fonts | `assets/logo.png` |

**Reference file guidelines**: Keep SKILL.md lean by moving detailed schemas, API docs, and examples to references. For large files (>10k words), include grep patterns in SKILL.md. Keep references one level deep — all should link directly from SKILL.md. Files >100 lines should have a table of contents.

**Do NOT create**: README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, or other auxiliary documentation. Skills are for AI agents, not human onboarding.

---

## Progressive Disclosure Patterns

**Pattern 1 — High-level guide with references**:
```markdown
## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```
Claude loads only what's needed.

**Pattern 2 — Domain/variant organization**:
```
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md
    ├── sales.md
    └── product.md
```
User asks about sales → Claude reads only `sales.md`.

**Pattern 3 — Conditional details**:
```markdown
For simple edits, modify XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

---

## Creation Process

### Step 1: Understand with Concrete Examples

*Skip only when usage patterns are already clearly understood.*

Clarify how the skill will be used through direct user examples or validated generated examples. Ask focused questions — avoid overwhelming with too many at once:

- What functionality should the skill support?
- What would a user say that should trigger it?
- Can you give example use cases?

Conclude when there's a clear picture of supported functionality.

### Step 2: Plan Reusable Contents

Analyze each example by considering how to execute it from scratch, then identify what would help when doing it repeatedly:

- Repeated code → `scripts/`
- Repeated boilerplate → `assets/`
- Repeated discovery of schemas/docs → `references/`

### Step 3: Initialize the Skill

*Skip if the skill already exists and only needs iteration.*

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates a template directory with SKILL.md frontmatter, TODO placeholders, and example `scripts/`, `references/`, and `assets/` directories. Customize or delete generated examples as needed.

### Step 4: Edit the Skill

Remember: the skill is for another Claude instance to use. Include information that's beneficial and non-obvious.

**Consult design pattern guides**:
- Multi-step processes → `references/workflows.md`
- Output formats/quality standards → `references/output-patterns.md`

**Implementation order**:
1. Start with reusable resources (`scripts/`, `references/`, `assets/`) — may require user input (e.g., brand assets, templates)
2. Test added scripts by running them; for many similar scripts, test a representative sample
3. Delete unused example files from initialization
4. Update SKILL.md

**SKILL.md writing guidelines**:

*Frontmatter*: Only `name` and `description`. Description must include all triggering context — the body isn't loaded until after triggering.

*Body*: Use imperative/infinitive form. Write instructions for using the skill and its bundled resources.

### Step 5: Validate the Skill

Run basic structure validation before packaging:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

Fix any reported issues before proceeding to packaging.

If the skill updates manifest.json, validate it:

```bash
python3 _shared/python/validate_manifest.py ~/.claude/manifest.json
```

### Step 6: Package the Skill

```bash
scripts/package_skill.py <path/to/skill-folder>
scripts/package_skill.py <path/to/skill-folder> ./dist  # optional output dir
```

Automatically validates (frontmatter, naming, structure, description quality) then creates a `.skill` file (zip with `.skill` extension). Fix any reported errors and re-run if validation fails.

### Step 7: Iterate

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Update SKILL.md or bundled resources
4. Test again