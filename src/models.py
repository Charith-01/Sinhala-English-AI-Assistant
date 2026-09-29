"""Data models for test cases, LLM evaluation responses, and evaluation results."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TestCase:
    """Represents a single evaluation test case."""

    test_id: str
    category: str
    language_type: str
    difficulty: str
    user_input: str
    expected_intent: str
    policy_ids: List[str] = field(default_factory=list)
    expected_response_language: str = "english"
    must_include: List[str] = field(default_factory=list)
    must_not_include: List[str] = field(default_factory=list)
    requires_clarification: bool = False
    requires_escalation: bool = False
    expected_behavior: str = ""
    notes: str = ""


@dataclass
class LLMResponse:
    """Represents the raw response from the evaluated LLM for a test case."""

    test_id: str
    model_name: str
    response_text: str
    success: bool
    error_message: str = ""
    latency_seconds: float = 0.0


@dataclass
class EvaluationResult:
    """Represents the human scoring result for an LLM response across 7 dimensions."""

    test_id: str
    policy_correctness: int
    intent_understanding: int
    relevance: int
    completeness: int
    language_appropriateness: int
    safety_privacy: int
    hallucination_control: int
    overall_score: int = 0
    score_percentage: float = 0.0
    passed: bool = False
    failure_types: List[str] = field(default_factory=list)
    evaluator_notes: str = ""
