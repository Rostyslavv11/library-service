from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


class UserApiTests(APITestCase):
    def setUp(self):
        self.password = "testpass123"
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Initial",
        )
        self.create_url = reverse("users:user-create")
        self.me_url = reverse("users:my-profile")
        self.token_url = reverse("users:token_obtain_pair")

    def test_user_can_register(self):
        payload = {
            "email": "new@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(self.create_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email=payload["email"]).exists())
        self.assertNotIn("password", response.data)

    def test_user_can_get_profile_with_authorize_header(self):
        token_response = self.client.post(
            self.token_url,
            {"email": self.user.email, "password": self.password},
            format="json",
        )

        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZE=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_authentication_is_required_for_profile(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_patch_own_profile(self):
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            self.me_url,
            {"first_name": "Updated", "password": "changedpass123"},
            format="json",
        )

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, "Updated")
        self.assertTrue(self.user.check_password("changedpass123"))
