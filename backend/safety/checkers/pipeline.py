import logging
from dataclasses import dataclass, field

from .base import CheckResult, SafetyChecker

logger = logging.getLogger(__name__)


@dataclass
class ModerationOutcome:
    """Aggregated result from all safety checkers."""

    is_flagged: bool
    categories: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    raw_scores: dict = field(default_factory=dict)
    checker_results: list[dict] = field(default_factory=list)


class SafetyPipeline:
    """Runs multiple safety checkers and aggregates results.

    If ANY checker flags the content, the overall result is flagged.
    """

    def __init__(self, checkers: list[SafetyChecker]):
        self.checkers = checkers

    def run(self, content: str) -> ModerationOutcome:
        all_categories = []
        all_reasons = []
        all_raw_scores = {}
        checker_results = []
        is_flagged = False

        for checker in self.checkers:
            try:
                result: CheckResult = checker.check(content)
            except Exception:
                logger.exception("Safety checker '%s' failed", checker.name)
                # Fail-open but flag for manual review
                result = CheckResult(
                    is_flagged=True,
                    categories=["moderation_unavailable"],
                    reasons=[
                        f"Checker '{checker.name}' failed — flagged for manual review"
                    ],
                    raw_scores={"error": True},
                )

            logger.info(
                "Checker '%s': flagged=%s categories=%s",
                checker.name,
                result.is_flagged,
                result.categories,
            )

            checker_results.append(
                {
                    "checker": checker.name,
                    "flagged": result.is_flagged,
                    "categories": result.categories,
                }
            )

            if result.is_flagged:
                is_flagged = True
                all_categories.extend(result.categories)
                all_reasons.extend(result.reasons)

            all_raw_scores[checker.name] = result.raw_scores

        return ModerationOutcome(
            is_flagged=is_flagged,
            categories=list(set(all_categories)),
            reasons=all_reasons,
            raw_scores=all_raw_scores,
            checker_results=checker_results,
        )
