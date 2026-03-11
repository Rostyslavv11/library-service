from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book_service.models import Book
from users.models import CustomUser


class BookApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )
        self.admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )
        self.book = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andy Hunt",
            cover=Book.CoverChoices.SOFT,
            inventory=5,
            daily_fee="1.50",
        )
        self.list_url = reverse("book_service:book_list_create")

    def test_anyone_can_list_books(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_admin_cannot_create_book(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.list_url,
            {
                "title": "Refactoring",
                "author": "Martin Fowler",
                "cover": Book.CoverChoices.HARD,
                "inventory": 4,
                "daily_fee": "2.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "title": "Refactoring",
                "author": "Martin Fowler",
                "cover": Book.CoverChoices.HARD,
                "inventory": 4,
                "daily_fee": "2.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title="Refactoring").exists())

    def test_non_admin_cannot_update_or_delete_book(self):
        self.client.force_authenticate(self.user)
        detail_url = reverse("book_service:book_detail", args=[self.book.id])

        patch_response = self.client.patch(
            detail_url, {"inventory": 2}, format="json"
        )
        delete_response = self.client.delete(detail_url)

        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_book_inventory(self):
        self.client.force_authenticate(self.admin)
        detail_url = reverse("book_service:book_detail", args=[self.book.id])

        response = self.client.patch(detail_url, {"inventory": 2}, format="json")

        self.book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book.inventory, 2)
