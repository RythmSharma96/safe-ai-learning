from rest_framework import generics, status
from rest_framework.response import Response

from accounts.permissions import IsLearner, IsTeacherOrAdmin

from . import services
from .models import Conversation
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    CreateConversationSerializer,
    FlaggedConversationDetailSerializer,
    FlaggedConversationListSerializer,
    SendMessageResponseSerializer,
    SendMessageSerializer,
)


class ConversationListCreateView(generics.ListCreateAPIView):
    """List own conversations (GET) or create a new one (POST). Learner only."""

    permission_classes = [IsLearner]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateConversationSerializer
        return ConversationListSerializer

    def get_queryset(self):
        return Conversation.objects.filter(learner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(learner=self.request.user)


class ConversationDetailView(generics.RetrieveAPIView):
    """Retrieve a conversation with its messages. Owner (learner) only."""

    serializer_class = ConversationDetailSerializer
    permission_classes = [IsLearner]

    def get_queryset(self):
        return Conversation.objects.filter(learner=self.request.user).prefetch_related(
            "messages__moderation_result"
        )


class SendMessageView(generics.CreateAPIView):
    """Send a message in a conversation and get an AI response. Owner only."""

    serializer_class = SendMessageSerializer
    permission_classes = [IsLearner]

    def get_conversation(self):
        return Conversation.objects.get(
            id=self.kwargs["conversation_id"],
            learner=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = self.get_conversation()
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = services.send_message(
            conversation=conversation,
            content=serializer.validated_data["content"],
        )

        response_serializer = SendMessageResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class FlaggedConversationListView(generics.ListAPIView):
    """List all flagged conversations. Teacher/Admin only."""

    serializer_class = FlaggedConversationListSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return Conversation.objects.filter(is_flagged=True).select_related("learner")


class FlaggedConversationDetailView(generics.RetrieveAPIView):
    """Retrieve a flagged conversation with full moderation details. Teacher/Admin only."""

    serializer_class = FlaggedConversationDetailSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return (
            Conversation.objects.filter(is_flagged=True)
            .select_related("learner")
            .prefetch_related("messages__moderation_result")
        )
