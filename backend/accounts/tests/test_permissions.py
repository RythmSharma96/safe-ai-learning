from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from accounts.permissions import IsLearner, IsTeacherOrAdmin

User = get_user_model()


class TestIsLearner(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsLearner()

    def test_learner_allowed(self):
        user = User(email="kid@test.com", role="learner")
        request = self.factory.get("/")
        request.user = user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_teacher_denied(self):
        user = User(email="teach@test.com", role="teacher")
        request = self.factory.get("/")
        request.user = user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_admin_denied(self):
        user = User(email="admin@test.com", role="admin")
        request = self.factory.get("/")
        request.user = user
        self.assertFalse(self.permission.has_permission(request, None))


class TestIsTeacherOrAdmin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsTeacherOrAdmin()

    def test_teacher_allowed(self):
        user = User(email="teach@test.com", role="teacher")
        request = self.factory.get("/")
        request.user = user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_admin_allowed(self):
        user = User(email="admin@test.com", role="admin")
        request = self.factory.get("/")
        request.user = user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_learner_denied(self):
        user = User(email="kid@test.com", role="learner")
        request = self.factory.get("/")
        request.user = user
        self.assertFalse(self.permission.has_permission(request, None))
