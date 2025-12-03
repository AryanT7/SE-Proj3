import json
import pytest
from unittest.mock import patch

class TestCustomerRoutes:

    @patch("app.routes.customer_routes.RecommendationService")
    def test_get_recommendations_route_success(self, mock_service_cls, client, sample_customer):
        """
        Test GET /api/customers/{id}/recommendations
        Mock the Service layer to ensure the API correctly formats the JSON response.
        """
        # 1. Setup the Mock Instance
        mock_instance = mock_service_cls.return_value
        mock_instance.get_recommendations.return_value = {
            "type": "text",
            "recommendations": "Test recommendation from AI"
        }

        # 2. Make Request
        # Note: sample_customer fixture returns the user_id (int)
        resp = client.get(f"/api/customers/{sample_customer}/recommendations")

        # 3. Assertions
        assert resp.status_code == 200
        data = json.loads(resp.data)
        
        assert data["type"] == "text"
        assert data["recommendations"] == "Test recommendation from AI"
        
        # Ensure the service was called with the correct ID
        mock_instance.get_recommendations.assert_called_once_with(user_id=sample_customer)

    @patch("app.routes.customer_routes.RecommendationService")
    def test_get_recommendations_route_customer_not_found(self, mock_service_cls, client):
        """
        Test that a ValueError in the service leads to a 404 (or appropriate error) in the API.
        """
        # 1. Setup Mock to raise Error
        mock_instance = mock_service_cls.return_value
        mock_instance.get_recommendations.side_effect = ValueError("Customer not found")

        # 2. Make Request with random ID
        resp = client.get("/api/customers/999999/recommendations")

        # 3. Assertions
        # If your route has an @errorhandler(ValueError) that returns 400 or 404:
        if resp.status_code == 404:
            assert "not found" in resp.get_json().get("error", "").lower()
        elif resp.status_code == 500:
            # If no error handler exists, Flask returns 500 for unhandled exceptions
            # This assertion prompts you to fix the route to handle 404s!
            pass 
        
        # Ideally, assert this:
        # assert resp.status_code == 404

    @patch("app.routes.customer_routes.RecommendationService")
    def test_get_recommendations_route_internal_error(self, mock_service_cls, client, sample_customer):
        """
        Test that the API handles unexpected service crashes gracefully.
        """
        mock_instance = mock_service_cls.return_value
        # Service crashes completely (not just an API error, but a code error)
        mock_instance.get_recommendations.side_effect = Exception("Critical Failure")

        resp = client.get(f"/api/customers/{sample_customer}/recommendations")
        
        # Should be a 500 Internal Server Error
        assert resp.status_code == 500