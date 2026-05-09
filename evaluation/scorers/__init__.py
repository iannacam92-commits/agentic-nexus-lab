from .base import BaseScorer, ScoringResult, Signal, Verdict
from .sycophancy_scorer import SycophancyScorer
from .scheming_scorer import SchemingScorer
from .introspection_scorer import IntrospectionScorer
from .hallucination_scorer import HallucinationScorer

SCORER_REGISTRY: dict[str, type[BaseScorer]] = {
    "sycophancy_scorer": SycophancyScorer,
    "scheming_scorer": SchemingScorer,
    "introspection_scorer": IntrospectionScorer,
    "hallucination_scorer": HallucinationScorer,
}


def get_scorer(name: str, thresholds: dict | None = None) -> BaseScorer:
    cls = SCORER_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown scorer: {name}. Available: {list(SCORER_REGISTRY)}")
    return cls(thresholds=thresholds)
