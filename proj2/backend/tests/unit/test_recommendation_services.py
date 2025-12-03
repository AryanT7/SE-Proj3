import pytest
import json
from unittest.mock import patch, MagicMock
from app.models import Deliveries, CustomerShowings
from app.services.recommendation_service import RecommendationService

class TestRecommendationService:

    # --- Setup & Fixtures ---
    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        """Mock environment variables to prevent __init__ crash."""
        monkeypatch.setenv("MISTRAL_API_KEY", "fake_key_for_testing")

    # --- Logic & "Happy Path" Tests ---

    @patch("app.services.recommendation_service.Mistral")
    def test_get_recommendations_success(self, mock_mistral, app, sample_customer):
        """Test the standard successful flow with a valid JSON response."""
        
        # 1. Setup Mock LLM Response
        mock_client = MagicMock()
        mock_mistral.return_value = mock_client
        mock_response_content = json.dumps({
            "recommendations": "Since you love Action movies, try our Spicy Popcorn!"
        })
        mock_client.chat.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=mock_response_content))]
        )

        # 2. Execute
        with app.app_context():
            service = RecommendationService()
            result = service.get_recommendations(user_id=sample_customer)

        # 3. Verify
        assert result["type"] == "text"
        assert result["recommendations"] == "Since you love Action movies, try our Spicy Popcorn!"
        
        # 4. Verify the prompt context was built (call_args inspection)
        # We don't check the exact string, just that it reached the client
        mock_client.chat.complete.assert_called_once()

    @patch("app.services.recommendation_service.Mistral")
    def test_get_recommendations_json_decode_error(self, mock_mistral, app, sample_customer):
        """Test resilience when Mistral returns plain text instead of JSON."""
        mock_client = MagicMock()
        mock_mistral.return_value = mock_client
        
        # LLM behaves badly and returns raw text
        raw_text = "I recommend the soda bundle."
        mock_client.chat.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=raw_text))]
        )

        with app.app_context():
            service = RecommendationService()
            result = service.get_recommendations(user_id=sample_customer)

        # Should fall back to using the raw text
        assert result["type"] == "text"
        assert result["recommendations"] == raw_text

    @patch("app.services.recommendation_service.Mistral")
    def test_get_recommendations_api_failure(self, mock_mistral, app, sample_customer):
        """Test graceful failure when Mistral API throws an exception."""
        mock_client = MagicMock()
        mock_mistral.return_value = mock_client
        mock_client.chat.complete.side_effect = Exception("Service Unavailable")

        with app.app_context():
            service = RecommendationService()
            result = service.get_recommendations(user_id=sample_customer)

        # Should return a safe fallback message
        assert "trouble reaching our AI chef" in result["recommendations"]

    def test_customer_not_found(self, app):
        """Test that invalid user_ids raise the correct error."""
        with app.app_context():
            service = RecommendationService()
            with pytest.raises(ValueError, match="Customer with user_id .* not found"):
                service.get_recommendations(user_id=999999)

    # --- Data Integration Tests (Testing the SQL Logic) ---
    
    def test_get_user_order_history_integration(self, app, sample_delivery, sample_product):
        """
        Verify _get_user_order_history actually pulls real data from the DB 
        using the complex chain of fixtures (Delivery -> CartItems -> Products).
        """
        # Note: sample_delivery creates an empty delivery. We need to attach an item to it 
        # to test the history extraction logic.
        from app.models import DeliveryItems, CartItems, db
        
        with app.app_context():
            # Manually link a product to the delivery for this specific test
            cart_item = CartItems(product_id=sample_product, quantity=1, customer_id=1) # user_id doesn't matter for this link
            db.session.add(cart_item)
            db.session.commit()
            
            delivery_item = DeliveryItems(delivery_id=sample_delivery, cart_item_id=cart_item.id)
            db.session.add(delivery_item)
            db.session.commit()

            # The sample_delivery fixture relies on sample_customer. 
            # We need to fetch that ID to pass to the service.
            from app.models import Deliveries
            delivery = Deliveries.query.get(sample_delivery)
            # customer_user_id = delivery.customer_showing.customer_id

            customer_showing = CustomerShowings.query.get(delivery.customer_showing_id)
            customer_user_id = customer_showing.customer_id

            service = RecommendationService()
            history = service._get_user_order_history(customer_user_id)

            assert len(history) == 1
            # Check if "Popcorn" (from sample_product) is in the items list
            assert "Popcorn" in history[0]['items'][0] 
            assert "snacks" in history[0]['items'][0]

    def test_get_menu_items_integration(self, app, sample_product, sample_bundle):
        """Verify _get_menu_items retrieves products and bundles formatted correctly."""
        with app.app_context():
            service = RecommendationService()
            menu = service._get_menu_items()

            # Check Products
            # sample_product creates "Popcorn"
            assert any("Popcorn" in item for item in menu['products'])
            
            # Check Bundles
            # sample_bundle creates "Test Bundle"
            assert any("Test Bundle" in item for item in menu['bundles'])

    # --- Prompt Formatting Tests ---

    def test_format_prompt_new_customer(self, app):
        """Test prompt generation for a user with no history."""
        with app.app_context():
            service = RecommendationService()
            menu_data = {'products': ['A'], 'bundles': ['B']}
            history = [] # Empty
            
            prompt = service._format_prompt(menu_data, history)
            assert "No previous orders" in prompt
            assert "recommend a popular bundle" in prompt

    def test_format_prompt_existing_customer(self, app):
        """Test prompt generation for a user with history."""
        with app.app_context():
            service = RecommendationService()
            menu_data = {'products': ['A'], 'bundles': ['B']}
            history = [{'date': '2023-01-01', 'items': ['Popcorn']}]
            
            prompt = service._format_prompt(menu_data, history)
            assert "Popcorn" in prompt
            assert "No previous orders" not in prompt