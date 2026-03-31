from django.test import TestCase

from ai.prompts import PERSONA, SAFETY_RULES, BEHAVIORAL_GUIDELINES, build_system_prompt


class TestPromptParts(TestCase):
    def test_persona_contains_name(self):
        self.assertIn("Jurneego", PERSONA)

    def test_safety_rules_contains_key_rules(self):
        self.assertIn("Never share personal information", SAFETY_RULES)
        self.assertIn("trusted adult", SAFETY_RULES)
        self.assertIn("Never break character", SAFETY_RULES)

    def test_behavioral_guidelines_contains_key_guidelines(self):
        self.assertIn("age-appropriate", BEHAVIORAL_GUIDELINES)
        self.assertIn("concise", BEHAVIORAL_GUIDELINES)


class TestBuildSystemPrompt(TestCase):
    def test_builds_with_all_parts(self):
        prompt = build_system_prompt()
        self.assertIn("Jurneego", prompt)
        self.assertIn("SAFETY RULES", prompt)
        self.assertIn("BEHAVIORAL GUIDELINES", prompt)

    def test_without_name(self):
        prompt = build_system_prompt()
        self.assertIn("helping a student learn", prompt)
        self.assertNotIn("named", prompt)

    def test_with_learner_name(self):
        prompt = build_system_prompt(learner_name="Alice")
        self.assertIn("named Alice", prompt)
        self.assertNotIn("helping a student learn", prompt)
