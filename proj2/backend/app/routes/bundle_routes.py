from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.models import *
from app.services.bundle_service import BundleService


# Blueprint for bundle-related endpoints
bundle_bp = Blueprint("bundles", __name__, url_prefix="/api")


# Helper function to retrieve the current user's id
def get_user_id():
    return current_user.id if current_user.is_authenticated else None


@bundle_bp.route('/bundles', methods=['POST'])
def create_bundle():
    """
    Create New Snack Bundle
    ---
    tags: [Snack Bundles]
    description: Creates a new snack bundle. Requires admin authentication.
    parameters:
      - in: body
        name: bundle_data
        required: true
        schema:
          type: object
          required:
            - name
            - total_price
            - product_items
          properties:
            name:
              type: string
              description: Bundle name
            description:
              type: string
              description: Bundle description
            total_price:
              type: number
              description: Total price before discount
            discount_percentage:
              type: number
              description: Discount percentage (0-100)
              default: 0
            product_items:
              type: array
              description: Array of products in the bundle
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                  quantity:
                    type: integer
                    default: 1
    responses:
      201:
        description: Bundle created successfully
        schema:
          type: object
          properties:
            message: {type: string}
            bundle_id: {type: integer}
            bundle: {type: object}
      400:
        description: Missing or invalid fields
      403:
        description: Unauthorized (not admin)
      500:
        description: Server error
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        service = BundleService(user_id)
        data = request.json

        required_fields = ['name', 'original_price', 'product_items']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        bundle = service.create_bundle(
            name=data['name'],
            description=data.get('description', ''),
            original_price=data['original_price'],
            product_items=data['product_items']
        )

        bundle_data = service.get_bundle_by_id(bundle.id)

        return jsonify({
            "message": "Bundle created successfully",
            "bundle_id": bundle.id,
            "bundle": bundle_data
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bundle_bp.route('/bundles', methods=['GET'])
def get_bundles():
    """
    Get All Snack Bundles
    ---
    tags: [Snack Bundles]
    description: Retrieves all available snack bundles. Admins can see unavailable bundles too.
    parameters:
      - in: query
        name: include_unavailable
        type: boolean
        description: Include unavailable bundles (admin only)
    responses:
      200:
        description: List of bundles
        schema:
          type: object
          properties:
            bundles:
              type: array
              items:
                type: object
      500:
        description: Server error
    """
    try:
        user_id = get_user_id()
        service = BundleService(user_id)

        include_unavailable = request.args.get('include_unavailable', 'false').lower() == 'true'

        # Only admins can see unavailable bundles
        if include_unavailable and user_id:
            try:
                service.validate_admin()
            except ValueError:
                include_unavailable = False

        bundles = service.get_all_bundles(include_unavailable=include_unavailable)

        return jsonify({"bundles": bundles}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bundle_bp.route('/bundles/<int:bundle_id>', methods=['GET'])
def get_bundle(bundle_id):
    """
    Get Specific Snack Bundle
    ---
    tags: [Snack Bundles]
    description: Retrieves a specific snack bundle by ID.
    parameters:
      - in: path
        name: bundle_id
        type: integer
        required: true
        description: The bundle ID
    responses:
      200:
        description: Bundle details
        schema:
          type: object
      404:
        description: Bundle not found
      500:
        description: Server error
    """
    try:
        user_id = get_user_id()
        service = BundleService(user_id)

        bundle = service.get_bundle_by_id(bundle_id)

        return jsonify(bundle), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bundle_bp.route('/bundles/<int:bundle_id>', methods=['PUT'])
def update_bundle(bundle_id):
    """
    Update Snack Bundle
    ---
    tags: [Snack Bundles]
    description: Updates an existing snack bundle. Requires admin authentication.
    parameters:
      - in: path
        name: bundle_id
        type: integer
        required: true
        description: The bundle ID to update
      - in: body
        name: bundle_data
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            total_price:
              type: number
            discount_percentage:
              type: number
            product_items:
              type: array
              items:
                type: object
                properties:
                  product_id: {type: integer}
                  quantity: {type: integer}
            is_available:
              type: boolean
    responses:
      200:
        description: Bundle updated successfully
      403:
        description: Unauthorized (not admin)
      404:
        description: Bundle not found
      500:
        description: Server error
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        service = BundleService(user_id)
        data = request.json

        bundle = service.update_bundle(
            bundle_id=bundle_id,
            name=data.get('name'),
            description=data.get('description'),
            original_price=data.get('original_price'),
            product_items=data.get('product_items'),
            is_available=data.get('is_available')
        )

        bundle_data = service.get_bundle_by_id(bundle.id)

        return jsonify({
            "message": "Bundle updated successfully",
            "bundle": bundle_data
        }), 200

    except ValueError as e:
        if "not found" in str(e):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bundle_bp.route('/bundles/<int:bundle_id>', methods=['DELETE'])
def delete_bundle(bundle_id):
    """
    Delete Snack Bundle
    ---
    tags: [Snack Bundles]
    description: Deletes a snack bundle. Requires admin authentication.
    parameters:
      - in: path
        name: bundle_id
        type: integer
        required: true
        description: The bundle ID to delete
    responses:
      200:
        description: Bundle deleted successfully
      403:
        description: Unauthorized (not admin)
      404:
        description: Bundle not found
      500:
        description: Server error
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        service = BundleService(user_id)
        service.delete_bundle(bundle_id)

        return jsonify({"message": "Bundle deleted successfully"}), 200

    except ValueError as e:
        if "not found" in str(e):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bundle_bp.route('/bundles/<int:bundle_id>/toggle', methods=['PATCH'])
def toggle_bundle_availability(bundle_id):
    """
    Toggle Bundle Availability
    ---
    tags: [Snack Bundles]
    description: Toggles a bundle's availability status. Requires admin authentication.
    parameters:
      - in: path
        name: bundle_id
        type: integer
        required: true
        description: The bundle ID
    responses:
      200:
        description: Bundle availability toggled successfully
        schema:
          type: object
          properties:
            message: {type: string}
            is_available: {type: boolean}
      403:
        description: Unauthorized (not admin)
      404:
        description: Bundle not found
      500:
        description: Server error
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        service = BundleService(user_id)
        bundle = service.toggle_availability(bundle_id)

        return jsonify({
            "message": "Bundle availability toggled successfully",
            "is_available": bundle.is_available
        }), 200

    except ValueError as e:
        if "not found" in str(e):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500
