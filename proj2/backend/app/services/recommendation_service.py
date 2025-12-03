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
        print("Priting bundles data:", bundles_data)
        
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


