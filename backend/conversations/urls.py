from django.urls import path

from . import views

app_name = "conversations"

urlpatterns = [
    path(
        "",
        views.ConversationListCreateView.as_view(),
        name="list-create",
    ),
    path(
        "<int:pk>/",
        views.ConversationDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:conversation_id>/messages/",
        views.SendMessageView.as_view(),
        name="send-message",
    ),
    path(
        "flagged/",
        views.FlaggedConversationListView.as_view(),
        name="flagged-list",
    ),
    path(
        "flagged/<int:pk>/",
        views.FlaggedConversationDetailView.as_view(),
        name="flagged-detail",
    ),
]
