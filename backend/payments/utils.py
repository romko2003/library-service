from decimal import Decimal
from django.conf import settings
from django.utils.timezone import now
from .models import Payment
from .stripe_helper import create_session
from borrowings.models import Borrowing


def _days_between(d1, d2):
    return (d2 - d1).days if d2 >= d1 else 0


def create_initial_payment_for_borrowing(borrowing: Borrowing) -> Payment:
    days = _days_between(borrowing.borrow_date, borrowing.expected_return_date)
    amount = Decimal(days) * borrowing.book.daily_fee
    session = create_session(
        name=f"Borrowing #{borrowing.id} — {borrowing.book.title}",
        amount_usd=amount,
    )
    return Payment.objects.create(
        borrowing=borrowing, type=Payment.PAYMENT, money_to_pay=amount,
        session_id=session.id, session_url=session.url
    )


def create_fine_payment_for_borrowing(borrowing: Borrowing) -> Payment:
    overdue_days = _days_between(borrowing.expected_return_date, borrowing.actual_return_date or now().date())
    multiplier = getattr(settings, "FINE_MULTIPLIER", 2)
    amount = borrowing.book.daily_fee * overdue_days * multiplier
    session = create_session(
        name=f"FINE for Borrowing #{borrowing.id}",
        amount_usd=amount,
    )
    return Payment.objects.create(
        borrowing=borrowing, type=Payment.FINE, money_to_pay=amount,
        session_id=session.id, session_url=session.url
    )
