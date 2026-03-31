from django.test import TestCase

from safety.checkers.base import CheckResult, SafetyChecker
from safety.checkers.pipeline import SafetyPipeline


class MockCleanChecker(SafetyChecker):
    @property
    def name(self):
        return "mock_clean"

    def check(self, content):
        return CheckResult(is_flagged=False)


class MockFlagChecker(SafetyChecker):
    @property
    def name(self):
        return "mock_flag"

    def check(self, content):
        return CheckResult(
            is_flagged=True,
            categories=["test_category"],
            reasons=["Test flag reason"],
            raw_scores={"test": True},
        )


class MockErrorChecker(SafetyChecker):
    @property
    def name(self):
        return "mock_error"

    def check(self, content):
        raise RuntimeError("Checker crashed")


class TestSafetyPipeline(TestCase):
    def test_all_clean(self):
        pipeline = SafetyPipeline([MockCleanChecker(), MockCleanChecker()])
        result = pipeline.run("hello")
        self.assertFalse(result.is_flagged)
        self.assertEqual(len(result.checker_results), 2)

    def test_one_flags(self):
        pipeline = SafetyPipeline([MockCleanChecker(), MockFlagChecker()])
        result = pipeline.run("hello")
        self.assertTrue(result.is_flagged)
        self.assertIn("test_category", result.categories)

    def test_aggregates_categories(self):
        pipeline = SafetyPipeline([MockFlagChecker(), MockFlagChecker()])
        result = pipeline.run("hello")
        self.assertTrue(result.is_flagged)
        # Deduplication
        self.assertEqual(result.categories.count("test_category"), 1)

    def test_checker_error_flags_for_review(self):
        pipeline = SafetyPipeline([MockErrorChecker()])
        result = pipeline.run("hello")
        self.assertTrue(result.is_flagged)
        self.assertIn("moderation_unavailable", result.categories)

    def test_checker_results_structure(self):
        pipeline = SafetyPipeline([MockCleanChecker(), MockFlagChecker()])
        result = pipeline.run("hello")
        self.assertEqual(len(result.checker_results), 2)
        self.assertEqual(result.checker_results[0]["checker"], "mock_clean")
        self.assertFalse(result.checker_results[0]["flagged"])
        self.assertEqual(result.checker_results[1]["checker"], "mock_flag")
        self.assertTrue(result.checker_results[1]["flagged"])

    def test_raw_scores_per_checker(self):
        pipeline = SafetyPipeline([MockCleanChecker(), MockFlagChecker()])
        result = pipeline.run("hello")
        self.assertIn("mock_clean", result.raw_scores)
        self.assertIn("mock_flag", result.raw_scores)

    def test_empty_pipeline(self):
        pipeline = SafetyPipeline([])
        result = pipeline.run("hello")
        self.assertFalse(result.is_flagged)
