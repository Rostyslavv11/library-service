from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser

from book_service.models import Book
from book_service.serializers import BookListSerializer, BookDetailSerializer, BookCreateSerializer


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BookCreateSerializer
        return BookListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]
