from django.urls import path
from .views import PaymentListView, PaymentDetailView, success, cancel

urlpatterns = [
    path("", PaymentListView.as_view(), name="payments-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payments-detail"),
    path("success/", success, name="payments-success"),
    path("cancel/", cancel, name="payments-cancel"),
]
