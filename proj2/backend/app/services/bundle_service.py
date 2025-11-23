from app.models import *
from app.app import db
from datetime import datetime

class BundleService:
    """Service layer for managing snack bundles.
    
    Handles creation, retrieval, updating, and deletion of snack bundles
    with their associated products.
    """

    def __init__(self, user_id=None):
        """Initialize the bundle service with the acting user context.

        Args:
            user_id: The id of the user performing actions (optional for read-only operations).
        """
        self.user_id = user_id

    def validate_admin(self):
        """Ensure the current user is a staff admin.

        Returns:
            Staff: The admin staff record.

        Raises:
            ValueError: If the user is not a staff admin.
        """
        if not self.user_id:
            raise ValueError("User authentication required")
        
        admin = Staff.query.filter_by(user_id=self.user_id).first()
        if not admin or admin.role != 'admin':
            raise ValueError("Unauthorized - Admin access required")
        return admin

    def create_bundle(self, name, description, original_price, product_items):
        """Create a new snack bundle (admin only) with 20% discount applied.

        Args:
            name: Bundle name.
            description: Bundle description.
            original_price: Original total price before discount.
            product_items: List of dicts with 'product_id' and 'quantity'.

        Returns:
            SnackBundles: The created bundle record.

        Raises:
            ValueError: If validation fails or user is not admin.
        """
        admin = self.validate_admin()

        # Validate product items exist
        if not product_items or len(product_items) == 0:
            raise ValueError("Bundle must contain at least one product")

        for item in product_items:
            product = Products.query.get(item['product_id'])
            if not product:
                raise ValueError(f"Product with ID {item['product_id']} not found")

        # Calculate discounted price (20% off)
        discounted_price = original_price * 0.80

        # Create bundle
        bundle = SnackBundles(
            name=name,
            description=description,
            original_price=original_price,
            total_price=discounted_price,
            created_by_staff_id=self.user_id,
            is_available=True
        )
        db.session.add(bundle)
        db.session.flush()

        # Add bundle items
        for item in product_items:
            bundle_item = BundleItems(
                bundle_id=bundle.id,
                product_id=item['product_id'],
                quantity=item.get('quantity', 1)
            )
            db.session.add(bundle_item)

        db.session.commit()
        return bundle

    def get_all_bundles(self, include_unavailable=False):
        """Retrieve all snack bundles with their items.

        Args:
            include_unavailable: If True, include unavailable bundles.

        Returns:
            List of dicts containing bundle info and items.
        """
        query = SnackBundles.query
        if not include_unavailable:
            query = query.filter_by(is_available=True)

        bundles = query.all()
        result = []

        for bundle in bundles:
            bundle_items = BundleItems.query.filter_by(bundle_id=bundle.id).all()
            items_data = []
            
            for item in bundle_items:
                product = Products.query.get(item.product_id)
                if product:
                    items_data.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'quantity': item.quantity,
                        'unit_price': float(product.unit_price)
                    })

            result.append({
                'id': bundle.id,
                'name': bundle.name,
                'description': bundle.description,
                'original_price': float(bundle.original_price),
                'total_price': float(bundle.total_price),
                'discount_percentage': 20.0,
                'is_available': bundle.is_available,
                'items': items_data,
                'date_added': bundle.date_added.isoformat() if bundle.date_added else None,
                'last_updated': bundle.last_updated.isoformat() if bundle.last_updated else None
            })

        return result

    def get_bundle_by_id(self, bundle_id):
        """Retrieve a specific bundle with its items.

        Args:
            bundle_id: The bundle ID.

        Returns:
            Dict containing bundle info and items.

        Raises:
            ValueError: If bundle not found.
        """
        bundle = SnackBundles.query.get(bundle_id)
        if not bundle:
            raise ValueError(f"Bundle with ID {bundle_id} not found")

        bundle_items = BundleItems.query.filter_by(bundle_id=bundle.id).all()
        items_data = []
        
        for item in bundle_items:
            product = Products.query.get(item.product_id)
            if product:
                items_data.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'unit_price': float(product.unit_price)
                })

        return {
            'id': bundle.id,
            'name': bundle.name,
            'description': bundle.description,
            'original_price': float(bundle.original_price),
            'total_price': float(bundle.total_price),
            'discount_percentage': 20.0,
            'is_available': bundle.is_available,
            'items': items_data,
            'created_by_staff_id': bundle.created_by_staff_id,
            'date_added': bundle.date_added.isoformat() if bundle.date_added else None,
            'last_updated': bundle.last_updated.isoformat() if bundle.last_updated else None
        }

    def update_bundle(self, bundle_id, name=None, description=None, original_price=None, 
                     product_items=None, is_available=None):
        """Update an existing bundle (admin only).

        Args:
            bundle_id: The bundle ID to update.
            name: New name (optional).
            description: New description (optional).
            original_price: New original price before discount (optional).
            product_items: New list of product items (optional, replaces existing).
            is_available: New availability status (optional).

        Returns:
            SnackBundles: The updated bundle record.

        Raises:
            ValueError: If bundle not found or user is not admin.
        """
        admin = self.validate_admin()

        bundle = SnackBundles.query.get(bundle_id)
        if not bundle:
            raise ValueError(f"Bundle with ID {bundle_id} not found")

        # Update fields if provided
        if name is not None:
            bundle.name = name
        if description is not None:
            bundle.description = description
        if original_price is not None:
            bundle.original_price = original_price
            bundle.total_price = original_price * 0.80  # Apply 20% discount
        if is_available is not None:
            bundle.is_available = is_available

        # Update product items if provided
        if product_items is not None:
            # Remove existing items
            BundleItems.query.filter_by(bundle_id=bundle_id).delete()
            
            # Add new items
            for item in product_items:
                product = Products.query.get(item['product_id'])
                if not product:
                    raise ValueError(f"Product with ID {item['product_id']} not found")
                
                bundle_item = BundleItems(
                    bundle_id=bundle.id,
                    product_id=item['product_id'],
                    quantity=item.get('quantity', 1)
                )
                db.session.add(bundle_item)

        db.session.commit()
        return bundle

    def delete_bundle(self, bundle_id):
        """Delete a bundle (admin only).

        Args:
            bundle_id: The bundle ID to delete.

        Returns:
            None

        Raises:
            ValueError: If bundle not found or user is not admin.
        """
        admin = self.validate_admin()

        bundle = SnackBundles.query.get(bundle_id)
        if not bundle:
            raise ValueError(f"Bundle with ID {bundle_id} not found")

        # Cascade delete will handle bundle_items
        db.session.delete(bundle)
        db.session.commit()

    def toggle_availability(self, bundle_id):
        """Toggle bundle availability (admin only).

        Args:
            bundle_id: The bundle ID.

        Returns:
            SnackBundles: The updated bundle record.

        Raises:
            ValueError: If bundle not found or user is not admin.
        """
        admin = self.validate_admin()

        bundle = SnackBundles.query.get(bundle_id)
        if not bundle:
            raise ValueError(f"Bundle with ID {bundle_id} not found")

        bundle.is_available = not bundle.is_available
        db.session.commit()
        return bundle
