# Contributing to Auto-Orchestrate

Thank you for your interest in contributing. This guide covers everything you need to get started: dev setup, how to create skills or modify agents, testing, code style, and the PR process.

See [ARCHITECTURE.md](claude-code/ARCHITECTURE.md) for the system architecture and [INTEGRATION.md](claude-code/INTEGRATION.md) for installation and integration patterns.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Layout](#project-layout)
3. [Creating a New Skill](#creating-a-new-skill)
4. [Modifying an Agent](#modifying-an-agent)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Pull Request Process](#pull-request-process)
8. [Adding a New Command](#adding-a-new-command)

---

## Development Setup

### Prerequisites

- **Claude Code CLI** — [install guide](https://docs.anthropic.com/en/docs/claude-code)
- **Python 3.10+** — required for skill scripts and tests
- No additional pip packages are required for the core library (stdlib only)

### Clone and install

```bash
git clone https://github.com/ribatshepo/Auto-Orchestrate.git
cd Auto-Orchestrate
chmod +x install.sh
./install.sh
```

The installer copies all files from `claude-code/` into `~/.claude/` and backs up your existing config first.

### Verify the installation

```bash
# Shared library tests
python3 -m pytest claude-code/skills/_shared/python/tests/ -v

# CI engine tests
python3 -m pytest claude-code/lib/ci_engine/tests/ -v

# Domain memory tests
python3 -m pytest claude-code/lib/domain_memory/tests/ -v
```

All tests should pass. If any fail, check that Python 3.10+ is your active interpreter.

### Working locally without reinstalling

After making changes to skill scripts or agent definitions, re-run the installer to push changes into `~/.claude/`. The installer is idempotent and always backs up first.

---

## Project Layout

```
Auto-Orchestrate/
├── install.sh                   # Copies claude-code/ → ~/.claude/
├── uninstall.sh                 # Removes ~/.claude/ installed files
└── claude-code/
    ├── agents/                  # Agent definitions (17 agents)
    ├── commands/                # Slash commands (auto-orchestrate, auto-debug, auto-audit)
    ├── lib/                     # Python libraries
    │   ├── ci_engine/           # Continuous improvement engine
    │   │   ├── ooda_controller.py         # Within-run OODA feedback loop
    │   │   ├── root_cause_classifier.py   # 8-category failure classification
    │   │   ├── retrospective_analyzer.py  # Post-run PDCA Check phase
    │   │   ├── improvement_recommender.py # Cross-run PDCA Act phase
    │   │   ├── stage_metrics_collector.py # Telemetry collection
    │   │   ├── baseline_manager.py        # Rolling baselines
    │   │   ├── schemas/                   # JSON schemas for data files
    │   │   └── tests/                     # Unit + integration tests
    │   └── domain_memory/       # Cross-session domain knowledge
    │       ├── store.py         # JSONL append/query engine (6 stores)
    │       ├── hooks.py         # Pipeline integration hooks
    │       ├── indexer.py       # SQLite index for fast queries
    │       └── tests/
    ├── skills/                  # Skill definitions (48 skills)
    │   └── _shared/python/      # Shared Python library (layered)
    │       ├── layer0/          # Foundation (colors, constants, exit codes)
    │       ├── layer1/          # Core utilities (config, file ops, logging, spec utils)
    │       ├── layer2/          # Mid-level (validation, task ops, webhooks)
    │       ├── layer3/          # High-level (backup, migration, diagnostics)
    │       └── tests/           # pytest test suite
    ├── _shared/
    │   ├── protocols/           # Agent communication contracts
    │   │   ├── output-standard.md   # Unified output file naming/structure
    │   │   └── output-schemas.md    # Inter-skill JSON output schemas
    │   ├── references/          # Agent-specific reference docs
    │   ├── templates/           # Skill boilerplate and anti-patterns
    │   ├── style-guides/        # Documentation style guide
    │   └── tokens/              # Placeholder token definitions
    ├── manifest.json            # Component registry for agent routing
    └── ARCHITECTURE.md          # Full architecture documentation
```

The shared Python library uses a layered import model. Higher layers may import from lower layers but not vice versa. The CI engine and domain memory libraries use stdlib only (no pip dependencies).

---

## Creating a New Skill

Skills are the atomic units of work in the system. Each skill lives in its own directory under `claude-code/skills/<skill-name>/`.

### Minimum required files

```
claude-code/skills/<skill-name>/
├── SKILL.md          # Skill definition (instructions for the AI)
└── scripts/          # Optional: Python scripts invoked by the skill
    └── my_script.py
```

### Step-by-step

1. **Copy the boilerplate** from `claude-code/_shared/templates/skill-boilerplate.md` as a starting point for `SKILL.md`.

2. **Define the skill interface** in `SKILL.md`:
   - What inputs it accepts (task context, file paths, config)
   - What actions it performs
   - What outputs it produces (manifest entry, output file)

3. **Write Python scripts** if the skill needs executable logic. Place them in `scripts/`. Follow the shared library patterns (see `layer0`–`layer3` in `_shared/python/`).

4. **Add tests** for any Python scripts in `claude-code/skills/_shared/python/tests/`. Name the file `test_<skill_name>.py`. See existing tests for patterns.

5. **Register the skill** in `claude-code/manifest.json`. Add an entry under `"skills"` with:
   - `name` — kebab-case skill name
   - `description` — one sentence, plain language
   - `dispatch_triggers` — keywords agents use to route to this skill
   - `path` — relative path to `SKILL.md`

6. **Re-install** to push changes: `./install.sh`

> **References subdirectory**: Skills that need lookup tables, pattern libraries, or reference data should place those files in `skills/<name>/references/`. Several skills use this pattern (e.g., `debug-diagnostics/references/error-categories.md`, `spec-compliance/references/compliance-patterns.md`). Reference files are loaded at the start of the SKILL.md `## Before You Begin` section.

### Frontmatter is authoritative (SKILL-FRONTMATTER-001)

When `checkpoint.optimizations.skill_frontmatter_routing` is on (default), skill **discovery** loads only the YAML frontmatter (~300 tok) — the body is loaded only at invocation. This means:

- **`name`, `description`, and `triggers` MUST be in the frontmatter** — not buried in body prose. Routing decisions are made from frontmatter alone.
- **Don't put trigger phrases in the body** thinking the discovery pass will find them. It won't. Add them to `triggers:` array.
- **Keep the body ≥ frontmatter in detail**: the body is the runtime instruction set; the frontmatter is the catalogue card.

Verify your skill is discoverable via the helper:

```bash
python3 -c "
import sys; sys.path.insert(0, 'claude-code/skills/_shared/python')
from layer1 import read_frontmatter
fm = read_frontmatter('claude-code/skills/my-skill')
print(fm['name'], fm.get('triggers', []))
"
```

### Manifest entry format

```json
{
  "name": "my-skill",
  "description": "One-sentence description of what this skill does.",
  "dispatch_triggers": ["trigger phrase", "another trigger"],
  "path": "skills/my-skill/SKILL.md"
}
```

---

## Modifying an Agent

Agents are defined in `claude-code/agents/<agent-name>.md`. They are Markdown files that describe the agent's role, decision flow, and constraints.

### Guidelines

- **Do not remove constraints** (MAIN-*, IMPL-*, AUTO-* blocks) without understanding their purpose. These gates enforce quality and safety.
- **Update `dispatch_triggers`** in `manifest.json` if you change what the agent responds to.
- **Update ARCHITECTURE.md** if the agent's capabilities or pipeline stage changes.
- **Test the change** by running a real orchestration task and verifying the agent behaves as expected.

### Manifest field usage (MANIFEST-DIGEST-001)

By default, subagents receive a **2.6k slim digest** of `manifest.json` (just `agents[].name + dispatch_triggers` + `skills[].name + triggers`) — not the full 19k file. Two exceptions get the full manifest automatically: `orchestrator` and `session-manager`. If your agent reads any of these manifest fields:

- `agents[].chaining` (producer/consumer relationships)
- `agents[].activation_rules` (auto-activation conditions)
- `skills[].chaining` (skill chain relationships)
- Full descriptions or schema-only fields

…you have two options:

1. **Per-task escape hatch**: any task whose `dispatch_hint` routes to your agent can set `needs_full_manifest: true` and that one spawn gets the full payload.
2. **Permanent**: add your agent name to the `needs_full_manifest()` list in `skills/_shared/python/layer1/manifest_digest.py` (currently `orchestrator` + `session-manager`).

If you discover at runtime that a field you needed isn't in the digest, your agent should emit `[MANIFEST-FIELD-MISSING]` in its return text — the loop controller will re-spawn once with `needs_full_manifest: true` automatically.

### Adding a new agent

1. Create `claude-code/agents/<agent-name>.md` following the structure of an existing agent.
2. Add the agent entry to `manifest.json` under `"agents"`.
3. Update `ARCHITECTURE.md` to document the new agent's role.
4. **Decide manifest digest eligibility**: if your agent only routes work (reads `dispatch_triggers`), the digest is sufficient. If it consumes chaining metadata or activation rules, add it to the `needs_full_manifest()` allowlist.
5. Re-install: `./install.sh`

---

## Adding a New Command

> **One-command framework**: Auto-Orchestrate exposes a single user-facing command, `/auto-orchestrate`. The previously-separate `/auto-debug`, `/auto-audit`, and various lifecycle commands (`/release-prep`, `/post-launch`, etc.) are now **internal phases** of `/auto-orchestrate` — they are not separate slash commands. Before adding a new command, consider whether it can be modelled as an internal phase instead. See `claude-code/_shared/protocols/command-dispatch.md` "Phase Catalog" for the existing internal phases.

Commands are Markdown files in `claude-code/commands/` with YAML frontmatter. They are slash commands invoked directly in Claude Code (e.g., `/auto-orchestrate`).

### Command frontmatter

```yaml
---
name: my-command
description: |
  One-line summary of what the command does.
triggers:
  - keyword trigger 1
  - keyword trigger 2
arguments:
  - name: my_arg
    type: string
    required: true
    description: What this argument controls.
---
```

### Command body

Commands contain their own constraint table (immutable rules), execution loop logic, and session management. Follow the pattern in `auto-debug.md` for cyclic commands or `auto-orchestrate.md` for linear stage-based commands.

### Registration

After creating `commands/my-command.md`, register it in `manifest.json`:
```json
{
  "name": "my-command",
  "description": "...",
  "path": "commands/my-command.md"
}
```
Add to the `"commands"` array. Run `python3 claude-code/skills/_shared/python/validate_manifest.py` to confirm registration.

---

## Testing

The project uses **pytest** for all automated tests.

### Run the full suite

```bash
python3 -m pytest claude-code/skills/_shared/python/tests/ -v
```

### Run a specific test file

```bash
python3 -m pytest claude-code/skills/_shared/python/tests/test_config.py -v
```

### Run tests matching a keyword

```bash
python3 -m pytest claude-code/skills/_shared/python/tests/ -k "backup" -v
```

### Test coverage

All Python functions added to the shared library (`layer0`–`layer3`) must have corresponding tests. Place them in the existing test file for that module, or create `test_<module>.py` if one does not exist.

### Smoke-test the optimization helpers

The 6-phase token-budget optimization suite ships three new layer1 helpers. Verify they import and run:

```bash
python3 -c "
import sys; sys.path.insert(0, 'claude-code/skills/_shared/python')
from layer1 import (
    read_frontmatter, list_skills_with_triggers,        # SKILL-FRONTMATTER-001
    build_digest, needs_full_manifest,                   # MANIFEST-DIGEST-001
    build_spawn_prompt_body,                             # TEMPLATE-EXTRACT-001
)
skills = list_skills_with_triggers('claude-code/skills/')
digest_tok = len(build_digest('claude-code/manifest.json')) // 4
core_only = build_spawn_prompt_body('claude-code/agents/orchestrator.md', stage=3, enabled=True)
print(f'helpers OK: {len(skills)} skills, ~{digest_tok} digest tok, ~{len(core_only)//4} core+stage3 tok')
"
```

Expected output: ~48 skills, ~2.6k digest tokens, ~8.3k core+stage3 tokens (your numbers may vary slightly as the codebase grows).

### What to test

- Happy paths (normal inputs produce expected outputs)
- Error paths (bad inputs raise correct exceptions or return error codes)
- Edge cases (empty inputs, large inputs, concurrent access where relevant)

---

## Code Style

### Python

- Follow **PEP 8** for formatting.
- Use **type hints** for all public functions.
- Write **docstrings** for public functions (one-line summary + parameter/return docs for complex functions).
- Keep functions short — if a function exceeds 40 lines, consider splitting it.
- Use only **standard library** modules. Do not add third-party dependencies to the shared library.
- Import only from the same layer or lower layers. Cross-layer import violations break the layered architecture.

### Markdown (agent definitions, skill docs)

- Follow the style guide at `claude-code/_shared/style-guides/style-guide.md`.
- Use plain, direct language. Avoid "utilize", "leverage", "powerful", "robust".
- Use active voice.
- Keep headings short and descriptive.
- Code examples must be complete and runnable.

### manifest.json

- Keep entries alphabetically sorted within `"agents"` and `"skills"` arrays.
- All string values use double quotes.
- No trailing commas.
- Validate with: `python3 claude-code/skills/_shared/python/validate_manifest.py`

---

## Pull Request Process

1. **Open an issue first** for non-trivial changes to discuss the approach before writing code.

2. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```

3. **Write tests** for any new Python code.

4. **Run the test suite** and make sure all tests pass:
   ```bash
   python3 -m pytest claude-code/skills/_shared/python/tests/ -v
   ```

5. **Validate manifest.json** if you changed it:
   ```bash
   python3 claude-code/skills/_shared/python/validate_manifest.py
   ```

6. **Update documentation** as needed: README.md, ARCHITECTURE.md, or the relevant SKILL.md.

7. **Submit the PR** with:
   - A clear title describing what changed (not what you did)
   - A description explaining *why* the change is needed
   - Reference to the issue number if one exists

8. **Keep PRs focused** — one logical change per PR. Split unrelated changes into separate PRs.

### Commit messages

Use the imperative mood and keep the subject line under 72 characters:

```
Add webhook retry with exponential backoff
Fix config loader ignoring empty values
Update skill-boilerplate with anti-patterns section
```

> **Note:** When using `/auto-orchestrate` or the `dev-workflow` skill, commit messages are generated automatically following conventional commit format. The skill displays copy-pasteable `git add`/`git commit`/`git push` commands but does NOT run them — you review and run the commands yourself.

---

## Questions

If something is unclear, open an issue or start a discussion. The project follows the architecture documented in [ARCHITECTURE.md](claude-code/ARCHITECTURE.md) — reading that first often answers structural questions.
