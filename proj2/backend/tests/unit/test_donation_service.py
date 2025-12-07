import pytest
from app.services.customer_service import CustomerService
from app.models import Deliveries, CustomerShowings, PaymentMethods, CartItems, Products
from app.app import db
from decimal import Decimal


class TestDonationService:
    """Unit tests for donation-related functionality in CustomerService."""

    # Test 1: Get list of NGOs
    def test_get_ngos_returns_all_ngos(self, app):
        """Test that get_ngos() returns the complete list of hardcoded NGOs."""
        with app.app_context():
            svc = CustomerService()
            ngos = svc.get_ngos()
            
            assert ngos is not None
            assert isinstance(ngos, list)
            assert len(ngos) == 6  # Should have 6 NGOs
            
            # Verify structure of NGO objects
            for ngo in ngos:
                assert 'id' in ngo
                assert 'name' in ngo
                assert 'cause' in ngo
                assert 'description' in ngo
                assert isinstance(ngo['id'], int)
                assert isinstance(ngo['name'], str)
            
            # Verify specific NGOs exist
            ngo_ids = [ngo['id'] for ngo in ngos]
            assert 1 in ngo_ids  # Animal Care Foundation
            assert 2 in ngo_ids  # Elderly Protection Network
            assert 6 in ngo_ids  # Homeless Shelter Initiative

    # Test 2: Create delivery with fixed donation amount
    def test_create_delivery_with_fixed_donation(self, app, sample_customer_showing, sample_payment_method, sample_product, sample_customer):
        """Test creating a delivery with a fixed dollar amount donation."""
        with app.app_context():
            # Add product to cart
            svc = CustomerService()
            svc.create_cart_item(
                customer_id=sample_customer,
                product_id=sample_product,
                quantity=2
            )
            
            # Create delivery with $5.00 donation to NGO 1
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=sample_payment_method,
                ngo_id=1,
                donation_amount=5.00
            )
            
            assert delivery is not None
            assert delivery.ngo_id == 1
            assert delivery.ngo_name == "Animal Care Foundation"
            assert delivery.donation_amount == Decimal('5.00')
            assert delivery.donation_percentage is None
            
            # Verify donation was added to total charge
            product = Products.query.get(sample_product)
            expected_total = (product.unit_price - product.discount) * 2
            expected_charge = expected_total + Decimal('5.00')
            
            # Check payment method was charged correctly
            payment_method = PaymentMethods.query.get(sample_payment_method)
            assert payment_method.balance < 100.00  # Should be reduced by the charge

    # Test 3: Create delivery with percentage-based donation
    def test_create_delivery_with_percentage_donation(self, app, sample_customer_showing, sample_payment_method, sample_product, sample_customer):
        """Test creating a delivery with a percentage-based donation."""
        with app.app_context():
            # Add product to cart
            svc = CustomerService()
            svc.create_cart_item(
                customer_id=sample_customer,
                product_id=sample_product,
                quantity=1
            )
            
            # Create delivery with 10% donation to NGO 2
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=sample_payment_method,
                ngo_id=2,
                donation_percentage=10.00
            )
            
            assert delivery is not None
            assert delivery.ngo_id == 2
            assert delivery.ngo_name == "Elderly Protection Network"
            assert delivery.donation_percentage == Decimal('10.00')
            
            # Verify donation amount was calculated correctly (10% of total)
            product = Products.query.get(sample_product)
            total_price = product.unit_price - product.discount
            expected_donation = (total_price * Decimal('10.00')) / Decimal('100.00')
            
            assert abs(float(delivery.donation_amount) - float(expected_donation)) < 0.01

