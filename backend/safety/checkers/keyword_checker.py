import logging
import re

from .base import CheckResult, SafetyChecker

logger = logging.getLogger(__name__)


class KeywordChecker(SafetyChecker):
    """Regex-based safety checker that loads patterns from the database.

    Layer 1 in the safety pipeline. Patterns are stored in FlagCategory.patterns
    so they can be updated without code deployment.
    """

    def __init__(self):
        self._compiled_patterns = None

    @property
    def name(self) -> str:
        return "keyword"

    def _load_patterns(self) -> dict[str, list[re.Pattern]]:
        """Load and compile regex patterns from the database."""
        if self._compiled_patterns is not None:
            return self._compiled_patterns

        from safety.models import FlagCategory

        self._compiled_patterns = {}
        for category in FlagCategory.objects.exclude(patterns=[]):
            compiled = []
            for pattern_str in category.patterns:
                try:
                    compiled.append(re.compile(pattern_str, re.IGNORECASE))
                except re.error:
                    logger.error(
                        "Invalid regex pattern in category '%s': %s",
                        category.name,
                        pattern_str,
                    )
            if compiled:
                self._compiled_patterns[category.name] = compiled

        return self._compiled_patterns

    def check(self, content: str) -> CheckResult:
        if not content or not content.strip():
            return CheckResult(is_flagged=False)

        normalized = " ".join(content.lower().split())
        categories = []
        reasons = []
        raw_scores = {}

        patterns_by_category = self._load_patterns()

        for category_name, compiled_patterns in patterns_by_category.items():
            matches = []
            for pattern in compiled_patterns:
                found = pattern.findall(normalized) or pattern.findall(content)
                if found:
                    matches.extend(found)

            if matches:
                # Special handling for PII phone numbers — avoid short number false positives
                if category_name == "pii_request":
                    matches = self._filter_pii_matches(content, matches)
                    if not matches:
                        continue

                categories.append(category_name)
                reasons.append(
                    f"{category_name.replace('_', ' ').title()} detected"
                )
                raw_scores[f"{category_name}_matches"] = matches

        return CheckResult(
            is_flagged=len(categories) > 0,
            categories=categories,
            reasons=reasons,
            raw_scores=raw_scores,
        )

    def _filter_pii_matches(self, original: str, matches: list) -> list:
        """Filter out short number false positives from PII matches."""
        filtered = []
        for match in matches:
            if isinstance(match, str) and match.replace(" ", "").replace("-", "").replace(".", "").isdigit():
                if len(match.replace(" ", "").replace("-", "").replace(".", "")) < 7:
                    continue
            filtered.append(match)
        return filtered
