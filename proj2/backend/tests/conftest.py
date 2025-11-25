# Test fixtures and test app setup for API testing

import pytest
from app.app import create_app, db
from database import create_tables, drop_all_tables, get_database
from app.models import *

# Create a fresh Flask app per test function and reset the MySQL test database
@pytest.fixture(scope='function')
def app():
    app = create_app('testing')
    with app.app_context():
        test_db = get_database('movie_munchers_test')
        drop_all_tables(test_db)
        create_tables(test_db)
        test_db.close()
        yield app
        db.session.remove()

# Provide a Flask test client bound to the app fixture
@pytest.fixture
def client(app):
    return app.test_client()

# Create a sample user and return its user_id
@pytest.fixture(scope='function')
def sample_user(app):
    from app.services.user_service import UserService
    user_service = UserService()
    with app.app_context():
        user = user_service.create_user(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            birthday='1990-01-01',
            password='password123',
            role='customer'
        )
        db.session.commit()
        user_id = user.id
    return user_id

# Create a sample customer (user + customer profile) and return customer user_id
@pytest.fixture(scope='function')
def sample_customer(app, sample_theatre):
    from app.services.customer_service import CustomerService
    customer_service = CustomerService()

    with app.app_context():
        customer = customer_service.create_customer(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            birthday='1990-01-01',
            password='password123',
            role='customer',
            default_theatre_id=sample_theatre
        )
        customer_id = customer.user_id
    return customer_id

# Create a supplier user and Suppliers row; return supplier user_id
@pytest.fixture(scope='function')
def sample_supplier(app):
    from app.services.user_service import UserService
    user_service = UserService()
    with app.app_context():
        supplier_user = user_service.create_user(
            name='Supplier',
            email='supplier@example.com',
            phone='5551112222',
            birthday='1980-01-01',
            password='password123',
            role='supplier'
        )
        supplier = Suppliers(
            user_id=supplier_user.id,
            company_name='Snacks Inc', 
            company_address='123 Supply St', 
            contact_phone='5553334444',
            is_open=True
        )
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.user_id
    return supplier_id

# Create a snack product for the sample supplier; return product id
@pytest.fixture(scope='function')
def sample_product(app, sample_supplier):
    with app.app_context():
        product = Products(
            supplier_id=sample_supplier,
            name='Popcorn',
            unit_price=5.99,
            inventory_quantity=100,
            category='snacks',
            is_available=True
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    return product_id

# Create an extra product (beverage) for the sample supplier; return product id
@pytest.fixture(scope='function')
def sample_product_extra(app, sample_supplier):
    with app.app_context():
        product = Products(
            supplier_id=sample_supplier,
            name='Soda',
            unit_price=2.99,
            inventory_quantity=50,
            category='beverages',
            is_available=True
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    return product_id

# Create a driver user and Drivers row; return driver user_id
@pytest.fixture(scope='function')
def sample_driver(app):
    from app.services.user_service import UserService
    user_service = UserService()
    with app.app_context():
        driver_user = user_service.create_user(
            name='Driver',
            email='driver@example.com',
            phone='5556667777',
            birthday='1980-01-01',
            password='password123',
            role='driver'
        )
        driver = Drivers(
            user_id=driver_user.id,
            license_plate='XYZ1234',
            vehicle_type='car',
            vehicle_color='blue',
            duty_status='available',
            rating=4.7,
            total_deliveries=10
        )
        db.session.add(driver)
        db.session.commit()
        driver_id = driver.user_id
    return driver_id

# Create a staff user and Staff row (runner) at a theatre; return staff user_id
@pytest.fixture(scope='function')
def sample_staff(app, sample_theatre):
    from app.services.user_service import UserService
    user_service = UserService()

    with app.app_context():
        staff_user = user_service.create_user(
            name='Test Staff',
            email='staff@example.com',
            phone='5554445555',
            birthday='1987-03-12',
            password='password123',
            role='staff'
        )
        staff = Staff(
            user_id=staff_user.id,
            theatre_id=sample_theatre,
            role='runner',          
            is_available=True
        )
        db.session.add(staff)
        db.session.commit()
        staff_id = staff_user.id 
    return staff_id

# Create an admin user and Staff row (admin) at a theatre; return admin user_id
@pytest.fixture(scope='function')
def sample_admin(app, sample_theatre):
    from app.services.user_service import UserService
    user_service = UserService()

    with app.app_context():
        admin_user = user_service.create_user(
            name="Admin",
            email="admin@example.com",
            phone="9000000001",
            birthday="2000-01-01",
            password="password",
            role="staff"
        )
        admin = Staff(user_id=admin_user.id, theatre_id=sample_theatre, role="admin", is_available=True)
        db.session.add(admin)
        db.session.commit()
        admin_id = admin_user.id 
    return admin_id

# Create a pending delivery (with a new PaymentMethods row); return delivery id
@pytest.fixture(scope='function')
def sample_delivery(app, sample_customer_showing, sample_driver, sample_customer):
    with app.app_context():
        payment_method = PaymentMethods(
            customer_id=sample_customer,
            card_number="4111111111111111",
            expiration_month=12,
            expiration_year=2026,
            billing_address="123 Test St",
            balance=500.00,
            is_default=True
        )
        db.session.add(payment_method)
        db.session.commit()

        delivery = Deliveries(
            driver_id=sample_driver,
            customer_showing_id=sample_customer_showing,
            payment_method_id=payment_method.id,
            staff_id=None,
            payment_status="pending",
            total_price=25.00,
            delivery_status="pending"
        )
        db.session.add(delivery)
        db.session.commit()
        delivery_id = delivery.id
    return delivery_id

# Mark an existing delivery as completed/fulfilled; return delivery id
@pytest.fixture(scope='function')
def sample_fulfilled_delivery(app, sample_delivery):
    from app.models import Deliveries
    with app.app_context():
        delivery = Deliveries.query.filter_by(id=sample_delivery).first()
        delivery.payment_status = 'completed'
        delivery.delivery_status = 'fulfilled'
        db.session.commit()
        return delivery.id

# Create a theatre and return its id
@pytest.fixture(scope='function')
def sample_theatre(app):
    with app.app_context():
        theatre = Theatres(name="Theatre 1", address="1 Theatre St", phone="9876543211", is_open=True)
        db.session.add(theatre)
        db.session.commit()
        theatre_id = theatre.id
    return theatre_id

# Create a movie and return its id
@pytest.fixture(scope='function')
def sample_movie(app):
    with app.app_context():
        movie = Movies(title='Test Movie', genre='Action', length_mins=120, release_year=2024, keywords='test', rating=4.5)
        db.session.add(movie)
        db.session.commit()
        movie_id = movie.id
    return movie_id

# Create an auditorium for a theatre and return its id
@pytest.fixture(scope='function')
def sample_auditorium(app, sample_theatre):
    with app.app_context():
        auditorium = Auditoriums(theatre_id=sample_theatre, number=1, capacity=100)
        db.session.add(auditorium)
        db.session.commit()
        auditorium_id = auditorium.id
    return auditorium_id

# Create a movie showing and return its id
@pytest.fixture(scope='function')
def sample_showing(app, sample_auditorium, sample_movie):
    with app.app_context():
        showing = MovieShowings(movie_id=sample_movie, auditorium_id=sample_auditorium, start_time='2025-12-01 19:00:00')
        db.session.add(showing)
        db.session.commit()
        showing_id = showing.id
    return showing_id

# Create a customer showing with a saved seat; return customer_showing id
@pytest.fixture(scope='function')
def sample_customer_showing(app, sample_customer, sample_auditorium, sample_showing):
    from app.services.customer_service import CustomerService
    customer_service = CustomerService()
    with app.app_context():
        seat = Seats(aisle='A', number=1, auditorium_id=sample_auditorium)
        db.session.add(seat)
        db.session.commit()

        customer_showing = customer_service.create_customer_showing(
            user_id=sample_customer,
            movie_showing_id=sample_showing,
            seat_id=seat.id
        )
        customer_showing_id = customer_showing.id
    return customer_showing_id

# NOTE: This fixture references sample_auditorium/sample_showing; ensure they are requested when using it
# Also note a duplicate fixture name 'sample_payment_method' is defined later which will override this one in pytest collection
@pytest.fixture(scope='function')
def sample_payment_method(app, sample_customer):
    from app.services.customer_service import CustomerService
    customer_service = CustomerService()
    with app.app_context():
        seat = Seats(aisle='A', number=1, auditorium_id=sample_auditorium)
        db.session.add(seat)
        db.session.commit()

        customer_showing = customer_service.create_customer_showing(
            user_id=sample_customer,
            movie_showing_id=sample_showing,
            seat_id=seat.id
        )
        customer_showing_id = customer_showing.id
    return customer_showing_id

# Create a PaymentMethods row for the sample customer; return payment method id
@pytest.fixture(scope='function')
def sample_payment_method(app, sample_customer):
    with app.app_context():
        pm = PaymentMethods(
            customer_id=sample_customer,
            card_number="4111111111111111",
            expiration_month=12,
            expiration_year=2027,
            billing_address="123 Test St",
            balance=100.00,
            is_default=True
        )
        db.session.add(pm)
        db.session.commit()
        return pm.id

# Create a low-balance PaymentMethods row; return payment method id
@pytest.fixture(scope='function')
def sample_payment_method_low_balance(app, sample_customer):
    with app.app_context():
        pm = PaymentMethods(
            customer_id=sample_customer,
            card_number="4111111111111112",
            expiration_month=11,
            expiration_year=2027,
            billing_address="456 Low Funds Ave",
            balance=5.00,
            is_default=False
        )
        db.session.add(pm)
        db.session.commit()
        return pm.id

# Create another customer and return the customer user_id
@pytest.fixture(scope='function')
def sample_other_customer(app, sample_theatre):
    from app.services.user_service import UserService
    user_service = UserService()
    with app.app_context():
        user = user_service.create_user(
            name='Other Customer',
            email='other_customer@example.com',
            phone='9998887777',
            birthday='1991-02-02',
            password='password123',
            role='customer'
        )
        customer = Customers(user_id=user.id, default_theatre_id=sample_theatre)
        db.session.add(customer)
        db.session.commit()
        return customer.user_id

# Create a PaymentMethods row for the other customer; return payment method id
@pytest.fixture(scope='function')
def sample_payment_method_other_customer(app, sample_other_customer):
    with app.app_context():
        pm = PaymentMethods(
            customer_id=sample_other_customer,
            card_number="4111111111111113",
            expiration_month=10,
            expiration_year=2028,
            billing_address="789 Other St",
            balance=100.00,
            is_default=False
        )
        db.session.add(pm)
        db.session.commit()
        return pm.id

# Log in the sample_user and return an authenticated client
@pytest.fixture(scope='function')
def authenticated_client(client, app, sample_user):
    with app.app_context():
        client.post('/api/users/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
    return client

# Create a sample bundle with products; return bundle id
@pytest.fixture(scope='function')
def sample_bundle(app, sample_admin, sample_product, sample_product_extra):
    from app.services.bundle_service import BundleService
    with app.app_context():
        bundle_service = BundleService(sample_admin)
        
        # Calculate original price
        product1 = Products.query.get(sample_product)
        product2 = Products.query.get(sample_product_extra)
        original_price = (float(product1.unit_price) * 2) + (float(product2.unit_price) * 1)
        
        bundle = bundle_service.create_bundle(
            name='Test Bundle',
            description='A test bundle with products',
            original_price=original_price,
            product_items=[
                {'product_id': sample_product, 'quantity': 2},
                {'product_id': sample_product_extra, 'quantity': 1}
            ]
        )
        return bundle.id

# Create another sample bundle; return bundle id
@pytest.fixture(scope='function')
def sample_bundle_extra(app, sample_admin, sample_product):
    from app.services.bundle_service import BundleService
    with app.app_context():
        bundle_service = BundleService(sample_admin)
        
        # Calculate original price
        product = Products.query.get(sample_product)
        original_price = float(product.unit_price) * 1
        
        bundle = bundle_service.create_bundle(
            name='Extra Bundle',
            description='Another test bundle',
            original_price=original_price,
            product_items=[
                {'product_id': sample_product, 'quantity': 1}
            ]
        )
        return bundle.id
