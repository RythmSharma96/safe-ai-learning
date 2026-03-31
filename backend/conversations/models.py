from django.conf import settings
from django.db import models


class Conversation(models.Model):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    is_flagged = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id} ({self.learner.email})"


class Message(models.Model):
    class Role(models.IntegerChoices):
        USER = 0, "User"
        ASSISTANT = 1, "Assistant"
        SYSTEM = 2, "System"

    # Mapping from integer role to OpenAI-compatible string
    ROLE_TO_STRING = {0: "user", 1: "assistant", 2: "system"}

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.SmallIntegerField(choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"

    @property
    def role_string(self):
        """Return OpenAI-compatible role string."""
        return self.ROLE_TO_STRING.get(self.role, "user")
