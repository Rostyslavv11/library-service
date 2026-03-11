from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from book_service.serializers import BookDetailSerializer
from book_service.models import Book
from borrowings.models import Borrowing


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )
        read_only_fields = fields


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date")
        read_only_fields = ("id",)

    def validate_borrow_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Borrow date cannot be in the future.")
        return value

    def validate(self, attrs):
        borrow_date = attrs.get("borrow_date", timezone.localdate())
        expected_return_date = attrs["expected_return_date"]

        if expected_return_date < borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return_date": (
                        "Expected return date must be greater than or equal to borrow date."
                    )
                }
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        book = (
            Book.objects.select_for_update()
            .only("id", "inventory")
            .get(id=validated_data["book"].id)
        )

        if book.inventory == 0:
            raise serializers.ValidationError(
                {"book": "Book inventory cannot be 0."}
            )

        Book.objects.filter(id=book.id).update(inventory=F("inventory") - 1)

        return Borrowing.objects.create(
            **validated_data,
            user=self.context["request"].user,
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError(
                {"actual_return_date": "Borrowing is already returned."}
            )
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        borrowing = (
            Borrowing.objects.select_for_update()
            .select_related("book")
            .get(pk=self.instance.pk)
        )

        if borrowing.actual_return_date is not None:
            raise serializers.ValidationError(
                {"actual_return_date": "Borrowing is already returned."}
            )

        borrowing.actual_return_date = timezone.localdate()
        borrowing.full_clean()
        borrowing.save(update_fields=["actual_return_date"])
        Book.objects.filter(id=borrowing.book_id).update(inventory=F("inventory") + 1)

        borrowing.refresh_from_db()
        return borrowing
