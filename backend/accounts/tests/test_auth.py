from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class TestSignup(APITestCase):
    def test_signup_learner(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "kid@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "Kid",
                "role": "learner",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "learner")
        self.assertEqual(response.data["email"], "kid@example.com")
        self.assertTrue(User.objects.filter(email="kid@example.com").exists())

    def test_signup_teacher(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "teacher@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "Teacher",
                "role": "teacher",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "teacher")

    def test_signup_admin_rejected(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "admin@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "Admin",
                "role": "admin",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="kid@example.com",
            password="testpass123",
        )
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "kid@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "Kid",
                "role": "learner",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestLogin(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="learner",
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "test@example.com", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "test@example.com", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestMe(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="learner",
            first_name="Test",
        )

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["role"], "learner")

    def test_me_unauthenticated(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
