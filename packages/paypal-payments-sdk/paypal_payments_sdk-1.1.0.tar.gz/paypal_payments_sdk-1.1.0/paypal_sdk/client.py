"""
PayPal SDK Client

Main client class for interacting with PayPal Payments API v2.
"""

import os
import time
import uuid
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from .models import (
    Authorization,
    Capture,
    Refund,
    CaptureRequest,
    RefundRequest,
    ReauthorizeRequest,
    ErrorResponse,
    Money,
    SearchResponse,
    BalancesResponse,
    TransactionSearchRequest,
    BalancesRequest,
)
from .exceptions import create_paypal_error, PayPalError


class PayPalClient:
    """
    PayPal Payments API v2 client.
    
    Provides methods to interact with PayPal's payment processing APIs
    including authorizations, captures, and refunds.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        mode: str = "sandbox",
        request_id: Optional[str] = None
    ):
        """
        Initialize the PayPal client.
        
        Args:
            client_id: PayPal client ID (defaults to PAYPAL_CLIENT_ID env var)
            client_secret: PayPal client secret (defaults to PAYPAL_CLIENT_SECRET env var)
            base_url: PayPal API base URL (defaults to PAYPAL_BASE_URL env var)
            mode: API mode - 'sandbox' or 'live' (defaults to PAYPAL_MODE env var)
            request_id: Optional request ID for idempotency
        """
        # Load environment variables
        load_dotenv()
        
        # Set credentials
        self.client_id = client_id or os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("PAYPAL_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("PayPal client_id and client_secret are required")
        
        # Set base URL
        if base_url:
            self.base_url = base_url
        else:
            env_url = os.getenv("PAYPAL_BASE_URL")
            if env_url:
                self.base_url = env_url
            else:
                # Default URLs based on mode
                env_mode = mode or os.getenv("PAYPAL_MODE", "sandbox")
                if env_mode == "live":
                    self.base_url = "https://api-m.paypal.com"
                else:
                    self.base_url = "https://api-m.sandbox.paypal.com"
        
        # Set request ID
        self.request_id = request_id or os.getenv("PAYPAL_REQUEST_ID")
        
        # Initialize session and token
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "PayPal-Python-SDK/1.0.0"
        })
    
    def _get_access_token(self) -> str:
        """
        Get or refresh the OAuth access token.
        
        Returns:
            Valid access token
            
        Raises:
            PayPalAuthenticationError: If authentication fails
        """
        # Check if we have a valid token
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        # Get new token
        auth_url = f"{self.base_url}/v1/oauth2/token"
        auth_data = {
            "grant_type": "client_credentials"
        }
        
        response = self.session.post(
            auth_url,
            data=auth_data,
            auth=(self.client_id, self.client_secret)
        )
        
        if response.status_code != 200:
            error_data = response.json() if response.content else {}
            raise create_paypal_error(response.status_code, error_data)
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        
        # Set expiration time (subtract 5 minutes for safety)
        expires_in = token_data.get("expires_in", 32400)  # 9 hours default
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        
        return self.access_token
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the PayPal API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            PayPalError: If the request fails
        """
        # Get access token
        token = self._get_access_token()
        
        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {token}"
        }
        
        if self.request_id:
            request_headers["PayPal-Request-Id"] = self.request_id
        
        if headers:
            request_headers.update(headers)
        
        # Make request
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers
            )
        except requests.RequestException as e:
            raise PayPalError(f"Request failed: {str(e)}")
        
        # Handle response
        if response.status_code in (200, 201, 204):
            if response.status_code == 204:
                return {}
            return response.json() if response.content else {}
        
        # Handle errors
        error_data = response.json() if response.content else {}
        raise create_paypal_error(response.status_code, error_data)
    
    # Authorization methods
    
    def get_authorization(self, authorization_id: str) -> Authorization:
        """
        Show details for an authorized payment.
        
        Args:
            authorization_id: The PayPal-generated ID for the authorized payment
            
        Returns:
            Authorization details
            
        Raises:
            PayPalNotFoundError: If authorization not found
            PayPalError: For other errors
        """
        endpoint = f"/v2/payments/authorizations/{authorization_id}"
        response_data = self._make_request("GET", endpoint)
        return Authorization(**response_data)
    
    def capture_authorization(
        self,
        authorization_id: str,
        capture_request: CaptureRequest
    ) -> Capture:
        """
        Capture an authorized payment.
        
        Args:
            authorization_id: The PayPal-generated ID for the authorized payment
            capture_request: Capture request data
            
        Returns:
            Capture details
            
        Raises:
            PayPalError: If capture fails
        """
        endpoint = f"/v2/payments/authorizations/{authorization_id}/capture"
        response_data = self._make_request(
            "POST",
            endpoint,
            data=capture_request.model_dump(exclude_none=True)
        )
        return Capture(**response_data)
    
    def reauthorize_authorization(
        self,
        authorization_id: str,
        reauthorize_request: ReauthorizeRequest
    ) -> Authorization:
        """
        Reauthorize an authorized payment.
        
        Args:
            authorization_id: The PayPal-generated ID for the authorized payment
            reauthorize_request: Reauthorize request data
            
        Returns:
            Reauthorized authorization details
            
        Raises:
            PayPalError: If reauthorization fails
        """
        endpoint = f"/v2/payments/authorizations/{authorization_id}/reauthorize"
        response_data = self._make_request(
            "POST",
            endpoint,
            data=reauthorize_request.model_dump(exclude_none=True)
        )
        return Authorization(**response_data)
    
    def void_authorization(self, authorization_id: str) -> Optional[Authorization]:
        """
        Void an authorized payment.
        
        Args:
            authorization_id: The PayPal-generated ID for the authorized payment
            
        Returns:
            Voided authorization details (if Prefer header is set to return=representation)
            
        Raises:
            PayPalError: If void fails
        """
        endpoint = f"/v2/payments/authorizations/{authorization_id}/void"
        headers = {"Prefer": "return=representation"}
        
        try:
            response_data = self._make_request("POST", endpoint, headers=headers)
            return Authorization(**response_data) if response_data else None
        except PayPalError as e:
            # If return=minimal is used, we get 204 No Content
            if e.status_code == 204:
                return None
            raise
    
    # Capture methods
    
    def get_capture(self, capture_id: str) -> Capture:
        """
        Show captured payment details.
        
        Args:
            capture_id: The PayPal-generated ID for the captured payment
            
        Returns:
            Capture details
            
        Raises:
            PayPalNotFoundError: If capture not found
            PayPalError: For other errors
        """
        endpoint = f"/v2/payments/captures/{capture_id}"
        response_data = self._make_request("GET", endpoint)
        return Capture(**response_data)
    
    def refund_capture(
        self,
        capture_id: str,
        refund_request: Optional[RefundRequest] = None
    ) -> Refund:
        """
        Refund a captured payment.
        
        Args:
            capture_id: The PayPal-generated ID for the captured payment
            refund_request: Refund request data (optional for full refund)
            
        Returns:
            Refund details
            
        Raises:
            PayPalError: If refund fails
        """
        endpoint = f"/v2/payments/captures/{capture_id}/refund"
        
        data = None
        if refund_request:
            data = refund_request.model_dump(exclude_none=True)
        
        response_data = self._make_request("POST", endpoint, data=data)
        return Refund(**response_data)
    
    # Refund methods
    
    def get_refund(self, refund_id: str) -> Refund:
        """
        Show refund details.
        
        Args:
            refund_id: The PayPal-generated ID for the refund
            
        Returns:
            Refund details
            
        Raises:
            PayPalNotFoundError: If refund not found
            PayPalError: For other errors
        """
        endpoint = f"/v2/payments/refunds/{refund_id}"
        response_data = self._make_request("GET", endpoint)
        return Refund(**response_data)
    
    # Convenience methods
    
    def create_capture_request(
        self,
        amount: Optional[Dict[str, str]] = None,
        invoice_id: Optional[str] = None,
        final_capture: bool = True,
        note_to_payer: Optional[str] = None,
        soft_descriptor: Optional[str] = None
    ) -> CaptureRequest:
        """
        Create a capture request object.
        
        Args:
            amount: Amount with currency_code and value
            invoice_id: External invoice number
            final_capture: Whether this is the final capture
            note_to_payer: Note to the payer
            soft_descriptor: Payment descriptor on payer's statement
            
        Returns:
            CaptureRequest object
        """
        money_obj = None
        if amount:
            money_obj = Money(**amount)
        
        return CaptureRequest(
            amount=money_obj,
            invoice_id=invoice_id,
            final_capture=final_capture,
            note_to_payer=note_to_payer,
            soft_descriptor=soft_descriptor
        )
    
    def create_refund_request(
        self,
        amount: Optional[Dict[str, str]] = None,
        custom_id: Optional[str] = None,
        invoice_id: Optional[str] = None,
        note_to_payer: Optional[str] = None
    ) -> RefundRequest:
        """
        Create a refund request object.
        
        Args:
            amount: Amount with currency_code and value (optional for full refund)
            custom_id: External ID for reconciliation
            invoice_id: External invoice ID
            note_to_payer: Reason for the refund
            
        Returns:
            RefundRequest object
        """
        money_obj = None
        if amount:
            money_obj = Money(**amount)
            
        return RefundRequest(
            amount=money_obj,
            custom_id=custom_id,
            invoice_id=invoice_id,
            note_to_payer=note_to_payer
        )
    
    def create_reauthorize_request(
        self,
        amount: Dict[str, str]
    ) -> ReauthorizeRequest:
        """
        Create a reauthorize request object.
        
        Args:
            amount: Amount with currency_code and value
            
        Returns:
            ReauthorizeRequest object
        """
        money_obj = Money(**amount)
        return ReauthorizeRequest(amount=money_obj)
    
    def create_money(self, currency_code: str, value: str) -> Dict[str, str]:
        """
        Create a money object.
        
        Args:
            currency_code: Three-character ISO currency code
            value: Amount value as string
            
        Returns:
            Money object as dictionary
        """
        return {
            "currency_code": currency_code,
            "value": value
        }
    
    def set_request_id(self, request_id: Optional[str] = None) -> None:
        """
        Set or generate a request ID for idempotency.
        
        Args:
            request_id: Custom request ID (generates UUID if None)
        """
        if request_id:
            self.request_id = request_id
        else:
            self.request_id = str(uuid.uuid4())
    
    def close(self) -> None:
        """Close the client session."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # Transaction Search API Methods

    def search_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        transaction_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        transaction_status: Optional[str] = None,
        transaction_amount: Optional[str] = None,
        transaction_currency: Optional[str] = None,
        payment_instrument_type: Optional[str] = None,
        store_id: Optional[str] = None,
        terminal_id: Optional[str] = None,
        fields: Optional[str] = "transaction_info",
        balance_affecting_records_only: Optional[str] = "Y",
        page_size: Optional[int] = 100,
        page: Optional[int] = 1
    ) -> SearchResponse:
        """
        Search for transactions.
        
        Args:
            start_date: Start date and time in ISO format
            end_date: End date and time in ISO format
            transaction_id: PayPal transaction ID (17-19 characters)
            transaction_type: Transaction event code
            transaction_status: Transaction status (D, P, S, V)
            transaction_amount: Amount range (e.g., "500 TO 1005")
            transaction_currency: Three-character ISO currency code
            payment_instrument_type: Payment instrument type (CREDITCARD, DEBITCARD)
            store_id: Store ID
            terminal_id: Terminal ID
            fields: Fields to include in response
            balance_affecting_records_only: Y for balance transactions only, N for all
            page_size: Number of items per page (1-500)
            page: Page number (1-based)
            
        Returns:
            SearchResponse object
        """
        # Build request parameters
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "fields": fields,
            "balance_affecting_records_only": balance_affecting_records_only,
            "page_size": page_size,
            "page": page
        }
        
        # Add optional parameters
        if transaction_id:
            params["transaction_id"] = transaction_id
        if transaction_type:
            params["transaction_type"] = transaction_type
        if transaction_status:
            params["transaction_status"] = transaction_status
        if transaction_amount:
            params["transaction_amount"] = transaction_amount
        if transaction_currency:
            params["transaction_currency"] = transaction_currency
        if payment_instrument_type:
            params["payment_instrument_type"] = payment_instrument_type
        if store_id:
            params["store_id"] = store_id
        if terminal_id:
            params["terminal_id"] = terminal_id
        
        # Make API call
        response = self._make_request(
            "GET",
            "/v1/reporting/transactions",
            params=params
        )
        
        return SearchResponse(**response)

    def get_balances(
        self,
        as_of_time: Optional[datetime] = None,
        currency_code: Optional[str] = None
    ) -> BalancesResponse:
        """
        Get account balances.
        
        Args:
            as_of_time: Date and time for balance snapshot
            currency_code: Three-character ISO currency code
            
        Returns:
            BalancesResponse object
        """
        params = {}
        
        if as_of_time:
            params["as_of_time"] = as_of_time.isoformat()
        if currency_code:
            params["currency_code"] = currency_code
        
        # Make API call
        response = self._make_request(
            "GET",
            "/v1/reporting/balances",
            params=params
        )
        
        return BalancesResponse(**response)

    def create_transaction_search_request(
        self,
        start_date: datetime,
        end_date: datetime,
        transaction_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        transaction_status: Optional[str] = None,
        transaction_amount: Optional[str] = None,
        transaction_currency: Optional[str] = None,
        payment_instrument_type: Optional[str] = None,
        store_id: Optional[str] = None,
        terminal_id: Optional[str] = None,
        fields: Optional[str] = "transaction_info",
        balance_affecting_records_only: Optional[str] = "Y",
        page_size: Optional[int] = 100,
        page: Optional[int] = 1
    ) -> TransactionSearchRequest:
        """
        Create a transaction search request object.
        
        Args:
            start_date: Start date and time in ISO format
            end_date: End date and time in ISO format
            transaction_id: PayPal transaction ID (17-19 characters)
            transaction_type: Transaction event code
            transaction_status: Transaction status (D, P, S, V)
            transaction_amount: Amount range (e.g., "500 TO 1005")
            transaction_currency: Three-character ISO currency code
            payment_instrument_type: Payment instrument type (CREDITCARD, DEBITCARD)
            store_id: Store ID
            terminal_id: Terminal ID
            fields: Fields to include in response
            balance_affecting_records_only: Y for balance transactions only, N for all
            page_size: Number of items per page (1-500)
            page: Page number (1-based)
            
        Returns:
            TransactionSearchRequest object
        """
        return TransactionSearchRequest(
            start_date=start_date,
            end_date=end_date,
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            transaction_status=transaction_status,
            transaction_amount=transaction_amount,
            transaction_currency=transaction_currency,
            payment_instrument_type=payment_instrument_type,
            store_id=store_id,
            terminal_id=terminal_id,
            fields=fields,
            balance_affecting_records_only=balance_affecting_records_only,
            page_size=page_size,
            page=page
        )

    def create_balances_request(
        self,
        as_of_time: Optional[datetime] = None,
        currency_code: Optional[str] = None
    ) -> BalancesRequest:
        """
        Create a balances request object.
        
        Args:
            as_of_time: Date and time for balance snapshot
            currency_code: Three-character ISO currency code
            
        Returns:
            BalancesRequest object
        """
        return BalancesRequest(
            as_of_time=as_of_time,
            currency_code=currency_code
        )
