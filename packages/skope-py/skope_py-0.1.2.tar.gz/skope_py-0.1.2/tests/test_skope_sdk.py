import pytest
from unittest.mock import Mock, patch
import requests
from skope import Skope, CreateEventRequest


class TestCreateEventRequest:
    def test_event_creation(self):
        event = CreateEventRequest(
            user_id="customer_123",
            unit="requests",
            value=10,
        )
        assert event.user_id == "customer_123"
        assert event.unit == "requests"
        assert event.value == 10

    def test_event_creation_with_properties(self):
        event = CreateEventRequest(
            user_id="customer_123",
            unit="requests",
            value=10,
            properties={"region": "us-east-1"}
        )
        assert event.properties == {"region": "us-east-1"}

class TestSkope:
    def test_client_initialization_default_url(self):
        client = Skope("test_api_key")
        assert client.base_url == "https://api.useskope.com"
        assert client.session.headers["x-api-key"] == "test_api_key"
        assert client.session.headers["Content-Type"] == "application/json"
        # Test that namespaced APIs are initialized
        assert client.events is not None
        assert client.invoices is not None
        assert client.pricing_rules is not None

    def test_client_initialization_custom_url(self):
        custom_url = "https://custom.api.com/"
        client = Skope("test_key", custom_url)
        assert client.base_url == "https://custom.api.com"

    @patch('skope.requests.Session.post')
    def test_events_create_success(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "events_processed": 2}
        mock_post.return_value = mock_response

        client = Skope("test_key")
        events = [
            CreateEventRequest(user_id="cust1", unit="units", value=10),
            CreateEventRequest(user_id="cust2", unit="requests", value=20)
        ]

        result = client.events.create(events)

        mock_post.assert_called_once_with(
            "https://api.useskope.com/v1/events",
            json=[
                {"user_id": "cust1", "unit": "units", "value": 10, "properties": None},
                {"user_id": "cust2", "unit": "requests", "value": 20, "properties": None}
            ]
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == {"success": True, "events_processed": 2}

    @patch('skope.requests.Session.post')
    def test_events_create_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
        mock_post.return_value = mock_response

        client = Skope("test_key")
        events = [CreateEventRequest(user_id="cust", unit="units", value=10)]

        with pytest.raises(requests.exceptions.HTTPError):
            client.events.create(events)

    def test_events_create_empty_list(self):
        with patch('skope.requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"success": True, "events_processed": 0}
            mock_post.return_value = mock_response

            client = Skope("test_key")
            result = client.events.create([])

            mock_post.assert_called_once_with(
                "https://api.useskope.com/v1/events",
                json=[]
            )
            assert result == {"success": True, "events_processed": 0}

    @patch('skope.requests.Session.get')
    def test_events_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "event_123",
                    "created_at": "2023-01-01T00:00:00Z",
                    "pricing_rule_id": "rule_123",
                    "value": 10.0,
                    "pricing_rule": {
                        "id": "rule_123",
                        "created_at": "2023-01-01T00:00:00Z",
                        "unit": {
                            "id": "unit_123",
                            "created_at": "2023-01-01T00:00:00Z",
                            "organization_id": "org_123",
                            "type": "usage",
                            "name": "API Requests",
                            "tag": "requests"
                        }
                    },
                    "user_name": "Test User"
                }
            ]
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.events.get()

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/events",
            params={}
        )
        mock_response.raise_for_status.assert_called_once()
        assert len(result) == 1
        assert result[0].id == "event_123"
        assert result[0].user_name == "Test User"

    @patch('skope.requests.Session.get')
    def test_events_get_with_user_id(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        client = Skope("test_key")
        client.events.get(user_id="test_user")

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/events",
            params={"user_id": "test_user"}
        )

    @patch('skope.requests.Session.get')
    def test_invoices_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "inv_123",
                    "created_at": "2023-01-01T00:00:00Z",
                    "relationship_id": "rel_123",
                    "status": "paid",
                    "amount": 100.0,
                    "period_start": "2023-01-01T00:00:00Z",
                    "period_end": "2023-01-31T23:59:59Z",
                    "source": "skope",
                    "user_name": "Test User"
                }
            ]
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.invoices.get()

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/invoices",
            params={}
        )
        assert len(result) == 1
        assert result[0].id == "inv_123"
        assert result[0].status == "paid"

    @patch('skope.requests.Session.get')
    def test_pricing_rules_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.pricing_rules.get()

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/pricing-rules",
            params={}
        )
        assert result == []

    @patch('skope.requests.Session.get')
    def test_pricing_rules_get_usage_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "used": 50,
                "remaining": 50,
                "limit": 100
            }
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.pricing_rules.get_usage("user_123", "requests")

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/pricing-rules/usage",
            params={"user_id": "user_123", "unit": "requests"}
        )
        assert result.used == 50
        assert result.remaining == 50
        assert result.limit == 100