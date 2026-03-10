from django.urls import path

from book_service.views import BookListCreateView, BookRetrieveUpdateDestroyView

urlpatterns = [
    path("", BookListCreateView.as_view(), name="book_list_create"),
    path("<int:pk>/", BookRetrieveUpdateDestroyView.as_view(), name="book_detail")
]

app_name = "book_service"