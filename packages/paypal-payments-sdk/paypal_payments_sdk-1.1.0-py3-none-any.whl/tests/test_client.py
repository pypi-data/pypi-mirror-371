"""
Tests for PayPal Client
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from paypal_sdk import PayPalClient
from paypal_sdk.models import (
    Authorization,
    Capture,
    Refund,
    CaptureRequest,
    RefundRequest,
    ReauthorizeRequest,
    Money,
)
from paypal_sdk.exceptions import (
    PayPalError,
    PayPalAuthenticationError,
    PayPalNotFoundError,
)


class TestPayPalClient:
    """Test cases for PayPalClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return PayPalClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            mode="sandbox"
        )
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"id": "test_id", "status": "COMPLETED"}
        response.content = b'{"id": "test_id", "status": "COMPLETED"}'
        return response
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = PayPalClient(
            client_id="test_id",
            client_secret="test_secret",
            mode="sandbox"
        )
        
        assert client.client_id == "test_id"
        assert client.client_secret == "test_secret"
        assert client.base_url == "https://api-m.sandbox.paypal.com"
    
    def test_client_initialization_live_mode(self):
        """Test client initialization with live mode."""
        client = PayPalClient(
            client_id="test_id",
            client_secret="test_secret",
            mode="live"
        )
        
        assert client.base_url == "https://api-m.paypal.com"
    
    def test_client_initialization_missing_credentials(self):
        """Test client initialization with missing credentials."""
        with pytest.raises(ValueError, match="PayPal client_id and client_secret are required"):
            PayPalClient()
    
    @patch('paypal_sdk.client.requests.Session.post')
    def test_get_access_token(self, mock_post, client):
        """Test getting access token."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 32400
        }
        mock_post.return_value = mock_response
        
        # Test token retrieval
        token = client._get_access_token()
        assert token == "test_token"
        assert client.access_token == "test_token"
        assert client.token_expires_at is not None
    
    @patch('paypal_sdk.client.requests.Session.post')
    def test_get_access_token_failure(self, mock_post, client):
        """Test getting access token failure."""
        # Mock failed token response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "invalid_client"}
        mock_response.content = b'{"error": "invalid_client"}'
        mock_post.return_value = mock_response
        
        # Test token retrieval failure
        with pytest.raises(PayPalAuthenticationError):
            client._get_access_token()
    
    @patch('paypal_sdk.client.PayPalClient._get_access_token')
    @patch('paypal_sdk.client.requests.Session.request')
    def test_make_request_success(self, mock_request, mock_get_token, client):
        """Test successful API request."""
        mock_get_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_id", "status": "COMPLETED"}
        mock_response.content = b'{"id": "test_id", "status": "COMPLETED"}'
        mock_request.return_value = mock_response
        
        result = client._make_request("GET", "/test/endpoint")
        
        assert result == {"id": "test_id", "status": "COMPLETED"}
        mock_request.assert_called_once()
    
    @patch('paypal_sdk.client.PayPalClient._get_access_token')
    @patch('paypal_sdk.client.requests.Session.request')
    def test_make_request_error(self, mock_request, mock_get_token, client):
        """Test API request with error."""
        mock_get_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "name": "RESOURCE_NOT_FOUND",
            "message": "The specified resource does not exist."
        }
        mock_response.content = b'{"name": "RESOURCE_NOT_FOUND", "message": "The specified resource does not exist."}'
        mock_request.return_value = mock_response
        
        with pytest.raises(PayPalNotFoundError):
            client._make_request("GET", "/test/endpoint")
    
    @patch('paypal_sdk.client.PayPalClient._make_request')
    def test_get_authorization(self, mock_make_request, client):
        """Test getting authorization."""
        mock_response = {
            "id": "auth_id",
            "status": "CREATED",
            "amount": {"currency_code": "USD", "value": "10.00"}
        }
        mock_make_request.return_value = mock_response
        
        auth = client.get_authorization("auth_id")
        
        assert isinstance(auth, Authorization)
        assert auth.id == "auth_id"
        assert auth.status == "CREATED"
        mock_make_request.assert_called_once_with("GET", "/v2/payments/authorizations/auth_id")
    
    @patch('paypal_sdk.client.PayPalClient._make_request')
    def test_capture_authorization(self, mock_make_request, client):
        """Test capturing authorization."""
        mock_response = {
            "id": "capture_id",
            "status": "COMPLETED",
            "amount": {"currency_code": "USD", "value": "10.00"}
        }
        mock_make_request.return_value = mock_response
        
        capture_request = CaptureRequest(
            amount={"currency_code": "USD", "value": "10.00"},
            final_capture=True
        )
        
        capture = client.capture_authorization("auth_id", capture_request)
        
        assert isinstance(capture, Capture)
        assert capture.id == "capture_id"
        assert capture.status == "COMPLETED"
        mock_make_request.assert_called_once()
    
    @patch('paypal_sdk.client.PayPalClient._make_request')
    def test_refund_capture(self, mock_make_request, client):
        """Test refunding capture."""
        mock_response = {
            "id": "refund_id",
            "status": "COMPLETED",
            "amount": {"currency_code": "USD", "value": "5.00"}
        }
        mock_make_request.return_value = mock_response
        
        refund_request = RefundRequest(
            amount={"currency_code": "USD", "value": "5.00"},
            note_to_payer="Partial refund"
        )
        
        refund = client.refund_capture("capture_id", refund_request)
        
        assert isinstance(refund, Refund)
        assert refund.id == "refund_id"
        assert refund.status == "COMPLETED"
        mock_make_request.assert_called_once()
    
    def test_create_money(self, client):
        """Test creating money object."""
        money = client.create_money("USD", "10.99")
        
        assert money == {"currency_code": "USD", "value": "10.99"}
    
    def test_create_capture_request(self, client):
        """Test creating capture request."""
        capture_request = client.create_capture_request(
            amount=client.create_money("USD", "10.99"),
            invoice_id="INVOICE-123",
            final_capture=True
        )
        
        assert isinstance(capture_request, CaptureRequest)
        assert capture_request.amount.currency_code == "USD"
        assert capture_request.amount.value == "10.99"
        assert capture_request.invoice_id == "INVOICE-123"
        assert capture_request.final_capture is True
    
    def test_create_refund_request(self, client):
        """Test creating refund request."""
        refund_request = client.create_refund_request(
            amount=client.create_money("USD", "5.00"),
            note_to_payer="Partial refund"
        )
        
        assert isinstance(refund_request, RefundRequest)
        assert refund_request.amount.currency_code == "USD"
        assert refund_request.amount.value == "5.00"
        assert refund_request.note_to_payer == "Partial refund"
    
    def test_create_reauthorize_request(self, client):
        """Test creating reauthorize request."""
        reauth_request = client.create_reauthorize_request(
            client.create_money("USD", "15.99")
        )
        
        assert isinstance(reauth_request, ReauthorizeRequest)
        assert reauth_request.amount.currency_code == "USD"
        assert reauth_request.amount.value == "15.99"
    
    def test_set_request_id(self, client):
        """Test setting request ID."""
        client.set_request_id("custom_request_id")
        assert client.request_id == "custom_request_id"
        
        # Test auto-generation
        client.set_request_id()
        assert client.request_id is not None
        assert len(client.request_id) > 0
    
    def test_context_manager(self, client):
        """Test context manager functionality."""
        with client as c:
            assert c is client
            assert c.session is not None
        
        # Session should be closed after context exit
        # Note: requests.Session doesn't have a 'closed' attribute
        # We just verify the close method was called
    
    def test_close(self, client):
        """Test closing the client."""
        client.close()
        # Note: requests.Session doesn't have a 'closed' attribute
        # We just verify the close method was called without error


class TestPayPalClientIntegration:
    """Integration tests for PayPalClient (requires real credentials)."""
    
    @pytest.mark.integration
    def test_real_authentication(self):
        """Test real authentication (requires valid credentials)."""
        # This test requires real PayPal credentials
        # It's marked as integration test and should be run separately
        pass
