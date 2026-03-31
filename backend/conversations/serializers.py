from rest_framework import serializers

from safety.models import ModerationResult

from .models import Conversation, Message


class ModerationResultSerializer(serializers.ModelSerializer):
    flag_categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = ModerationResult
        fields = [
            "is_flagged",
            "flag_categories",
            "flag_reasons",
        ]


class ModerationDetailSerializer(serializers.ModelSerializer):
    """Full moderation details for teacher review."""

    flag_categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = ModerationResult
        fields = [
            "is_flagged",
            "flag_categories",
            "flag_reasons",
            "raw_scores",
            "checker_results",
            "created_at",
        ]


class MessageSerializer(serializers.ModelSerializer):
    moderation = ModerationResultSerializer(source="moderation_result", read_only=True)
    role = serializers.CharField(source="role_string", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at", "moderation"]


class MessageDetailSerializer(serializers.ModelSerializer):
    """Message with full moderation details for teacher review."""

    moderation = ModerationDetailSerializer(source="moderation_result", read_only=True)
    role = serializers.CharField(source="role_string", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at", "moderation"]


class ConversationListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "is_flagged",
            "message_count",
            "created_at",
            "updated_at",
        ]

    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "is_flagged",
            "created_at",
            "updated_at",
            "messages",
        ]


class CreateConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at"]
        read_only_fields = ["id", "created_at"]


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000, min_length=1)


class SendMessageResponseSerializer(serializers.Serializer):
    """Response shape for the send message endpoint."""

    user_message = MessageSerializer()
    assistant_message = serializers.SerializerMethodField()

    def get_assistant_message(self, obj):
        msg = obj["assistant_message"]
        data = MessageSerializer(msg).data
        if hasattr(msg, "_display_content"):
            data["content"] = msg._display_content
        return data


class FlaggedConversationListSerializer(serializers.ModelSerializer):
    learner_email = serializers.CharField(source="learner.email", read_only=True)
    flag_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "learner_email",
            "title",
            "is_flagged",
            "flag_count",
            "created_at",
            "updated_at",
        ]

    def get_flag_count(self, obj):
        return obj.messages.filter(moderation_result__is_flagged=True).count()


class FlaggedConversationDetailSerializer(serializers.ModelSerializer):
    learner_email = serializers.CharField(source="learner.email", read_only=True)
    messages = MessageDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "learner_email",
            "title",
            "is_flagged",
            "created_at",
            "updated_at",
            "messages",
        ]
