from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Borrowing(models.Model):
    borrow_date = models.DateField(default=timezone.localdate)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        "book_service.Book",
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(expected_return_date__isnull=True)
                    | Q(expected_return_date__gte=F("borrow_date"))
                ) & (
                    Q(actual_return_date__isnull=True)
                    | Q(actual_return_date__gte=F("borrow_date"))
                ),
                name="borrowing_dates_are_valid",
            )
        ]
        ordering = ["-borrow_date", "-id"]

    def clean(self):
        errors = {}

        if self.borrow_date and self.borrow_date > timezone.localdate():
            errors["borrow_date"] = "Borrow date cannot be in the future."

        if (
            self.borrow_date
            and self.expected_return_date
            and self.expected_return_date < self.borrow_date
        ):
            errors["expected_return_date"] = (
                "Expected return date must be greater than or equal to borrow date."
            )

        if (
            self.borrow_date
            and self.actual_return_date
            and self.actual_return_date < self.borrow_date
        ):
            errors["actual_return_date"] = (
                "Actual return date must be greater than or equal to borrow date."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Borrowing {self.id}"
