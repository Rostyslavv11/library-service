from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from book_service.models import Book
from borrowings.models import Borrowing
from users.models import CustomUser


class Command(BaseCommand):
    help = "Seed demo books, users, and borrowings data."

    def handle(self, *args, **options):
        admin, _ = CustomUser.objects.get_or_create(
            email="admin@library.local",
            defaults={"is_staff": True, "is_superuser": True},
        )
        if not admin.has_usable_password():
            admin.set_password("admin12345")
            admin.save(update_fields=["password"])

        user, _ = CustomUser.objects.get_or_create(
            email="reader@library.local",
            defaults={"first_name": "Reader"},
        )
        if not user.has_usable_password():
            user.set_password("reader12345")
            user.save(update_fields=["password"])

        clean_code, _ = Book.objects.get_or_create(
            title="Clean Code",
            defaults={
                "author": "Robert C. Martin",
                "inventory": 3,
                "daily_fee": "1.75",
            },
        )
        ddd, _ = Book.objects.get_or_create(
            title="Domain-Driven Design",
            defaults={
                "author": "Eric Evans",
                "inventory": 2,
                "daily_fee": "2.10",
            },
        )

        today = timezone.localdate()

        Borrowing.objects.get_or_create(
            book=clean_code,
            user=user,
            borrow_date=today - timedelta(days=5),
            expected_return_date=today + timedelta(days=5),
        )
        Borrowing.objects.get_or_create(
            book=ddd,
            user=user,
            borrow_date=today - timedelta(days=12),
            expected_return_date=today - timedelta(days=2),
            actual_return_date=today - timedelta(days=1),
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded demo users, books, and borrowings."
            )
        )
