import json
import pytest
from app.app import db
from app.models import Deliveries
from app.services.customer_service import CustomerService
from decimal import Decimal


class TestDonationRoutes:
    """API tests for donation-related routes."""

    # Test 1: Get list of NGOs via API
    def test_get_ngos_endpoint(self, client):
        """Test GET /api/ngos returns the list of available NGOs."""
        response = client.get('/api/ngos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Response can be a list or dict with 'ngos' key
        if isinstance(data, list):
            ngos = data
        else:
            assert 'ngos' in data
            ngos = data['ngos']
        
        assert len(ngos) == 6  # Should have 6 NGOs
        
        # Verify structure
        for ngo in ngos:
            assert 'id' in ngo
            assert 'name' in ngo
            assert 'cause' in ngo
            assert 'description' in ngo

    # Test 2: Get NGO total donations
    def test_get_ngo_donations_endpoint(self, client, app, sample_customer_showing, sample_payment_method, sample_product, sample_customer):
        """Test GET /api/ngos/<ngo_id>/donations returns total donations for an NGO."""
        # First create a delivery with a donation to establish baseline
        with app.app_context():
            # Add product to cart
            svc = CustomerService()
            svc.create_cart_item(
                customer_id=sample_customer,
                product_id=sample_product,
                quantity=1
            )
            
            # Create delivery with donation
            delivery = svc.create_delivery(
                customer_showing_id=sample_customer_showing,
                payment_method_id=sample_payment_method,
                ngo_id=1,
                donation_amount=10.00
            )
        
        # Now test the endpoint
        response = client.get('/api/ngos/1/donations')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'ngo_id' in data
        assert 'total_amount_donated' in data
        assert data['ngo_id'] == 1
        assert float(data['total_amount_donated']) >= 10.00  # At least the donation we just made

    # Test 3: Create delivery with donation via API
    def test_create_delivery_with_donation_api(self, client, app, sample_customer_showing, sample_payment_method, sample_product, sample_customer):
        """Test POST /api/deliveries with donation parameters creates delivery with donation info."""
        with app.app_context():
            # Add product to cart
            svc = CustomerService()
            svc.create_cart_item(
                customer_id=sample_customer,
                product_id=sample_product,
                quantity=1
            )
        
        # Create delivery with donation
        response = client.post('/api/deliveries', json={
            'customer_showing_id': sample_customer_showing,
            'payment_method_id': sample_payment_method,
            'ngo_id': 3,
            'donation_amount': 8.50
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['message'] == 'Delivery created successfully'
        assert 'delivery_id' in data
        
        # Verify delivery was created with donation in database
        with app.app_context():
            delivery = Deliveries.query.filter_by(id=data['delivery_id']).first()
            assert delivery is not None
            assert delivery.ngo_id == 3
            assert delivery.ngo_name == 'Hope for Children'
            assert abs(float(delivery.donation_amount) - 8.50) < 0.01

