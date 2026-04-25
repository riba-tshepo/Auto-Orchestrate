#!/usr/bin/env python3
"""
Error Budget Calculator — compute error budgets and burn-rate thresholds.

Given an SLO target and measurement window, returns the error budget in minutes
and as percent-of-window. Optionally computes burn-rate alert thresholds per the
multi-window multi-burn-rate (MWMBR) pattern.

Usage:
    calculate_error_budget.py --target PERCENT --window-days N
                              [--burn-rate-alerts] [-o json|human]
    calculate_error_budget.py --target 99.9 --window-days 28
    calculate_error_budget.py --target 99.95 --window-days 90 --burn-rate-alerts

Exit codes:
    0  EXIT_SUCCESS
    2  EXIT_INVALID_INPUT — invalid target or window
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


def humanize_minutes(minutes: float) -> str:
    if minutes < 1:
        return f"~{minutes * 60:.1f} seconds"
    if minutes < 60:
        return f"~{minutes:.1f} minutes"
    if minutes < 60 * 24:
        hrs = minutes / 60
        return f"~{int(hrs)}h {int((hrs - int(hrs)) * 60)}min"
    days = minutes / (60 * 24)
    return f"~{days:.1f} days"


def burn_rate_alerts(slo_target_fraction: float) -> dict:
    """Compute MWMBR alert thresholds per Google SRE workbook."""
    allowed_error_rate = 1 - slo_target_fraction

    return {
        "page_fast": {
            "burn_rate": 14.4,
            "lookback_window": "1h",
            "rationale": "Exhausts 28d budget in 2 days; wake someone up",
            "alert_threshold_error_rate": 14.4 * allowed_error_rate,
            "secondary_window": "5m",
        },
        "page_slow": {
            "burn_rate": 6.0,
            "lookback_window": "6h",
            "rationale": "Exhausts 28d budget in 5 days; wake someone up",
            "alert_threshold_error_rate": 6.0 * allowed_error_rate,
            "secondary_window": "30m",
        },
        "ticket_fast": {
            "burn_rate": 3.0,
            "lookback_window": "1d",
            "rationale": "Concerning trend; investigate during business hours",
            "alert_threshold_error_rate": 3.0 * allowed_error_rate,
        },
        "ticket_slow": {
            "burn_rate": 1.0,
            "lookback_window": "3d",
            "rationale": "On track to exhaust budget; investigate",
            "alert_threshold_error_rate": 1.0 * allowed_error_rate,
        },
        "policy_note": (
            "Use AND-combined multi-window pattern: e.g., PAGE when 1h burn >=14.4 "
            "AND 5min burn >=14.4. Reduces false positives from one-off spikes."
        ),
    }


def calculate(target_percent: float, window_days: int) -> dict:
    if not (0 < target_percent < 100):
        raise ValueError(f"target_percent must be between 0 and 100; got {target_percent}")
    if window_days <= 0:
        raise ValueError(f"window_days must be positive; got {window_days}")

    target_fraction = target_percent / 100.0
    window_minutes = window_days * 24 * 60
    error_budget_minutes = window_minutes * (1 - target_fraction)
    error_budget_percent = (1 - target_fraction) * 100

    return {
        "slo_target_percent": target_percent,
        "slo_target_fraction": target_fraction,
        "window_days": window_days,
        "window_minutes": window_minutes,
        "error_budget_minutes": error_budget_minutes,
        "error_budget_percent_of_window": error_budget_percent,
        "error_budget_human": humanize_minutes(error_budget_minutes),
        "tier": classify_tier(target_percent),
    }


def classify_tier(target_percent: float) -> str:
    if target_percent >= 99.99:
        return "mission-critical"
    if target_percent >= 99.95:
        return "critical"
    if target_percent >= 99.9:
        return "standard"
    if target_percent >= 99:
        return "best-effort"
    return "below-best-effort (review with product/sre)"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Calculate error budget and burn-rate thresholds.")
    p.add_argument("--target", type=float, required=True,
                   help="SLO target as percent (e.g., 99.9 for 99.9 percent)")
    p.add_argument("--window-days", type=int, default=28,
                   help="Measurement window in days (default: 28 for rolling)")
    p.add_argument("--burn-rate-alerts", action="store_true",
                   help="Include MWMBR burn-rate alert thresholds")
    p.add_argument("-o", "--output", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    try:
        result = calculate(args.target, args.window_days)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return EXIT_INVALID_INPUT

    if args.burn_rate_alerts:
        result["burn_rate_alerts"] = burn_rate_alerts(result["slo_target_fraction"])

    if args.output == "json":
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"SLO target: {result['slo_target_percent']}%  ({result['tier']} tier)")
        print(f"Window: {result['window_days']} days ({result['window_minutes']:,} minutes)")
        print(f"Error budget: {result['error_budget_minutes']:.2f} minutes "
              f"({result['error_budget_percent_of_window']:.4f}% of window)")
        print(f"Human: {result['error_budget_human']}")
        if args.burn_rate_alerts:
            print("\nBurn-rate alert thresholds:")
            for alert_name, spec in result["burn_rate_alerts"].items():
                if alert_name == "policy_note":
                    continue
                print(f"  {alert_name}: burn_rate >= {spec['burn_rate']}x over {spec['lookback_window']} "
                      f"=> error_rate >= {spec['alert_threshold_error_rate']:.4%}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
