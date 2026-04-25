---
name: release-notes-generator
description: |
  Generate structured release notes from git history using conventional-commits
  categorization. Implements P-061 (Release Notes Process) and supports P-048
  (Production Release Management). Parses `git log <from>..<to>`, categorizes
  commits (feat/fix/docs/perf/security/breaking), links to issues/PRs, and
  produces a Highlights → Features → Fixes → Performance → Security →
  Breaking Changes → Dependencies → Contributors structure.
  Use when user says "release notes", "changelog", "generate release notes",
  "what changed since last release".
triggers:
  - release notes
  - changelog
  - generate release notes
  - what changed since last release
---

# Release Notes Generator Skill

You produce structured release notes for a release candidate by parsing git history between two refs and categorizing commits via conventional-commits prefixes. Output is a markdown changelog suitable for publishing to users and downstream consumers.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Phase 7 (Release Prep) co-agent | P-061 (Release Notes Process) | technical-writer produces release-notes-draft.md |
| Phase 7 (Release Prep) | P-048 (Production Release Management) | TPM uses release notes as input to release artifact |

## How to use

### Step 1: Determine the ref range

Default: from the previous release tag to HEAD.

```
PREVIOUS_TAG=$(git describe --tags --abbrev=0)
git log ${PREVIOUS_TAG}..HEAD ...
```

Override via arguments to `parse_git_log.py` if releasing from a different branch or to a specific candidate ref.

### Step 2: Parse the git log

```
python3 ~/.claude/skills/release-notes-generator/scripts/parse_git_log.py \
  --from-ref <previous-tag> \
  --to-ref HEAD \
  --output structured.json
```

The script:
- Runs `git log <from>..<to> --no-merges --pretty=format:%H|%an|%ae|%ad|%s`
- Categorizes each commit by conventional-commits prefix
- Detects breaking changes (`feat!:`, `BREAKING CHANGE:` in body)
- Extracts issue/PR references (`#123`, `(#456)`)
- Returns structured JSON: `{categories: {feat: [...], fix: [...], ...}, breaking_changes: [...], contributors: [...]}`

### Step 3: Render the markdown

```
python3 ~/.claude/skills/release-notes-generator/scripts/render_release_notes.py \
  --input structured.json \
  --version <semver> \
  --release-date <YYYY-MM-DD> \
  --output release-notes-draft.md
```

Output follows the structure in `references/release-notes-template.md`.

### Step 4: Human review pass

The auto-generated draft IS the starting point — a human (technical-writer agent or PM) reviews and:
- Curates the **Highlights** section (3-5 most user-impactful items)
- Verifies BREAKING CHANGES section is accurate and includes migration guidance
- Removes internal-only commits (e.g., `chore:`, internal refactors with no user impact)
- Adds release theme/narrative if applicable

### Step 5: Write final to release artifact

Place at:
- Phase 7 prep: `.orchestrate/<session>/phase-7/release-notes-draft.md`
- Final release: `CHANGELOG.md` in project repo (prepend new release block)

## Conventional commits cheat-sheet

See `references/conventional-commits.md` for full reference. Key prefixes:

| Prefix | Section in release notes | Notes |
|--------|--------------------------|-------|
| `feat:` | Features | New user-facing capability |
| `fix:` | Fixes | Bug fixes |
| `perf:` | Performance | Speed/efficiency improvements |
| `docs:` | (only if user-facing docs) | Internal docs usually excluded |
| `security:` or `fix(sec):` | Security | Security-related fixes |
| `feat!:` or `BREAKING CHANGE:` in body | Breaking Changes | MUST be in section + migration guide |
| `chore:`, `refactor:`, `test:`, `style:` | (excluded by default) | Internal-only |

## Output structure

See `references/release-notes-template.md` for the full template. Sections:

1. **Header** — version, date, link to git tag
2. **Highlights** — 3–5 curated items
3. **Features** — `feat:` commits
4. **Fixes** — `fix:` commits
5. **Performance** — `perf:` commits
6. **Security** — `security:` or `fix(sec):` commits
7. **Breaking Changes** — with migration guide per change
8. **Dependencies** — significant version bumps
9. **Contributors** — list of unique authors

## Outputs

- `structured.json` — intermediate machine-readable changelog
- `release-notes-draft.md` — human-reviewable markdown
- (final) `CHANGELOG.md` updated with new release block

## Related skills

- `docs-write` — for general documentation; release-notes is the specialized form
- `cab-reviewer` — at Phase 7, the CAB review reads release notes for user-impact assessment
- `dev-workflow` — for the conventional-commits convention enforced at commit time

## Reference

- `references/release-notes-template.md` — output structure
- `references/conventional-commits.md` — prefix cheat-sheet
- Canonical processes: P-061 in `processes/10_documentation_knowledge.md`; P-048 in `processes/07_infrastructure_platform.md`
