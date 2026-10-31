from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.models import (
    BillingCycle,
    CustomerStatus,
    InvoiceStatus,
    LedgerEntryType,
    PaymentStatus,
    PlanStatus,
    SubscriptionStatus,
)

# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------


class PlanCreate(BaseModel):
    name: str
    description: str | None = None
    billing_cycle: BillingCycle
    price: Decimal
    currency: str = "USD"

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Plan price must be greater than 0.")
        return value


class PlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    status: PlanStatus | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value <= 0:
            raise ValueError("Plan price must be greater than 0.")
        return value


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    billing_cycle: BillingCycle
    price: Decimal
    currency: str
    status: PlanStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    company_name: str | None = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    company_name: str | None
    status: CustomerStatus
    created_at: datetime


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------


class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int
    start_date: date | None = None  # defaults to today in the service


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    plan_id: int
    status: SubscriptionStatus
    start_date: date
    current_period_start: date
    current_period_end: date
    cancelled_at: datetime | None


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------


class InvoiceGenerateRequest(BaseModel):
    subscription_id: int
    period_start: date | None = None
    period_end: date | None = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subscription_id: int
    customer_id: int
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    status: InvoiceStatus
    period_start: date
    period_end: date
    due_date: date
    created_at: datetime


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


class PaymentRecordRequest(BaseModel):
    invoice_id: int
    amount: Decimal
    currency: str = "USD"
    status: PaymentStatus
    provider_reference: str | None = None
    failure_reason: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Payment amount must be greater than 0.")
        return value


class PaymentAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider_reference: str | None
    failure_reason: str | None
    created_at: datetime


class PaymentRecordResponse(BaseModel):
    payment_attempt: PaymentAttemptOut
    invoice: InvoiceOut


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------


class LedgerEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    invoice_id: int
    entry_type: LedgerEntryType
    amount: Decimal
    currency: str
    reference_id: str
    description: str
    created_at: datetime
