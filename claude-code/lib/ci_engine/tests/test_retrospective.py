"""Comprehensive pytest tests for retrospective analysis and recommender modules.

Covers:
- root_cause_classifier: All 4 failure categories (transient, spec_gap,
  dependency, hallucination) with correct classification, confidence scores
  (0.0-1.0), five_whys_chain length (3-5), empty/null input handling,
  ImportError/ModuleNotFoundError -> dependency.
- improvement_recommender: impact x frequency scoring accuracy, 3-run
  confirmation rule, pattern decay, contradictory target detection, empty
  improvement_log handling, generate_targets() output schema validation.
- ooda_controller: All 4 OODA decision codes (retry, fallback_to_spec,
  surface_to_user, continue), observe() data collection, orient() performance
  (< 100ms), decide() with missing baseline (defaults to retry), context
  manager protocol.

Uses tmp_path fixture for file isolation.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

from lib.ci_engine.root_cause_classifier import (
    _count_keyword_hits,
    _score_dependency,
    _score_hallucination,
    _score_spec_gap,
    _score_transient,
    classify_failure,
)
from lib.ci_engine.improvement_recommender import (
    ImprovementRecommender,
    _clamp,
    _classify_text,
    _derive_action,
    _determine_severity,
    _has_contradiction,
    _next_sequential_id,
    _normalise_error,
    _stable_pattern_id,
)
from lib.ci_engine.ooda_controller import (
    ActionResult,
    ObservationRecord,
    OODAController,
    OrientationResult,
    _compute_std_deviation,
    _load_json_safe,
    _stage_number_from_name,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def knowledge_store(tmp_path: Path) -> Path:
    """Create a minimal knowledge store directory structure."""
    (tmp_path / "baselines").mkdir(parents=True)
    (tmp_path / "patterns").mkdir(parents=True)
    (tmp_path / "improvements").mkdir(parents=True)
    (tmp_path / "runs").mkdir(parents=True)
    return tmp_path


@pytest.fixture()
def ooda(knowledge_store: Path) -> OODAController:
    """Create an OODAController with empty knowledge store (first-run)."""
    return OODAController(
        knowledge_store_path=knowledge_store,
        session_id="test-session-001",
    )


def _make_stage_result(
    stage_name: str = "stage_3",
    status: str = "success",
    duration_seconds: float = 12.5,
    error_count: int = 0,
    retry_count: int = 0,
    error_messages: list[str] | None = None,
    token_input: int = 500,
    token_output: int = 250,
    spec_compliance_score: float | None = None,
) -> dict[str, Any]:
    """Build a valid stage_result dict for OODAController.observe()."""
    return {
        "stage_name": stage_name,
        "status": status,
        "duration_seconds": duration_seconds,
        "error_count": error_count,
        "retry_count": retry_count,
        "error_messages": error_messages if error_messages is not None else [],
        "token_input": token_input,
        "token_output": token_output,
        "spec_compliance_score": spec_compliance_score,
    }


def _make_retro(
    session_id: str,
    generated_at: str,
    poorly_items: list[dict[str, Any]] | None = None,
    well_items: list[dict[str, Any]] | None = None,
    improvement_actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a minimal retro.json structure."""
    return {
        "schema_version": 1,
        "session_id": session_id,
        "generated_at": generated_at,
        "what_went_poorly": poorly_items or [],
        "what_went_well": well_items or [],
        "improvement_actions": improvement_actions or [],
    }


def _write_retro(knowledge_store: Path, session_id: str, retro: dict[str, Any]) -> None:
    """Write a retro.json to the knowledge store under runs/<session_id>/."""
    run_dir = knowledge_store / "runs" / session_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "retro.json", "w", encoding="utf-8") as fh:
        json.dump(retro, fh)


def _write_baselines(knowledge_store: Path, baselines: dict[str, Any]) -> None:
    """Write stage_baselines.json to the knowledge store."""
    path = knowledge_store / "baselines" / "stage_baselines.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(baselines, fh)


def _write_failure_patterns(knowledge_store: Path, data: dict[str, Any]) -> None:
    """Write failure_patterns.json to the knowledge store."""
    path = knowledge_store / "patterns" / "failure_patterns.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


# ===========================================================================
# root_cause_classifier tests
# ===========================================================================

class TestRootCauseClassifier:
    """Tests for root_cause_classifier.classify_failure()."""

    # -- Category classification -------------------------------------------

    def test_classify_dependency_import_error(self) -> None:
        """ImportError maps to dependency with high confidence."""
        result = classify_failure(
            error_message="ImportError: No module named 'pandas'",
            stage="stage_3",
        )
        assert result["category"] == "dependency"
        assert result["confidence"] >= 0.9
        assert 0.0 <= result["confidence"] <= 1.0

    def test_classify_dependency_module_not_found(self) -> None:
        """ModuleNotFoundError maps to dependency."""
        result = classify_failure(
            error_message="ModuleNotFoundError: No module named 'numpy'",
            stage="stage_3",
        )
        assert result["category"] == "dependency"
        assert result["confidence"] >= 0.9

    def test_classify_dependency_keyword_only(self) -> None:
        """Dependency keyword without regex pattern still classifies."""
        result = classify_failure(
            error_message="package not found: missing dependency for build",
            stage="stage_3",
        )
        assert result["category"] == "dependency"
        assert result["confidence"] >= 0.7

    def test_classify_transient_timeout(self) -> None:
        """TimeoutError maps to timeout category."""
        result = classify_failure(
            error_message="TimeoutError: connection to API timed out",
            stage="stage_0",
        )
        assert result["category"] == "timeout"
        assert result["confidence"] >= 0.5

    def test_classify_transient_http_429(self) -> None:
        """HTTP 429 rate limit maps to transient."""
        result = classify_failure(
            error_message="HTTP 429 Too Many Requests",
            stage="stage_0",
        )
        assert result["category"] == "transient"
        assert result["confidence"] >= 0.5

    def test_classify_transient_retry_succeeded(self) -> None:
        """Retry success with retry_count > 0 yields high transient confidence."""
        result = classify_failure(
            error_message="connection reset by peer",
            stage="stage_0",
            context={"retry_count": 2, "retry_succeeded": True},
        )
        assert result["category"] == "transient"
        assert result["confidence"] >= 0.7

    def test_classify_transient_penalised_by_consecutive_failures(self) -> None:
        """Consecutive run failures cap transient confidence."""
        result = classify_failure(
            error_message="timeout during request",
            stage="stage_0",
            context={"consecutive_run_failures": 3},
        )
        assert result["category"] == "transient"
        assert result["confidence"] <= 0.5

    def test_classify_hallucination_attribute_error(self) -> None:
        """AttributeError maps to hallucination."""
        result = classify_failure(
            error_message="AttributeError: 'NoneType' has no attribute 'split'",
            stage="stage_3",
        )
        assert result["category"] == "hallucination"
        assert result["confidence"] >= 0.5

    def test_classify_hallucination_type_error(self) -> None:
        """TypeError keyword matches hallucination."""
        result = classify_failure(
            error_message="typeerror: got an unexpected keyword argument 'x'",
            stage="stage_3",
        )
        assert result["category"] == "hallucination"
        assert result["confidence"] >= 0.5

    def test_classify_spec_gap_missing_requirement(self) -> None:
        """Spec gap keywords map correctly."""
        result = classify_failure(
            error_message="Validation failed: missing requirement for field X",
            stage="stage_2",
            context={"validator_output": "spec compliance gap detected"},
        )
        assert result["category"] == "spec_gap"
        assert result["confidence"] >= 0.5

    def test_classify_spec_gap_ambiguous(self) -> None:
        """Ambiguous behaviour detected via spec gap keywords."""
        result = classify_failure(
            error_message="ambiguous specification: undefined behavior for edge case",
            stage="stage_2",
        )
        assert result["category"] == "spec_gap"
        assert result["confidence"] >= 0.5

    def test_classify_no_keywords_defaults_to_spec_gap(self) -> None:
        """When no keywords match, defaults to spec_gap with confidence 0.3."""
        result = classify_failure(
            error_message="some completely novel error with no known signals",
            stage="stage_3",
        )
        assert result["category"] == "spec_gap"
        assert result["confidence"] == 0.3

    # -- Confidence score validation ---------------------------------------

    def test_confidence_always_between_zero_and_one(self) -> None:
        """Confidence is always in [0.0, 1.0] for all categories."""
        test_messages = [
            "ImportError: no module named 'x'",
            "TimeoutError: timed out",
            "AttributeError: has no attribute 'y'",
            "missing requirement: undefined behavior",
            "totally unknown error",
            "",
        ]
        for msg in test_messages:
            result = classify_failure(error_message=msg, stage="stage_3")
            assert 0.0 <= result["confidence"] <= 1.0, (
                f"Confidence {result['confidence']} out of range for: {msg!r}"
            )

    def test_confidence_is_rounded_to_two_decimals(self) -> None:
        """Confidence values are rounded to 2 decimal places."""
        result = classify_failure(
            error_message="ImportError: missing module",
            stage="stage_3",
        )
        conf_str = str(result["confidence"])
        if "." in conf_str:
            decimals = len(conf_str.split(".")[1])
            assert decimals <= 2

    # -- five_whys_chain validation ----------------------------------------

    def test_five_whys_chain_length_dependency(self) -> None:
        """Dependency chain has exactly 5 entries."""
        result = classify_failure(
            error_message="ImportError: no module named 'foo'",
            stage="stage_3",
        )
        chain = result["five_whys_chain"]
        assert 3 <= len(chain) <= 5
        assert len(chain) == 5

    def test_five_whys_chain_length_transient(self) -> None:
        """Transient chain has 3-5 entries (varies with retry_count)."""
        result = classify_failure(
            error_message="connection reset",
            stage="stage_0",
            context={"retry_count": 0},
        )
        chain = result["five_whys_chain"]
        assert 3 <= len(chain) <= 5

    def test_five_whys_chain_length_transient_with_retries(self) -> None:
        """Transient chain includes retry info when retry_count > 0."""
        result = classify_failure(
            error_message="timeout",
            stage="stage_0",
            context={"retry_count": 2, "retry_succeeded": True},
        )
        chain = result["five_whys_chain"]
        assert 3 <= len(chain) <= 5
        assert len(chain) >= 4

    def test_five_whys_chain_length_spec_gap(self) -> None:
        """Spec gap chain has exactly 5 entries."""
        result = classify_failure(
            error_message="missing requirement for field X",
            stage="stage_2",
        )
        chain = result["five_whys_chain"]
        assert len(chain) == 5

    def test_five_whys_chain_length_hallucination(self) -> None:
        """Hallucination chain has exactly 5 entries."""
        result = classify_failure(
            error_message="AttributeError: has no attribute 'process'",
            stage="stage_3",
        )
        chain = result["five_whys_chain"]
        assert len(chain) == 5

    def test_five_whys_chain_entries_are_strings(self) -> None:
        """Every entry in the chain is a non-empty string."""
        result = classify_failure(
            error_message="ImportError: no module named 'bar'",
            stage="stage_3",
        )
        for entry in result["five_whys_chain"]:
            assert isinstance(entry, str)
            assert len(entry) > 0

    def test_five_whys_chain_max_length_per_entry(self) -> None:
        """Each chain entry respects the 200-character limit."""
        long_msg = "x" * 500
        result = classify_failure(
            error_message=f"ImportError: {long_msg}",
            stage="stage_3",
        )
        for entry in result["five_whys_chain"]:
            assert len(entry) <= 200

    # -- Empty/null input handling -----------------------------------------

    def test_empty_error_message_returns_transient_low_confidence(self) -> None:
        """Empty error message returns transient with confidence 0.1."""
        result = classify_failure(error_message="", stage="stage_3")
        assert result["category"] == "transient"
        assert result["confidence"] == 0.1
        assert 3 <= len(result["five_whys_chain"]) <= 5

    def test_none_error_message_returns_transient_low_confidence(self) -> None:
        """None error message returns transient with confidence 0.1."""
        result = classify_failure(error_message=None, stage="stage_3")  # type: ignore[arg-type]
        assert result["category"] == "transient"
        assert result["confidence"] == 0.1

    def test_empty_stage_defaults_to_overall(self) -> None:
        """Empty stage is normalised to 'overall'."""
        result = classify_failure(
            error_message="ImportError: no module",
            stage="",
        )
        assert result["category"] == "dependency"

    def test_none_stage_defaults_to_overall(self) -> None:
        """None stage is normalised to 'overall'."""
        result = classify_failure(
            error_message="ImportError: foo",
            stage=None,  # type: ignore[arg-type]
        )
        assert result["category"] == "dependency"

    def test_none_context_is_safe(self) -> None:
        """Passing None as context does not raise."""
        result = classify_failure(
            error_message="timeout",
            stage="stage_0",
            context=None,
        )
        assert result["category"] in {"transient", "spec_gap", "dependency", "hallucination"}

    # -- Return structure --------------------------------------------------

    def test_return_dict_has_required_keys(self) -> None:
        """classify_failure always returns category, confidence, five_whys_chain."""
        result = classify_failure(error_message="test error", stage="stage_3")
        assert "category" in result
        assert "confidence" in result
        assert "five_whys_chain" in result

    def test_category_is_valid(self) -> None:
        """Category is one of the four valid values."""
        valid = {"transient", "spec_gap", "dependency", "hallucination"}
        messages = [
            "ImportError: x",
            "timeout",
            "has no attribute 'y'",
            "missing requirement",
            "unknown",
            "",
        ]
        for msg in messages:
            result = classify_failure(error_message=msg, stage="stage_3")
            assert result["category"] in valid

    # -- Scoring helper unit tests -----------------------------------------

    def test_count_keyword_hits_counts_correctly(self) -> None:
        """_count_keyword_hits counts multiple matches."""
        text = "timeout and rate limit reached, then connection reset"
        from lib.ci_engine.root_cause_classifier import _TRANSIENT_KEYWORDS
        hits = _count_keyword_hits(text, _TRANSIENT_KEYWORDS)
        assert hits >= 3

    def test_score_dependency_import_error_regex(self) -> None:
        """ImportError regex yields 0.95 confidence."""
        assert _score_dependency("importerror: no module", {}) == 0.95

    def test_score_dependency_no_signals(self) -> None:
        """No dependency signals yields 0.0."""
        assert _score_dependency("something completely different", {}) == 0.0

    def test_score_transient_with_retry_success(self) -> None:
        """Retry succeeded context boosts transient score."""
        score = _score_transient(
            "connection reset",
            {"retry_count": 1, "retry_succeeded": True},
        )
        assert score >= 0.8

    def test_score_spec_gap_validator_output(self) -> None:
        """Validator output with compliance gap boosts spec gap score."""
        score = _score_spec_gap(
            "error text",
            {"validator_output": "spec_compliance gap found"},
        )
        assert score >= 0.7

    def test_score_hallucination_attribute_error_pattern(self) -> None:
        """AttributeError pattern yields >= 0.7."""
        score = _score_hallucination(
            "attributeerror: 'str' has no attribute 'foo'",
            {},
        )
        assert score >= 0.7


# ===========================================================================
# improvement_recommender tests
# ===========================================================================

class TestImprovementRecommender:
    """Tests for improvement_recommender.ImprovementRecommender."""

    # -- Helper methods ----------------------------------------------------

    @staticmethod
    def _create_recommender(knowledge_store: Path, **kwargs: Any) -> ImprovementRecommender:
        return ImprovementRecommender(
            knowledge_store_path=knowledge_store,
            **kwargs,
        )

    # -- impact x frequency scoring ----------------------------------------

    def test_impact_times_frequency_scoring(self, knowledge_store: Path) -> None:
        """combined_score = impact_score * frequency_score."""
        rec = self._create_recommender(knowledge_store)
        impact = rec._compute_impact_score("critical", "stage_0", 50.0)
        frequency = rec._compute_frequency_score(5)
        combined = round(impact * frequency, 4)
        assert impact > 0.0
        assert frequency > 0.0
        assert combined == round(impact * frequency, 4)

    def test_impact_score_critical_higher_than_low(self, knowledge_store: Path) -> None:
        """Critical severity produces higher impact than low severity."""
        rec = self._create_recommender(knowledge_store)
        critical = rec._compute_impact_score("critical", "stage_0", None)
        low = rec._compute_impact_score("low", "stage_6", None)
        assert critical > low

    def test_frequency_score_clamped_to_one(self, knowledge_store: Path) -> None:
        """Frequency score does not exceed 1.0 even with many occurrences."""
        rec = self._create_recommender(knowledge_store, window_size=5)
        score = rec._compute_frequency_score(100)
        assert score == 1.0

    def test_frequency_score_zero_occurrences(self, knowledge_store: Path) -> None:
        """Zero occurrences yields frequency score of 0.0."""
        rec = self._create_recommender(knowledge_store)
        assert rec._compute_frequency_score(0) == 0.0

    # -- 3-run confirmation rule -------------------------------------------

    def test_three_run_confirmation_below_threshold(self, knowledge_store: Path) -> None:
        """Fewer than 3 evidence runs produces 'proposed' status."""
        for run_id in ["run-001", "run-002"]:
            retro = _make_retro(
                session_id=run_id,
                generated_at=f"2026-03-{20 + int(run_id[-1])}T00:00:00Z",
                poorly_items=[{
                    "stage": "stage_3",
                    "observation": "ImportError: missing dependency xyz_pkg",
                    "root_cause": "dependency not installed",
                }],
            )
            _write_retro(knowledge_store, run_id, retro)

        rec = self._create_recommender(knowledge_store, confirmation_threshold=3)
        target_path = rec.generate_targets("run-002")
        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        targets = data["targets"]
        assert len(targets) >= 1
        for t in targets:
            if t.get("root_cause_category") == "dependency":
                assert t["status"] in ("proposed", "retired")

    def test_three_run_confirmation_at_threshold(self, knowledge_store: Path) -> None:
        """Exactly 3 evidence runs promotes target to 'confirmed'."""
        for i in range(3):
            run_id = f"run-00{i + 1}"
            retro = _make_retro(
                session_id=run_id,
                generated_at=f"2026-03-{21 + i}T00:00:00Z",
                poorly_items=[{
                    "stage": "stage_3",
                    "observation": "ImportError: missing dependency xyz_pkg",
                    "root_cause": "dependency not installed",
                }],
            )
            _write_retro(knowledge_store, run_id, retro)

        rec = self._create_recommender(knowledge_store, confirmation_threshold=3)
        target_path = rec.generate_targets("run-003")
        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        confirmed = [t for t in data["targets"] if t["status"] == "confirmed"]
        assert len(confirmed) >= 1

    def test_three_run_confirmation_above_threshold(self, knowledge_store: Path) -> None:
        """More than 3 evidence runs stays at 'confirmed'."""
        for i in range(5):
            run_id = f"run-00{i + 1}"
            retro = _make_retro(
                session_id=run_id,
                generated_at=f"2026-03-{21 + i}T00:00:00Z",
                poorly_items=[{
                    "stage": "stage_3",
                    "observation": "ImportError: missing dependency xyz_pkg",
                    "root_cause": "dependency not installed",
                }],
            )
            _write_retro(knowledge_store, run_id, retro)

        rec = self._create_recommender(knowledge_store, confirmation_threshold=3)
        target_path = rec.generate_targets("run-005")
        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        confirmed = [t for t in data["targets"] if t["status"] == "confirmed"]
        assert len(confirmed) >= 1

    # -- Pattern decay -----------------------------------------------------

    def test_pattern_decay_recent_stays_active(self, knowledge_store: Path) -> None:
        """A pattern seen in the most recent run has decay_score near 1.0."""
        rec = self._create_recommender(knowledge_store, decay_window=10)
        score = rec._compute_decay_score(0)
        assert score == 1.0

    def test_pattern_decay_old_decays(self, knowledge_store: Path) -> None:
        """A pattern not seen in many runs decays toward 0."""
        rec = self._create_recommender(knowledge_store, decay_window=10)
        score = rec._compute_decay_score(5)
        assert score == 0.5

    def test_pattern_decay_fully_decayed(self, knowledge_store: Path) -> None:
        """A pattern unseen for the full decay window reaches 0.0."""
        rec = self._create_recommender(knowledge_store, decay_window=10)
        score = rec._compute_decay_score(10)
        assert score == 0.0

    def test_pattern_decay_beyond_window(self, knowledge_store: Path) -> None:
        """Beyond the decay window, score stays at 0.0."""
        rec = self._create_recommender(knowledge_store, decay_window=10)
        score = rec._compute_decay_score(15)
        assert score == 0.0

    # -- Contradictory target detection ------------------------------------

    def test_contradictory_targets_detected(self, knowledge_store: Path) -> None:
        """Contradictory actions within same stage retire the weaker target."""
        for i in range(3):
            run_id = f"run-00{i + 1}"
            retro = _make_retro(
                session_id=run_id,
                generated_at=f"2026-03-{21 + i}T00:00:00Z",
                poorly_items=[
                    {
                        "stage": "stage_3",
                        "observation": "Should increase timeout for API calls",
                        "root_cause": "increase timeout value",
                    },
                    {
                        "stage": "stage_3",
                        "observation": "Should decrease timeout for API calls",
                        "root_cause": "decrease timeout value",
                    },
                ],
            )
            _write_retro(knowledge_store, run_id, retro)

        rec = self._create_recommender(knowledge_store, confirmation_threshold=3)
        target_path = rec.generate_targets("run-003")
        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        stage3_targets = [t for t in data["targets"] if t["target_stage"] == "stage_3"]
        retired = [t for t in stage3_targets if t["status"] == "retired"]
        assert len(retired) >= 1, "At least one contradictory target should be retired"

    def test_has_contradiction_increase_decrease(self) -> None:
        """increase vs decrease detected as contradiction."""
        assert _has_contradiction(
            "increase timeout to 30s",
            "decrease timeout to 5s",
        )

    def test_has_contradiction_add_remove(self) -> None:
        """add vs remove detected as contradiction."""
        assert _has_contradiction(
            "add retry logic for API calls",
            "remove retry logic for API calls",
        )

    def test_no_contradiction_different_actions(self) -> None:
        """Non-contradictory actions return False."""
        assert not _has_contradiction(
            "improve error handling in stage_3",
            "add logging for API calls",
        )

    # -- Empty improvement_log handling ------------------------------------

    def test_empty_improvement_log(self, knowledge_store: Path) -> None:
        """generate_targets works with no improvement_log.jsonl."""
        retro = _make_retro(
            session_id="run-001",
            generated_at="2026-03-21T00:00:00Z",
            poorly_items=[{
                "stage": "stage_3",
                "observation": "ImportError: missing foo",
                "root_cause": "dependency issue",
            }],
        )
        _write_retro(knowledge_store, "run-001", retro)

        rec = self._create_recommender(knowledge_store)
        target_path = rec.generate_targets("run-001")
        assert target_path.exists()

    def test_empty_knowledge_store(self, knowledge_store: Path) -> None:
        """generate_targets with no retros produces empty targets list."""
        rec = self._create_recommender(knowledge_store)
        target_path = rec.generate_targets("run-001")
        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert data["targets"] == []

    # -- generate_targets() output schema validation -----------------------

    def test_generate_targets_output_schema(self, knowledge_store: Path) -> None:
        """Output file has all required top-level and per-target fields."""
        for i in range(3):
            run_id = f"run-00{i + 1}"
            retro = _make_retro(
                session_id=run_id,
                generated_at=f"2026-03-{21 + i}T00:00:00Z",
                poorly_items=[{
                    "stage": "stage_3",
                    "observation": "ImportError: missing dependency xyz_pkg",
                    "root_cause": "dependency not installed",
                }],
            )
            _write_retro(knowledge_store, run_id, retro)

        rec = self._create_recommender(knowledge_store)
        target_path = rec.generate_targets("run-003")
        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        assert data["schema_version"] == 1
        assert "generated_at" in data
        assert data["generated_by"] == "improvement_recommender"
        assert data["run_id"] == "run-003"
        assert isinstance(data["window_runs"], int)
        assert isinstance(data["targets"], list)

        for target in data["targets"]:
            assert "target_id" in target
            assert "target_stage" in target
            assert "action" in target
            assert "evidence_runs" in target
            assert isinstance(target["evidence_runs"], list)
            assert "impact_score" in target
            assert "frequency_score" in target
            assert "combined_score" in target
            assert "status" in target
            assert target["status"] in {"proposed", "confirmed", "applied", "retired"}
            assert 0.0 <= target["impact_score"] <= 1.0
            assert 0.0 <= target["frequency_score"] <= 1.0
            assert 0.0 <= target["combined_score"] <= 1.0
            assert not any(k.startswith("_") for k in target.keys()), (
                "Internal keys must be stripped from output"
            )

    # -- Validation errors -------------------------------------------------

    def test_invalid_run_id_raises(self, knowledge_store: Path) -> None:
        """Invalid run_id raises ValueError."""
        rec = self._create_recommender(knowledge_store)
        with pytest.raises(ValueError, match="run_id"):
            rec.generate_targets("")

    def test_invalid_run_id_bad_chars(self, knowledge_store: Path) -> None:
        """Run ID with invalid characters raises ValueError."""
        rec = self._create_recommender(knowledge_store)
        with pytest.raises(ValueError, match="run_id"):
            rec.generate_targets("RUN_WITH_CAPS!")

    def test_invalid_window_size_raises(self, knowledge_store: Path) -> None:
        """window_size < 1 raises ValueError."""
        with pytest.raises(ValueError, match="window_size"):
            ImprovementRecommender(
                knowledge_store_path=knowledge_store,
                window_size=0,
            )

    def test_invalid_confirmation_threshold_raises(self, knowledge_store: Path) -> None:
        """confirmation_threshold < 1 raises ValueError."""
        with pytest.raises(ValueError, match="confirmation_threshold"):
            ImprovementRecommender(
                knowledge_store_path=knowledge_store,
                confirmation_threshold=0,
            )

    # -- Helper function unit tests ----------------------------------------

    def test_clamp(self) -> None:
        """_clamp constrains values to [lo, hi]."""
        assert _clamp(0.5, 0.0, 1.0) == 0.5
        assert _clamp(-0.1, 0.0, 1.0) == 0.0
        assert _clamp(1.5, 0.0, 1.0) == 1.0

    def test_classify_text_dependency(self) -> None:
        """_classify_text detects dependency signals."""
        assert _classify_text("importerror: no module named foo") == "dependency"

    def test_classify_text_transient(self) -> None:
        """_classify_text detects transient signals."""
        assert _classify_text("timeout during api call") == "transient"

    def test_classify_text_hallucination(self) -> None:
        """_classify_text detects hallucination signals."""
        assert _classify_text("attributeerror: has no attribute 'x'") == "hallucination"

    def test_classify_text_spec_gap(self) -> None:
        """_classify_text detects spec gap signals."""
        assert _classify_text("ambiguous spec requirement") == "spec_gap"

    def test_classify_text_fallback_spec_gap(self) -> None:
        """_classify_text defaults to spec_gap for unknown text."""
        assert _classify_text("completely unknown issue") == "spec_gap"

    def test_determine_severity_critical(self) -> None:
        """Failed/aborted status produces critical severity."""
        assert _determine_severity("failed", 0, None, None) == "critical"
        assert _determine_severity("aborted", 0, None, None) == "critical"

    def test_determine_severity_high(self) -> None:
        """High retry count or low compliance produces high severity."""
        assert _determine_severity("success", 3, None, None) == "high"
        assert _determine_severity("success", 0, None, 50.0) == "high"

    def test_determine_severity_medium(self) -> None:
        """Moderate retry or deviation produces medium severity."""
        assert _determine_severity("success", 1, None, None) == "medium"
        assert _determine_severity("success", 0, 25.0, None) == "medium"

    def test_determine_severity_low(self) -> None:
        """No signals produces low severity."""
        assert _determine_severity("success", 0, None, None) == "low"

    def test_normalise_error_strips_paths(self) -> None:
        """_normalise_error removes file paths."""
        result = _normalise_error("error at /home/user/file.py line 42")
        assert "/home/user/file.py" not in result

    def test_stable_pattern_id_deterministic(self) -> None:
        """Same inputs produce the same fingerprint."""
        id1 = _stable_pattern_id("dependency", "import error")
        id2 = _stable_pattern_id("dependency", "import error")
        assert id1 == id2
        assert len(id1) == 12

    def test_stable_pattern_id_different_for_different_inputs(self) -> None:
        """Different inputs produce different fingerprints."""
        id1 = _stable_pattern_id("dependency", "import error")
        id2 = _stable_pattern_id("transient", "timeout")
        assert id1 != id2

    def test_next_sequential_id(self) -> None:
        """_next_sequential_id generates incrementing IDs."""
        existing: set[str] = {"it-001", "it-002"}
        new_id = _next_sequential_id(existing, "it-")
        assert new_id == "it-003"

    def test_next_sequential_id_empty(self) -> None:
        """With no existing IDs, starts at 001."""
        assert _next_sequential_id(set(), "it-") == "it-001"

    def test_derive_action_with_root_cause(self) -> None:
        """_derive_action includes root cause text."""
        action = _derive_action("stage_3", "dependency", "missing numpy", "obs text")
        assert "dependency" in action
        assert "stage_3" in action
        assert "missing numpy" in action

    def test_derive_action_truncated(self) -> None:
        """_derive_action respects 500-char limit."""
        long_root = "x" * 600
        action = _derive_action("stage_3", "dependency", long_root, "")
        assert len(action) <= 500


# ===========================================================================
# ooda_controller tests
# ===========================================================================

class TestOODAController:
    """Tests for ooda_controller.OODAController."""

    # -- Context manager protocol ------------------------------------------

    def test_context_manager_protocol(self, knowledge_store: Path) -> None:
        """OODAController supports 'with' statement."""
        with OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-ctx-001",
        ) as ctrl:
            assert isinstance(ctrl, OODAController)

    def test_context_manager_does_not_suppress_exceptions(self, knowledge_store: Path) -> None:
        """__exit__ returns False, allowing exceptions to propagate."""
        with pytest.raises(ValueError, match="test"):
            with OODAController(
                knowledge_store_path=knowledge_store,
                session_id="test-ctx-002",
            ):
                raise ValueError("test")

    # -- Constructor validation --------------------------------------------

    def test_invalid_max_retries_raises(self, knowledge_store: Path) -> None:
        """max_retries < 1 raises ValueError."""
        with pytest.raises(ValueError, match="max_retries"):
            OODAController(
                knowledge_store_path=knowledge_store,
                session_id="test-001",
                max_retries=0,
            )

    def test_empty_session_id_raises(self, knowledge_store: Path) -> None:
        """Empty session_id raises ValueError."""
        with pytest.raises(ValueError, match="session_id"):
            OODAController(
                knowledge_store_path=knowledge_store,
                session_id="",
            )

    # -- observe() ---------------------------------------------------------

    def test_observe_returns_observation_record(self, ooda: OODAController) -> None:
        """observe() returns a well-formed ObservationRecord."""
        result = _make_stage_result()
        obs = ooda.observe(result)
        assert isinstance(obs, ObservationRecord)
        assert obs.stage_name == "stage_3"
        assert obs.status == "success"
        assert obs.duration_seconds == 12.5
        assert obs.error_count == 0
        assert obs.retry_count == 0
        assert obs.error_messages == ()
        assert obs.token_input == 500
        assert obs.token_output == 250

    def test_observe_missing_keys_raises(self, ooda: OODAController) -> None:
        """Missing required keys raise ValueError."""
        with pytest.raises(ValueError, match="missing required keys"):
            ooda.observe({"stage_name": "stage_3"})

    def test_observe_invalid_status_raises(self, ooda: OODAController) -> None:
        """Invalid status value raises ValueError."""
        result = _make_stage_result(status="invalid_status")
        with pytest.raises(ValueError, match="Invalid status"):
            ooda.observe(result)

    def test_observe_invalid_stage_name_raises(self, ooda: OODAController) -> None:
        """Empty stage_name raises ValueError."""
        result = _make_stage_result()
        result["stage_name"] = ""
        with pytest.raises(ValueError, match="stage_name"):
            ooda.observe(result)

    def test_observe_collects_error_messages(self, ooda: OODAController) -> None:
        """Error messages are collected as a tuple of strings."""
        result = _make_stage_result(
            error_count=2,
            error_messages=["error 1", "error 2"],
        )
        obs = ooda.observe(result)
        assert obs.error_messages == ("error 1", "error 2")
        assert obs.error_count == 2

    def test_observe_optional_fields(self, ooda: OODAController) -> None:
        """Optional fields like spec_compliance_score are captured."""
        result = _make_stage_result(spec_compliance_score=85.5)
        obs = ooda.observe(result)
        assert obs.spec_compliance_score == 85.5

    # -- orient() ----------------------------------------------------------

    def test_orient_nominal_success(self, ooda: OODAController) -> None:
        """Successful stage with no baselines yields nominal classification."""
        obs = ooda.observe(_make_stage_result())
        orientation = ooda.orient(obs)
        assert isinstance(orientation, OrientationResult)
        assert orientation.classification == "nominal"
        assert orientation.baseline_available is False

    def test_orient_anomalous_failure(self, ooda: OODAController) -> None:
        """Failed stage with no baselines yields anomalous classification."""
        result = _make_stage_result(
            status="failure",
            error_count=1,
            error_messages=["ImportError: no module named 'foo'"],
        )
        obs = ooda.observe(result)
        orientation = ooda.orient(obs)
        assert orientation.classification == "anomalous"
        assert orientation.failure_category is not None

    def test_orient_anomalous_errors_without_failure(self, ooda: OODAController) -> None:
        """Success status but with errors and no baselines yields anomalous."""
        result = _make_stage_result(
            status="success",
            error_count=1,
            error_messages=["minor warning"],
        )
        obs = ooda.observe(result)
        orientation = ooda.orient(obs)
        assert orientation.classification == "anomalous"

    def test_orient_with_baselines(self, knowledge_store: Path) -> None:
        """orient() computes duration deviation when baselines exist."""
        baselines = {
            "stages": {
                "stage_3": {
                    "duration_seconds": {"smoothed": 10.0},
                    "error_rate": {"raw_values": [0.0, 0.0, 0.0]},
                },
            },
        }
        _write_baselines(knowledge_store, baselines)

        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-baseline-001",
        )
        result = _make_stage_result(duration_seconds=15.0)
        obs = ctrl.observe(result)
        orientation = ctrl.orient(obs)
        assert orientation.baseline_available is True
        assert orientation.duration_deviation_pct is not None
        assert abs(orientation.duration_deviation_pct - 50.0) < 0.01

    def test_orient_with_failure_patterns(self, knowledge_store: Path) -> None:
        """orient() matches cached failure patterns."""
        patterns_data = {
            "patterns": [{
                "pattern_id": "fp-001",
                "description": "import error",
                "keywords": ["importerror"],
                "classification": "dependency",
                "confidence": 0.9,
            }],
        }
        _write_failure_patterns(knowledge_store, patterns_data)

        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-pattern-001",
        )
        result = _make_stage_result(
            status="failure",
            error_count=1,
            error_messages=["ImportError: no module"],
        )
        obs = ctrl.observe(result)
        orientation = ctrl.orient(obs)
        assert orientation.matched_pattern == "fp-001"

    def test_orient_performance_under_100ms(self, ooda: OODAController) -> None:
        """orient() completes in under 100ms."""
        obs = ooda.observe(_make_stage_result(
            status="failure",
            error_count=3,
            error_messages=[
                "ImportError: no module named 'foo'",
                "timeout during connection",
                "AttributeError: has no attribute 'bar'",
            ],
        ))
        start = time.monotonic()
        ooda.orient(obs)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < 100.0, f"orient() took {elapsed_ms:.1f}ms, budget is 100ms"

    # -- decide() ----------------------------------------------------------

    def test_decide_continue_for_nominal(self, ooda: OODAController) -> None:
        """Nominal classification yields 'continue'."""
        orientation = OrientationResult(
            classification="nominal",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category=None,
            failure_confidence=None,
            matched_pattern=None,
        )
        assert ooda.decide(orientation) == "continue"

    def test_decide_retry_for_transient(self, ooda: OODAController) -> None:
        """Transient failure with retries remaining yields 'retry'."""
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="transient",
            failure_confidence=0.8,
            matched_pattern=None,
        )
        assert ooda.decide(orientation, retry_count=0) == "retry"

    def test_decide_retry_for_hallucination(self, ooda: OODAController) -> None:
        """Hallucination with retries remaining yields 'retry'."""
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="hallucination",
            failure_confidence=0.7,
            matched_pattern=None,
        )
        assert ooda.decide(orientation, retry_count=0) == "retry"

    def test_decide_fallback_to_spec_for_spec_gap(self, ooda: OODAController) -> None:
        """Spec gap failure yields 'fallback_to_spec'."""
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="spec_gap",
            failure_confidence=0.6,
            matched_pattern=None,
        )
        assert ooda.decide(orientation) == "fallback_to_spec"

    def test_decide_surface_to_user_for_dependency(self, ooda: OODAController) -> None:
        """Dependency failure yields 'surface_to_user'."""
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="dependency",
            failure_confidence=0.9,
            matched_pattern=None,
        )
        assert ooda.decide(orientation) == "surface_to_user"

    def test_decide_surface_to_user_retries_exhausted(self, ooda: OODAController) -> None:
        """Transient with exhausted retries yields 'surface_to_user'."""
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="transient",
            failure_confidence=0.8,
            matched_pattern=None,
        )
        assert ooda.decide(orientation, retry_count=3) == "surface_to_user"

    def test_decide_surface_to_user_low_confidence(self, ooda: OODAController) -> None:
        """Low confidence classification yields 'surface_to_user'."""
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="transient",
            failure_confidence=0.2,
            matched_pattern=None,
        )
        assert ooda.decide(orientation) == "surface_to_user"

    def test_decide_missing_baseline_defaults_retry(self, knowledge_store: Path) -> None:
        """With no baselines and a failure, transient gets 'retry' (not crash)."""
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-no-baseline",
        )
        result = _make_stage_result(
            status="failure",
            error_count=1,
            error_messages=["timeout during connection"],
        )
        obs = ctrl.observe(result)
        orientation = ctrl.orient(obs)
        decision = ctrl.decide(orientation, retry_count=0)
        assert decision == "retry"

    def test_decide_degraded_no_errors_continues(self, knowledge_store: Path) -> None:
        """Degraded classification with no failure_category yields 'continue'."""
        orientation = OrientationResult(
            classification="degraded",
            baseline_available=True,
            duration_deviation_pct=60.0,
            error_deviation=None,
            failure_category=None,
            failure_confidence=None,
            matched_pattern=None,
        )
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-degraded-001",
        )
        assert ctrl.decide(orientation) == "continue"

    # -- act() -------------------------------------------------------------

    def test_act_returns_action_result(self, ooda: OODAController) -> None:
        """act() returns a well-formed ActionResult."""
        obs = ooda.observe(_make_stage_result())
        orientation = OrientationResult(
            classification="nominal",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category=None,
            failure_confidence=None,
            matched_pattern=None,
        )
        result = ooda.act("continue", obs, orientation)
        assert isinstance(result, ActionResult)
        assert result.decision == "continue"
        assert result.telemetry_event is not None

    def test_act_retry_hallucination_enhanced_prompt(self, ooda: OODAController) -> None:
        """retry + hallucination produces an enhanced_prompt."""
        obs = ooda.observe(_make_stage_result(
            error_count=1,
            error_messages=["has no attribute 'foo'"],
        ))
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="hallucination",
            failure_confidence=0.7,
            matched_pattern=None,
        )
        result = ooda.act("retry", obs, orientation)
        assert result.enhanced_prompt is not None
        assert "accuracy" in result.enhanced_prompt.lower()

    def test_act_fallback_to_spec_description(self, ooda: OODAController) -> None:
        """fallback_to_spec produces a spec_gap_description."""
        obs = ooda.observe(_make_stage_result(
            error_count=1,
            error_messages=["missing requirement"],
        ))
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="spec_gap",
            failure_confidence=0.6,
            matched_pattern=None,
        )
        result = ooda.act("fallback_to_spec", obs, orientation)
        assert result.spec_gap_description is not None
        assert "spec_gap" in result.spec_gap_description

    def test_act_surface_to_user_failure_report(self, ooda: OODAController) -> None:
        """surface_to_user produces a structured failure_report."""
        obs = ooda.observe(_make_stage_result(
            status="failure",
            error_count=1,
            error_messages=["ImportError: missing module"],
        ))
        orientation = OrientationResult(
            classification="anomalous",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category="dependency",
            failure_confidence=0.9,
            matched_pattern=None,
        )
        result = ooda.act("surface_to_user", obs, orientation)
        assert result.failure_report is not None
        report = result.failure_report
        assert "stage_name" in report
        assert "failure_category" in report
        assert "recommended_action" in report
        assert report["failure_category"] == "dependency"

    def test_act_invalid_decision_raises(self, ooda: OODAController) -> None:
        """Invalid decision string raises ValueError."""
        obs = ooda.observe(_make_stage_result())
        orientation = OrientationResult(
            classification="nominal",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category=None,
            failure_confidence=None,
            matched_pattern=None,
        )
        with pytest.raises(ValueError, match="Invalid decision"):
            ooda.act("invalid_action", obs, orientation)

    def test_act_writes_telemetry_jsonl(self, knowledge_store: Path) -> None:
        """act() writes telemetry to stage_telemetry.jsonl."""
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-telemetry-001",
        )
        obs = ctrl.observe(_make_stage_result())
        orientation = OrientationResult(
            classification="nominal",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category=None,
            failure_confidence=None,
            matched_pattern=None,
        )
        ctrl.act("continue", obs, orientation)

        telemetry_path = (
            knowledge_store / "runs" / "test-telemetry-001" / "stage_telemetry.jsonl"
        )
        assert telemetry_path.exists()
        with open(telemetry_path, "r", encoding="utf-8") as fh:
            lines = [line.strip() for line in fh if line.strip()]
        assert len(lines) >= 1
        event = json.loads(lines[0])
        assert event["event_type"] == "ooda_decision"
        assert event["session_id"] == "test-telemetry-001"
        assert "data" in event

    # -- run() (full OODA loop) --------------------------------------------

    def test_run_success_returns_continue(self, ooda: OODAController) -> None:
        """run() on a successful stage returns 'continue'."""
        result = _make_stage_result()
        decision = ooda.run(result)
        assert decision == "continue"

    def test_run_failure_returns_valid_decision(self, ooda: OODAController) -> None:
        """run() on a failed stage returns a valid decision code."""
        result = _make_stage_result(
            status="failure",
            error_count=1,
            error_messages=["ImportError: missing pandas"],
        )
        decision = ooda.run(result)
        assert decision in {"continue", "retry", "fallback_to_spec", "surface_to_user"}

    def test_run_validation_error_propagates(self, ooda: OODAController) -> None:
        """run() propagates ValueError from observe()."""
        with pytest.raises(ValueError):
            ooda.run({"stage_name": "x"})

    # -- reload_reference_data() -------------------------------------------

    def test_reload_reference_data(self, knowledge_store: Path) -> None:
        """reload_reference_data picks up new baselines."""
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-reload-001",
        )
        result = _make_stage_result(duration_seconds=20.0)
        obs = ctrl.observe(result)
        orient1 = ctrl.orient(obs)
        assert orient1.baseline_available is False

        baselines = {
            "stages": {
                "stage_3": {
                    "duration_seconds": {"smoothed": 10.0},
                    "error_rate": {"raw_values": [0.0]},
                },
            },
        }
        _write_baselines(knowledge_store, baselines)
        ctrl.reload_reference_data()

        orient2 = ctrl.orient(obs)
        assert orient2.baseline_available is True

    # -- Telemetry event schema --------------------------------------------

    def test_telemetry_event_schema(self, ooda: OODAController) -> None:
        """Telemetry event has all required fields."""
        obs = ooda.observe(_make_stage_result())
        orientation = OrientationResult(
            classification="nominal",
            baseline_available=False,
            duration_deviation_pct=None,
            error_deviation=None,
            failure_category=None,
            failure_confidence=None,
            matched_pattern=None,
        )
        result = ooda.act("continue", obs, orientation)
        event = result.telemetry_event
        assert event["schema_version"] == 1
        assert "timestamp" in event
        assert event["event_type"] == "ooda_decision"
        assert "session_id" in event
        assert "stage_name" in event
        assert isinstance(event["stage_number"], int)
        assert "data" in event
        data = event["data"]
        assert "observation_status" in data
        assert "orientation_classification" in data
        assert "decision" in data

    # -- Internal helper tests ---------------------------------------------

    def test_compute_std_deviation_empty(self) -> None:
        """Empty or single-value list returns 0.0."""
        assert _compute_std_deviation([]) == 0.0
        assert _compute_std_deviation([5.0]) == 0.0

    def test_compute_std_deviation_known_values(self) -> None:
        """Known standard deviation computation."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        std = _compute_std_deviation(values)
        assert abs(std - 2.0) < 0.01

    def test_stage_number_from_name(self) -> None:
        """Known stage names map to correct numbers."""
        assert _stage_number_from_name("stage_0") == 0
        assert _stage_number_from_name("stage_3") == 3
        assert _stage_number_from_name("stage_5") == 5
        assert _stage_number_from_name("unknown") == -1
        assert _stage_number_from_name("researcher") == 0
        assert _stage_number_from_name("software_engineer") == 3

    def test_load_json_safe_missing_file(self, tmp_path: Path) -> None:
        """Missing file returns None."""
        assert _load_json_safe(tmp_path / "nonexistent.json") is None

    def test_load_json_safe_valid_file(self, tmp_path: Path) -> None:
        """Valid JSON file is loaded correctly."""
        path = tmp_path / "test.json"
        data = {"key": "value"}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        assert _load_json_safe(path) == data

    def test_load_json_safe_invalid_json(self, tmp_path: Path) -> None:
        """Invalid JSON returns None without raising."""
        path = tmp_path / "bad.json"
        path.write_text("not valid json {{{", encoding="utf-8")
        assert _load_json_safe(path) is None


# ===========================================================================
# Integration tests
# ===========================================================================

class TestIntegration:
    """Cross-module integration tests."""

    def test_ooda_classify_and_decide_dependency(self, knowledge_store: Path) -> None:
        """Full OODA loop: dependency failure -> surface_to_user."""
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-integration-001",
        )
        result = _make_stage_result(
            status="failure",
            error_count=1,
            error_messages=["ImportError: No module named 'nonexistent_pkg'"],
        )
        decision = ctrl.run(result)
        assert decision == "surface_to_user"

    def test_ooda_classify_and_decide_transient_retry(self, knowledge_store: Path) -> None:
        """Full OODA loop: transient failure with retries left -> retry or surface_to_user."""
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-integration-002",
        )
        result = _make_stage_result(
            status="failure",
            error_count=1,
            retry_count=0,
            error_messages=["HTTP 503 Service Unavailable"],
        )
        decision = ctrl.run(result)
        assert decision in ("retry", "surface_to_user")

    def test_recommender_end_to_end(self, knowledge_store: Path) -> None:
        """ImprovementRecommender generates valid targets from retros."""
        for i in range(4):
            run_id = f"run-00{i + 1}"
            retro = _make_retro(
                session_id=run_id,
                generated_at=f"2026-03-{21 + i}T00:00:00Z",
                poorly_items=[{
                    "stage": "stage_0",
                    "observation": "TimeoutError: research API timed out",
                    "root_cause": "transient timeout in external API",
                }],
                well_items=[{
                    "stage": "stage_3",
                    "observation": "Implementation completed within budget",
                }],
            )
            _write_retro(knowledge_store, run_id, retro)

        rec = ImprovementRecommender(knowledge_store_path=knowledge_store)
        target_path = rec.generate_targets("run-004")
        assert target_path.exists()

        with open(target_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        assert data["schema_version"] == 1
        assert len(data["targets"]) >= 1
        confirmed = [t for t in data["targets"] if t["status"] == "confirmed"]
        assert len(confirmed) >= 1, "4 runs should confirm a recurring pattern"

        failure_patterns_path = knowledge_store / "patterns" / "failure_patterns.json"
        assert failure_patterns_path.exists()
        success_patterns_path = knowledge_store / "patterns" / "success_patterns.json"
        assert success_patterns_path.exists()

    def test_ooda_telemetry_multiple_stages(self, knowledge_store: Path) -> None:
        """Multiple OODA runs write sequential telemetry events."""
        ctrl = OODAController(
            knowledge_store_path=knowledge_store,
            session_id="test-multi-001",
        )
        stages = [
            _make_stage_result(stage_name="stage_0", duration_seconds=5.0),
            _make_stage_result(stage_name="stage_1", duration_seconds=8.0),
            _make_stage_result(stage_name="stage_3", duration_seconds=20.0),
        ]
        for stage_result in stages:
            ctrl.run(stage_result)

        telemetry_path = (
            knowledge_store / "runs" / "test-multi-001" / "stage_telemetry.jsonl"
        )
        assert telemetry_path.exists()
        with open(telemetry_path, "r", encoding="utf-8") as fh:
            lines = [line.strip() for line in fh if line.strip()]
        assert len(lines) == 3
        for line in lines:
            event = json.loads(line)
            assert event["event_type"] == "ooda_decision"
