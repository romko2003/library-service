from rest_framework import serializers
from .models import Borrowing
from books.serializers import BookSerializer
from books.models import Book


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id","user","book","borrow_date","expected_return_date","actual_return_date","is_active")
        read_only_fields = ("user",)


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id","book","expected_return_date")

    def validate(self, attrs):
        book: Book = attrs["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is out of stock")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        borrowing = Borrowing.objects.create(user=request.user, **validated_data)
        book = borrowing.book
        book.inventory -= 1
        book.save(update_fields=["inventory"])

        # Стартова оплата
        from payments.utils import create_initial_payment_for_borrowing
        create_initial_payment_for_borrowing(borrowing)
        return borrowing
