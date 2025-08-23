"""
Tests for Transaction Search API functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from paypal_sdk import (
    PayPalClient,
    SearchResponse,
    BalancesResponse,
    TransactionSearchRequest,
    BalancesRequest,
    TransactionStatusEnum,
    PaymentInstrumentTypeEnum,
    TransactionDetail,
    TransactionInfo,
    Money,
    BalanceDetail
)


class TestTransactionSearchAPI:
    """Test cases for Transaction Search API."""
    
    @pytest.fixture
    def client(self):
        """Create a PayPal client for testing."""
        return PayPalClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            mode="sandbox"
        )
    
    @pytest.fixture
    def sample_transaction_info(self):
        """Sample transaction info for testing."""
        return {
            "transaction_id": "12345678901234567",
            "transaction_status": "S",
            "transaction_amount": {
                "currency_code": "USD",
                "value": "10.00"
            },
            "transaction_initiation_date": "2024-01-01T00:00:00Z",
            "transaction_subject": "Test transaction"
        }
    
    @pytest.fixture
    def sample_search_response(self, sample_transaction_info):
        """Sample search response for testing."""
        return {
            "transaction_details": [
                {
                    "transaction_info": sample_transaction_info
                }
            ],
            "account_number": "123456789",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z",
            "last_refreshed_datetime": "2024-01-31T23:59:59Z",
            "page": 1,
            "total_items": 1,
            "total_pages": 1,
            "links": []
        }
    
    @pytest.fixture
    def sample_balances_response(self):
        """Sample balances response for testing."""
        return {
            "balances": [
                {
                    "currency": "USD",
                    "primary": True,
                    "total_balance": {
                        "currency_code": "USD",
                        "value": "1000.00"
                    },
                    "available_balance": {
                        "currency_code": "USD",
                        "value": "950.00"
                    },
                    "withheld_balance": {
                        "currency_code": "USD",
                        "value": "50.00"
                    }
                }
            ],
            "account_id": "2ABCDEFGHIJKL",
            "as_of_time": "2024-01-31T23:59:59Z",
            "last_refresh_time": "2024-01-31T23:59:59Z"
        }
    
    def test_search_transactions(self, client, sample_search_response):
        """Test searching for transactions."""
        with patch.object(client, '_make_request', return_value=sample_search_response):
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            response = client.search_transactions(
                start_date=start_date,
                end_date=end_date,
                fields="transaction_info",
                page_size=10
            )
            
            assert isinstance(response, SearchResponse)
            assert response.total_items == 1
            assert response.page == 1
            assert len(response.transaction_details) == 1
            
            transaction = response.transaction_details[0]
            assert isinstance(transaction, TransactionDetail)
            assert transaction.transaction_info is not None
            assert transaction.transaction_info.transaction_id == "12345678901234567"
    
    def test_search_transactions_with_filters(self, client, sample_search_response):
        """Test searching for transactions with filters."""
        with patch.object(client, '_make_request', return_value=sample_search_response):
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            response = client.search_transactions(
                start_date=start_date,
                end_date=end_date,
                transaction_status=TransactionStatusEnum.S,
                transaction_currency="USD",
                payment_instrument_type=PaymentInstrumentTypeEnum.CREDITCARD,
                fields="transaction_info,payer_info",
                page_size=5
            )
            
            assert isinstance(response, SearchResponse)
            assert response.total_items == 1
    
    def test_get_balances(self, client, sample_balances_response):
        """Test getting account balances."""
        with patch.object(client, '_make_request', return_value=sample_balances_response):
            response = client.get_balances()
            
            assert isinstance(response, BalancesResponse)
            assert response.account_id == "2ABCDEFGHIJKL"
            assert len(response.balances) == 1
            
            balance = response.balances[0]
            assert isinstance(balance, BalanceDetail)
            assert balance.currency == "USD"
            assert balance.primary is True
            assert balance.total_balance.value == "1000.00"
            assert balance.available_balance.value == "950.00"
            assert balance.withheld_balance.value == "50.00"
    
    def test_get_balances_with_parameters(self, client, sample_balances_response):
        """Test getting account balances with parameters."""
        with patch.object(client, '_make_request', return_value=sample_balances_response):
            as_of_time = datetime.utcnow()
            
            response = client.get_balances(
                as_of_time=as_of_time,
                currency_code="USD"
            )
            
            assert isinstance(response, BalancesResponse)
            assert len(response.balances) == 1
    
    def test_create_transaction_search_request(self, client):
        """Test creating a transaction search request."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        request = client.create_transaction_search_request(
            start_date=start_date,
            end_date=end_date,
            transaction_status=TransactionStatusEnum.S,
            fields="transaction_info",
            page_size=10
        )
        
        assert isinstance(request, TransactionSearchRequest)
        assert request.start_date == start_date
        assert request.end_date == end_date
        assert request.transaction_status == TransactionStatusEnum.S
        assert request.fields == "transaction_info"
        assert request.page_size == 10
    
    def test_create_balances_request(self, client):
        """Test creating a balances request."""
        as_of_time = datetime.utcnow()
        
        request = client.create_balances_request(
            as_of_time=as_of_time,
            currency_code="USD"
        )
        
        assert isinstance(request, BalancesRequest)
        assert request.as_of_time == as_of_time
        assert request.currency_code == "USD"
    
    def test_transaction_status_enum(self):
        """Test transaction status enum values."""
        assert TransactionStatusEnum.D == "D"  # Denied
        assert TransactionStatusEnum.P == "P"  # Pending
        assert TransactionStatusEnum.S == "S"  # Success
        assert TransactionStatusEnum.V == "V"  # Voided
    
    def test_payment_instrument_type_enum(self):
        """Test payment instrument type enum values."""
        assert PaymentInstrumentTypeEnum.CREDITCARD == "CREDITCARD"
        assert PaymentInstrumentTypeEnum.DEBITCARD == "DEBITCARD"
    
    def test_search_response_model(self, sample_search_response):
        """Test SearchResponse model."""
        response = SearchResponse(**sample_search_response)
        
        assert response.total_items == 1
        assert response.page == 1
        assert response.total_pages == 1
        assert len(response.transaction_details) == 1
        
        transaction = response.transaction_details[0]
        assert transaction.transaction_info is not None
        assert transaction.transaction_info.transaction_id == "12345678901234567"
    
    def test_balances_response_model(self, sample_balances_response):
        """Test BalancesResponse model."""
        response = BalancesResponse(**sample_balances_response)
        
        assert response.account_id == "2ABCDEFGHIJKL"
        assert len(response.balances) == 1
        
        balance = response.balances[0]
        assert balance.currency == "USD"
        assert balance.primary is True
        assert balance.total_balance.value == "1000.00"
    
    def test_transaction_info_model(self, sample_transaction_info):
        """Test TransactionInfo model."""
        info = TransactionInfo(**sample_transaction_info)
        
        assert info.transaction_id == "12345678901234567"
        assert info.transaction_status == "S"
        assert info.transaction_amount.value == "10.00"
        assert info.transaction_amount.currency_code == "USD"
        assert info.transaction_subject == "Test transaction"
    
    def test_money_model(self):
        """Test Money model."""
        money = Money(currency_code="USD", value="10.00")
        
        assert money.currency_code == "USD"
        assert money.value == "10.00"
    
    def test_balance_detail_model(self):
        """Test BalanceDetail model."""
        balance = BalanceDetail(
            currency="USD",
            primary=True,
            total_balance=Money(currency_code="USD", value="1000.00"),
            available_balance=Money(currency_code="USD", value="950.00"),
            withheld_balance=Money(currency_code="USD", value="50.00")
        )
        
        assert balance.currency == "USD"
        assert balance.primary is True
        assert balance.total_balance.value == "1000.00"
        assert balance.available_balance.value == "950.00"
        assert balance.withheld_balance.value == "50.00"
