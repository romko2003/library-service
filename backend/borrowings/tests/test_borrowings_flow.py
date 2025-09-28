import pytest
from datetime import date, timedelta
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from books.models import Book
from borrowings.models import Borrowing

pytestmark = pytest.mark.django_db


def test_create_borrowing_decrements_inventory(monkeypatch):
    # Stub out Stripe session creation to keep test offline
    from payments import utils as pay_utils
    monkeypatch.setattr(pay_utils, "create_initial_payment_for_borrowing", lambda b: None)

    user = User.objects.create_user(email="u@u.com", password="12345")
    book = Book.objects.create(title="T", author="A", cover="HARD", inventory=2, daily_fee="1.50")

    client = APIClient()
    client.force_authenticate(user)

    url = reverse("borrowings-list")
    payload = {"book": book.id, "expected_return_date": (date.today() + timedelta(days=3)).isoformat()}
    res = client.post(url, payload, format="json")
    assert res.status_code == 201

    book.refresh_from_db()
    assert book.inventory == 1


def test_cannot_borrow_when_no_inventory(monkeypatch):
    from payments import utils as pay_utils
    monkeypatch.setattr(pay_utils, "create_initial_payment_for_borrowing", lambda b: None)

    user = User.objects.create_user(email="u@u.com", password="12345")
    book = Book.objects.create(title="T", author="A", cover="HARD", inventory=0, daily_fee="1.00")

    client = APIClient()
    client.force_authenticate(user)
    url = reverse("borrowings-list")
    payload = {"book": book.id, "expected_return_date": (date.today() + timedelta(days=2)).isoformat()}
    res = client.post(url, payload, format="json")
    assert res.status_code == 400


def test_return_increments_inventory(monkeypatch):
    from payments import utils as pay_utils
    monkeypatch.setattr(pay_utils, "create_initial_payment_for_borrowing", lambda b: None)
    monkeypatch.setattr(pay_utils, "create_fine_payment_for_borrowing", lambda b: None)

    user = User.objects.create_user(email="u@u.com", password="12345")
    book = Book.objects.create(title="T", author="A", cover="HARD", inventory=1, daily_fee="1.00")
    borrowing = Borrowing.objects.create(
        user=user, book=book, expected_return_date=date.today() + timedelta(days=2)
    )
    book.inventory -= 1; book.save()

    client = APIClient()
    client.force_authenticate(user)
    url = reverse("borrowings-return", kwargs={"pk": borrowing.id})
    res = client.post(url)
    assert res.status_code == 200

    book.refresh_from_db()
    assert book.inventory == 1


def test_non_staff_sees_only_own_borrowings(api_client=None):
    client = APIClient()
    u1 = User.objects.create_user(email="u1@u.com", password="12345")
    u2 = User.objects.create_user(email="u2@u.com", password="12345")
    book = Book.objects.create(title="T", author="A", cover="HARD", inventory=5, daily_fee="1.00")
    Borrowing.objects.create(user=u1, book=book, expected_return_date=date.today())
    Borrowing.objects.create(user=u2, book=book, expected_return_date=date.today())

    client.force_authenticate(u1)
    url = reverse("borrowings-list")
    res = client.get(url)
    assert res.status_code == 200
    assert all(item["user"] == u1.id for item in res.data)
