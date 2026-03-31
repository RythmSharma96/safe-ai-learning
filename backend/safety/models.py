from django.db import models


class FlagCategory(models.Model):
    """Constrained set of flag categories used by the safety pipeline."""

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "flag categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    # Canonical category names — used by checkers and seed data
    SELF_HARM = "self_harm"
    SEXUAL_CONTENT = "sexual_content"
    PII_REQUEST = "pii_request"
    MANIPULATION = "manipulation"
    HARM_CONTENT = "harm_content"
    MODERATION_UNAVAILABLE = "moderation_unavailable"


class ModerationResult(models.Model):
    message = models.OneToOneField(
        "conversations.Message",
        on_delete=models.CASCADE,
        related_name="moderation_result",
    )
    is_flagged = models.BooleanField(default=False, db_index=True)
    flag_categories = models.ManyToManyField(FlagCategory, blank=True)
    flag_reasons = models.JSONField(default=list)
    raw_scores = models.JSONField(default=dict)
    checker_results = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "FLAGGED" if self.is_flagged else "clean"
        return f"Moderation {self.id} [{status}]"
