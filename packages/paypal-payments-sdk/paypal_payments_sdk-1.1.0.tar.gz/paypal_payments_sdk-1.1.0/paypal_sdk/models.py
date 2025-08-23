"""
PayPal SDK Models

Pydantic models for PayPal Payments API v2 data structures.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator, RootModel


# Enums
class AuthorizationStatusEnum(str, Enum):
    CREATED = "CREATED"
    CAPTURED = "CAPTURED"
    DENIED = "DENIED"
    PARTIALLY_CAPTURED = "PARTIALLY_CAPTURED"
    VOIDED = "VOIDED"
    PENDING = "PENDING"


class CaptureStatusEnum(str, Enum):
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"


class RefundStatusEnum(str, Enum):
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class SellerProtectionStatusEnum(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    PARTIALLY_ELIGIBLE = "PARTIALLY_ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class DisbursementModeEnum(str, Enum):
    INSTANT = "INSTANT"
    DELAYED = "DELAYED"


class CardBrandEnum(str, Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    DISCOVER = "DISCOVER"
    AMEX = "AMEX"
    SOLO = "SOLO"
    JCB = "JCB"
    STAR = "STAR"
    DELTA = "DELTA"
    SWITCH = "SWITCH"
    MAESTRO = "MAESTRO"
    CB_NATIONALE = "CB_NATIONALE"
    CONFIGOGA = "CONFIGOGA"
    CONFIDIS = "CONFIDIS"
    ELECTRON = "ELECTRON"
    CETELEM = "CETELEM"
    CHINA_UNION_PAY = "CHINA_UNION_PAY"
    DINERS = "DINERS"
    ELO = "ELO"
    HIPER = "HIPER"
    HIPERCARD = "HIPERCARD"
    RUPAY = "RUPAY"
    GE = "GE"
    SYNCHRONY = "SYNCHRONY"
    EFTPOS = "EFTPOS"
    UNKNOWN = "UNKNOWN"


class AvsCodeEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    I = "I"
    M = "M"
    N = "N"
    P = "P"
    R = "R"
    S = "S"
    U = "U"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"
    NULL = "Null"
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"


class CvvCodeEnum(str, Enum):
    E = "E"
    I = "I"
    M = "M"
    N = "N"
    P = "P"
    S = "S"
    U = "U"
    X = "X"
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"


class DisputeCategoriesEnum(str, Enum):
    ITEM_NOT_RECEIVED = "ITEM_NOT_RECEIVED"
    UNAUTHORIZED_TRANSACTION = "UNAUTHORIZED_TRANSACTION"


class AuthorizationIncompleteReasonEnum(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    DECLINED_BY_RISK_FRAUD_FILTERS = "DECLINED_BY_RISK_FRAUD_FILTERS"


class CaptureIncompleteReasonEnum(str, Enum):
    BUYER_COMPLAINT = "BUYER_COMPLAINT"
    CHARGEBACK = "CHARGEBACK"
    ECHECK = "ECHECK"
    INTERNATIONAL_WITHDRAWAL = "INTERNATIONAL_WITHDRAWAL"
    OTHER = "OTHER"
    PENDING_REVIEW = "PENDING_REVIEW"
    RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION = "RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION"
    REFUNDED = "REFUNDED"
    TRANSACTION_APPROVED_AWAITING_FUNDING = "TRANSACTION_APPROVED_AWAITING_FUNDING"
    UNILATERAL = "UNILATERAL"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"
    DECLINED_BY_RISK_FRAUD_FILTERS = "DECLINED_BY_RISK_FRAUD_FILTERS"


class RefundIncompleteReasonEnum(str, Enum):
    ECHECK = "ECHECK"


# Type aliases
CurrencyCode = str
AvsCode = str
CvvCode = str
ResponseCode = str
PaymentAdviceCode = str


# Base models
class Money(BaseModel):
    """Money object with currency and value."""
    currency_code: CurrencyCode = Field(..., min_length=3, max_length=3)
    value: str = Field(..., max_length=32, pattern=r"^((-?[0-9]+)|(-?([0-9]+)?[.][0-9]+))$")


class LinkDescription(BaseModel):
    """HATEOAS link description."""
    href: str = Field(..., max_length=20000)
    rel: str = Field(..., max_length=100)
    method: Optional[str] = Field(None, min_length=3, max_length=6, pattern=r"^[A-Z]*$")


class ActivityTimestamps(BaseModel):
    """Transaction date and time stamps."""
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class PayeeBase(BaseModel):
    """Payee base information."""
    email_address: Optional[str] = Field(None, max_length=254)
    merchant_id: Optional[str] = Field(None, min_length=13, max_length=13, pattern=r"^[2-9A-HJ-NP-Z]{13}$")


class PlatformFee(BaseModel):
    """Platform fee information."""
    amount: Money
    payee: Optional[PayeeBase] = None


class PaymentInstruction(BaseModel):
    """Payment instruction for captures."""
    platform_fees: Optional[List[PlatformFee]] = Field(None, max_length=1)
    disbursement_mode: Optional[DisbursementModeEnum] = DisbursementModeEnum.INSTANT
    payee_receivable_fx_rate_id: Optional[str] = Field(None, min_length=1, max_length=4000, pattern=r"^.*$")


class NetworkTransactionReference(BaseModel):
    """Network transaction reference."""
    id: str = Field(..., min_length=9, max_length=36, pattern=r"^[a-zA-Z0-9-_@.:&+=*^'~#!$%()]+$")
    date: Optional[str] = Field(None, min_length=4, max_length=4, pattern=r"^[0-9]+$")
    network: Optional[CardBrandEnum] = None
    acquirer_reference_number: Optional[str] = Field(None, min_length=1, max_length=36, pattern=r"^[a-zA-Z0-9]+$")


class ExchangeRate(BaseModel):
    """Exchange rate information."""
    source_currency: CurrencyCode
    target_currency: CurrencyCode
    value: str


class NetAmountBreakdownItem(BaseModel):
    """Net amount breakdown item."""
    payable_amount: Optional[Money] = None
    converted_amount: Optional[Money] = None
    exchange_rate: Optional[ExchangeRate] = None


class DisputeCategories(RootModel):
    """Dispute categories."""
    root: List[DisputeCategoriesEnum]


class SellerProtection(BaseModel):
    """Seller protection information."""
    status: SellerProtectionStatusEnum
    dispute_categories: Optional[List[DisputeCategoriesEnum]] = None


class SellerReceivableBreakdown(BaseModel):
    """Seller receivable breakdown."""
    gross_amount: Money
    paypal_fee: Optional[Money] = None
    paypal_fee_in_receivable_currency: Optional[Money] = None
    net_amount: Optional[Money] = None
    receivable_amount: Optional[Money] = None
    exchange_rate: Optional[ExchangeRate] = None
    platform_fees: Optional[List[PlatformFee]] = Field(None, max_length=1)


class SellerPayableBreakdown(BaseModel):
    """Seller payable breakdown."""
    gross_amount: Optional[Money] = None
    paypal_fee: Optional[Money] = None
    paypal_fee_in_receivable_currency: Optional[Money] = None
    net_amount: Optional[Money] = None
    net_amount_in_receivable_currency: Optional[Money] = None
    platform_fees: Optional[List[PlatformFee]] = Field(None, max_length=1)
    net_amount_breakdown: Optional[List[NetAmountBreakdownItem]] = None
    total_refunded_amount: Optional[Money] = None


class ProcessorResponse(BaseModel):
    """Processor response information."""
    avs_code: Optional[AvsCode] = None
    cvv_code: Optional[CvvCode] = None
    response_code: Optional[ResponseCode] = None
    payment_advice_code: Optional[PaymentAdviceCode] = None


class RelatedIds(BaseModel):
    """Related identifiers."""
    order_id: Optional[str] = Field(None, min_length=1, max_length=20, pattern=r"^[A-Z0-9]+$")
    authorization_id: Optional[str] = Field(None, min_length=1, max_length=20, pattern=r"^[A-Z0-9]+$")
    capture_id: Optional[str] = Field(None, min_length=1, max_length=20, pattern=r"^[A-Z0-9]+$")


class SupplementaryData(BaseModel):
    """Supplementary data."""
    related_ids: Optional[RelatedIds] = None


# Status models
class AuthorizationStatusDetails(BaseModel):
    """Authorization status details."""
    reason: Optional[AuthorizationIncompleteReasonEnum] = None


class AuthorizationStatus(BaseModel):
    """Authorization status."""
    status: AuthorizationStatusEnum
    status_details: Optional[AuthorizationStatusDetails] = None


class CaptureStatusDetails(BaseModel):
    """Capture status details."""
    reason: Optional[CaptureIncompleteReasonEnum] = None


class CaptureStatus(BaseModel):
    """Capture status."""
    status: CaptureStatusEnum
    status_details: Optional[CaptureStatusDetails] = None


class RefundStatusDetails(BaseModel):
    """Refund status details."""
    reason: Optional[RefundIncompleteReasonEnum] = None


class RefundStatus(BaseModel):
    """Refund status."""
    status: RefundStatusEnum
    status_details: Optional[RefundStatusDetails] = None


# Main entity models
class Authorization(BaseModel):
    """Authorization entity."""
    id: Optional[str] = None
    amount: Optional[Money] = None
    invoice_id: Optional[str] = None
    custom_id: Optional[str] = Field(None, max_length=255)
    network_transaction_reference: Optional[NetworkTransactionReference] = None
    seller_protection: Optional[SellerProtection] = None
    expiration_time: Optional[datetime] = None
    links: Optional[List[LinkDescription]] = None
    supplementary_data: Optional[SupplementaryData] = None
    payee: Optional[PayeeBase] = None
    
    # Status fields
    status: Optional[AuthorizationStatusEnum] = None
    status_details: Optional[AuthorizationStatusDetails] = None
    
    # Timestamps
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class Capture(BaseModel):
    """Capture entity."""
    id: Optional[str] = None
    amount: Optional[Money] = None
    invoice_id: Optional[str] = None
    custom_id: Optional[str] = Field(None, max_length=255)
    network_transaction_reference: Optional[NetworkTransactionReference] = None
    seller_protection: Optional[SellerProtection] = None
    final_capture: Optional[bool] = False
    seller_receivable_breakdown: Optional[SellerReceivableBreakdown] = None
    disbursement_mode: Optional[DisbursementModeEnum] = DisbursementModeEnum.INSTANT
    links: Optional[List[LinkDescription]] = None
    processor_response: Optional[ProcessorResponse] = None
    supplementary_data: Optional[SupplementaryData] = None
    payee: Optional[PayeeBase] = None
    
    # Status fields
    status: Optional[CaptureStatusEnum] = None
    status_details: Optional[CaptureStatusDetails] = None
    
    # Timestamps
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class Refund(BaseModel):
    """Refund entity."""
    id: Optional[str] = None
    amount: Optional[Money] = None
    invoice_id: Optional[str] = None
    custom_id: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[A-Za-z0-9-_.,]*$")
    acquirer_reference_number: Optional[str] = Field(None, min_length=1, max_length=36, pattern=r"^[a-zA-Z0-9]+$")
    note_to_payer: Optional[str] = None
    seller_payable_breakdown: Optional[SellerPayableBreakdown] = None
    payer: Optional[PayeeBase] = None
    links: Optional[List[LinkDescription]] = None
    
    # Status fields
    status: Optional[RefundStatusEnum] = None
    status_details: Optional[RefundStatusDetails] = None
    
    # Timestamps
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


# Request models
class CaptureRequest(BaseModel):
    """Capture request."""
    amount: Optional[Money] = None
    invoice_id: Optional[str] = Field(None, max_length=127)
    final_capture: Optional[bool] = False
    payment_instruction: Optional[PaymentInstruction] = None
    note_to_payer: Optional[str] = Field(None, max_length=255)
    soft_descriptor: Optional[str] = Field(None, max_length=22)


class RefundRequest(BaseModel):
    """Refund request."""
    amount: Optional[Money] = None
    custom_id: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^.*$")
    invoice_id: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^.*$")
    note_to_payer: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^.*$")
    payment_instruction: Optional[PaymentInstruction] = None


class ReauthorizeRequest(BaseModel):
    """Reauthorize request."""
    amount: Money


# Error models
class ErrorLocation(str, Enum):
    BODY = "body"
    PATH = "path"
    QUERY = "query"


class ErrorDetails(BaseModel):
    """Error details."""
    field: Optional[str] = None
    value: Optional[str] = None
    location: Optional[ErrorLocation] = ErrorLocation.BODY
    issue: str
    description: Optional[str] = None


class ErrorLinkDescription(BaseModel):
    """Error link description."""
    href: str = Field(..., max_length=20000)
    rel: str = Field(..., max_length=100)
    method: Optional[str] = Field(None, min_length=3, max_length=6, pattern=r"^[A-Z]*$")


class ErrorResponse(BaseModel):
    """Error response."""
    name: Optional[str] = None
    message: Optional[str] = None
    details: Optional[List[ErrorDetails]] = None
    debug_id: Optional[str] = None
    links: Optional[List[ErrorLinkDescription]] = None


# Transaction Search API Models

class TransactionStatusEnum(str, Enum):
    """Transaction status codes."""
    D = "D"  # Denied
    P = "P"  # Pending
    S = "S"  # Success
    V = "V"  # Voided


class PaymentInstrumentTypeEnum(str, Enum):
    """Payment instrument types."""
    CREDITCARD = "CREDITCARD"
    DEBITCARD = "DEBITCARD"


class BalanceAffectingRecordsEnum(str, Enum):
    """Balance affecting records filter."""
    Y = "Y"  # Only balance transactions
    N = "N"  # All transactions


class Name(BaseModel):
    """Name object."""
    prefix: Optional[str] = Field(None, max_length=140)
    given_name: Optional[str] = Field(None, max_length=140)
    surname: Optional[str] = Field(None, max_length=140)
    middle_name: Optional[str] = Field(None, max_length=140)
    suffix: Optional[str] = Field(None, max_length=140)
    alternate_full_name: Optional[str] = Field(None, max_length=300)
    full_name: Optional[str] = Field(None, max_length=300)


class Address(BaseModel):
    """Address object."""
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=40)
    country_code: Optional[str] = Field(None, min_length=2, max_length=2, pattern=r"^([A-Z]{2}|C2)$")
    postal_code: Optional[str] = None


class Phone(BaseModel):
    """Phone object."""
    country_code: str = Field(..., min_length=1, max_length=3, pattern=r"^[0-9]{1,3}?$")
    national_number: str = Field(..., min_length=1, max_length=14, pattern=r"^[0-9]{1,14}?$")
    extension_number: Optional[str] = Field(None, min_length=1, max_length=15, pattern=r"^[0-9]{1,15}?$")


class PayerInfo(BaseModel):
    """Payer information."""
    account_id: Optional[str] = Field(None, min_length=1, max_length=13, pattern=r"^[a-zA-Z0-9]*$")
    email_address: Optional[str] = Field(None, min_length=3, max_length=254, pattern=r"^.+@[^\"\\-].+$")
    phone_number: Optional[Phone] = None
    address_status: Optional[str] = Field(None, min_length=1, max_length=1, pattern=r"^[N|Y]$")
    payer_status: Optional[str] = Field(None, min_length=1, max_length=1, pattern=r"^[N|Y]$")
    payer_name: Optional[Name] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2, pattern=r"^([A-Z]{2}|C2)$")
    address: Optional[Address] = None


class ShippingInfo(BaseModel):
    """Shipping information."""
    name: Optional[str] = Field(None, min_length=1, max_length=500, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    method: Optional[str] = Field(None, min_length=1, max_length=500, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    address: Optional[Address] = None
    secondary_shipping_address: Optional[Address] = None


class StoreInfo(BaseModel):
    """Store information."""
    store_id: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9]*$")
    terminal_id: Optional[str] = Field(None, min_length=1, max_length=60, pattern=r"^[a-zA-Z0-9]*$")


class AuctionInfo(BaseModel):
    """Auction information."""
    auction_site: Optional[str] = Field(None, min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    auction_item_site: Optional[str] = Field(None, min_length=1, max_length=4000, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    auction_buyer_id: Optional[str] = Field(None, min_length=1, max_length=500, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    auction_closing_date: Optional[datetime] = None


class CheckoutOption(BaseModel):
    """Checkout option."""
    checkout_option_name: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    checkout_option_value: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")


class ItemDetail(BaseModel):
    """Item detail."""
    item_code: Optional[str] = Field(None, min_length=1, max_length=1000, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    item_name: Optional[str] = Field(None, min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    item_description: Optional[str] = Field(None, min_length=1, max_length=2000, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    item_options: Optional[str] = Field(None, min_length=1, max_length=4000, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    item_quantity: Optional[str] = Field(None, min_length=1, max_length=4000, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    item_unit_price: Optional[Money] = None
    item_amount: Optional[Money] = None
    discount_amount: Optional[Money] = None
    adjustment_amount: Optional[Money] = None
    gift_wrap_amount: Optional[Money] = None
    tax_percentage: Optional[str] = Field(None, max_length=10, pattern=r"^((-?[0-9]+)|(-?([0-9]+)?[.][0-9]+))$")
    tax_amounts: Optional[List[Dict[str, Money]]] = None
    basic_shipping_amount: Optional[Money] = None
    extra_shipping_amount: Optional[Money] = None
    handling_amount: Optional[Money] = None
    insurance_amount: Optional[Money] = None
    total_item_amount: Optional[Money] = None
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    checkout_options: Optional[List[CheckoutOption]] = None


class CartInfo(BaseModel):
    """Cart information."""
    item_details: Optional[List[ItemDetail]] = None
    tax_inclusive: Optional[bool] = False
    paypal_invoice_id: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")


class IncentiveDetail(BaseModel):
    """Incentive detail."""
    incentive_type: Optional[str] = Field(None, min_length=1, max_length=500, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    incentive_code: Optional[str] = Field(None, min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    incentive_amount: Optional[Money] = None
    incentive_program_code: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")


class IncentiveInfo(BaseModel):
    """Incentive information."""
    incentive_details: Optional[List[IncentiveDetail]] = None


class TransactionInfo(BaseModel):
    """Transaction information."""
    paypal_account_id: Optional[str] = Field(None, min_length=1, max_length=24, pattern=r"^[a-zA-Z0-9]*$")
    transaction_id: Optional[str] = Field(None, min_length=1, max_length=24, pattern=r"^[a-zA-Z0-9]*$")
    paypal_reference_id: Optional[str] = Field(None, min_length=1, max_length=24, pattern=r"^[a-zA-Z0-9]*$")
    paypal_reference_id_type: Optional[str] = Field(None, min_length=3, max_length=3, pattern=r"^[a-zA-Z0-9]*$")
    transaction_event_code: Optional[str] = Field(None, min_length=1, max_length=5, pattern=r"^[a-zA-Z0-9]*$")
    transaction_initiation_date: Optional[datetime] = None
    transaction_updated_date: Optional[datetime] = None
    transaction_amount: Optional[Money] = None
    fee_amount: Optional[Money] = None
    discount_amount: Optional[Money] = None
    insurance_amount: Optional[Money] = None
    sales_tax_amount: Optional[Money] = None
    shipping_amount: Optional[Money] = None
    shipping_discount_amount: Optional[Money] = None
    shipping_tax_amount: Optional[Money] = None
    other_amount: Optional[Money] = None
    tip_amount: Optional[Money] = None
    transaction_status: Optional[str] = Field(None, min_length=1, max_length=1, pattern=r"^[a-zA-Z0-9]*$")
    transaction_subject: Optional[str] = Field(None, min_length=1, max_length=256, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    transaction_note: Optional[str] = Field(None, min_length=1, max_length=4000, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    payment_tracking_id: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^[a-zA-Z0-9]*$")
    bank_reference_id: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^[a-zA-Z0-9]*$")
    ending_balance: Optional[Money] = None
    available_balance: Optional[Money] = None
    invoice_id: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    custom_field: Optional[str] = Field(None, min_length=1, max_length=127, pattern=r"^[a-zA-Z0-9_'\-., \":;\\!?]*$")
    protection_eligibility: Optional[str] = Field(None, min_length=1, max_length=2, pattern=r"^[a-zA-Z0-9]*$")
    credit_term: Optional[str] = Field(None, min_length=1, max_length=25, pattern=r"^[a-zA-Z0-9.]*$")
    credit_transactional_fee: Optional[Money] = None
    credit_promotional_fee: Optional[Money] = None
    annual_percentage_rate: Optional[str] = Field(None, pattern=r"^((-?[0-9]+)|(-?([0-9]+)?[.][0-9]+))$")
    payment_method_type: Optional[str] = Field(None, min_length=1, max_length=20, pattern=r"^[a-zA-Z0-9-]*$")
    instrument_type: Optional[str] = Field(None, min_length=1, max_length=64)
    instrument_sub_type: Optional[str] = Field(None, min_length=1, max_length=64)


class TransactionDetail(BaseModel):
    """Transaction detail."""
    transaction_info: Optional[TransactionInfo] = None
    payer_info: Optional[PayerInfo] = None
    shipping_info: Optional[ShippingInfo] = None
    cart_info: Optional[CartInfo] = None
    store_info: Optional[StoreInfo] = None
    auction_info: Optional[AuctionInfo] = None
    incentive_info: Optional[IncentiveInfo] = None


class BalanceDetail(BaseModel):
    """Balance detail."""
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    primary: Optional[bool] = None
    total_balance: Optional[Money] = None
    available_balance: Optional[Money] = None
    withheld_balance: Optional[Money] = None


class SearchResponse(BaseModel):
    """Search response."""
    transaction_details: Optional[List[TransactionDetail]] = None
    account_number: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9]*$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_refreshed_datetime: Optional[datetime] = None
    page: Optional[int] = Field(None, minimum=0, maximum=2147483647)
    total_items: Optional[int] = Field(None, minimum=0, maximum=2147483647)
    total_pages: Optional[int] = Field(None, minimum=0, maximum=2147483647)
    links: Optional[List[LinkDescription]] = None


class BalancesResponse(BaseModel):
    """Balances response."""
    balances: Optional[List[BalanceDetail]] = None
    account_id: Optional[str] = Field(None, min_length=13, max_length=13)
    as_of_time: Optional[datetime] = None
    last_refresh_time: Optional[datetime] = None


# Request models for Transaction Search API
class TransactionSearchRequest(BaseModel):
    """Transaction search request parameters."""
    transaction_id: Optional[str] = Field(None, min_length=17, max_length=19)
    transaction_type: Optional[str] = None
    transaction_status: Optional[str] = None
    transaction_amount: Optional[str] = None
    transaction_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    start_date: datetime
    end_date: datetime
    payment_instrument_type: Optional[str] = None
    store_id: Optional[str] = None
    terminal_id: Optional[str] = None
    fields: Optional[str] = Field(default="transaction_info")
    balance_affecting_records_only: Optional[str] = Field(default="Y")
    page_size: Optional[int] = Field(default=100, minimum=1, maximum=500)
    page: Optional[int] = Field(default=1, minimum=1, maximum=2147483647)


class BalancesRequest(BaseModel):
    """Balances request parameters."""
    as_of_time: Optional[datetime] = None
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
