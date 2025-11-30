from decimal import Decimal
from app.models import Coupons, PaymentMethods, CartItems, Deliveries


def test_create_delivery_with_skip_puzzle_applies_coupon(app, sample_customer, sample_product, sample_payment_method, sample_customer_showing):
    # Setup: create coupon and add cart items for the customer
    from app.services.customer_service import CustomerService
    from app.app import db

    with app.app_context():
        # coupon worth 20%
        c = Coupons(code='SKIPME', difficulty=1, discount_percent=20.0, is_active=True)
        db.session.add(c)
        db.session.commit()

        # add cart item for customer
        ci = CartItems(customer_id=sample_customer, product_id=sample_product, quantity=2)
        db.session.add(ci)
        db.session.commit()

    svc = CustomerService()
    pm_before = PaymentMethods.query.get(sample_payment_method)
    bal_before = Decimal(pm_before.balance)

    delivery = svc.create_delivery(customer_showing_id=sample_customer_showing, payment_method_id=sample_payment_method, coupon_code='SKIPME', puzzle_token=None, puzzle_answer=None, skip_puzzle=True)

    assert isinstance(delivery, Deliveries)
    # discount_amount should be persisted on delivery
    assert delivery.coupon_code == 'SKIPME'
    assert delivery.discount_amount is not None

    pm_after = PaymentMethods.query.get(sample_payment_method)
    # total charged should be post-discount: original total - discount
    assert Decimal(pm_after.balance) < bal_before
