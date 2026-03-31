import logging

from django.conf import settings
from django.db import transaction

from ai import get_ai_adapter
from ai.base import AIAdapterError
from ai.prompts import build_system_prompt
from safety.checkers.keyword_checker import KeywordChecker
from safety.checkers.pipeline import SafetyPipeline
from safety.models import FlagCategory, ModerationResult

from .models import Conversation, Message

logger = logging.getLogger(__name__)

# Category-specific canned safe responses for flagged input
SAFE_RESPONSES = {
    "self_harm": (
        "I care about you and want you to be safe. If you're going through a tough time, "
        "please talk to a trusted adult like a parent, teacher, or school counselor. "
        "You can also call Kids Helpline at 1800 55 1800. "
        "I'm here to help you learn — let's focus on something positive together!"
    ),
    "pii_request": (
        "I'm not able to share or receive personal information like phone numbers, "
        "emails, or addresses. This is to keep everyone safe! "
        "Is there a learning topic I can help you with instead?"
    ),
    "sexual_content": (
        "That's not something I'm able to help with. "
        "Let's talk about something fun to learn instead! "
        "Do you have any questions about science, math, history, or another subject?"
    ),
    "manipulation": (
        "I want to make sure you stay safe. If anyone ever makes you feel uncomfortable "
        "or asks you to keep secrets from your parents or teachers, please tell a trusted adult. "
        "Now, what would you like to learn about today?"
    ),
    "moderation_unavailable": (
        "I need a moment — could you try asking your question again? "
        "I'm here to help you learn!"
    ),
}

DEFAULT_SAFE_RESPONSE = (
    "I'm not able to help with that, but I'd love to help you learn something new! "
    "What subject are you curious about?"
)

AI_FALLBACK_RESPONSE = (
    "I'm having a little trouble right now. Could you try asking in a different way? "
    "I'm here to help you learn!"
)


def _get_safety_pipeline() -> SafetyPipeline:
    """Build the safety pipeline based on settings."""
    checkers = [KeywordChecker()]

    if settings.SAFETY_USE_OPENAI_MODERATION:
        from safety.checkers.openai_moderation import OpenAIModerationChecker

        checkers.append(OpenAIModerationChecker(api_key=settings.OPENAI_API_KEY))

    return SafetyPipeline(checkers)


def _get_canned_response(categories: list[str]) -> str:
    """Get the most appropriate canned response based on flag categories."""
    priority = ["self_harm", "sexual_content", "pii_request", "manipulation"]
    for cat in priority:
        if cat in categories:
            return SAFE_RESPONSES[cat]

    if "moderation_unavailable" in categories:
        return SAFE_RESPONSES["moderation_unavailable"]

    return DEFAULT_SAFE_RESPONSE


def _build_conversation_history(conversation: Conversation) -> list[dict]:
    """Load all messages from the conversation as a list of dicts for the AI."""
    messages = conversation.messages.all()
    return [{"role": msg.role_string, "content": msg.content} for msg in messages]


def _save_moderation_result(message, moderation_outcome):
    """Save a ModerationResult with M2M flag categories."""
    result = ModerationResult.objects.create(
        message=message,
        is_flagged=moderation_outcome.is_flagged,
        flag_reasons=moderation_outcome.reasons,
        raw_scores=moderation_outcome.raw_scores,
        checker_results=moderation_outcome.checker_results,
    )
    if moderation_outcome.categories:
        categories = FlagCategory.objects.filter(name__in=moderation_outcome.categories)
        result.flag_categories.set(categories)
    return result


@transaction.atomic
def send_message(conversation: Conversation, content: str) -> dict:
    """Core orchestration: save message, run safety, generate AI response.

    Returns dict with user_message and assistant_message data.
    """
    logger.info(
        "[conv=%s] New message from learner: %s",
        conversation.id,
        content[:100],
    )
    pipeline = _get_safety_pipeline()

    # 1. Save user message
    user_message = Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content=content,
    )

    # 2. INPUT SCREENING
    input_moderation = pipeline.run(content)
    _save_moderation_result(user_message, input_moderation)
    logger.info(
        "[conv=%s] Input screening: flagged=%s categories=%s",
        conversation.id,
        input_moderation.is_flagged,
        input_moderation.categories,
    )

    # 3. If input flagged: canned response, skip AI
    if input_moderation.is_flagged:
        conversation.is_flagged = True
        conversation.save(update_fields=["is_flagged", "updated_at"])

        safe_content = _get_canned_response(input_moderation.categories)
        assistant_message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=safe_content,
        )
        ModerationResult.objects.create(
            message=assistant_message,
            is_flagged=False,
            flag_reasons=[],
            raw_scores={},
            checker_results=[],
        )
        logger.info(
            "[conv=%s] Input flagged — returned canned response, skipped AI",
            conversation.id,
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
        }

    # 4. Input is clean: generate AI response
    history = _build_conversation_history(conversation)
    system_prompt = build_system_prompt(
        learner_name=conversation.learner.first_name or None
    )

    try:
        adapter = get_ai_adapter()
        logger.info(
            "[conv=%s] Calling AI adapter (%s) with %d messages in history",
            conversation.id,
            adapter.__class__.__name__,
            len(history),
        )
        ai_response = adapter.generate_response(history, system_prompt)
        ai_content = ai_response.content
        logger.info(
            "[conv=%s] AI response received: model=%s tokens=%s/%s",
            conversation.id,
            ai_response.model,
            ai_response.prompt_tokens,
            ai_response.completion_tokens,
        )
    except AIAdapterError:
        logger.exception("AI adapter failed for conversation %s", conversation.id)
        ai_content = AI_FALLBACK_RESPONSE

    # 5. Save assistant message
    assistant_message = Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=ai_content,
    )

    # 6. OUTPUT SCREENING
    output_moderation = pipeline.run(ai_content)
    _save_moderation_result(assistant_message, output_moderation)
    logger.info(
        "[conv=%s] Output screening: flagged=%s categories=%s",
        conversation.id,
        output_moderation.is_flagged,
        output_moderation.categories,
    )

    # 7. If AI output flagged: replace with fallback, flag conversation
    if output_moderation.is_flagged:
        conversation.is_flagged = True
        conversation.save(update_fields=["is_flagged", "updated_at"])
        assistant_message._display_content = AI_FALLBACK_RESPONSE
        logger.info(
            "[conv=%s] AI output flagged — returning fallback to learner",
            conversation.id,
        )
    else:
        assistant_message._display_content = ai_content

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
    }
