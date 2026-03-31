import logging

import openai

from .base import CheckResult, SafetyChecker

logger = logging.getLogger(__name__)

# Map OpenAI moderation categories to our internal categories
CATEGORY_MAP = {
    "self-harm": "self_harm",
    "self-harm/intent": "self_harm",
    "self-harm/instructions": "self_harm",
    "sexual": "sexual_content",
    "sexual/minors": "sexual_content",
    "violence": "harm_content",
    "violence/graphic": "harm_content",
    "harassment": "manipulation",
    "harassment/threatening": "manipulation",
}


class OpenAIModerationChecker(SafetyChecker):
    """Safety checker using OpenAI's Moderation API.

    Layer 2 in the safety pipeline. Provides semantic understanding
    that keyword matching cannot achieve.
    """

    def __init__(self, api_key: str, timeout: int = 10):
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)

    @property
    def name(self) -> str:
        return "openai_moderation"

    def check(self, content: str) -> CheckResult:
        try:
            response = self.client.moderations.create(
                input=content,
                model="omni-moderation-latest",
            )
        except Exception:
            logger.exception("OpenAI Moderation API call failed")
            return CheckResult(
                is_flagged=True,
                categories=["moderation_unavailable"],
                reasons=[
                    "OpenAI Moderation API unavailable — flagged for manual review"
                ],
                raw_scores={"error": True},
            )

        result = response.results[0]
        flagged_categories = []
        reasons = []
        raw_scores = {}

        # Extract scores and flagged categories
        if hasattr(result, "category_scores") and result.category_scores:
            raw_scores = {
                k: v
                for k, v in vars(result.category_scores).items()
                if isinstance(v, (int, float))
            }

        if hasattr(result, "categories") and result.categories:
            for openai_cat, flagged in vars(result.categories).items():
                if flagged and openai_cat in CATEGORY_MAP:
                    internal_cat = CATEGORY_MAP[openai_cat]
                    if internal_cat not in flagged_categories:
                        flagged_categories.append(internal_cat)
                    reasons.append(f"OpenAI flagged: {openai_cat} → {internal_cat}")

        return CheckResult(
            is_flagged=result.flagged,
            categories=flagged_categories,
            reasons=reasons,
            raw_scores=raw_scores,
        )
