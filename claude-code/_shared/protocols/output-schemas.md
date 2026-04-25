# Inter-Skill Output Schema Reference

This document defines the expected JSON output formats for skill scripts that produce
structured data consumed by downstream skills or the orchestrator.

## Skill Script Output Convention

All skill scripts MUST:
1. Output valid JSON to stdout on success
2. Use exit codes from `layer0.exit_codes` (0 = success, 1 = error, 2 = invalid args, 5 = validation error)
3. Output error messages via `layer1.emit_error()` to stderr (never stdout)

## Error Classifier (`debug-diagnostics/scripts/error_classifier.py`)

```json
{
  "category": "network|syntax|runtime|import|docker|unknown",
  "error_type": "ConnectionRefused|SyntaxError|...",
  "message": "Human-readable summary",
  "file": "path/to/file.py",
  "line": 42,
  "confidence": 0.95
}
```

**Consumed by**: debug-diagnostics SKILL.md Phase 2 (categorization)

## Diagnostic Collector (`debug-diagnostics/scripts/diagnostic_collector.py`)

```json
{
  "category": "docker|python|node|network|system",
  "diagnostics": [
    { "check": "python3 --version", "output": "Python 3.11.7", "status": "ok" }
  ],
  "summary": "System diagnostics for <category>",
  "timestamp": "2026-01-01T00:00:00Z"
}
```

**Consumed by**: debug-diagnostics SKILL.md Phase 3

## Dependency Parser (`dependency-analyzer/scripts/dependency_parser.py`)

```json
{
  "modules": [
    { "name": "module_name", "path": "path/to/module.py", "imports": ["dep1", "dep2"] }
  ],
  "edges": [
    { "from": "module_a", "to": "module_b", "type": "import" }
  ],
  "circular": []
}
```

**Consumed by**: graph_builder.py, layer_validator.py

## Metric Collector (`codebase-stats/scripts/metric_collector.py`)

```json
{
  "timestamp": "2026-01-01T00:00:00Z",
  "source_dir": "./src",
  "metrics": {
    "total_files": 42,
    "total_lines": 5000,
    "avg_complexity": 3.5,
    "max_complexity": 15,
    "test_ratio": 0.3,
    "doc_coverage": 0.7
  },
  "by_language": {
    "python": { "files": 30, "lines": 4000 }
  }
}
```

**Consumed by**: trend_comparator.py, codebase-stats SKILL.md

## Spec Parser (`spec-compliance/scripts/spec_parser.py`)

```json
{
  "source": "docs/spec.md",
  "format": "markdown",
  "requirements": [
    {
      "id": "REQ-001",
      "description": "The system must...",
      "priority": "MUST",
      "type": "functional",
      "keywords": ["auth", "login"],
      "source_line": 42
    }
  ],
  "total_count": 15
}
```

**Consumed by**: compliance_checker.py, spec-compliance SKILL.md

## Compliance Checker (`spec-compliance/scripts/compliance_checker.py`)

```json
{
  "spec_source": "docs/spec.md",
  "project_root": ".",
  "requirements_checked": 15,
  "results": [
    {
      "requirement_id": "REQ-001",
      "status": "PASS|PARTIAL|FAIL|MISSING",
      "evidence": ["src/auth.py:42 - login function"],
      "confidence": 0.8
    }
  ],
  "summary": {
    "pass": 10,
    "partial": 3,
    "fail": 1,
    "missing": 1,
    "compliance_score": 75.0
  }
}
```

**Consumed by**: spec-compliance SKILL.md, auditor agent

## Security Pattern Detector (`security-auditor/scripts/pattern_detector.py`)

```json
{
  "source_dir": "./src",
  "findings": [
    {
      "severity": "high|medium|low|info",
      "category": "injection|xss|hardcoded-secret|...",
      "file": "path/to/file.py",
      "line": 42,
      "description": "SQL injection via string formatting",
      "recommendation": "Use parameterized queries"
    }
  ],
  "summary": { "high": 1, "medium": 2, "low": 5, "info": 3 }
}
```

**Consumed by**: security-auditor SKILL.md, software-engineer quality pipeline

## File Analyzer (`refactor-executor/scripts/file_analyzer.py`)

```json
{
  "file": "path/to/module.py",
  "total_lines": 500,
  "threshold_lines": 300,
  "exceeds_threshold": true,
  "functions": [
    { "name": "func_name", "start_line": 10, "end_line": 80, "lines": 70, "complexity": 8 }
  ],
  "classes": [
    { "name": "ClassName", "start_line": 100, "end_line": 450, "lines": 350, "methods": 12 }
  ]
}
```

**Consumed by**: split_planner.py, refactor-executor SKILL.md
