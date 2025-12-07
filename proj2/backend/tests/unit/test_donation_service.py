"""
Comprehensive unit tests for the donation feature.
Tests cover functionality, edge cases, and real user workflows.
"""
import pytest
from app.services.customer_service import CustomerService
from app.models import (
    Deliveries, PaymentMethods, CartItems, Products, 
    CustomerShowings, Theatres, Auditoriums, Seats, 
    MovieShowings, Movies, Suppliers
)
from app.app import db
from decimal import Decimal


class TestDonationService:
    """Test suite for donation functionality in customer service."""

    # Test 1: Get list of NGOs returns all available NGOs
    def test_get_ngos_returns_all_ngos(self, app):
        """Verify that get_ngos returns the complete list of hardcoded NGOs."""
        with app.app_context():
            svc = CustomerService()
            ngos = svc.get_ngos()
            
            assert isinstance(ngos, list)
            assert len(ngos) == 6  # We have 6 hardcoded NGOs
            
            # Verify structure of each NGO
            for ngo in ngos:
                assert 'id' in ngo
                assert 'name' in ngo
                assert 'cause' in ngo
                assert 'description' in ngo
                assert isinstance(ngo['id'], int)
                assert isinstance(ngo['name'], str)
                assert len(ngo['name']) > 0
            
            # Verify specific NGOs exist
            ngo_names = [ngo['name'] for ngo in ngos]
            assert 'Animal Care Foundation' in ngo_names
            assert 'Homeless Shelter Initiative' in ngo_names

    # Test 2: Create delivery with fixed donation amount
    def test_create_delivery_with_fixed_donation_amount(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test creating a delivery with a fixed dollar amount donation."""
        with app.app_context():
            # Setup: Create product, add to cart, create payment method
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
            
            # Add product to cart
            svc = CustomerService()
            cart_item = svc.create_cart_item(
                customer_id=sample_customer,
                product_id=product.id,
                quantity=2
            )
            
            # Create payment method with sufficient balance
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('50.00'),  # Enough for $20 + $5 donation
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            # Create delivery with fixed donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id,
                ngo_id=1,  # Animal Care Foundation
                donation_amount=5.00
            )
            
            # Verify donation was saved correctly
            assert delivery.ngo_id == 1
            assert delivery.ngo_name == 'Animal Care Foundation'
            assert float(delivery.donation_amount) == 5.00
            assert delivery.donation_percentage is None
            
            # Verify payment was charged correctly (total + donation)
            payment_method_after = PaymentMethods.query.get(payment_method.id)
            expected_charge = Decimal('20.00') + Decimal('5.00')  # $20 product + $5 donation
            expected_balance = Decimal('50.00') - expected_charge
            assert abs(float(payment_method_after.balance) - float(expected_balance)) < 0.01

    # Test 3: Create delivery with percentage-based donation
    def test_create_delivery_with_percentage_donation(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test creating a delivery with a percentage-based donation."""
        with app.app_context():
            # Setup product and cart
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
            
            svc = CustomerService()
            cart_item = svc.create_cart_item(
                customer_id=sample_customer,
                product_id=product.id,
                quantity=1
            )
            
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
            
            # Create delivery with 2.5% donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id,
                ngo_id=2,  # Elderly Protection Network
                donation_percentage=2.5
            )
            
            # Verify donation calculation: 2.5% of $100 = $2.50
            assert delivery.ngo_id == 2
            assert delivery.ngo_name == 'Elderly Protection Network'
            assert abs(float(delivery.donation_amount) - 2.50) < 0.01
            assert abs(float(delivery.donation_percentage) - 2.5) < 0.01
            
            # Verify payment charge includes donation
            payment_method_after = PaymentMethods.query.get(payment_method.id)
            expected_charge = Decimal('100.00') + Decimal('2.50')
            expected_balance = Decimal('150.00') - expected_charge
            assert abs(float(payment_method_after.balance) - float(expected_balance)) < 0.01

    # Test 4: Donation with coupon discount (donation calculated on original total)
    def test_create_delivery_with_donation_and_coupon(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that donation is calculated on original total, not discounted total."""
        with app.app_context():
            # Setup product
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
            
            svc = CustomerService()
            cart_item = svc.create_cart_item(
                customer_id=sample_customer,
                product_id=product.id,
                quantity=1
            )
            
            # Create coupon with 20% discount
            from app.models import Coupons
            coupon = Coupons(code='TEST20', discount_percent=Decimal('20.00'), difficulty=1, is_active=True)
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
            
            # Create delivery with 5% donation and 20% coupon
            # Donation should be 5% of $100 = $5 (not 5% of $80)
            # Final charge: $100 - $20 (discount) + $5 (donation) = $85
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id,
                coupon_code='TEST20',
                skip_puzzle=True,
                ngo_id=3,  # Hope for Children
                donation_percentage=5.0
            )
            
            # Verify donation is based on original total
            assert abs(float(delivery.donation_amount) - 5.00) < 0.01  # 5% of $100, not $80
            assert abs(float(delivery.discount_amount) - 20.00) < 0.01  # 20% discount
            
            # Verify final charge
            payment_method_after = PaymentMethods.query.get(payment_method.id)
            expected_charge = Decimal('100.00') - Decimal('20.00') + Decimal('5.00')  # $85
            expected_balance = Decimal('150.00') - expected_charge
            assert abs(float(payment_method_after.balance) - float(expected_balance)) < 0.01

    # Test 5: Invalid NGO ID raises error
    def test_create_delivery_with_invalid_ngo_id(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that providing an invalid NGO ID raises ValueError."""
        with app.app_context():
            # Setup minimal requirements
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
            
            # Try with invalid NGO ID
            with pytest.raises(ValueError, match="Invalid NGO id"):
                svc.create_delivery(
                    customer_showing_id=sample_customer_showing,
                    payment_method_id=payment_method.id,
                    ngo_id=999,  # Invalid NGO ID
                    donation_amount=5.00
                )

    # Test 6: Negative donation amount raises error
    def test_create_delivery_with_negative_donation_amount(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that negative donation amounts are rejected."""
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
            
            with pytest.raises(ValueError, match="Donation amount cannot be negative"):
                svc.create_delivery(
                    customer_showing_id=sample_customer_showing,
                    payment_method_id=payment_method.id,
                    ngo_id=1,
                    donation_amount=-5.00
                )

    # Test 7: Donation percentage out of range raises error
    def test_create_delivery_with_invalid_donation_percentage(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that donation percentages outside 0-100 range are rejected."""
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
            
            # Test percentage > 100
            with pytest.raises(ValueError, match="Donation percentage must be between 0 and 100"):
                svc.create_delivery(
                    customer_showing_id=sample_customer_showing,
                    payment_method_id=payment_method.id,
                    ngo_id=1,
                    donation_percentage=150.0
                )
            
            # Test negative percentage
            with pytest.raises(ValueError, match="Donation percentage must be between 0 and 100"):
                svc.create_delivery(
                    customer_showing_id=sample_customer_showing,
                    payment_method_id=payment_method.id,
                    ngo_id=1,
                    donation_percentage=-5.0
                )

    # Test 8: Zero donation amount is allowed
    def test_create_delivery_with_zero_donation(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that zero donation is allowed (user selects NGO but chooses not to donate)."""
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
            
            # Create delivery with zero donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id,
                ngo_id=4,  # Medical Support Alliance
                donation_amount=0.00
            )
            
            # Verify zero donation is stored
            assert delivery.ngo_id == 4
            assert delivery.ngo_name == 'Medical Support Alliance'
            assert float(delivery.donation_amount) == 0.00
            
            # Verify payment doesn't include donation
            payment_method_after = PaymentMethods.query.get(payment_method.id)
            expected_balance = Decimal('50.00') - Decimal('10.00')  # Only product price
            assert abs(float(payment_method_after.balance) - float(expected_balance)) < 0.01

    # Test 9: Donation details included in get_delivery_details
    def test_get_delivery_details_includes_donation_info(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that get_delivery_details returns donation information when present."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Test Product',
                unit_price=Decimal('50.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
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
            
            # Create delivery with donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id,
                ngo_id=5,  # Disease Relief Fund
                donation_percentage=3.0
            )
            
            # Get delivery details
            details = svc.get_delivery_details(delivery.id)
            
            # Verify donation info is included
            assert 'donation' in details
            assert details['donation'] is not None
            assert details['donation']['ngo_id'] == 5
            assert details['donation']['ngo_name'] == 'Disease Relief Fund'
            assert abs(details['donation']['donation_amount'] - 1.50) < 0.01  # 3% of $50
            assert abs(details['donation']['donation_percentage'] - 3.0) < 0.01

    # Test 10: Delivery without donation has null donation in details
    def test_get_delivery_details_no_donation_returns_null(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that deliveries without donations return null donation info."""
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
            
            # Create delivery without donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id
            )
            
            # Get delivery details
            details = svc.get_delivery_details(delivery.id)
            
            # Verify donation is null
            assert 'donation' in details
            assert details['donation'] is None

    # Test 11: Insufficient funds when donation is included
    def test_create_delivery_insufficient_funds_with_donation(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that insufficient funds error occurs when donation makes total too high."""
        with app.app_context():
            # Setup
            supplier = Suppliers(user_id=sample_supplier, company_name='Test Supplier', 
                              company_address='123 St', contact_phone='555-0000', is_open=True)
            db.session.add(supplier)
            db.session.commit()
            
            product = Products(
                supplier_id=sample_supplier,
                name='Test Product',
                unit_price=Decimal('50.00'),
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            db.session.add(product)
            db.session.commit()
            
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            # Payment method with balance less than product + donation
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('52.00'),  # Enough for $50 product but not $50 + $5 donation
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            # Try to create delivery with donation that exceeds balance
            with pytest.raises(ValueError, match="Insufficient funds"):
                svc.create_delivery(
                    customer_showing_id=sample_customer_showing,
                    payment_method_id=payment_method.id,
                    ngo_id=6,  # Homeless Shelter Initiative
                    donation_amount=5.00  # Total would be $55, but only $52 available
                )

    # Test 12: Large percentage donation (edge case)
    def test_create_delivery_with_large_percentage_donation(self, app, sample_customer, sample_customer_showing, sample_supplier):
        """Test that large percentage donations (like 100%) work correctly."""
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
            
            svc = CustomerService()
            svc.create_cart_item(customer_id=sample_customer, product_id=product.id, quantity=1)
            
            payment_method = PaymentMethods(
                customer_id=sample_customer,
                card_number='4111111111111111',
                expiration_month=12,
                expiration_year=2026,
                billing_address='123 Test St',
                balance=Decimal('50.00'),  # Enough for $10 + $10 donation
                is_default=True
            )
            db.session.add(payment_method)
            db.session.commit()
            
            # Create delivery with 100% donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=payment_method.id,
                ngo_id=1,
                donation_percentage=100.0
            )
            
            # Verify 100% donation = full product price
            assert abs(float(delivery.donation_amount) - 10.00) < 0.01
            assert abs(float(delivery.donation_percentage) - 100.0) < 0.01
            
            # Verify charge: $10 product + $10 donation = $20
            payment_method_after = PaymentMethods.query.get(payment_method.id)
            expected_balance = Decimal('50.00') - Decimal('20.00')
            assert abs(float(payment_method_after.balance) - float(expected_balance)) < 0.01

