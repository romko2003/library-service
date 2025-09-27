from django.db import models


class Book(models.Model):
    HARD, SOFT = "HARD", "SOFT"
    COVER_CHOICES = [(HARD, HARD), (SOFT, SOFT)]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=10, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self): return f"{self.title} — {self.author}"
