from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIResponse:
    """Response from an AI adapter."""

    content: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    finish_reason: str | None = None


class AIAdapterError(Exception):
    """Raised when the AI adapter fails to generate a response."""

    pass


class AIAdapter(ABC):
    """Abstract base class for AI adapters."""

    @abstractmethod
    def generate_response(
        self,
        conversation_history: list[dict],
        system_prompt: str,
    ) -> AIResponse:
        """Generate an AI response given conversation history and system prompt.

        Args:
            conversation_history: List of {"role": "user"|"assistant", "content": "..."}
            system_prompt: The system prompt to use.

        Returns:
            AIResponse with the generated content.

        Raises:
            AIAdapterError: On any failure.
        """
        ...
