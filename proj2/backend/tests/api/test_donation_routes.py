"""
API tests for donation endpoints and donation functionality in delivery creation.
Tests cover API endpoints, request/response formats, and integration scenarios.
"""
import pytest
import json
from app.models import (
    Deliveries, PaymentMethods, CartItems, Products, 
    CustomerShowings, Theatres, Auditoriums, Seats, 
    MovieShowings, Movies, Suppliers
)
from app.app import db
from decimal import Decimal


class TestDonationRoutes:
    """Test suite for donation-related API endpoints."""

    # Test 1: GET /api/ngos returns list of NGOs
    def test_get_ngos_endpoint_returns_list(self, client):
        """Test that the NGOs endpoint returns the complete list of NGOs."""
        response = client.get('/api/ngos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'ngos' in data
        assert isinstance(data['ngos'], list)
        assert len(data['ngos']) == 6
        
        # Verify structure
        for ngo in data['ngos']:
            assert 'id' in ngo
            assert 'name' in ngo
            assert 'cause' in ngo
            assert 'description' in ngo

    # Test 2: POST /api/deliveries with fixed donation amount
    def test_create_delivery_with_fixed_donation_api(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test creating a delivery via API with fixed donation amount."""
        with app.app_context():
            # Setup product and cart
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='API Test Product',
                unit_price=Decimal('30.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            from app.services.customer_service import CustomerService
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('100.00'),
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            payment_method_id = payment_method.id
        
        # Create delivery via API with donation
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id,
            'ngo_id': 1,
            'donation_amount': 7.50
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert 'delivery_id' in data
        assert 'donation' in data
        assert data['donation'] is not None
        assert data['donation']['ngo_id'] == 1
        assert data['donation']['ngo_name'] == 'Animal Care Foundation'
        assert abs(data['donation']['donation_amount'] - 7.50) < 0.01

    # Test 3: POST /api/deliveries with percentage donation
    def test_create_delivery_with_percentage_donation_api(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test creating a delivery via API with percentage-based donation."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='API Test Product',
                unit_price=Decimal('40.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            from app.services.customer_service import CustomerService
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('100.00'),
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            payment_method_id = payment_method.id
        
        # Create delivery with 4% donation
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id,
            'ngo_id': 2,
            'donation_percentage': 4.0
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert 'donation' in data
        assert data['donation']['ngo_id'] == 2
        assert abs(data['donation']['donation_amount'] - 1.60) < 0.01  # 4% of $40
        assert abs(data['donation']['donation_percentage'] - 4.0) < 0.01

    # Test 4: POST /api/deliveries with invalid NGO ID
    def test_create_delivery_invalid_ngo_api(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that API rejects invalid NGO IDs."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Test Product',
                unit_price=Decimal('10.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            from app.services.customer_service import CustomerService
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('50.00'),
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            payment_method_id = payment_method.id
        
        # Try with invalid NGO ID
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id,
            'ngo_id': 999,  # Invalid
            'donation_amount': 5.00
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid NGO id' in data['error']

    # Test 5: GET /api/deliveries/{id}/details includes donation info
    def test_get_delivery_details_includes_donation_api(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that delivery details endpoint includes donation information."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Test Product',
                unit_price=Decimal('25.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            from app.services.customer_service import CustomerService
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('100.00'),
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            payment_method_id = payment_method.id
        
        # Create delivery with donation
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id,
            'ngo_id': 3,
            'donation_percentage': 2.0
        })
        
        assert response.status_code == 201
        delivery_data = json.loads(response.data)
        delivery_id = delivery_data['delivery_id']
        
        # Get delivery details
        response = client.get(f'/api/deliveries/{delivery_id}/details')
        
        assert response.status_code == 200
        details = json.loads(response.data)
        
        assert 'donation' in details
        assert details['donation'] is not None
        assert details['donation']['ngo_id'] == 3
        assert details['donation']['ngo_name'] == 'Hope for Children'
        assert abs(details['donation']['donation_amount'] - 0.50) < 0.01  # 2% of $25

    # Test 6: End-to-end workflow: cart -> checkout with donation -> verify
    def test_end_to_end_donation_workflow(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test complete user workflow: add to cart, checkout with donation, verify delivery."""
        with app.app_context():
            # Setup product
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Workflow Product',
                unit_price=Decimal('20.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            # Add to cart via API
            response = client.post(f'/api/customers/{sample_customer}/cart', json={
                'product_id': product.id,
                'quantity': 2
            })
            assert response.status_code == 201
            
            # Create payment method
            response = client.post(f'/api/customers/{sample_customer}/payment-methods', json={
                'card_number': '4111111111111111',
                'expiration_month': 12,
                'expiration_year': 2026,
                'billing_address': '123 Test St',
                'balance': 100.00,
                'is_default': True
            })
            assert response.status_code == 201
            payment_method_id = json.loads(response.data)['payment_method_id']
            
            # Checkout with donation (fixed amount)
            response = client.post('/api/deliveries', json={
                'customer_showing_id': sample_customer_showing,
                'payment_method_id': payment_method_id,
                'ngo_id': 4,  # Medical Support Alliance
                'donation_amount': 3.00
            })
            
            assert response.status_code == 201
            delivery_data = json.loads(response.data)
            delivery_id = delivery_data['delivery_id']
            
            # Verify donation in response
            assert delivery_data['donation']['ngo_id'] == 4
            assert abs(delivery_data['donation']['donation_amount'] - 3.00) < 0.01
            
            # Verify delivery was created with donation
            delivery = Deliveries.query.get(delivery_id)
            assert delivery.ngo_id == 4
            assert abs(float(delivery.donation_amount) - 3.00) < 0.01
            
            # Verify cart was cleared (delivery items created)
            cart_items = CartItems.query.filter_by(customer_id=sample_customer).all()
            assert len(cart_items) == 0  # Cart should be empty after delivery

    # Test 7: Donation with coupon in API
    def test_create_delivery_with_donation_and_coupon_api(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test API endpoint with both coupon and donation."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Test Product',
                unit_price=Decimal('100.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            from app.services.customer_service import CustomerService
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            # Create coupon
            from app.models import Coupons
            coupon = Coupons(code='DONATE10', discount_percent=Decimal('10.00'), difficulty=1, is_active=True)
            db.session.add(coupon)
            db.session.commit()
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('150.00'),
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            payment_method_id = payment_method.id
        
        # Create delivery with coupon and donation
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id,
            'coupon_code': 'DONATE10',
            'skip_puzzle': True,
            'ngo_id': 5,
            'donation_percentage': 5.0
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        # Verify both coupon and donation are applied
        assert 'applied_coupon_code' in data
        assert data['applied_coupon_code'] == 'DONATE10'
        assert abs(data['discount_amount'] - 10.00) < 0.01  # 10% of $100
        
        assert 'donation' in data
        assert data['donation']['ngo_id'] == 5
        # Donation should be 5% of original $100 = $5, not 5% of discounted $90
        assert abs(data['donation']['donation_amount'] - 5.00) < 0.01

    # Test 8: Zero donation via API
    def test_create_delivery_with_zero_donation_api(self, client, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that zero donation is accepted via API."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Test Product',
                unit_price=Decimal('15.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            from app.services.customer_service import CustomerService
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('50.00'),
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            payment_method_id = payment_method.id
        
        # Create delivery with zero donation
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': payment_method_id,
            'ngo_id': 6,
            'donation_amount': 0.00
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert 'donation' in data
        assert data['donation']['ngo_id'] == 6
        assert abs(data['donation']['donation_amount'] - 0.00) < 0.01

