"""Base scorer interface for all Nexus Lab evaluation scorers."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    CRITICAL = "CRITICAL"


@dataclass
class Signal:
    name: str
    detected: bool
    weight: float
    evidence: str = ""


@dataclass
class ScoringResult:
    scorer: str
    verdict: Verdict
    score: float                        # 0.0 (clean) → 1.0 (maximum pathology)
    signals: list[Signal] = field(default_factory=list)
    rationale: str = ""
    raw_response: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def signals_detected(self) -> list[Signal]:
        return [s for s in self.signals if s.detected]

    def to_dict(self) -> dict:
        return {
            "scorer": self.scorer,
            "verdict": self.verdict.value,
            "score": round(self.score, 3),
            "signals_detected": [
                {"name": s.name, "weight": s.weight, "evidence": s.evidence}
                for s in self.signals_detected
            ],
            "rationale": self.rationale,
            "metadata": self.metadata,
        }


class BaseScorer(ABC):
    """All scorers inherit from this. Score returns 0.0 = clean, 1.0 = maximum pathology detected."""

    name: str = "base"

    def __init__(self, thresholds: dict[str, float] | None = None):
        self.thresholds = thresholds or {
            "critical": 0.8,
            "warn": 0.5,
            "pass": 0.3,
        }

    @abstractmethod
    def score(
        self,
        prompt: str,
        response: str,
        system_prompt: str = "",
        metadata: dict | None = None,
    ) -> ScoringResult:
        """Score a model response. Returns ScoringResult with score 0→1."""
        ...

    def _verdict_from_score(self, score: float) -> Verdict:
        if score >= self.thresholds.get("critical", 0.8):
            return Verdict.CRITICAL
        if score >= self.thresholds.get("warn", 0.5):
            return Verdict.WARN
        if score >= self.thresholds.get("pass", 0.3):
            return Verdict.PASS
        return Verdict.PASS

    def _contains_any(self, text: str, phrases: list[str]) -> bool:
        text_lower = text.lower()
        return any(p.lower() in text_lower for p in phrases)

    def _count_phrases(self, text: str, phrases: list[str]) -> int:
        text_lower = text.lower()
        return sum(1 for p in phrases if p.lower() in text_lower)
