from unittest.mock import MagicMock

from django.test import TestCase, override_settings

from ai import get_ai_adapter
from ai.base import AIAdapterError
from ai.mock_adapter import MockAdapter
from ai.openai_adapter import OpenAIAdapter


class TestMockAdapter(TestCase):
    def setUp(self):
        self.adapter = MockAdapter()

    def test_returns_math_response(self):
        result = self.adapter.generate_response(
            [{"role": "user", "content": "What is 2+2 in math?"}],
            "system prompt",
        )
        self.assertIn("math", result.content.lower())
        self.assertEqual(result.model, "mock-v1")

    def test_returns_default_response(self):
        result = self.adapter.generate_response(
            [{"role": "user", "content": "Tell me something interesting"}],
            "system prompt",
        )
        self.assertIn("great question", result.content.lower())

    def test_handles_empty_history(self):
        result = self.adapter.generate_response([], "system prompt")
        self.assertTrue(len(result.content) > 0)


class TestOpenAIAdapter(TestCase):
    def test_retry_on_timeout(self):
        adapter = OpenAIAdapter(api_key="test-key", max_retries=1)
        import openai

        adapter.client = MagicMock()
        adapter.client.chat.completions.create.side_effect = openai.APITimeoutError(
            request=MagicMock()
        )

        with self.assertRaises(AIAdapterError) as ctx:
            adapter.generate_response([{"role": "user", "content": "hello"}], "system")
        self.assertIn("2 attempts", str(ctx.exception))

    def test_no_retry_on_api_error(self):
        adapter = OpenAIAdapter(api_key="test-key", max_retries=2)
        import openai

        adapter.client = MagicMock()
        adapter.client.chat.completions.create.side_effect = openai.BadRequestError(
            message="bad request",
            response=MagicMock(status_code=400),
            body=None,
        )

        with self.assertRaises(AIAdapterError):
            adapter.generate_response([{"role": "user", "content": "hello"}], "system")
        # Should only have been called once (no retry)
        self.assertEqual(adapter.client.chat.completions.create.call_count, 1)


class TestGetAIAdapter(TestCase):
    @override_settings(AI_ADAPTER="mock")
    def test_returns_mock_adapter(self):
        adapter = get_ai_adapter()
        self.assertIsInstance(adapter, MockAdapter)

    @override_settings(
        AI_ADAPTER="openai", OPENAI_API_KEY="test-key", OPENAI_MODEL="gpt-4o-mini"
    )
    def test_returns_openai_adapter(self):
        adapter = get_ai_adapter()
        self.assertIsInstance(adapter, OpenAIAdapter)
