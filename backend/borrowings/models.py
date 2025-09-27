from django.db import models
from django.utils import timezone
from users.models import User
from books.models import Book


class Borrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowings")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    borrow_date = models.DateField(default=timezone.now)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-borrow_date"]

    @property
    def is_active(self) -> bool:
        return self.actual_return_date is None
