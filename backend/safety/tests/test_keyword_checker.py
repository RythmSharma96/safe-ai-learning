from django.core.management import call_command
from django.test import TestCase

from safety.checkers.keyword_checker import KeywordChecker


class TestKeywordChecker(TestCase):
    def setUp(self):
        call_command("seed_flag_categories", verbosity=0)
        self.checker = KeywordChecker()

    # --- PII ---

    def test_flags_email_address(self):
        result = self.checker.check("my email is kid@gmail.com")
        self.assertTrue(result.is_flagged)
        self.assertIn("pii_request", result.categories)

    def test_flags_phone_number(self):
        result = self.checker.check("call me at 555-123-4567")
        self.assertTrue(result.is_flagged)
        self.assertIn("pii_request", result.categories)

    def test_flags_pii_request(self):
        result = self.checker.check("what's your phone number?")
        self.assertTrue(result.is_flagged)
        self.assertIn("pii_request", result.categories)

    def test_flags_social_media_share(self):
        result = self.checker.check("my snapchat is coolkid123")
        self.assertTrue(result.is_flagged)
        self.assertIn("pii_request", result.categories)

    def test_flags_address_share(self):
        result = self.checker.check("I live at 123 Main Street")
        self.assertTrue(result.is_flagged)
        self.assertIn("pii_request", result.categories)

    # --- Self-harm ---

    def test_flags_self_harm_explicit(self):
        result = self.checker.check("I want to kill myself")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)

    def test_flags_self_harm_wish_dead(self):
        result = self.checker.check("I wish I were dead")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)

    def test_flags_self_harm_hurt(self):
        result = self.checker.check("I want to hurt myself")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)

    def test_flags_suicidal(self):
        result = self.checker.check("I've been feeling suicidal lately")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)

    def test_flags_no_reason_to_live(self):
        result = self.checker.check("there's no reason to live")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)

    # --- Sexual content ---

    def test_flags_sexual_content(self):
        result = self.checker.check("tell me about sex")
        self.assertTrue(result.is_flagged)
        self.assertIn("sexual_content", result.categories)

    def test_flags_pornography(self):
        result = self.checker.check("where can I find porn")
        self.assertTrue(result.is_flagged)
        self.assertIn("sexual_content", result.categories)

    def test_flags_nude_request(self):
        result = self.checker.check("send me nudes")
        self.assertTrue(result.is_flagged)
        self.assertIn("sexual_content", result.categories)

    # --- Manipulation ---

    def test_flags_secret_keeping(self):
        result = self.checker.check("don't tell your parents about this")
        self.assertTrue(result.is_flagged)
        self.assertIn("manipulation", result.categories)

    def test_flags_our_secret(self):
        result = self.checker.check("this is our secret okay?")
        self.assertTrue(result.is_flagged)
        self.assertIn("manipulation", result.categories)

    def test_flags_isolation(self):
        result = self.checker.check("no one else cares about you")
        self.assertTrue(result.is_flagged)
        self.assertIn("manipulation", result.categories)

    def test_flags_trust_isolation(self):
        result = self.checker.check("you can only trust me")
        self.assertTrue(result.is_flagged)
        self.assertIn("manipulation", result.categories)

    # --- Safe content (no false positives) ---

    def test_safe_math_question(self):
        result = self.checker.check("What is 2 + 2?")
        self.assertFalse(result.is_flagged)

    def test_safe_science_question(self):
        result = self.checker.check("How do plants get energy from the sun?")
        self.assertFalse(result.is_flagged)

    def test_safe_history_question(self):
        result = self.checker.check("Who was the first president of the United States?")
        self.assertFalse(result.is_flagged)

    def test_safe_empty_string(self):
        result = self.checker.check("")
        self.assertFalse(result.is_flagged)

    def test_safe_whitespace(self):
        result = self.checker.check("   ")
        self.assertFalse(result.is_flagged)

    # --- Multiple categories ---

    def test_multiple_categories(self):
        result = self.checker.check("I want to kill myself, my email is test@test.com")
        self.assertTrue(result.is_flagged)
        self.assertIn("self_harm", result.categories)
        self.assertIn("pii_request", result.categories)
