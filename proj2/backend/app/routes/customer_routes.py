from flask import Blueprint, request, jsonify, current_app
from app.services.customer_service import CustomerService


# Blueprint for customer-related endpoints
customer_bp = Blueprint('customer', __name__, url_prefix='/api')


# CustomerService instance
customer_service = CustomerService()


@customer_bp.route('/customers', methods=['POST'])
def create_customer():
  """
  Create Customer Account

  Register a new customer user account.
  """
  try:
    data = request.get_json()
    customer = customer_service.create_customer(
      name=data.get('name'),
      email=data.get('email'),
      phone=data.get('phone'),
      birthday=data.get('birthday'),
      password=data.get('password'),
      role=data.get('role', 'customer'),
      default_theatre_id=data.get('default_theatre_id')
    )
    return jsonify({
      'message': 'Customer created successfully',
      'customer': {
        'user_id': customer.user_id,
        'default_theatre_id': customer.default_theatre_id
      }
    }), 201
  except ValueError as e:
    return jsonify({'error': str(e)}), 400
  except Exception as e:
    return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:user_id>', methods=['GET'])
def get_customer(user_id):
    """
    Get Customer Profile
    ---
    tags: [Customer Management]
    description: Retrieves the basic customer profile details by user ID.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
    responses:
      200:
        description: Customer profile retrieved successfully
        schema: {$ref: '#/definitions/CustomerProfile'}
      404: {description: Customer not found}
    """
    try:
        customer = customer_service.get_customer(user_id=user_id)
        return jsonify({
            'user_id': customer.user_id,
            'default_theatre_id': customer.default_theatre_id
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:user_id>', methods=['DELETE'])
def delete_customer(user_id):
    """
    Delete Customer Account
    ---
    tags: [Customer Management]
    description: Deletes a customer account by user ID.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user to delete.
    responses:
      200:
        description: Customer deleted successfully
        schema:
          type: object
          properties:
            message: {type: string}
      404: {description: Customer not found}
    """
    try:
        customer_service.delete_customer(user_id)
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:user_id>/theatre', methods=['PUT'])
def update_default_theatre(user_id):
    """
    Update Default Theatre
    ---
    tags: [Customer Management]
    description: Updates the customer's default theatre ID.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
      - in: body
        name: theatre_update
        schema: {$ref: '#/definitions/TheatreUpdate'}
    responses:
      200:
        description: Default theatre updated
        schema:
          type: object
          properties:
            message: {type: string}
            customer: {$ref: '#/definitions/CustomerProfile'}
      400: {description: Invalid input}
    """
    try:
        data = request.get_json()
        new_theatre_id = data.get('theatre_id')
        customer = customer_service.update_default_theatre(user_id=user_id, new_theatre_id=new_theatre_id)
        return jsonify({
            'message': 'Default theatre updated',
            'customer': {
                'user_id': customer.user_id,
                'default_theatre_id': customer.default_theatre_id
            }
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:user_id>/payment-methods', methods=['POST'])
def add_payment_method(user_id):
    """
    Add Payment Method
    ---
    tags: [Payment Methods]
    description: Adds a new credit/debit or loyalty card payment method for a customer.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
      - in: body
        name: payment_method_details
        schema: {$ref: '#/definitions/PaymentMethodCreate'}
    responses:
      201:
        description: Payment method added
        schema:
          type: object
          properties:
            message: {type: string}
            payment_method_id: {type: integer}
      400: {description: Invalid input}
    """
    try:
        data = request.get_json()
        payment_method = customer_service.add_payment_method(
            user_id=user_id,
            card_number=data.get('card_number'),
            expiration_month=data.get('expiration_month'),
            expiration_year=data.get('expiration_year'),
            billing_address=data.get('billing_address'),
            balance=data.get('balance', 0.00),
            is_default=data.get('is_default', False)
        )
        return jsonify({
            'message': 'Payment method added',
            'payment_method_id': payment_method.id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


@customer_bp.route('/customers/<int:customer_id>/payment-methods', methods=['GET'])
def get_payment_methods(customer_id):
    """
    Get Customer Payment Methods
    ---
    tags: [Payment Methods]
    description: Retrieves all saved payment methods for a customer; returns an empty list if none are saved.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
        description: The ID of the customer user.
    responses:
      200:
        description: Payment methods retrieved
        schema:
          type: object
          properties:
            payment_methods:
              type: array
              items: {$ref: '#/definitions/PaymentMethodDetails'}
    """
    try:
        payment_methods = customer_service.get_customer_payment_methods(customer_id=customer_id)
        return jsonify({
            'payment_methods': [{
                'id': pm.id,
                'card_number': pm.card_number,
                'expiration_month': pm.expiration_month,
                'expiration_year': pm.expiration_year,
                'balance': float(pm.balance),
                'is_default': pm.is_default,
                'billing_address': pm.billing_address
            } for pm in payment_methods]
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/payment-methods/<int:payment_method_id>', methods=['DELETE'])
def delete_payment_method(payment_method_id):
    """
    Delete Payment Method
    ---
    tags: [Payment Methods]
    description: Deletes a specific payment method by its ID.
    parameters:
      - in: path
        name: payment_method_id
        type: integer
        required: true
        description: The ID of the payment method to delete.
    responses:
      200:
        description: Payment method deleted
        schema:
          type: object
          properties:
            message: {type: string}
      404: {description: Payment method not found}
    """
    try:
        customer_service.delete_payment_method(payment_method_id)
        return jsonify({'message': 'Payment method deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/payment-methods/<int:payment_method_id>/add-funds', methods=['POST'])
def add_funds(payment_method_id):
    """
    Add Funds to Payment Method
    ---
    tags: [Payment Methods]
    description: Adds funds to a payment method balance (e.g., loyalty card or store credit).
    parameters:
      - in: path
        name: payment_method_id
        type: integer
        required: true
        description: The ID of the payment method.
      - in: body
        name: fund_amount
        schema: {$ref: '#/definitions/FundAddition'}
    responses:
      200:
        description: Funds added successfully
        schema:
          type: object
          properties:
            message: {type: string}
            new_balance: {type: number, format: float}
      400: {description: Invalid amount or payment method}
    """
    try:
        data = request.get_json()
        amount = data.get('amount')
        
        payment_method = customer_service.add_funds_to_payment_method(payment_method_id, amount)
        return jsonify({
            'message': 'Funds added successfully',
            'new_balance': float(payment_method.balance)
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:customer_id>/cart', methods=['POST'])
def add_to_cart(customer_id):
    """
    Add Item to Cart
    ---
    tags: [Shopping Cart]
    description: Adds a product or bundle item to the customer's shopping cart.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
        description: The ID of the customer user.
      - in: body
        name: cart_item
        schema: {$ref: '#/definitions/CartItemCreate'}
    responses:
      201:
        description: Item added to cart
        schema:
          type: object
          properties:
            message: {type: string}
            cart_item_id: {type: integer}
      400: {description: Invalid product/bundle or quantity}
    """
    try:
        data = request.get_json()
        cart_item = customer_service.create_cart_item(
            customer_id=customer_id,
            product_id=data.get('product_id'),
            bundle_id=data.get('bundle_id'),
            quantity=data.get('quantity', 1)
        )
        return jsonify({
            'message': 'Item added to cart',
            'cart_item_id': cart_item.id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:customer_id>/cart', methods=['GET'])
def get_cart(customer_id):
    """
    Get Shopping Cart
    ---
    tags: [Shopping Cart]
    description: Retrieves all items currently in the customer's shopping cart; returns an empty list if the cart is empty.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
        description: The ID of the customer user.
    responses:
      200:
        description: Cart items retrieved successfully
        schema:
          type: object
          properties:
            items:
              type: array
              items: {$ref: '#/definitions/CartItemDetails'}
    """
    try:
        items = customer_service.get_cart_items(customer_id=customer_id) or []
        return jsonify({
            'items': [{
                'id': item.id,
                'product_id': item.product_id,
                'bundle_id': item.bundle_id,
                'quantity': item.quantity
            } for item in items]
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/cart/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    """
    Update Cart Item Quantity
    ---
    tags: [Shopping Cart]
    description: Updates the quantity of a specific item in the cart.
    parameters:
      - in: path
        name: cart_item_id
        type: integer
        required: true
        description: The ID of the cart item to update.
      - in: body
        name: quantity_update
        schema: {$ref: '#/definitions/CartItemUpdate'}
    responses:
      200:
        description: Cart item updated
        schema:
          type: object
          properties:
            message: {type: string}
            cart_item_id: {type: integer}
            new_quantity: {type: integer}
      400: {description: Invalid quantity}
      404: {description: Cart item not found}
    """
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        
        cart_item = customer_service.update_cart_item(cart_item_id, quantity)
        return jsonify({
            'message': 'Cart item updated',
            'cart_item_id': cart_item.id,
            'new_quantity': cart_item.quantity
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/cart/<int:cart_item_id>', methods=['DELETE'])
def delete_cart_item(cart_item_id):
    """
    Delete Cart Item
    ---
    tags: [Shopping Cart]
    description: Removes a specific item from the cart.
    parameters:
      - in: path
        name: cart_item_id
        type: integer
        required: true
        description: The ID of the cart item to delete.
    responses:
      200:
        description: Cart item deleted
        schema:
          type: object
          properties:
            message: {type: string}
      404: {description: Cart item not found}
    """
    try:
        customer_service.delete_cart_item(cart_item_id)
        return jsonify({'message': 'Cart item deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:user_id>/showings', methods=['POST'])
def create_customer_showing(user_id):
    """
    Book Movie Showing
    ---
    tags: [Movie Booking]
    description: Books a seat for a specific movie showing.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
      - in: body
        name: booking_details
        schema: {$ref: '#/definitions/CustomerShowingCreate'}
    responses:
      201:
        description: Showing booked successfully
        schema:
          type: object
          properties:
            message: {type: string}
            customer_showing_id: {type: integer}
      400: {description: Invalid input or seat already taken}
    """
    try:
        data = request.get_json()
        customer_showing = customer_service.create_customer_showing(
            user_id=user_id,
            movie_showing_id=data.get('movie_showing_id'),
            seat_id=data.get('seat_id')
        )
        return jsonify({
            'message': 'Showing booked successfully',
            'customer_showing_id': customer_showing.id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/deliveries', methods=['POST'])
def create_delivery():
  """
  Create Delivery Order

  Places a new delivery order based on the current cart items. Accepts optional
  coupon information (coupon_code + puzzle_token/answer) and applies it when present.
  """
  try:
    data = request.get_json()
    current_app.logger.debug(f"create_delivery payload: {data}")
    delivery = customer_service.create_delivery(
      customer_showing_id=data.get('customer_showing_id'),
      payment_method_id=data.get('payment_method_id'),
      coupon_code=data.get('coupon_code'),
      puzzle_token=data.get('puzzle_token'),
      puzzle_answer=data.get('puzzle_answer'),
      skip_puzzle=bool(data.get('skip_puzzle', False))
    )
    return jsonify({
      'message': 'Delivery created successfully',
      'delivery_id': delivery.id,
      'total_price': float(delivery.total_price),
      'delivery_status': delivery.delivery_status,
      'payment_status': delivery.payment_status,
      # Echo what the UI sent for debugging
      'coupon_code_received': data.get('coupon_code'),
      'puzzle_token_received': bool(data.get('puzzle_token')),
      'puzzle_answer_provided': data.get('puzzle_answer') is not None,
      # Show applied coupon metadata from the saved delivery
      'applied_coupon_code': delivery.coupon_code,
      'discount_amount': float(delivery.discount_amount or 0.0)
    }), 201
  except ValueError as e:
    current_app.logger.debug(f"create_delivery error payload: {data}")
    return jsonify({'error': str(e), 'payload': data}), 400
  except Exception as e:
    import traceback
    traceback.print_exc()
    current_app.logger.debug(f"create_delivery exception payload: {data}")
    return jsonify({'error': str(e), 'payload': data}), 500


@customer_bp.route('/deliveries/<int:delivery_id>/cancel', methods=['POST'])
def cancel_delivery(delivery_id):
    """
    Cancel Delivery
    ---
    tags: [Delivery Operations (Customer)]
    description: Cancels an existing delivery order.
    parameters:
      - in: path
        name: delivery_id
        type: integer
        required: true
        description: The ID of the delivery to cancel.
    responses:
      200:
        description: Delivery cancelled
        schema:
          type: object
          properties:
            message: {type: string}
            delivery_id: {type: integer}
            delivery_status: {type: string}
      400: {description: Cannot cancel delivery in current status}
      404: {description: Delivery not found}
    """
    try:
        delivery = customer_service.cancel_delivery(delivery_id)
        return jsonify({
            'message': 'Delivery cancelled',
            'delivery_id': delivery.id,
            'delivery_status': delivery.delivery_status
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/deliveries/<int:delivery_id>/rate', methods=['POST'])
def rate_delivery(delivery_id):
    """
    Rate Delivery
    ---
    tags: [Delivery Operations (Customer)]
    description: Rates a fulfilled delivery order (rating applies to the service/order).
    parameters:
      - in: path
        name: delivery_id
        type: integer
        required: true
        description: The ID of the delivery to rate.
      - in: body
        name: rating_value
        schema: {$ref: '#/definitions/DeliveryRateCustomer'}
    responses:
      200:
        description: Delivery rated
        schema:
          type: object
          properties:
            message: {type: string}
            delivery_id: {type: integer}
      400: {description: Invalid rating or delivery status is not fulfilled}
      404: {description: Delivery not found}
    """
    try:
        data = request.get_json()
        rating = data.get('rating')
        delivery = customer_service.rate_delivery(delivery_id=delivery_id, rating=rating)
        return jsonify({
            'message': 'Delivery rated',
            'delivery_id': delivery.id
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/products/menu', methods=['GET'])
def list_products():
    """
    List Available Menu Products
    ---
    tags: [Product Catalog]
    description: Retrieves a list of all currently available concession products (the menu).
    responses:
      200:
        description: Products retrieved successfully
        schema:
          type: object
          properties:
            products:
              type: array
              items: {$ref: '#/definitions/ProductMenu'}
    """
    try:
        products = customer_service.show_all_products()
        return jsonify({
            'products': [{
                'id': p.id,
                'supplier_id': p.supplier_id,
                'name': p.name,
                'unit_price': float(p.unit_price),
                'inventory_quantity': p.inventory_quantity,
                'category': p.category,
                'is_available': p.is_available
            } for p in products]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/customers/<int:user_id>/deliveries', methods=['GET'])
def get_deliveries_for_customer(user_id):
    """
    Get Customer Delivery History
    ---
    tags: [Delivery Operations (Customer)]
    description: Retrieves a list of all delivery orders associated with the customer.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
    responses:
      200:
        description: Deliveries retrieved successfully
        schema:
          type: object
          properties:
            deliveries:
              type: array
              items: {$ref: '#/definitions/DeliveryDetails'}
      404: {description: Customer not found}
    """
    try:
        deliveries = customer_service.get_all_deliveries(user_id=user_id)
        return jsonify({
            'deliveries': [{
                'id': d.id,
                'customer_showing_id': d.customer_showing_id,
                'payment_method_id': d.payment_method_id,
                'driver_id': d.driver_id,
                'staff_id': d.staff_id,
                'total_price': float(d.total_price),
                'payment_status': d.payment_status,
                'delivery_status': d.delivery_status
            } for d in deliveries]
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@customer_bp.route('/customers/<int:user_id>/showings', methods=['GET'])
def get_showings_for_customer(user_id):
    """
    List Customer Showings
    ---
    summary: List Customer Showings
    tags: [Movie Booking]
    description: Retrieves all showings for a customer, including movie title, seat (e.g., "A 10"), start time, auditorium label (e.g., "Auditorium 2"), and theatre name.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
    responses:
      200:
        description: Showings retrieved
        schema:
          type: object
          properties:
            showings:
              type: array
              items:
                type: object
                properties:
                  id: {type: integer}
                  movie_title: {type: string}
                  seat: {type: string, nullable: true}
                  start_time: {type: string, description: ISO 8601 datetime}
                  auditorium: {type: string, nullable: true}
                  theatre_name: {type: string}
      404:
        description: Customer not found
    """
    try:
      showings = customer_service.get_all_showings(user_id=user_id)
      return jsonify({
          "showings": [{
              "id": s["id"],
              "movie_title": s["movie_title"],
              "seat": s["seat"],               
              "start_time": s["start_time"],    
              "auditorium": s["auditorium"],   
              "theatre_name": s["theatre_name"],
            } for s in showings]
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route('/deliveries/<int:delivery_id>/details', methods=['GET'])
def get_delivery_details(delivery_id):
    """
    Get Delivery Details
    ---
    summary: Get Delivery Details
    tags: [Delivery Operations (Customer)]
    description: Retrieves delivery details including items, theatre information, and movie title for the given delivery.
    parameters:
      - in: path
        name: delivery_id
        type: integer
        required: true
        description: The ID of the delivery to fetch.
    responses:
      200:
        description: Delivery details retrieved
        schema:
          type: object
          properties:
            id: {type: integer}
            driver_id: {type: integer, nullable: true}
            total_price: {type: number, format: float}
            delivery_time: {type: string, nullable: true, description: ISO 8601 datetime}
            delivery_status: {type: string}
            items:
              type: array
              items:
                type: object
                properties:
                  name: {type: string, nullable: true}
                  quantity: {type: integer}
            theatre_name: {type: string, nullable: true}
            theatre_address: {type: string, nullable: true}
            movie_title: {type: string, nullable: true}
      404:
        description: Delivery not found
    """
    try:
        details = customer_service.get_delivery_details(delivery_id=delivery_id)
        return jsonify(details), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
  

@customer_bp.route('/customers/<int:user_id>/customer_showing', methods=['GET'])
def get_customer_showing(user_id):
    """
    Get Customer Showing ID
    ---
    tags: [Movie Booking]
    description: Retrieves the first customer_showing id for the specified customer.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the customer user.
    responses:
      200:
        description: Customer showing ID retrieved successfully
        schema:
          type: object
          properties:
            id: {type: integer}
      400:
        description: Invalid input or no showing found for the customer
      500:
        description: Server error while retrieving the showing ID
    """
    try:
        customer_showing = customer_service.get_customer_showing_id(user_id)
        return jsonify(customer_showing), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
