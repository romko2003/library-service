from django.urls import path
from .views import BorrowingListCreateView, BorrowingDetailView, return_borrowing

urlpatterns = [
    path("", BorrowingListCreateView.as_view(), name="borrowings-list"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowings-detail"),
    path("<int:pk>/return/", return_borrowing, name="borrowings-return"),
]
