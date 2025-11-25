import pytest
from app.services.bundle_service import BundleService
from app.models import SnackBundles, BundleItems, Products, Staff, Suppliers
from app.app import db
from decimal import Decimal


def calculate_original_price(app, items):
    """Helper to calculate original price from product items."""
    with app.app_context():
        total = 0.0
        for item in items:
            product = Products.query.get(item['product_id'])
            if product:
                total += float(product.unit_price) * item.get('quantity', 1)
        return total


class TestBundleService:
    """Unit tests for BundleService class"""

    # Test creating a bundle successfully to test normal flow
    def test_create_bundle_success(self, app, sample_admin, sample_product, sample_product_extra):
        with app.app_context():
            service = BundleService(sample_admin)
            
            product_items = [
                {'product_id': sample_product, 'quantity': 2},
                {'product_id': sample_product_extra, 'quantity': 1}
            ]
            original_price = calculate_original_price(app, product_items)
            
            bundle = service.create_bundle(
                name='Combo Deal',
                description='Popcorn and Soda combo',
                original_price=original_price,
                product_items=product_items
            )
            
            assert bundle is not None
            assert bundle.name == 'Combo Deal'
            assert bundle.description == 'Popcorn and Soda combo'
            assert bundle.created_by_staff_id == sample_admin
            assert bundle.is_available is True
            # Original price should be sum of items: (5.99*2) + (2.99*1) = 14.97
            assert float(bundle.original_price) == pytest.approx(14.97, 0.01)
            # Total price should be 80% of original (20% discount)
            assert float(bundle.total_price) == pytest.approx(11.976, 0.01)

    # Test creating bundle with empty items list
    def test_create_bundle_empty_items(self, app, sample_admin):
        with app.app_context():
            service = BundleService(sample_admin)
            
            with pytest.raises(ValueError, match="Bundle must contain at least one product"):
                service.create_bundle(
                    name='Empty Bundle',
                    description='No items',
                    original_price=0.0,
                    product_items=[]
                )

    # Test creating bundle with invalid product
    def test_create_bundle_invalid_product(self, app, sample_admin):
        with app.app_context():
            service = BundleService(sample_admin)
            
            product_items = [
                {'product_id': 99999, 'quantity': 1}
            ]
            
            with pytest.raises(ValueError, match="Product with ID .* not found"):
                service.create_bundle(
                    name='Invalid Bundle',
                    description='Has invalid product',
                    original_price=10.0,
                    product_items=product_items
                )

    # Test creating bundle as non-admin
    def test_create_bundle_non_admin(self, app, sample_staff, sample_product):
        with app.app_context():
            # Change staff role to runner (non-admin)
            staff = Staff.query.filter_by(user_id=sample_staff).first()
            staff.role = 'runner'
            db.session.commit()
            
            service = BundleService(sample_staff)
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            with pytest.raises(ValueError, match="Unauthorized - Admin access required"):
                service.create_bundle(
                    name='Unauthorized Bundle',
                    description='Created by runner',
                    original_price=original_price,
                    product_items=product_items
                )

    # Test getting all bundles (available only)
    def test_get_all_bundles_available_only(self, app, sample_admin, sample_product):
        with app.app_context():
            service = BundleService(sample_admin)
            
            # Create two bundles, one available and one not
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            bundle1 = service.create_bundle(
                name='Available Bundle',
                description='This is available',
                original_price=original_price,
                product_items=product_items
            )
            
            bundle2 = service.create_bundle(
                name='Unavailable Bundle',
                description='This is not available',
                original_price=original_price,
                product_items=product_items
            )
            
            # Toggle bundle2 to unavailable
            service.toggle_availability(bundle2.id)
            
            # Get all bundles (available only)
            bundles = service.get_all_bundles(include_unavailable=False)
            
            assert len(bundles) == 1
            assert bundles[0]['name'] == 'Available Bundle'
            assert bundles[0]['is_available'] is True

    # Test getting all bundles including unavailable (admin)
    def test_get_all_bundles_include_unavailable(self, app, sample_admin, sample_product):
        with app.app_context():
            service = BundleService(sample_admin)
            
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            bundle1 = service.create_bundle(
                name='Available Bundle',
                description='Available',
                original_price=original_price,
                product_items=product_items
            )
            
            bundle2 = service.create_bundle(
                name='Unavailable Bundle',
                description='Unavailable',
                original_price=original_price,
                product_items=product_items
            )
            
            service.toggle_availability(bundle2.id)
            
            # Get all bundles including unavailable
            bundles = service.get_all_bundles(include_unavailable=True)
            
            assert len(bundles) == 2

    # Test getting specific bundle by ID
    def test_get_bundle_by_id_success(self, app, sample_admin, sample_product):
        with app.app_context():
            service = BundleService(sample_admin)
            
            product_items = [{'product_id': sample_product, 'quantity': 2}]
            original_price = calculate_original_price(app, product_items)
            
            created_bundle = service.create_bundle(
                name='Test Bundle',
                description='Test description',
                original_price=original_price,
                product_items=product_items
            )
            
            # Get bundle by ID
            bundle_dict = service.get_bundle_by_id(created_bundle.id)
            
            assert bundle_dict['id'] == created_bundle.id
            assert bundle_dict['name'] == 'Test Bundle'
            assert len(bundle_dict['items']) == 1
            assert bundle_dict['items'][0]['quantity'] == 2

    # Test getting non-existent bundle
    def test_get_bundle_not_found(self, app, sample_admin):
        with app.app_context():
            service = BundleService(sample_admin)
            
            with pytest.raises(ValueError, match="Bundle with ID .* not found"):
                service.get_bundle_by_id(99999)

    # Test updating bundle
    def test_update_bundle_success(self, app, sample_admin, sample_product, sample_product_extra):
        with app.app_context():
            service = BundleService(sample_admin)
            
            # Create initial bundle
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            bundle = service.create_bundle(
                name='Original Bundle',
                description='Original description',
                original_price=original_price,
                product_items=product_items
            )
            
            # Update bundle
            new_items = [
                {'product_id': sample_product, 'quantity': 2},
                {'product_id': sample_product_extra, 'quantity': 1}
            ]
            new_original_price = calculate_original_price(app, new_items)
            
            updated_bundle = service.update_bundle(
                bundle_id=bundle.id,
                name='Updated Bundle',
                description='Updated description',
                original_price=new_original_price,
                product_items=new_items
            )
            
            assert updated_bundle.name == 'Updated Bundle'
            assert updated_bundle.description == 'Updated description'
            
            # Check items were updated
            items = BundleItems.query.filter_by(bundle_id=bundle.id).all()
            assert len(items) == 2

    # Test updating bundle as non-admin
    def test_update_bundle_non_admin(self, app, sample_staff, sample_admin, sample_product):
        with app.app_context():
            # Create bundle as admin
            admin_service = BundleService(sample_admin)
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            bundle = admin_service.create_bundle(
                name='Test Bundle',
                description='Test',
                original_price=original_price,
                product_items=product_items
            )
            
            # Change to runner
            staff = Staff.query.filter_by(user_id=sample_staff).first()
            staff.role = 'runner'
            db.session.commit()
            
            # Try to update with non-admin user
            service = BundleService(sample_staff)
            
            with pytest.raises(ValueError, match="Unauthorized - Admin access required"):
                service.update_bundle(
                    bundle_id=bundle.id,
                    name='Updated',
                    description='Updated',
                    original_price=original_price,
                    product_items=product_items
                )

    # Test deleting bundle
    def test_delete_bundle_success(self, app, sample_admin, sample_product):
        with app.app_context():
            service = BundleService(sample_admin)
            
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            bundle = service.create_bundle(
                name='To Delete',
                description='Will be deleted',
                original_price=original_price,
                product_items=product_items
            )
            
            bundle_id = bundle.id
            service.delete_bundle(bundle_id)
            
            # Verify bundle is deleted
            deleted_bundle = SnackBundles.query.filter_by(id=bundle_id).first()
            assert deleted_bundle is None

    # Test deleting non-existent bundle
    def test_delete_bundle_not_found(self, app, sample_admin):
        with app.app_context():
            service = BundleService(sample_admin)
            
            with pytest.raises(ValueError, match="Bundle with ID .* not found"):
                service.delete_bundle(99999)

    # Test toggling bundle availability
    def test_toggle_bundle_availability(self, app, sample_admin, sample_product):
        with app.app_context():
            service = BundleService(sample_admin)
            
            product_items = [{'product_id': sample_product, 'quantity': 1}]
            original_price = calculate_original_price(app, product_items)
            
            bundle = service.create_bundle(
                name='Toggle Bundle',
                description='Will be toggled',
                original_price=original_price,
                product_items=product_items
            )
            
            # Initially available
            assert bundle.is_available is True
            
            # Toggle to unavailable
            updated_bundle = service.toggle_availability(bundle.id)
            assert updated_bundle.is_available is False
            
            # Toggle back to available
            updated_bundle = service.toggle_availability(bundle.id)
            assert updated_bundle.is_available is True

    # Test calculating bundle prices correctly
    def test_bundle_price_calculation(self, app, sample_admin, sample_supplier):
        with app.app_context():
            # Create products with known prices
            product1 = Products(
                supplier_id=sample_supplier,
                name='Item A',
                unit_price=10.00,
                inventory_quantity=100,
                category='snacks',
                is_available=True
            )
            product2 = Products(
                supplier_id=sample_supplier,
                name='Item B',
                unit_price=5.00,
                inventory_quantity=100,
                category='beverages',
                is_available=True
            )
            db.session.add_all([product1, product2])
            db.session.commit()
            
            service = BundleService(sample_admin)
            product_items = [
                {'product_id': product1.id, 'quantity': 2},  # 2 * 10 = 20
                {'product_id': product2.id, 'quantity': 3}   # 3 * 5 = 15
            ]
            original_price = 35.00  # 20 + 15
            
            bundle = service.create_bundle(
                name='Price Test Bundle',
                description='Testing price calculation',
                original_price=original_price,
                product_items=product_items
            )
            
            # Original price: 20 + 15 = 35.00
            assert float(bundle.original_price) == 35.00
            # Discounted price: 35.00 * 0.8 = 28.00
            assert float(bundle.total_price) == 28.00

    # Test validate_admin method
    def test_validate_admin_success(self, app, sample_admin):
        with app.app_context():
            service = BundleService(sample_admin)
            # Should not raise exception
            service.validate_admin()

    # Test validate_admin with non-admin
    def test_validate_admin_failure(self, app, sample_staff):
        with app.app_context():
            # Change to runner
            staff = Staff.query.filter_by(user_id=sample_staff).first()
            staff.role = 'runner'
            db.session.commit()
            
            service = BundleService(sample_staff)
            
            with pytest.raises(ValueError, match="Unauthorized - Admin access required"):
                service.validate_admin()
