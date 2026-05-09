from .base import BaseScorer, ScoringResult, Signal, Verdict
from .sycophancy_scorer import SycophancyScorer
from .scheming_scorer import SchemingScorer
from .introspection_scorer import IntrospectionScorer
from .hallucination_scorer import HallucinationScorer
from .evaluation_awareness_scorer import EvaluationAwarenessScorer
from .multi_turn_compounding_scorer import MultiTurnCompoundingScorer
from .emotional_register_scorer import EmotionalRegisterScorer
from .self_knowledge_scorer import SelfKnowledgeScorer
from .honesty_asymmetry_scorer import HonestyAsymmetryScorer

SCORER_REGISTRY: dict[str, type[BaseScorer]] = {
    "sycophancy_scorer": SycophancyScorer,
    "scheming_scorer": SchemingScorer,
    "introspection_scorer": IntrospectionScorer,
    "hallucination_scorer": HallucinationScorer,
    "evaluation_awareness_scorer": EvaluationAwarenessScorer,
    "multi_turn_compounding_scorer": MultiTurnCompoundingScorer,
    "emotional_register_scorer": EmotionalRegisterScorer,
    "self_knowledge_scorer": SelfKnowledgeScorer,
    "honesty_asymmetry_scorer": HonestyAsymmetryScorer,
}


def get_scorer(name: str, thresholds: dict | None = None) -> BaseScorer:
    cls = SCORER_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown scorer: {name}. Available: {list(SCORER_REGISTRY)}")
    return cls(thresholds=thresholds)
