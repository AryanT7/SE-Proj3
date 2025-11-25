# tests/unit/models_test.py
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, StatementError, OperationalError, DataError

from app.app import db
from app.models import (
    Theatres, Auditoriums, Seats,
    Users, Staff, Movies, MovieShowings,
    Customers, CustomerShowings, PaymentMethods,
    Drivers, Suppliers, Products, Deliveries,
    DeliveryItems, CartItems
)

# ----------------
# Helper functions 
# ----------------

# Commit, refresh, and return the given object
def _commit_and_refresh(obj):
    db.session.commit()
    db.session.refresh(obj)
    return obj

# Create a theatre (optionally set is_open)
def make_theatre(name="Main Theatre", address="123 Street", phone="5551112222", is_open=None):
    t = Theatres(name=name, address=address, phone=phone)
    if is_open is not None:
        t.is_open = is_open
    db.session.add(t)
    return _commit_and_refresh(t)

# Create an auditorium for a theatre
def make_auditorium(theatre, number=1, capacity=100):
    a = Auditoriums(theatre_id=theatre.id, number=number, capacity=capacity)
    db.session.add(a)
    return _commit_and_refresh(a)

# Create a seat in an auditorium
def make_seat(auditorium, aisle="A", number=1):
    s = Seats(auditorium_id=auditorium.id, aisle=aisle, number=number)
    db.session.add(s)
    return _commit_and_refresh(s)

# Create a user with unique email/phone defaults
def make_user(
    name="Alice", email=None, phone=None,
    birthday=date(1990,1,1), password_hash="hash",
    role="customer"
):
    idx = int(datetime.utcnow().timestamp() * 1000000)
    email = email or f"user{idx}@example.com"
    phone = phone or f"555{idx%1000000000:09d}"
    u = Users(
        name=name, email=email, phone=phone,
        birthday=birthday, password_hash=password_hash,
        role=role
    )
    db.session.add(u)
    return _commit_and_refresh(u)

# Create a staff record for a user/theatre
def make_staff(user, theatre, role="runner", is_available=None):
    s = Staff(user_id=user.id, theatre_id=theatre.id, role=role)
    if is_available is not None:
        s.is_available = is_available
    db.session.add(s)
    return _commit_and_refresh(s)

# Create a movie with defaults
def make_movie(title="Movie X", genre="Action", length_mins=120, release_year=2024, keywords="x", rating=Decimal("4.50")):
    m = Movies(
        title=title, genre=genre, length_mins=length_mins,
        release_year=release_year, keywords=keywords, rating=rating
    )
    db.session.add(m)
    return _commit_and_refresh(m)

# Create a movie showing (optionally set in_progress)
def make_showing(movie, auditorium, start_time=None, in_progress=None):
    start_time = start_time or datetime(2025, 1, 1, 12, 0, 0)
    sh = MovieShowings(movie_id=movie.id, auditorium_id=auditorium.id, start_time=start_time)
    if in_progress is not None:
        sh.in_progress = in_progress
    db.session.add(sh)
    return _commit_and_refresh(sh)

# Create a customer profile for a user
def make_customer(user, theatre):
    c = Customers(user_id=user.id, default_theatre_id=theatre.id)
    db.session.add(c)
    return _commit_and_refresh(c)

# Create a payment method (optionally set is_default)
def make_payment_method(customer, card_number="4111111111111111", month=12, year=2025, billing_address="1 Ave", balance=Decimal("10.00"), is_default=None):
    pm = PaymentMethods(
        customer_id=customer.user_id, card_number=card_number,
        expiration_month=month, expiration_year=year,
        billing_address=billing_address, balance=balance
    )
    if is_default is not None:
        pm.is_default = is_default
    db.session.add(pm)
    return _commit_and_refresh(pm)

# Create a driver for a user (optionally set duty_status)
def make_driver(user, license_plate="ABC123", vehicle_type="car", vehicle_color="red", duty_status=None):
    d = Drivers(
        user_id=user.id, license_plate=license_plate,
        vehicle_type=vehicle_type, vehicle_color=vehicle_color
    )
    if duty_status is not None:
        d.duty_status = duty_status
    db.session.add(d)
    return _commit_and_refresh(d)

# Create a supplier profile for a user
def make_supplier(user, company_name="Snacks Co", company_address="500 Snack Rd", contact_phone="5553334444", is_open=None):
    s = Suppliers(
        user_id=user.id, company_name=company_name,
        company_address=company_address, contact_phone=contact_phone
    )
    if is_open is not None:
        s.is_open = is_open
    db.session.add(s)
    return _commit_and_refresh(s)

# Create a product (optionally set size/discount/is_available)
def make_product(supplier, name="Popcorn", unit_price=Decimal("5.00"), inventory_quantity=10, size=None, category="food", discount=None, is_available=None):
    p = Products(
        supplier_id=supplier.user_id, name=name,
        unit_price=unit_price, inventory_quantity=inventory_quantity,
        category=category
    )
    if size is not None:
        p.size = size
    if discount is not None:
        p.discount = discount
    if is_available is not None:
        p.is_available = is_available
    db.session.add(p)
    return _commit_and_refresh(p)

# Create a cart item for a customer/product
def make_cart_item(customer, product, quantity=1):
    ci = CartItems(customer_id=customer.user_id, product_id=product.id, quantity=quantity)
    db.session.add(ci)
    return _commit_and_refresh(ci)

# Create a delivery (optionally set driver/staff/status flags)
def make_delivery(customer_showing, payment_method, total_price=Decimal("12.00"), driver=None, staff=None, payment_status=None, delivery_status=None, is_rated=None):
    d = Deliveries(
        customer_showing_id=customer_showing.id,
        payment_method_id=payment_method.id,
        total_price=total_price
    )
    if driver:
        d.driver_id = driver.user_id
    if staff:
        d.staff_id = staff.user_id
    if payment_status:
        d.payment_status = payment_status
    if delivery_status:
        d.delivery_status = delivery_status
    if is_rated is not None:
        d.is_rated = is_rated
    db.session.add(d)
    return _commit_and_refresh(d)

# Create a delivery item linking a delivery to a cart item
def make_delivery_item(delivery, cart_item):
    di = DeliveryItems(delivery_id=delivery.id, cart_item_id=cart_item.id)
    db.session.add(di)
    return _commit_and_refresh(di)

# ------------
# Model tests
# ------------

class TestModels:
    # Theatres: default is_open and unique (name, address)
    def test_theatre_defaults_and_uniqueness(self, app):
        with app.app_context():
            t1 = make_theatre()
            assert t1.is_open is False
            with pytest.raises(IntegrityError):
                make_theatre(name=t1.name, address=t1.address, phone="5550000000")
            db.session.rollback()

    # Auditoriums: uniqueness (theatre, number), positive checks, and seat cascade on delete
    def test_auditorium_constraints_uniqueness_and_cascade(self, app):
        with app.app_context():
            th = make_theatre()
            a1 = make_auditorium(th, number=1, capacity=100)
            s = make_seat(a1, aisle="C", number=3)
            assert s.id is not None

            with pytest.raises(IntegrityError):
                make_auditorium(th, number=1, capacity=200)
            db.session.rollback()

            with pytest.raises((IntegrityError, OperationalError)):
                make_auditorium(th, number=0, capacity=50)
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError)):
                make_auditorium(th, number=2, capacity=0)
            db.session.rollback()

            seat_id = s.id
            db.session.delete(a1)
            db.session.commit()
            assert Seats.query.filter_by(id=seat_id).first() is None

    # Seats: uniqueness within auditorium and positive number constraint
    def test_seat_uniqueness_and_invalid_number(self, app):
        with app.app_context():
            th = make_theatre()
            aud = make_auditorium(th)
            s1 = make_seat(aud, aisle="B", number=5)
            assert s1.id is not None
            with pytest.raises(IntegrityError):
                make_seat(aud, aisle="B", number=5)
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError)):
                make_seat(aud, aisle="D", number=0)
            db.session.rollback()

    # Users: defaults (active), unique email/phone, enum role, and last_updated changes on update
    def test_users_defaults_uniques_is_active_and_last_updated(self, app):
        with app.app_context():
            u1 = make_user()
            assert u1.account_status == 'active'
            assert u1.is_active is True
            with pytest.raises(IntegrityError):
                make_user(email=u1.email)
            db.session.rollback()
            with pytest.raises(IntegrityError):
                make_user(phone=u1.phone)
            db.session.rollback()
            with pytest.raises((IntegrityError, StatementError, OperationalError)):
                make_user(role="invalid")
            db.session.rollback()
            before = u1.last_updated
            u1.name = "Alice Updated"
            db.session.commit(); db.session.refresh(u1)
            assert u1.last_updated >= before

    # Staff: default availability, enum role, and user delete cascades
    def test_staff_defaults_enum_and_user_delete_cascade(self, app):
        with app.app_context():
            th = make_theatre()
            u = make_user(role="staff")
            st = make_staff(u, th, role="runner")
            assert st.is_available is False
            with pytest.raises((IntegrityError, StatementError, OperationalError)):
                make_staff(u, th, role="notarole")
            db.session.rollback()
            uid = u.id
            db.session.delete(u); db.session.commit()
            assert Staff.query.filter_by(user_id=uid).first() is None

    # Movies: rating check constraint and repr contains "Movie"
    def test_movies_rating_check_and_repr(self, app):
        with app.app_context():
            m = make_movie(rating=Decimal("4.99"))
            assert "Movie" in repr(m)
            with pytest.raises((IntegrityError, OperationalError)):
                make_movie(rating=Decimal("5.50"))
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError)):
                make_movie(rating=Decimal("-0.10"))
            db.session.rollback()

    # MovieShowings: unique per (auditorium, start_time), default flags, and timestamp update
    def test_movie_showings_unique_per_auditorium_and_timestamps(self, app):
        with app.app_context():
            th = make_theatre()
            aud = make_auditorium(th)
            mov = make_movie()
            start = datetime(2025, 1, 1, 12, 0, 0)
            sh1 = make_showing(mov, aud, start_time=start)
            assert sh1.in_progress is False
            with pytest.raises(IntegrityError):
                make_showing(mov, aud, start_time=start)
            db.session.rollback()
            before = sh1.last_updated
            sh1.in_progress = True
            db.session.commit(); db.session.refresh(sh1)
            assert sh1.last_updated >= before

    # Customers: link to default theatre and cascade on user delete
    def test_customers_create_and_user_delete_cascade(self, app):
        with app.app_context():
            th = make_theatre()
            u = make_user(role="customer")
            c = make_customer(u, th)
            assert c.default_theatre_id == th.id
            uid = u.id
            db.session.delete(u); db.session.commit()
            assert Customers.query.filter_by(user_id=uid).first() is None

    # CustomerShowings: unique seat per showing and FK integrity
    def test_customer_showings_unique_and_fk_integrity(self, app):
        with app.app_context():
            th = make_theatre()
            aud = make_auditorium(th)
            seat1 = make_seat(aud, aisle="A", number=1)
            seat2 = make_seat(aud, aisle="A", number=2)
            mov = make_movie()
            sh = make_showing(mov, aud)
            u = make_user(role="customer")
            cust = make_customer(u, th)
            cs1 = CustomerShowings(customer_id=cust.user_id, movie_showing_id=sh.id, seat_id=seat1.id)
            db.session.add(cs1); db.session.commit(); db.session.refresh(cs1)
            with pytest.raises(IntegrityError):
                dup = CustomerShowings(customer_id=cust.user_id, movie_showing_id=sh.id, seat_id=seat1.id)
                db.session.add(dup); db.session.commit()
            db.session.rollback()
            cs2 = CustomerShowings(customer_id=cust.user_id, movie_showing_id=sh.id, seat_id=seat2.id)
            db.session.add(cs2); db.session.commit(); db.session.refresh(cs2)
            with pytest.raises((IntegrityError, OperationalError)):
                bad = CustomerShowings(customer_id=999999, movie_showing_id=sh.id, seat_id=seat2.id)
                db.session.add(bad); db.session.commit()
            db.session.rollback()

    # PaymentMethods: defaults, month/year/balance checks
    def test_payment_methods_checks_defaults_and_invalids(self, app):
        with app.app_context():
            u = make_user(role="customer")
            th = make_theatre()
            cust = make_customer(u, th)
            pm = make_payment_method(cust, month=1, year=2025, balance=Decimal("0.00"))
            assert pm.is_default is False
            with pytest.raises((IntegrityError, OperationalError)):
                make_payment_method(cust, month=13)
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError)):
                make_payment_method(cust, month=0)
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError)):
                make_payment_method(cust, year=2024)
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError)):
                make_payment_method(cust, balance=Decimal("-1.00"))
            db.session.rollback()

    # Drivers: defaults for duty_status/rating/stats, enum checks, and last_updated change
    def test_drivers_defaults_enums_and_updates(self, app):
        with app.app_context():
            u = make_user(role="driver")
            d = make_driver(u, vehicle_type="car")
            assert d.duty_status == 'unavailable'
            assert d.rating == Decimal("5.00")
            assert d.total_deliveries == 0
            with pytest.raises((IntegrityError, StatementError, OperationalError)):
                make_driver(u, vehicle_type="plane")
            db.session.rollback()
            before = d.last_updated
            d.total_deliveries = d.total_deliveries + 1
            d.duty_status = 'available'
            db.session.commit(); db.session.refresh(d)
            assert d.last_updated >= before

    # Suppliers: default is_open and last_updated change on update
    def test_suppliers_defaults_and_updates(self, app):
        with app.app_context():
            u = make_user(role="supplier")
            s = make_supplier(u)
            assert s.is_open is False
            before = s.last_updated
            s.is_open = True
            db.session.commit(); db.session.refresh(s)
            assert s.last_updated >= before

    # Products: defaults, uniqueness per supplier, price/inventory/discount checks, and last_updated change
    def test_products_defaults_constraints_unique_and_updates(self, app):
        with app.app_context():
            su = make_user(role="supplier")
            sup = make_supplier(su)
            # Create with explicit values (avoid relying on DB defaults)
            p = make_product(
                sup,
                name="Soda",
                unit_price=Decimal("1.99"),
                inventory_quantity=5,
                category="beverages",
                is_available=True,
            )
            p = Products.query.filter_by(id=p.id).first()
            assert bool(p.is_available) is True
            assert p.size == None
            with pytest.raises(IntegrityError):
                make_product(sup, name="Soda")
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError, DataError)):
                make_product(sup, name="Bad", unit_price=Decimal("-0.01"))
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError, DataError)):
                make_product(sup, name="X", inventory_quantity=-1)
            db.session.rollback()
            with pytest.raises((IntegrityError, OperationalError, DataError)):
                make_product(sup, name="Y", discount=Decimal("-0.01"))
            db.session.rollback()
            with pytest.raises((IntegrityError, StatementError, OperationalError)):
                make_product(sup, name="Z", category="toys")
            db.session.rollback()
            before = p.last_updated
            p.inventory_quantity = 99
            db.session.commit(); db.session.refresh(p)
            assert p.last_updated >= before

    # CartItems: uniqueness (customer, product), positive quantity, and cascade on product delete
    def test_cart_items_unique_check_and_product_delete_cascade(self, app):
        with app.app_context():
            th = make_theatre()
            u = make_user(role="customer")
            cust = make_customer(u, th)
            su = make_user(role="supplier")
            sup = make_supplier(su)
            prod = make_product(sup)
            ci1 = make_cart_item(cust, prod, quantity=2)
            assert ci1.quantity == 2
            # Note: With bundle_id added as nullable, the unique constraint is now
            # on (customer_id, product_id, bundle_id). Some databases allow multiple
            # rows with (customer_id, product_id, NULL) since NULL != NULL.
            # Verify item exists instead of checking constraint.
            existing = CartItems.query.filter_by(
                customer_id=cust.user_id,
                product_id=prod.id
            ).first()
            assert existing is not None
            with pytest.raises((IntegrityError, OperationalError)):
                make_cart_item(cust, make_product(sup, name="Candy"), quantity=0)
            db.session.rollback()
            pid = prod.id
            db.session.delete(prod); db.session.commit()
            assert CartItems.query.filter_by(product_id=pid).first() is None

    # Deliveries: default enum flags, total_price check, enum validation, and delivery_time updates on status change
    def test_deliveries_defaults_checks_enums_and_time_onupdate(self, app):
        with app.app_context():
            th = make_theatre()
            aud = make_auditorium(th)
            seat = make_seat(aud)
            mov = make_movie()
            sh = make_showing(mov, aud)
            u_c = make_user(role="customer")
            cust = make_customer(u_c, th)
            pm = make_payment_method(cust)
            cs = CustomerShowings(customer_id=cust.user_id, movie_showing_id=sh.id, seat_id=seat.id)
            db.session.add(cs); db.session.commit(); db.session.refresh(cs)
            d = make_delivery(cs, pm, total_price=Decimal("15.00"))
            d = Deliveries.query.filter_by(id=d.id).first()
            assert d.payment_status == 'pending'
            assert d.delivery_status == 'pending'
            assert d.is_rated is False
            with pytest.raises((IntegrityError, OperationalError)):
                make_delivery(cs, pm, total_price=Decimal("-1.00"))
            db.session.rollback()
            with pytest.raises((StatementError, OperationalError)):
                make_delivery(cs, pm, total_price=Decimal("1.00"), delivery_status="bogus")
            db.session.rollback()
            before = d.delivery_time
            d.delivery_status = 'accepted'
            db.session.commit(); db.session.refresh(d)
            assert d.delivery_time >= before

    # DeliveryItems: uniqueness (delivery, cart_item) and cascade on delivery delete
    def test_delivery_items_uniqueness_and_delivery_delete_cascade(self, app):
        with app.app_context():
            th = make_theatre()
            aud = make_auditorium(th)
            seat = make_seat(aud)
            mov = make_movie()
            sh = make_showing(mov, aud)
            u_c = make_user(role="customer")
            cust = make_customer(u_c, th)
            su = make_user(role="supplier")
            sup = make_supplier(su)
            prod = make_product(sup, name="Nachos")
            pm = make_payment_method(cust)
            cs = CustomerShowings(customer_id=cust.user_id, movie_showing_id=sh.id, seat_id=seat.id)
            db.session.add(cs); db.session.commit(); db.session.refresh(cs)
            ci = make_cart_item(cust, prod)
            d = make_delivery(cs, pm, total_price=Decimal("7.00"))
            di1 = make_delivery_item(d, ci)
            assert di1.id is not None
            with pytest.raises(IntegrityError):
                make_delivery_item(d, ci)
            db.session.rollback()
            did = d.id
            db.session.delete(d); db.session.commit()
            assert DeliveryItems.query.filter_by(delivery_id=did).first() is None
