import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from books.models import Book

pytestmark = pytest.mark.django_db


def test_public_can_list_books():
    Book.objects.create(title="T1", author="A", cover="HARD", inventory=2, daily_fee="1.00")
    url = reverse("books-list")
    client = APIClient()
    res = client.get(url)
    assert res.status_code == 200
    assert len(res.data) >= 1


def test_non_staff_cannot_create_book():
    user = User.objects.create_user(email="u@u.com", password="12345")
    client = APIClient()
    client.force_authenticate(user)
    url = reverse("books-list")
    payload = {"title":"New","author":"A","cover":"HARD","inventory":1,"daily_fee":"2.00"}
    res = client.post(url, payload, format="json")
    assert res.status_code in (401, 403)


def test_staff_can_create_book():
    admin = User.objects.create_superuser(email="admin@a.com", password="12345")
    client = APIClient()
    client.force_authenticate(admin)
    url = reverse("books-list")
    payload = {"title":"New","author":"A","cover":"HARD","inventory":1,"daily_fee":"2.00"}
    res = client.post(url, payload, format="json")
    assert res.status_code == 201
