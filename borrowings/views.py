from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReadSerializer,
    BorrowingReturnSerializer,
)


class BorrowingListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_value = is_active.lower()
            if is_active_value == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active_value == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset


class BorrowingRetrieveView(generics.RetrieveAPIView):
    serializer_class = BorrowingReadSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)


class BorrowingReturnView(generics.GenericAPIView):
    serializer_class = BorrowingReturnSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        borrowing = self.get_object()
        serializer = self.get_serializer(instance=borrowing, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            BorrowingReadSerializer(serializer.instance).data,
            status=status.HTTP_200_OK,
        )


