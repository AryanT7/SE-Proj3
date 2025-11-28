from app.models import *
from app.app import db
from mistralai import Mistral
import os
import json
from typing import Dict, List

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class RecommendationService:
    """Service layer for generating personalized menu recommendations using Mistral LLM."""
    
    def __init__(self):
        """Initialize the recommendation service with Mistral API client."""
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-medium"  # or "mistral-small"
    
    def _get_user_order_history(self, user_id: int) -> List[Dict]:
        """Retrieve user's past order history with items."""
        from app.services.customer_service import CustomerService
        customer_service = CustomerService()
        
        deliveries = customer_service.get_all_deliveries(user_id=user_id)
        order_history = []
        
        for delivery in deliveries:
            delivery_items = DeliveryItems.query.filter_by(delivery_id=delivery.id).all()
            items = []
            
            for di in delivery_items:
                cart_item = CartItems.query.filter_by(id=di.cart_item_id).first()
                if cart_item:
                    if cart_item.product_id:
                        product = Products.query.get(cart_item.product_id)
                        if product:
                            items.append(f"{product.name} ({product.category})")
                    elif cart_item.bundle_id:
                        bundle = SnackBundles.query.get(cart_item.bundle_id)
                        if bundle:
                            items.append(f"{bundle.name} (Bundle)")
            
            if items:
                order_history.append({
                    'date': delivery.date_added.isoformat() if delivery.date_added else "Unknown",
                    'items': items
                })
        
        print(order_history)
        
        return order_history
    
    def _get_menu_items(self) -> Dict:
        """Retrieve all available menu items and bundles."""
        products = Products.query.filter_by(is_available=True).all()
        products_data = [f"{p.name} (${p.unit_price})" for p in products]
        
        from app.services.bundle_service import BundleService
        bundle_service = BundleService()
        bundles = bundle_service.get_all_bundles(include_unavailable=False)
        bundles_data = [f"{b['name']} (${b['total_price']})" for b in bundles]
        
        
        return {
            'products': products_data,
            'bundles': bundles_data
        }
    
    def _format_prompt(self, menu_data: Dict, order_history: List[Dict]) -> str:
        """Format the prompt for Mistral LLM to request ONLY text."""
        prompt = """You are a friendly and helpful assistant for a movie theater concession stand. 
Your task is to provide a short, personalized paragraph recommending food and snacks based on a customer's order history.

AVAILABLE MENU:

Products: """ + ", ".join(menu_data['products']) + """

Bundles: """ + ", ".join(menu_data['bundles']) + """

CUSTOMER ORDER HISTORY:

"""
        if order_history:
            for order in order_history[-5:]:  # Limit to last 5 orders for brevity
                prompt += f"- Date {order['date']}: {', '.join(order['items'])}\n"
        else:
            prompt += "No previous orders (New Customer).\n"
        
        prompt += """
Based on this history, write a friendly recommendation. 
- If they are a new customer, recommend a popular bundle.
- If they have history, suggest something similar or complementary to what they usually get.
- Do not simply list items; write it as a natural conversation.

REQUIRED OUTPUT FORMAT:

You must respond with a valid JSON object containing a single key "recommendations".

Example:
{
  "recommendations": "Since you usually enjoy popcorn, we recommend trying our new sweet and salty combo!"
}
"""
        return prompt
    
    def get_recommendations(self, user_id: int) -> Dict:
        """Generate text-based personalized recommendations."""
        # Validate customer exists
        customer = Customers.query.filter_by(user_id=user_id).first()
        if not customer:
            raise ValueError(f"Customer with user_id {user_id} not found")
        
        # Get menu data and order history
        menu_data = self._get_menu_items()
        order_history = self._get_user_order_history(user_id)
        
        # Format prompt
        prompt = self._format_prompt(menu_data, order_history)
        
        try:
            # Call Mistral API
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse response
            content = response.choices[0].message.content
            parsed_response = json.loads(content)
            
            # Return simple text structure
            return {
                'type': 'text',
                'recommendations': parsed_response.get('recommendations', "Check out our latest menu items!")
            }
                
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw content if possible
            return {
                'type': 'text',
                'recommendations': content if 'content' in locals() else "We recommend checking out our bundles tab!"
            }
        except Exception as e:
            # Return a fallback message instead of crashing
            return {
                'type': 'text',
                'recommendations': "We're having trouble reaching our AI chef right now, but our Popcorn Combo is always a winner!"
            }


# from app.models import *
# from app.app import db
# from mistralai import Mistral
# import os
# import json
# from typing import Dict, List, Optional
# # backend/app/app.py

# from dotenv import load_dotenv
# import os

# load_dotenv() # This loads the variables

# # --- ADD THESE 3 LINES FOR DEBUGGING ---
# print("--- DEBUG ENV CHECK ---")
# print(f"Current Working Directory: {os.getcwd()}")
# print(f"Mistral Key found: {'Yes' if os.getenv('MISTRAL_API_KEY') else 'No'}")
# # ---------------------------------------


# class RecommendationService:
#     """Service layer for generating personalized menu recommendations using Mistral LLM."""
    
#     def __init__(self):
#         """Initialize the recommendation service with Mistral API client."""
#         api_key = os.getenv('MISTRAL_API_KEY')
#         if not api_key:
#             raise ValueError("MISTRAL_API_KEY environment variable not set")
#         self.client = Mistral(api_key=api_key)
#         self.model = "mistral-medium"  # or "mistral-small" for faster/cheaper
    
#     def _get_user_order_history(self, user_id: int) -> List[Dict]:
#         """Retrieve user's past order history with items.
        
#         Args:
#             user_id: Customer user ID.
            
#         Returns:
#             List of order dictionaries with items.
#         """
#         from app.services.customer_service import CustomerService
#         customer_service = CustomerService()
        
#         deliveries = customer_service.get_all_deliveries(user_id=user_id)
#         order_history = []
        
#         for delivery in deliveries:
#             # Get delivery items
#             delivery_items = DeliveryItems.query.filter_by(delivery_id=delivery.id).all()
#             items = []
            
#             for di in delivery_items:
#                 cart_item = CartItems.query.filter_by(id=di.cart_item_id).first()
#                 if cart_item:
#                     if cart_item.product_id:
#                         product = Products.query.get(cart_item.product_id)
#                         if product:
#                             items.append({
#                                 'type': 'product',
#                                 'id': product.id,
#                                 'name': product.name,
#                                 'category': product.category,
#                                 'quantity': cart_item.quantity
#                             })
#                     elif cart_item.bundle_id:
#                         bundle = SnackBundles.query.get(cart_item.bundle_id)
#                         if bundle:
#                             items.append({
#                                 'type': 'bundle',
#                                 'id': bundle.id,
#                                 'name': bundle.name,
#                                 'quantity': cart_item.quantity
#                             })
            
#             if items:
#                 order_history.append({
#                     'delivery_id': delivery.id,
#                     'date': delivery.date_added.isoformat() if delivery.date_added else None,
#                     'items': items
#                 })
        
#         return order_history
    
#     def _get_menu_items(self) -> Dict:
#         """Retrieve all available menu items and bundles.
        
#         Returns:
#             Dictionary with 'products' and 'bundles' lists.
#         """
#         # Get all available products
#         products = Products.query.filter_by(is_available=True).all()
#         products_data = []
#         for product in products:
#             products_data.append({
#                 'id': product.id,
#                 'name': product.name,
#                 'category': product.category,
#                 'price': float(product.unit_price),
#                 'size': product.size,
#                 'keywords': product.keywords
#             })
        
#         # Get all available bundles
#         from app.services.bundle_service import BundleService
#         bundle_service = BundleService()
#         bundles_data = bundle_service.get_all_bundles(include_unavailable=False)
        
#         return {
#             'products': products_data,
#             'bundles': bundles_data
#         }
    
#     def _format_prompt(self, menu_data: Dict, order_history: List[Dict]) -> str:
#         """Format the prompt for Mistral LLM.
        
#         Args:
#             menu_data: Dictionary with products and bundles.
#             order_history: List of past orders.
            
#         Returns:
#             Formatted prompt string.
#         """
#         prompt = """You are a helpful assistant for a movie theater concession stand. 
# Your task is to provide personalized food and snack recommendations based on a customer's order history.

# MENU ITEMS:
# """
#         # Add products
#         prompt += "\nPRODUCTS:\n"
#         for product in menu_data['products']:
#             prompt += f"- ID: {product['id']}, Name: {product['name']}, Category: {product['category']}, Price: ${product['price']:.2f}"
#             if product.get('size'):
#                 prompt += f", Size: {product['size']}"
#             if product.get('keywords'):
#                 prompt += f", Keywords: {product['keywords']}"
#             prompt += "\n"
        
#         # Add bundles
#         prompt += "\nBUNDLES/COMBOS:\n"
#         for bundle in menu_data['bundles']:
#             prompt += f"- ID: {bundle['id']}, Name: {bundle['name']}, Description: {bundle.get('description', 'N/A')}, Price: ${bundle['total_price']:.2f}"
#             prompt += f", Items: {', '.join([item['product_name'] for item in bundle.get('items', [])])}\n"
        
#         # Add order history
#         if order_history:
#             prompt += "\nCUSTOMER ORDER HISTORY:\n"
#             for order in order_history[-10:]:  # Last 10 orders
#                 prompt += f"Order from {order.get('date', 'N/A')}:\n"
#                 for item in order['items']:
#                     if item['type'] == 'product':
#                         prompt += f"  - {item['name']} (Category: {item['category']}) x{item['quantity']}\n"
#                     else:
#                         prompt += f"  - {item['name']} (Bundle) x{item['quantity']}\n"
#         else:
#             prompt += "\nCUSTOMER ORDER HISTORY: No previous orders (new customer)\n"
        
#         prompt += """
# Based on the customer's order history and available menu items, provide personalized recommendations.

# Please respond in JSON format with one of these two structures:

# OPTION 1 - Text-based recommendations:
# {
#   "type": "text",
#   "recommendations": "A friendly text description of recommended items and why they might like them"
# }

# OPTION 2 - Item ID-based recommendations:
# {
#   "type": "items",
#   "recommendations": [
#     {"type": "product", "id": 123, "reason": "why this product"},
#     {"type": "bundle", "id": 456, "reason": "why this bundle"}
#   ]
# }

# Prefer OPTION 2 (item IDs) when you can identify specific items. Use OPTION 1 (text) for general suggestions or when explaining categories.
# Provide 3-5 specific recommendations when using item IDs.
# """
#         return prompt
    
#     def get_recommendations(self, user_id: int) -> Dict:
#         """Generate personalized recommendations for a user.
        
#         Args:
#             user_id: Customer user ID.
            
#         Returns:
#             Dictionary with recommendations (either text or item IDs).
            
#         Raises:
#             ValueError: If user is not a customer or if API call fails.
#         """
#         # Validate customer exists
#         customer = Customers.query.filter_by(user_id=user_id).first()
#         if not customer:
#             raise ValueError(f"Customer with user_id {user_id} not found")
        
#         # Get menu data and order history
#         menu_data = self._get_menu_items()
#         order_history = self._get_user_order_history(user_id)
        
#         # Format prompt
#         prompt = self._format_prompt(menu_data, order_history)
        
#         try:
#             # Call Mistral API
#             response = self.client.chat.complete(
#                 model=self.model,
#                 messages=[
#                     {"role": "user", "content": prompt}
#                 ],
#                 response_format={"type": "json_object"}  # Force JSON response
#             )
            
#             # Parse response
#             content = response.choices[0].message.content
#             recommendations = json.loads(content)
            
#             # Validate and enrich recommendations
#             if recommendations.get('type') == 'items':
#                 # Validate that recommended IDs exist
#                 validated_items = []
#                 for item in recommendations.get('recommendations', []):
#                     item_type = item.get('type')
#                     item_id = item.get('id')
                    
#                     if item_type == 'product':
#                         product = Products.query.get(item_id)
#                         if product and product.is_available:
#                             validated_items.append({
#                                 'type': 'product',
#                                 'id': item_id,
#                                 'name': product.name,
#                                 'category': product.category,
#                                 'price': float(product.unit_price),
#                                 'reason': item.get('reason', '')
#                             })
#                     elif item_type == 'bundle':
#                         bundle = SnackBundles.query.get(item_id)
#                         if bundle and bundle.is_available:
#                             validated_items.append({
#                                 'type': 'bundle',
#                                 'id': item_id,
#                                 'name': bundle.name,
#                                 'price': float(bundle.total_price),
#                                 'reason': item.get('reason', '')
#                             })
                
#                 return {
#                     'type': 'items',
#                     'recommendations': validated_items
#                 }
#             else:
#                 # Text-based recommendations
#                 return {
#                     'type': 'text',
#                     'recommendations': recommendations.get('recommendations', 'No recommendations available.')
#                 }
                
#         except json.JSONDecodeError:
#             # If JSON parsing fails, return as text
#             return {
#                 'type': 'text',
#                 'recommendations': content if 'content' in locals() else 'Unable to generate recommendations at this time.'
#             }
#         except Exception as e:
#             raise ValueError(f"Failed to generate recommendations: {str(e)}")