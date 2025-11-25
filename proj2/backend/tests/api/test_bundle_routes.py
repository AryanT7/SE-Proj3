import json
import pytest
from app.app import db
from app.models import SnackBundles, BundleItems, Products


class TestBundleRoutes:
    """Integration tests for bundle_routes.py"""

    # Test creating a bundle via API
    def test_create_bundle_success(self, client, app, sample_admin, sample_product, sample_product_extra):
        with app.app_context():
            # Login as admin
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            # Calculate original price
            product1 = Products.query.get(sample_product)
            product2 = Products.query.get(sample_product_extra)
            original_price = (float(product1.unit_price) * 2) + (float(product2.unit_price) * 1)
            
            response = client.post('/api/bundles', json={
                'name': 'API Bundle',
                'description': 'Created via API',
                'original_price': original_price,
                'product_items': [
                    {'product_id': sample_product, 'quantity': 2},
                    {'product_id': sample_product_extra, 'quantity': 1}
                ]
            })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Bundle created successfully'
            assert 'bundle_id' in data
            assert data['bundle']['name'] == 'API Bundle'

    # Test creating bundle without authentication
    def test_create_bundle_unauthorized(self, client, sample_product):
        with client.application.app_context():
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
        response = client.post('/api/bundles', json={
            'name': 'Unauthorized Bundle',
            'description': 'Should fail',
            'original_price': original_price,
            'product_items': [{'product_id': sample_product, 'quantity': 1}]
        })
        
        assert response.status_code in [401, 403]

    # Test creating bundle with missing fields
    def test_create_bundle_missing_fields(self, client, app, sample_admin):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            response = client.post('/api/bundles', json={
                'name': 'Incomplete Bundle'
                # Missing original_price and product_items
            })
            
            assert response.status_code == 400

    # Test creating bundle with empty items
    def test_create_bundle_empty_items(self, client, app, sample_admin):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            response = client.post('/api/bundles', json={
                'name': 'Empty Bundle',
                'description': 'No items',
                'original_price': 10.0,
                'product_items': []
            })
            
            assert response.status_code in [400, 403]

    # Test getting all bundles
    def test_get_bundles_success(self, client, app, sample_admin, sample_product):
        with app.app_context():
            # Create a bundle first
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            client.post('/api/bundles', json={
                'name': 'Test Bundle',
                'description': 'For listing',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 1}]
            })
            
            # Get all bundles
            response = client.get('/api/bundles')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'bundles' in data
            assert isinstance(data['bundles'], list)
            assert len(data['bundles']) > 0

    # Test getting all bundles including unavailable (admin only)
    def test_get_bundles_include_unavailable_admin(self, client, app, sample_admin, sample_product):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle
            create_response = client.post('/api/bundles', json={
                'name': 'Available Bundle',
                'description': 'Will toggle',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 1}]
            })
            bundle_id = json.loads(create_response.data)['bundle_id']
            
            # Toggle to unavailable
            client.patch(f'/api/bundles/{bundle_id}/toggle')
            
            # Get bundles including unavailable
            response = client.get('/api/bundles?include_unavailable=true')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['bundles']) >= 1

    # Test getting specific bundle by ID
    def test_get_bundle_by_id_success(self, client, app, sample_admin, sample_product):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price) * 2
            
            # Create bundle
            create_response = client.post('/api/bundles', json={
                'name': 'Specific Bundle',
                'description': 'Get by ID',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 2}]
            })
            bundle_id = json.loads(create_response.data)['bundle_id']
            
            # Get bundle by ID
            response = client.get(f'/api/bundles/{bundle_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            # get_bundle returns bundle dict directly (not wrapped in 'bundle' key)
            assert data['id'] == bundle_id
            assert data['name'] == 'Specific Bundle'
            assert len(data['items']) == 1

    # Test getting non-existent bundle
    def test_get_bundle_not_found(self, client):
        response = client.get('/api/bundles/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    # Test updating bundle
    def test_update_bundle_success(self, client, app, sample_admin, sample_product, sample_product_extra):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle
            create_response = client.post('/api/bundles', json={
                'name': 'Original Name',
                'description': 'Original description',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 1}]
            })
            bundle_id = json.loads(create_response.data)['bundle_id']
            
            # Calculate new price
            product1 = Products.query.get(sample_product)
            product2 = Products.query.get(sample_product_extra)
            new_original_price = (float(product1.unit_price) * 2) + (float(product2.unit_price) * 1)
            
            # Update bundle
            response = client.put(f'/api/bundles/{bundle_id}', json={
                'name': 'Updated Name',
                'description': 'Updated description',
                'original_price': new_original_price,
                'product_items': [
                    {'product_id': sample_product, 'quantity': 2},
                    {'product_id': sample_product_extra, 'quantity': 1}
                ]
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Bundle updated successfully'
            assert data['bundle']['name'] == 'Updated Name'

    # Test updating non-existent bundle
    def test_update_bundle_not_found(self, client, app, sample_admin, sample_product):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            response = client.put('/api/bundles/99999', json={
                'name': 'Updated',
                'description': 'Updated',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 1}]
            })
            
            assert response.status_code in [403, 404]

    # Test deleting bundle
    def test_delete_bundle_success(self, client, app, sample_admin, sample_product):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle
            create_response = client.post('/api/bundles', json={
                'name': 'To Delete',
                'description': 'Will be deleted',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 1}]
            })
            bundle_id = json.loads(create_response.data)['bundle_id']
            
            # Delete bundle
            response = client.delete(f'/api/bundles/{bundle_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Bundle deleted successfully'
            
            # Verify deletion
            get_response = client.get(f'/api/bundles/{bundle_id}')
            assert get_response.status_code == 404

    # Test deleting non-existent bundle
    def test_delete_bundle_not_found(self, client, app, sample_admin):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            response = client.delete('/api/bundles/99999')
            
            assert response.status_code in [403, 404]

    # Test toggling bundle availability
    def test_toggle_bundle_availability(self, client, app, sample_admin, sample_product):
        with app.app_context():
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            product = Products.query.get(sample_product)
            original_price = float(product.unit_price)
            
            # Create bundle
            create_response = client.post('/api/bundles', json={
                'name': 'Toggle Bundle',
                'description': 'Will toggle',
                'original_price': original_price,
                'product_items': [{'product_id': sample_product, 'quantity': 1}]
            })
            bundle_id = json.loads(create_response.data)['bundle_id']
            
            # Initially available
            get_response = client.get(f'/api/bundles/{bundle_id}')
            bundle_data = json.loads(get_response.data)
            assert bundle_data['is_available'] is True
            
            # Toggle to unavailable
            toggle_response = client.patch(f'/api/bundles/{bundle_id}/toggle')
            assert toggle_response.status_code == 200
            toggle_data = json.loads(toggle_response.data)
            # Toggle returns {"message": ..., "is_available": ...}
            assert toggle_data['is_available'] is False
            
            # Toggle back to available
            toggle_response = client.patch(f'/api/bundles/{bundle_id}/toggle')
            assert toggle_response.status_code == 200
            toggle_data = json.loads(toggle_response.data)
            assert toggle_data['is_available'] is True

    # Test bundle price calculation through API
    def test_bundle_price_calculation_api(self, client, app, sample_admin, sample_supplier):
        with app.app_context():
            # Create products with known prices
            product1 = Products(
                supplier_id=sample_supplier,
                name='Product A',
                unit_price=10.00,
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            product2 = Products(
                supplier_id=sample_supplier,
                name='Product B',
                unit_price=5.00,
                inventory_quantity=100,
                category='beverages',
                is_available=True
            )
            db.session.add_all([product1, product2])
            db.session.commit()
            
            client.post('/api/users/login', json={
                'email': 'admin@example.com',
                'password': 'password'
            })
            
            # Create bundle with 2xA (20) + 3xB (15) = 35 original, 28 discounted
            response = client.post('/api/bundles', json={
                'name': 'Price Test',
                'description': 'Testing prices',
                'original_price': 35.00,
                'product_items': [
                    {'product_id': product1.id, 'quantity': 2},
                    {'product_id': product2.id, 'quantity': 3}
                ]
            })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert float(data['bundle']['original_price']) == 35.00
            assert float(data['bundle']['total_price']) == 28.00
