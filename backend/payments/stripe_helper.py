import os
import stripe
from decimal import Decimal

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_session(*, name: str, amount_usd: Decimal):
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": name},
                "unit_amount": int(Decimal(amount_usd) * 100),
            },
            "quantity": 1,
        }],
        success_url=os.getenv("FRONTEND_SUCCESS_URL"),
        cancel_url=os.getenv("FRONTEND_CANCEL_URL"),
    )
    return session
