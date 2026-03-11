from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from book_service.models import Book
from borrowings.models import Borrowing
from users.models import CustomUser


class BorrowingApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )
        self.other_user = CustomUser.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )
        self.book = Book.objects.create(
            title="Clean Architecture",
            author="Robert C. Martin",
            inventory=3,
            daily_fee="2.50",
        )
        self.other_book = Book.objects.create(
            title="Domain-Driven Design",
            author="Eric Evans",
            inventory=2,
            daily_fee="3.00",
        )
        self.list_url = reverse("borrowings:borrowing-list")

    def test_authentication_is_required_for_borrowings(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_borrowing_and_inventory_decreases(self):
        self.client.force_authenticate(self.user)
        payload = {
            "book": self.book.id,
            "borrow_date": timezone.localdate().isoformat(),
            "expected_return_date": (
                timezone.localdate() + timedelta(days=7)
            ).isoformat(),
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.book.refresh_from_db()

        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(self.book.inventory, 2)
        self.assertIsNone(borrowing.actual_return_date)

    def test_create_borrowing_fails_when_inventory_is_zero(self):
        self.book.inventory = 0
        self.book.save(update_fields=["inventory"])
        self.client.force_authenticate(self.user)
        payload = {
            "book": self.book.id,
            "borrow_date": timezone.localdate().isoformat(),
            "expected_return_date": (
                timezone.localdate() + timedelta(days=7)
            ).isoformat(),
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["book"]), "Book inventory cannot be 0.")

    def test_non_admin_sees_only_own_borrowings(self):
        own_borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=5),
        )
        Borrowing.objects.create(
            book=self.other_book,
            user=self.other_user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_borrowing.id)
        self.assertEqual(response.data[0]["book"]["id"], self.book.id)

    def test_admin_can_filter_by_user_id(self):
        user_borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=5),
        )
        Borrowing.objects.create(
            book=self.other_book,
            user=self.other_user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.list_url, {"user_id": self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], user_borrowing.id)

    def test_is_active_filter_returns_only_not_returned_borrowings(self):
        active_borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=5),
        )
        Borrowing.objects.create(
            book=self.other_book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
            actual_return_date=timezone.localdate() + timedelta(days=1),
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url, {"is_active": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], active_borrowing.id)

    def test_non_admin_cannot_access_other_user_borrowing_detail(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.other_user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse("borrowings:borrowing-detail", args=[borrowing.id])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_return_borrowing_and_inventory_increases(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
        )
        self.book.inventory = 1
        self.book.save(update_fields=["inventory"])
        self.client.force_authenticate(self.user)

        response = self.client.post(
            reverse("borrowings:borrowing-return", args=[borrowing.id])
        )

        borrowing.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(borrowing.actual_return_date, timezone.localdate())
        self.assertEqual(self.book.inventory, 2)

    def test_cannot_return_borrowing_twice(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
            actual_return_date=timezone.localdate(),
        )
        self.client.force_authenticate(self.user)

        response = self.client.post(
            reverse("borrowings:borrowing-return", args=[borrowing.id])
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_cannot_return_other_user_borrowing(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.other_user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=3),
        )
        self.client.force_authenticate(self.user)

        response = self.client.post(
            reverse("borrowings:borrowing-return", args=[borrowing.id])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
