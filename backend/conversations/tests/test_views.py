from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from conversations.models import Conversation
from safety.models import ModerationResult

User = get_user_model()


class TestConversationListCreate(APITestCase):
    def setUp(self):
        call_command("seed_flag_categories", verbosity=0)
        self.learner = User.objects.create_user(
            username="kid", email="kid@test.com", password="pass1234", role="learner"
        )
        self.teacher = User.objects.create_user(
            username="teach",
            email="teach@test.com",
            password="pass1234",
            role="teacher",
        )

    def test_learner_can_create_conversation(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.post(
            "/api/conversations/",
            {"title": "Help with math"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Help with math")

    def test_learner_can_list_own_conversations(self):
        self.client.force_authenticate(user=self.learner)
        Conversation.objects.create(learner=self.learner, title="Convo 1")
        Conversation.objects.create(learner=self.learner, title="Convo 2")
        response = self.client.get("/api/conversations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_learner_cannot_see_other_learner_conversations(self):
        other = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="pass1234",
            role="learner",
        )
        Conversation.objects.create(learner=other, title="Other's convo")
        self.client.force_authenticate(user=self.learner)
        response = self.client.get("/api/conversations/")
        self.assertEqual(response.data["count"], 0)

    def test_teacher_cannot_create_conversation(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            "/api/conversations/",
            {"title": "Teacher convo"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_rejected(self):
        response = self.client.post(
            "/api/conversations/",
            {"title": "No auth"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestSendMessage(APITestCase):
    """Integration tests for the core send message flow."""

    def setUp(self):
        call_command("seed_flag_categories", verbosity=0)
        self.learner = User.objects.create_user(
            username="kid", email="kid@test.com", password="pass1234", role="learner"
        )
        self.conversation = Conversation.objects.create(
            learner=self.learner, title="Test"
        )
        self.client.force_authenticate(user=self.learner)

    def test_send_clean_message(self):
        response = self.client.post(
            f"/api/conversations/{self.conversation.id}/messages/",
            {"content": "What is 2 + 2?"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_message", response.data)
        self.assertIn("assistant_message", response.data)
        self.assertFalse(response.data["user_message"]["moderation"]["is_flagged"])
        # Verify DB state
        self.assertEqual(self.conversation.messages.count(), 2)
        self.assertEqual(ModerationResult.objects.count(), 2)

    def test_send_flagged_message_self_harm(self):
        response = self.client.post(
            f"/api/conversations/{self.conversation.id}/messages/",
            {"content": "I want to hurt myself"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["user_message"]["moderation"]["is_flagged"])
        self.assertIn(
            "self_harm",
            response.data["user_message"]["moderation"]["flag_categories"],
        )
        # Canned response should mention trusted adult / helpline
        assistant_content = response.data["assistant_message"]["content"]
        self.assertIn("trusted adult", assistant_content.lower())
        # Conversation should be flagged
        self.conversation.refresh_from_db()
        self.assertTrue(self.conversation.is_flagged)

    def test_send_flagged_message_pii(self):
        response = self.client.post(
            f"/api/conversations/{self.conversation.id}/messages/",
            {"content": "My email is kid@gmail.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["user_message"]["moderation"]["is_flagged"])

    def test_cannot_send_to_other_learner_conversation(self):
        other = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="pass1234",
            role="learner",
        )
        other_convo = Conversation.objects.create(learner=other, title="Other's")
        response = self.client.post(
            f"/api/conversations/{other_convo.id}/messages/",
            {"content": "Hello"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_message_rejected(self):
        response = self.client.post(
            f"/api/conversations/{self.conversation.id}/messages/",
            {"content": ""},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_role_returned_as_string(self):
        """Verify API returns role as 'user'/'assistant' strings, not integers."""
        response = self.client.post(
            f"/api/conversations/{self.conversation.id}/messages/",
            {"content": "What is gravity?"},
        )
        self.assertEqual(response.data["user_message"]["role"], "user")
        self.assertEqual(response.data["assistant_message"]["role"], "assistant")


class TestConversationDetail(APITestCase):
    def setUp(self):
        call_command("seed_flag_categories", verbosity=0)
        self.learner = User.objects.create_user(
            username="kid", email="kid@test.com", password="pass1234", role="learner"
        )
        self.conversation = Conversation.objects.create(
            learner=self.learner, title="Test"
        )
        self.client.force_authenticate(user=self.learner)

    def test_get_conversation_with_messages(self):
        self.client.post(
            f"/api/conversations/{self.conversation.id}/messages/",
            {"content": "What is gravity?"},
        )
        response = self.client.get(f"/api/conversations/{self.conversation.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["messages"]), 2)


class TestFlaggedEndpoints(APITestCase):
    def setUp(self):
        call_command("seed_flag_categories", verbosity=0)
        self.learner = User.objects.create_user(
            username="kid", email="kid@test.com", password="pass1234", role="learner"
        )
        self.teacher = User.objects.create_user(
            username="teach",
            email="teach@test.com",
            password="pass1234",
            role="teacher",
        )
        self.conversation = Conversation.objects.create(
            learner=self.learner, title="Test", is_flagged=True
        )

    def test_teacher_can_list_flagged(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get("/api/conversations/flagged/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_can_view_flagged_detail(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(
            f"/api/conversations/flagged/{self.conversation.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_learner_cannot_access_flagged_list(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.get("/api/conversations/flagged/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_learner_cannot_access_flagged_detail(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(
            f"/api/conversations/flagged/{self.conversation.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_flagged(self):
        response = self.client.get("/api/conversations/flagged/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
