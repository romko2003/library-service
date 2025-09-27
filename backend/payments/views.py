import os
import stripe
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Payment.objects.select_related("borrowing","borrowing__user")
        return qs if self.request.user.is_staff else qs.filter(borrowing__user=self.request.user)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Payment.objects.select_related("borrowing","borrowing__user")
        return qs if self.request.user.is_staff else qs.filter(borrowing__user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def success(request):
    session_id = request.query_params.get("session_id")
    if not session_id:
        return Response({"detail":"session_id required"}, status=400)
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    session = stripe.checkout.Session.retrieve(session_id)
    payment = get_object_or_404(Payment, session_id=session_id)
    if session.get("payment_status") == "paid":
        payment.status = Payment.PAID
        payment.save(update_fields=["status"])
        return Response({"status":"paid"})
    return Response({"status":"not paid yet"}, status=202)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def cancel(_request):
    return Response({"message":"Payment can be made later. Session valid ~24h."})
