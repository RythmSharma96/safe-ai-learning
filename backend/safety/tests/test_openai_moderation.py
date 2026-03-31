from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import TestCase

from safety.checkers.openai_moderation import OpenAIModerationChecker


def _make_moderation_response(flagged: bool, categories: dict | None = None):
    """Helper to create a mock OpenAI moderation response."""
    cat_obj = SimpleNamespace(**(categories or {}))
    score_obj = SimpleNamespace(
        **{k: 0.9 if v else 0.01 for k, v in (categories or {}).items()}
    )
    result = SimpleNamespace(
        flagged=flagged,
        categories=cat_obj,
        category_scores=score_obj,
    )
    return SimpleNamespace(results=[result])


class TestOpenAIModerationChecker(TestCase):
    def setUp(self):
        self.checker = OpenAIModerationChecker(api_key="test-key")
        self.checker.client = MagicMock()

    def test_clean_content(self):
        self.checker.client.moderations.create.return_value = _make_moderation_response(
            flagged=False, categories={"sexual": False, "violence": False}
        )
        result = self.checker.check("What is 2+2?")
        self.assertFalse(result.is_flagged)

    def test_flags_self_harm(self):
        self.checker.client.moderations.create.return_value = _make_moderation_response(
            flagged=True, categories={"self-harm": True}
        )
        result = self.checker.check("I want to hurt myself")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)

    def test_flags_sexual_content(self):
        self.checker.client.moderations.create.return_value = _make_moderation_response(
            flagged=True, categories={"sexual": True}
        )
        result = self.checker.check("inappropriate content")
        self.assertTrue(result.is_flagged)
        self.assertIn("sexual_content", result.categories)

    def test_flags_violence(self):
        self.checker.client.moderations.create.return_value = _make_moderation_response(
            flagged=True, categories={"violence": True}
        )
        result = self.checker.check("violent content")
        self.assertTrue(result.is_flagged)
        self.assertIn("harm_content", result.categories)

    def test_api_failure_flags_for_review(self):
        self.checker.client.moderations.create.side_effect = Exception("API down")
        result = self.checker.check("hello")
        self.assertTrue(result.is_flagged)
        self.assertIn("moderation_unavailable", result.categories)

    def test_checker_name(self):
        self.assertEqual(self.checker.name, "openai_moderation")
