from .base import AIAdapter, AIAdapterError, AIResponse


def get_ai_adapter() -> AIAdapter:
    """Factory: return the configured AI adapter based on Django settings."""
    from django.conf import settings

    if settings.AI_ADAPTER == "openai":
        from .openai_adapter import OpenAIAdapter

        return OpenAIAdapter(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
        )

    from .mock_adapter import MockAdapter

    return MockAdapter()


__all__ = ["AIAdapter", "AIAdapterError", "AIResponse", "get_ai_adapter"]
