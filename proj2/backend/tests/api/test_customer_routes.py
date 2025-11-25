import json
from app.app import db
from app.models import Theatres, MovieShowings, Movies, Auditoriums, Seats


# Test class for customer_routes.py
class TestCustomerRoutes:

    # Test creating a valid customer
    def test_create_customer_success(self, client, app):
        with app.app_context():
            theatre = Theatres(name='Test Cinema', address='123 Main St', phone='5551234567', is_open=True)
            db.session.add(theatre)
            db.session.commit()
            theatre_id = theatre.id

        response = client.post('/api/customers', json={
            'name': 'New Customer',
            'email': 'newcustomer@example.com',
            'phone': '5559998888',
            'birthday': '1990-01-01',
            'password': 'password123',
            'role': 'customer',
            'default_theatre_id': theatre_id
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Customer created successfully'
        assert 'user_id' in data['customer']
        assert data['customer']['default_theatre_id'] == theatre_id

    # Test creating an invalid customer (not enough fields)
    def test_create_customer_missing_fields(self, client):
        response = client.post('/api/customers', json={
            'user_id': 1
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test retrieving an existing customer
    def test_get_customer_success(self, client, sample_customer):
        response = client.get(f'/api/customers/{sample_customer}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_id'] == sample_customer
        assert 'default_theatre_id' in data

    # Test retrieving a non-existent customer
    def test_get_customer_not_found(self, client):
        response = client.get('/api/customers/99999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    # Test deleting an existing customer
    def test_delete_customer_success(self, client, sample_customer):
        response = client.delete(f'/api/customers/{sample_customer}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Customer deleted successfully'

        response = client.get(f'/api/customers/{sample_customer}')
        assert response.status_code == 404

    # Test deleting a non-existent customer
    def test_delete_customer_not_found(self, client):
        response = client.delete('/api/customers/99999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    # Test updating default theatre successfully
    def test_update_default_theatre_success(self, client, app, sample_customer):
        with app.app_context():
            new_theatre = Theatres(name='New Cinema', address='456 Oak St', phone='5559999999', is_open=True)
            db.session.add(new_theatre)
            db.session.commit()
            theatre_id = new_theatre.id

        response = client.put(f'/api/customers/{sample_customer}/theatre', json={
            'theatre_id': theatre_id
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Default theatre updated'
        assert data['customer']['default_theatre_id'] == theatre_id

    # Test updating default theatre with invalid theatre id
    def test_update_default_theatre_not_found(self, client, sample_customer):
        response = client.put(f'/api/customers/{sample_customer}/theatre', json={
            'theatre_id': 99999
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test adding a payment method
    def test_add_payment_method_success(self, client, sample_customer):
        response = client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': '789 Pine St',
            'balance': 100.00,
            'is_default': True
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Payment method added'
        assert 'payment_method_id' in data

    # Test duplicate payment method rejected
    def test_add_payment_method_duplicate(self, client, sample_customer):
        client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': '789 Pine St',
            'balance': 100.00,
            'is_default': True
        })

        response = client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': 'Different Address',
            'balance': 50.00,
            'is_default': False
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test listing payment methods
    def test_get_payment_methods_success(self, client, sample_customer):
        client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1111222233334444',
            'expiration_month': 6,
            'expiration_year': 2026,
            'billing_address': 'Address 1',
            'balance': 100.00,
            'is_default': True
        })

        client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '5555666677778888',
            'expiration_month': 9,
            'expiration_year': 2028,
            'billing_address': 'Address 2',
            'balance': 200.00,
            'is_default': False
        })

        response = client.get(f'/api/customers/{sample_customer}/payment-methods')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'payment_methods' in data
        assert len(data['payment_methods']) == 2

    # Test listing payment methods when none exist returns empty list
    def test_get_payment_methods_none_returns_empty(self, client, sample_customer):
        response = client.get(f'/api/customers/{sample_customer}/payment-methods')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'payment_methods' in data
        assert len(data['payment_methods']) == 0

    # Test deleting a payment method
    def test_delete_payment_method_success(self, client, sample_customer):
        add_response = client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': '789 Pine St',
            'balance': 100.00,
            'is_default': True
        })
        pm_id = json.loads(add_response.data)['payment_method_id']

        response = client.delete(f'/api/payment-methods/{pm_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Payment method deleted'

    # Test deleting a non-existent payment method
    def test_delete_payment_method_not_found(self, client):
        response = client.delete('/api/payment-methods/99999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    # Test adding funds to a payment method
    def test_add_funds_success(self, client, sample_customer):
        add_response = client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': '789 Pine St',
            'balance': 100.00,
            'is_default': True
        })
        pm_id = json.loads(add_response.data)['payment_method_id']

        response = client.post(f'/api/payment-methods/{pm_id}/add-funds', json={
            'amount': 50.00
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Funds added successfully'
        assert data['new_balance'] == 150.00

    # Test rejecting invalid add-funds amount
    def test_add_funds_invalid_amount(self, client, sample_customer):
        add_response = client.post(f'/api/customers/{sample_customer}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': '789 Pine St',
            'balance': 100.00,
            'is_default': True
        })
        pm_id = json.loads(add_response.data)['payment_method_id']

        response = client.post(f'/api/payment-methods/{pm_id}/add-funds', json={
            'amount': 0.00
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test adding item to cart
    def test_add_to_cart_success(self, client, app, sample_customer, sample_product):
        with app.app_context():
            response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'product_id': sample_product,
                'quantity': 2
            })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Item added to cart'
        assert 'cart_item_id' in data

    # Test rejecting invalid cart quantity
    def test_add_to_cart_invalid_quantity(self, client, sample_customer, sample_product):
        response = client.post(f'/api/customers/{sample_customer}/cart', json={
            'product_id': sample_product,
            'quantity': 0
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test updating cart item quantity
    def test_update_cart_item_success(self, client, sample_customer, sample_product_extra):
        add_response = client.post(f'/api/customers/{sample_customer}/cart', json={
            'product_id': sample_product_extra,
            'quantity': 1
        })
        cart_item_id = json.loads(add_response.data)['cart_item_id']

        response = client.put(f'/api/cart/{cart_item_id}', json={
            'quantity': 3
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Cart item updated'
        assert data['new_quantity'] == 3

    # Test updating a non-existent cart item
    def test_update_cart_item_not_found(self, client):
        response = client.put('/api/cart/99999', json={
            'quantity': 1
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test deleting a cart item
    def test_delete_cart_item_success(self, client, sample_customer, sample_product):
        add_response = client.post(f'/api/customers/{sample_customer}/cart', json={
            'product_id': sample_product,
            'quantity': 2
        })
        cart_item_id = json.loads(add_response.data)['cart_item_id']

        response = client.delete(f'/api/cart/{cart_item_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Cart item deleted'

    # Test deleting a non-existent cart item
    def test_delete_cart_item_not_found(self, client):
        response = client.delete('/api/cart/99999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    # Test creating customer showing
    def test_create_customer_showing_success(self, client, app, sample_customer):
        with app.app_context():
            from app.services.customer_service import CustomerService
            customer_service = CustomerService()
            customer = customer_service.get_customer(sample_customer)
            theatre_id = customer.default_theatre_id

            auditorium = Auditoriums(theatre_id=theatre_id, number=1, capacity=100)
            db.session.add(auditorium)
            db.session.commit()

            seat = Seats(aisle='A', number=1, auditorium_id=auditorium.id)
            db.session.add(seat)
            db.session.commit()

            movie = Movies(
                title='Test Movie',
                genre='Action',
                length_mins=120,
                release_year=2024,
                keywords='test',
                rating=4.5
            )
            db.session.add(movie)
            db.session.commit()

            showing = MovieShowings(
                movie_id=movie.id,
                auditorium_id=auditorium.id,
                start_time='2025-12-01 19:00:00'
            )
            db.session.add(showing)
            db.session.commit()

            showing_id = showing.id
            seat_id = seat.id

        response = client.post(f'/api/customers/{sample_customer}/showings', json={
            'movie_showing_id': showing_id,
            'seat_id': seat_id
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Showing booked successfully'
        assert 'customer_showing_id' in data

    # Test creating showing with invalid id
    def test_create_customer_showing_invalid_showing(self, client, sample_customer):
        response = client.post(f'/api/customers/{sample_customer}/showings', json={
            'movie_showing_id': 99999,
            'seat_id': 1
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test delivery creation fails with insufficient funds
    def test_create_delivery_insufficient_funds(self, client, app, sample_customer_showing, sample_product):
        with app.app_context():
            from app.services.customer_service import CustomerService
            from app.models import CartItems, CustomerShowings
            customer_service = CustomerService()

            showing = CustomerShowings.query.filter_by(id=sample_customer_showing).first()
            customer = customer_service.get_customer(showing.customer_id)

            payment_method = customer_service.add_payment_method(
                user_id=customer.user_id,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2027,
                billing_address='123 Payment St',
                balance=2.00,
                is_default=True
            )

            cart_item = CartItems(
                customer_id=customer.user_id,
                product_id=sample_product,
                quantity=1
            )
            db.session.add(cart_item)
            db.session.commit()

            payment_method_id = payment_method.id

        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test cancelling a non-existent delivery
    def test_cancel_delivery_not_found(self, client):
        response = client.post('/api/deliveries/99999/cancel')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test end-to-end basic customer flow
    def test_customer_flow(self, client, app):
        with app.app_context():
            theatre = Theatres(name='Cinema', address='123 St', phone='5551111111', is_open=True)
            db.session.add(theatre)
            db.session.commit()
            theatre_id = theatre.id

        response = client.post('/api/customers', json={
            'name': 'Flow Customer',
            'email': 'flow@example.com',
            'phone': '5554445555',
            'birthday': '1990-01-01',
            'password': 'password123',
            'role': 'customer',
            'default_theatre_id': theatre_id
        })
        assert response.status_code == 201

        user_id = json.loads(response.data)['customer']['user_id']

        response = client.post(f'/api/customers/{user_id}/payment-methods', json={
            'card_number': '1234567812345678',
            'expiration_month': 12,
            'expiration_year': 2027,
            'billing_address': '789 Pine St',
            'balance': 100.00,
            'is_default': True
        })
        assert response.status_code == 201

        response = client.get(f'/api/customers/{user_id}')
        assert response.status_code == 200

        response = client.delete(f'/api/customers/{user_id}')
        assert response.status_code == 200

   # Test getting showings for valid customer
    def test_get_showings_for_customer_success(self, client, app, sample_customer, sample_customer_showing):
        with app.app_context():
            response = client.get(f"/api/customers/{sample_customer}/showings")
            assert response.status_code == 200 
            data = response.get_json()  
            assert "showings" in data and isinstance(data["showings"], list) 
            assert len(data["showings"]) == 1 
            showing = data["showings"][0]
            for key in ("id", "movie_title", "seat", "start_time", "auditorium", "theatre_name"):
                assert key in showing  
            from app.models import CustomerShowings
            assert showing["id"] == sample_customer_showing 

    # Test getting delivery details for valid delivery
    def test_get_delivery_details_success(self, client, app, sample_delivery):
        with app.app_context():
            response = client.get(f"/api/deliveries/{sample_delivery}/details")
            assert response.status_code == 200
            data = response.get_json()
            for key in ("id", "driver_id", "total_price", "delivery_time", "delivery_status", "items", "theatre_name", "theatre_address", "movie_title"):
                assert key in data
            assert isinstance(data["items"], list)

    # Test getting delivery details for invalid delivery
    def test_get_delivery_details_not_found(self, client, app):
        with app.app_context():
            response = client.get("/api/deliveries/999999/details")
            assert response.status_code == 404
            body = response.get_json()
            assert "error" in body

    # --- Tests for Cart with Bundles ---

    # Test adding a bundle to cart via API
    def test_add_bundle_to_cart_success(self, client, app, sample_customer, sample_admin, sample_product):
        with app.app_context():
            from app.services.bundle_service import BundleService
            from app.models import Products
            
            # Calculate original price
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price) * 2
            
            # Create a bundle
            bundle_service = BundleService(sample_admin)
            bundle = bundle_service.create_bundle(
                name='API Test Bundle',
                description='Bundle for API testing',
                original_price=original_price,
                product_items=[{'product_id': sample_product, 'quantity': 2}]
            )
            
            # Add bundle to cart
            response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'bundle_id': bundle.id,
                'quantity': 1
            })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Item added to cart'
            assert 'cart_item_id' in data

    # Test adding bundle with invalid ID
    def test_add_bundle_to_cart_not_found(self, client, sample_customer):
        response = client.post(f'/api/customers/{sample_customer}/cart', json={
            'bundle_id': 99999,
            'quantity': 1
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    # Test adding both product and bundle (should fail)
    def test_add_cart_item_both_product_and_bundle_error(self, client, sample_customer, sample_product, sample_admin):
        with client.application.app_context():
            from app.services.bundle_service import BundleService
            from app.models import Products
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            bundle_service = BundleService(sample_admin)
            bundle = bundle_service.create_bundle(
                name='Test Bundle',
                description='Test',
                original_price=original_price,
                product_items=[{'product_id': sample_product, 'quantity': 1}]
            )
            
            response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'product_id': sample_product,
                'bundle_id': bundle.id,
                'quantity': 1
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    # Test getting cart with both products and bundles
    def test_get_cart_with_products_and_bundles(self, client, app, sample_customer, sample_product, sample_admin):
        with app.app_context():
            from app.services.bundle_service import BundleService
            from app.models import Products
            
            # Calculate original price
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create a bundle
            bundle_service = BundleService(sample_admin)
            bundle = bundle_service.create_bundle(
                name='Cart Test Bundle',
                description='Bundle for cart retrieval test',
                original_price=original_price,
                product_items=[{'product_id': sample_product, 'quantity': 1}]
            )
            
            # Add product to cart
            client.post(f'/api/customers/{sample_customer}/cart', json={
                'product_id': sample_product,
                'quantity': 2
            })
            
            # Add bundle to cart
            client.post(f'/api/customers/{sample_customer}/cart', json={
                'bundle_id': bundle.id,
                'quantity': 1
            })
            
            # Get cart
            response = client.get(f'/api/customers/{sample_customer}/cart')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'items' in data
            assert len(data['items']) == 2
            
            # Verify one has product_id and one has bundle_id
            product_items = [item for item in data['items'] if item.get('product_id')]
            bundle_items = [item for item in data['items'] if item.get('bundle_id')]
            
            assert len(product_items) == 1
            assert len(bundle_items) == 1
            assert bundle_items[0]['bundle_id'] == bundle.id

    # Test updating cart item quantity (works for both products and bundles)
    def test_update_cart_item_bundle_quantity(self, client, app, sample_customer, sample_admin, sample_product):
        with app.app_context():
            from app.services.bundle_service import BundleService
            from app.models import Products
            
            # Calculate original price
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle and add to cart
            bundle_service = BundleService(sample_admin)
            bundle = bundle_service.create_bundle(
                name='Update Test Bundle',
                description='Bundle for update test',
                original_price=original_price,
                product_items=[{'product_id': sample_product, 'quantity': 1}]
            )
            
            add_response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'bundle_id': bundle.id,
                'quantity': 1
            })
            cart_item_id = json.loads(add_response.data)['cart_item_id']
            
            # Update quantity
            response = client.put(f'/api/cart/{cart_item_id}', json={
                'quantity': 3
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['new_quantity'] == 3

    # Test deleting bundle from cart
    def test_delete_bundle_from_cart(self, client, app, sample_customer, sample_admin, sample_product):
        with app.app_context():
            from app.services.bundle_service import BundleService
            from app.models import Products
            
            # Calculate original price
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle and add to cart
            bundle_service = BundleService(sample_admin)
            bundle = bundle_service.create_bundle(
                name='Delete Test Bundle',
                description='Bundle for delete test',
                original_price=original_price,
                product_items=[{'product_id': sample_product, 'quantity': 1}]
            )
            
            add_response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'bundle_id': bundle.id,
                'quantity': 1
            })
            cart_item_id = json.loads(add_response.data)['cart_item_id']
            
            # Delete cart item
            response = client.delete(f'/api/cart/{cart_item_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Cart item deleted'
            
            # Verify item is deleted
            get_response = client.get(f'/api/customers/{sample_customer}/cart')
            cart_data = json.loads(get_response.data)
            assert len(cart_data['items']) == 0

    # Test adding unavailable bundle to cart
    def test_add_unavailable_bundle_to_cart_error(self, client, app, sample_customer, sample_admin, sample_product):
        with app.app_context():
            from app.services.bundle_service import BundleService
            from app.models import Products
            
            # Calculate original price
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle
            bundle_service = BundleService(sample_admin)
            bundle = bundle_service.create_bundle(
                name='Unavailable Bundle',
                description='Will be unavailable',
                original_price=original_price,
                product_items=[{'product_id': sample_product, 'quantity': 1}]
            )
            
            # Toggle to unavailable
            bundle_service.toggle_availability(bundle.id)
            
            # Try to add to cart
            response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'bundle_id': bundle.id,
                'quantity': 1
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
