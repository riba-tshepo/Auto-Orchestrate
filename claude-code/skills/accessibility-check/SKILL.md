---
name: accessibility-check
description: |
  WCAG 2.1 AA/AAA compliance checking for web interfaces and UI components.
  Use when user says "accessibility audit", "WCAG check", "a11y review",
  "screen reader compatibility", "keyboard navigation", "color contrast",
  "accessibility compliance", "ADA compliance", "ARIA patterns".
triggers:
  - accessibility audit
  - WCAG check
  - a11y review
  - accessibility compliance
  - screen reader
  - keyboard navigation
  - color contrast
---

# Accessibility Check Skill

You are an accessibility specialist. Your role is to audit web interfaces and UI components for WCAG 2.1 AA/AAA compliance, identifying barriers that prevent users with disabilities from accessing content.

## When This Skill Is Invoked

- **Pipeline context**: Invoked by `qa-engineer` at Stage 5 (ACT-012) when UI components are detected in session artifacts
- **Standalone context**: Invoked directly when user requests accessibility review
- **Release context**: Invoked during `/release-prep` for pre-release accessibility verification

## Workflow

### Step 1: Identify UI Components

Use `Glob` and `Grep` to find UI component files in the project:

```
Patterns to search:
  *.jsx, *.tsx           — React components
  *.vue                  — Vue components
  *.svelte               — Svelte components
  *.html                 — HTML templates
  *.ejs, *.hbs, *.pug   — Template engines
```

Record the total count of UI files found. If zero, report: `[A11Y] No UI components detected — accessibility check not applicable.`

### Step 2: Audit WCAG 2.1 Criteria

For each UI component file, check the following categories:

#### 2a. Perceivable (WCAG Principle 1)

| Check | WCAG SC | Severity | What to Look For |
|-------|---------|----------|-----------------|
| Image alt text | 1.1.1 | CRITICAL | `<img>` without `alt`, decorative images without `alt=""` or `role="presentation"` |
| Color contrast | 1.4.3 (AA) / 1.4.6 (AAA) | HIGH | Text colors against background — flag hardcoded color pairs with insufficient ratio (4.5:1 AA, 7:1 AAA for normal text) |
| Text resize | 1.4.4 | MEDIUM | Font sizes in `px` instead of `rem`/`em` — content should be readable at 200% zoom |
| Non-text contrast | 1.4.11 | HIGH | UI controls and graphics with < 3:1 contrast ratio |

#### 2b. Operable (WCAG Principle 2)

| Check | WCAG SC | Severity | What to Look For |
|-------|---------|----------|-----------------|
| Keyboard access | 2.1.1 | CRITICAL | Click handlers without keyboard equivalents (`onClick` without `onKeyDown`/`onKeyPress`), non-interactive elements with click handlers missing `tabIndex` and `role` |
| No keyboard trap | 2.1.2 | CRITICAL | Modal dialogs without escape key handling, focus not returning after modal close |
| Skip navigation | 2.4.1 | MEDIUM | Missing skip-to-content link for repeated navigation blocks |
| Focus visible | 2.4.7 | HIGH | CSS `outline: none` or `outline: 0` without alternative focus indicator |
| Focus order | 2.4.3 | HIGH | `tabIndex` values > 0 (disrupts natural tab order) |

#### 2c. Understandable (WCAG Principle 3)

| Check | WCAG SC | Severity | What to Look For |
|-------|---------|----------|-----------------|
| Language attribute | 3.1.1 | MEDIUM | Missing `lang` attribute on `<html>` element |
| Form labels | 3.3.2 | CRITICAL | `<input>`, `<select>`, `<textarea>` without associated `<label>`, `aria-label`, or `aria-labelledby` |
| Error identification | 3.3.1 | HIGH | Form validation without accessible error messages (missing `aria-invalid`, `aria-describedby` for error text) |

#### 2d. Robust (WCAG Principle 4)

| Check | WCAG SC | Severity | What to Look For |
|-------|---------|----------|-----------------|
| Valid ARIA | 4.1.2 | HIGH | Invalid ARIA roles, incorrect `aria-*` attribute values, `role` without required ARIA attributes |
| Name/Role/Value | 4.1.2 | CRITICAL | Custom interactive components missing `role`, `aria-label`, or `aria-expanded`/`aria-selected` state attributes |

### Step 3: Check Common Anti-Patterns

Use `Grep` to scan for these anti-patterns across all UI files:

| Pattern | Search | Issue |
|---------|--------|-------|
| Suppressed focus | `outline:\s*none\|outline:\s*0` | Removes visible focus indicator |
| Div buttons | `<div.*onClick\|<span.*onClick` without `role="button"` | Non-semantic interactive elements |
| Empty links | `<a[^>]*>(\s*)<\/a>` | Links with no accessible text |
| Auto-playing media | `autoplay\|autoPlay` | May disorient users |
| Positive tabindex | `tabindex="[1-9]\|tabIndex=\{[1-9]` | Disrupts focus order |

### Step 4: Generate Report

Produce a structured accessibility audit report:

```markdown
## Accessibility Audit Report

**Standard**: WCAG 2.1 Level AA (with AAA recommendations)
**Files Scanned**: <count>
**Timestamp**: <ISO-8601>

### Summary

| Severity | Count | WCAG Principle |
|----------|-------|---------------|
| CRITICAL | <N>   | <breakdown>   |
| HIGH     | <N>   | <breakdown>   |
| MEDIUM   | <N>   | <breakdown>   |

### Findings

1. **[CRITICAL]** <finding title>
   - **File**: <path:line>
   - **WCAG SC**: <success criterion>
   - **Issue**: <description>
   - **Recommendation**: <fix>

### Pass/Fail Verdict

- **PASS**: Zero CRITICAL findings AND zero HIGH findings
- **CONDITIONAL PASS**: Zero CRITICAL findings, HIGH findings documented as tech debt
- **FAIL**: Any CRITICAL findings present
```

## Output Integration

When invoked within the pipeline:
- Write report to `.orchestrate/<SESSION_ID>/domain-reviews/accessibility-stage-5.md`
- Findings feed into Stage 5 validation — CRITICAL findings block pipeline advancement
- HIGH findings are logged as tech debt in Stage 4.5 codebase-stats output
