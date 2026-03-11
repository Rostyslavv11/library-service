from django.urls import path

from borrowings.views import (
    BorrowingListCreateView,
    BorrowingRetrieveView,
    BorrowingReturnView,
)

urlpatterns = [
    path("", BorrowingListCreateView.as_view(), name="borrowing-list"),
    path("<int:pk>/", BorrowingRetrieveView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return/", BorrowingReturnView.as_view(), name="borrowing-return"),
]

app_name = "borrowings"
