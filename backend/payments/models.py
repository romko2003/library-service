from django.db import models
from borrowings.models import Borrowing


class Payment(models.Model):
    PENDING, PAID, EXPIRED = "PENDING","PAID","EXPIRED"
    PAYMENT, FINE = "PAYMENT","FINE"

    status = models.CharField(max_length=10, choices=[(PENDING,PENDING),(PAID,PAID),(EXPIRED,EXPIRED)], default=PENDING)
    type = models.CharField(max_length=10, choices=[(PAYMENT,PAYMENT),(FINE,FINE)], default=PAYMENT)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name="payments")

    session_url = models.URLField(null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
