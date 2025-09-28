import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

pytestmark = pytest.mark.django_db


def test_non_staff_sees_only_own_payments():
    u1 = User.objects.create_user(email="u1@u.com", password="12345")
    u2 = User.objects.create_user(email="u2@u.com", password="12345")
    book = Book.objects.create(title="T", author="A", cover="HARD", inventory=1, daily_fee="1.00")
    b1 = Borrowing.objects.create(user=u1, book=book, expected_return_date=None)
    b2 = Borrowing.objects.create(user=u2, book=book, expected_return_date=None)
    Payment.objects.create(borrowing=b1, money_to_pay="1.00")
    Payment.objects.create(borrowing=b2, money_to_pay="1.00")

    client = APIClient()
    client.force_authenticate(u1)
    url = reverse("payments-list")
    res = client.get(url)
    assert res.status_code == 200
    assert all(p["borrowing"] == b1.id for p in res.data)
