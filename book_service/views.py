from rest_framework import generics
from book_service.models import Book
from book_service.serializers import BookListSerializer, BookDetailSerializer, BookCreateSerializer


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    def get_serializer_class(self):
        if self.request.method == "POST":
            return BookCreateSerializer
        return BookListSerializer


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer

