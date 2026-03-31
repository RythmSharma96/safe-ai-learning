from .base import AIAdapter, AIResponse


class MockAdapter(AIAdapter):
    """Deterministic mock adapter for testing and development."""

    RESPONSES = {
        "math": "Great question! Let's work through this math problem step by step. "
        "Remember, the key is to take it one piece at a time!",
        "science": "Science is fascinating! Here's what I know about that topic. "
        "The natural world is full of amazing patterns and processes.",
        "history": "That's an interesting history question! Let me share what I know. "
        "Understanding the past helps us make sense of the present.",
        "help": "Of course I can help! What specific topic would you like to explore? "
        "I'm here to learn together with you.",
    }

    DEFAULT_RESPONSE = (
        "That's a great question! Let me help you think about that. "
        "The best way to learn is to break things down into smaller pieces. "
        "What part would you like to start with?"
    )

    def generate_response(
        self,
        conversation_history: list[dict],
        system_prompt: str,
    ) -> AIResponse:
        last_message = (
            conversation_history[-1]["content"].lower() if conversation_history else ""
        )

        for keyword, response in self.RESPONSES.items():
            if keyword in last_message:
                return AIResponse(content=response, model="mock-v1")

        return AIResponse(content=self.DEFAULT_RESPONSE, model="mock-v1")
