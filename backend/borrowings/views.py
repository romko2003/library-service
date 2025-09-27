from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Borrowing
from .serializers import BorrowingReadSerializer, BorrowingCreateSerializer
from .filters import BorrowingFilter
from payments.utils import create_fine_payment_for_borrowing


class BorrowingListCreateView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related("book","user").all()
    filterset_class = BorrowingFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return BorrowingCreateSerializer if self.request.method == "POST" else BorrowingReadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        # admin може фільтрувати user_id у FilterSet
        return qs


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related("book","user")
    serializer_class = BorrowingReadSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def return_borrowing(request, pk: int):
    borrowing = get_object_or_404(Borrowing, pk=pk)
    if not (request.user.is_staff or borrowing.user_id == request.user.id):
        return Response(status=status.HTTP_403_FORBIDDEN)
    if borrowing.actual_return_date:
        return Response({"detail":"Already returned"}, status=400)

    from django.utils.timezone import now
    borrowing.actual_return_date = now().date()
    borrowing.save(update_fields=["actual_return_date"])

    book = borrowing.book
    book.inventory += 1
    book.save(update_fields=["inventory"])

    if borrowing.actual_return_date > borrowing.expected_return_date:
        create_fine_payment_for_borrowing(borrowing)

    return Response({"status":"returned"}, status=200)
