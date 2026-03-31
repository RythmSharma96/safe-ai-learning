import logging

import openai

from .base import AIAdapter, AIAdapterError, AIResponse

logger = logging.getLogger(__name__)


class OpenAIAdapter(AIAdapter):
    """Real OpenAI ChatCompletion adapter."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: int = 30,
        max_retries: int = 2,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ):
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response(
        self,
        conversation_history: list[dict],
        system_prompt: str,
    ) -> AIResponse:
        messages = [{"role": "system", "content": system_prompt}] + conversation_history

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                choice = response.choices[0]
                return AIResponse(
                    content=choice.message.content,
                    model=response.model,
                    prompt_tokens=response.usage.prompt_tokens
                    if response.usage
                    else None,
                    completion_tokens=response.usage.completion_tokens
                    if response.usage
                    else None,
                    finish_reason=choice.finish_reason,
                )
            except (openai.APITimeoutError, openai.APIConnectionError) as e:
                last_error = e
                logger.warning(
                    "OpenAI transient error (attempt %d/%d): %s",
                    attempt + 1,
                    self.max_retries + 1,
                    e,
                )
                continue
            except openai.APIError as e:
                raise AIAdapterError(f"OpenAI API error: {e}") from e

        raise AIAdapterError(
            f"OpenAI API failed after {self.max_retries + 1} attempts: {last_error}"
        )
