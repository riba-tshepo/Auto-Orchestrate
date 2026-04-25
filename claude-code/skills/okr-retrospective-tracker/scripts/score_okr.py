#!/usr/bin/env python3
"""
OKR Scorer — score Key Result achievement on the 0.0-1.0 scale.

Implements Google-style OKR scoring with 4 calculation methods:
linear, threshold, weighted-milestones, inverse-direction.

Usage:
    score_okr.py --target VALUE --actual VALUE [--baseline VALUE]
                 [--direction higher_better|lower_better|threshold]
                 [-o json|human]

Examples:
    score_okr.py --target 100 --actual 78 --direction higher_better
    score_okr.py --target 200 --actual 230 --baseline 500 --direction lower_better
    score_okr.py --target 1 --actual 1 --direction threshold

Exit codes:
    0  EXIT_SUCCESS
    2  EXIT_INVALID_INPUT — invalid args or unparseable values
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SHARED_PY = SCRIPT_DIR.parent.parent / "_shared" / "python"
if SHARED_PY.exists():
    sys.path.insert(0, str(SHARED_PY))
    try:
        from layer0.exit_codes import EXIT_SUCCESS, EXIT_INVALID_INPUT  # type: ignore
    except ImportError:
        EXIT_SUCCESS = 0
        EXIT_INVALID_INPUT = 2
else:
    EXIT_SUCCESS = 0
    EXIT_INVALID_INPUT = 2


def interpret_score(score: float) -> tuple[str, str]:
    if score >= 1.0:
        return "hit", "1.0 — Hit. Rare; if frequent, targets are too soft."
    if score >= 0.7:
        return "stretch_achieved", "0.7+ — Stretch achieved. Most ambitious target reached."
    if score >= 0.6:
        return "solid_achievement", "0.6-0.7 — Solid achievement; on track."
    if score >= 0.4:
        return "partial", "0.4-0.6 — Partial; significant progress but missed target."
    if score >= 0.2:
        return "started", "0.2-0.4 — Started; substantial gap to target."
    return "no_progress", "0.0-0.2 — Failed to materially advance the metric."


def score_higher_better(target: float, actual: float, baseline: float | None = None) -> dict:
    """For metrics where larger is better."""
    if baseline is not None and baseline != target:
        # Linear from baseline to target
        if target == baseline:
            score = 1.0 if actual >= target else 0.0
        else:
            progress = actual - baseline
            total_needed = target - baseline
            score = max(0.0, min(1.0, progress / total_needed))
        method = "linear-with-baseline"
    else:
        # Simple ratio: actual / target
        if target == 0:
            score = 1.0 if actual >= 0 else 0.0
        else:
            score = max(0.0, min(1.0, actual / target))
        method = "linear-ratio"

    return {
        "score": round(score, 2),
        "method": method,
        "target": target,
        "actual": actual,
        "baseline": baseline,
        "direction": "higher_better",
    }


def score_lower_better(target: float, actual: float, baseline: float | None = None) -> dict:
    """For metrics where smaller is better (e.g., latency, error rate, abandonment)."""
    if baseline is None:
        # Need a baseline to score lower-is-better; without it, use ratio if both positive
        if target == 0:
            score = 1.0 if actual <= 0 else 0.0
        elif actual <= 0:
            score = 1.0
        else:
            score = max(0.0, min(1.0, target / actual))
        method = "inverse-ratio"
    else:
        # Linear from baseline (start, bad) to target (end, good)
        if baseline == target:
            score = 1.0 if actual <= target else 0.0
        else:
            progress = baseline - actual  # how much we improved
            total_improvement_needed = baseline - target
            score = max(0.0, min(1.0, progress / total_improvement_needed))
        method = "linear-improvement"

    return {
        "score": round(score, 2),
        "method": method,
        "target": target,
        "actual": actual,
        "baseline": baseline,
        "direction": "lower_better",
    }


def score_threshold(target: float, actual: float) -> dict:
    """For binary outcomes (achieved or not)."""
    score = 1.0 if actual >= target else 0.0
    return {
        "score": score,
        "method": "threshold",
        "target": target,
        "actual": actual,
        "baseline": None,
        "direction": "threshold",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Score OKR Key Result achievement.")
    p.add_argument("--target", type=float, required=True, help="The target value")
    p.add_argument("--actual", type=float, required=True, help="The actual measured value")
    p.add_argument("--baseline", type=float, help="Optional baseline (Day 0) value for linear-improvement")
    p.add_argument("--direction", choices=("higher_better", "lower_better", "threshold"),
                   default="higher_better", help="Metric direction (default: higher_better)")
    p.add_argument("-o", "--output", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    if args.direction == "higher_better":
        result = score_higher_better(args.target, args.actual, args.baseline)
    elif args.direction == "lower_better":
        result = score_lower_better(args.target, args.actual, args.baseline)
    else:
        result = score_threshold(args.target, args.actual)

    interpretation_band, interpretation_text = interpret_score(result["score"])
    result["interpretation"] = interpretation_band
    result["interpretation_text"] = interpretation_text

    if args.output == "json":
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"Score: {result['score']}")
        print(f"Interpretation: {result['interpretation_text']}")
        print(f"Method: {result['method']}")
        print(f"Target: {result['target']} | Actual: {result['actual']} | Baseline: {result['baseline']}")
        print(f"Direction: {result['direction']}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
