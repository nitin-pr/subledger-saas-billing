from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.ledger_repository import LedgerRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.customer_service import CustomerService
from app.services.invoice_service import InvoiceService
from app.services.ledger_service import LedgerService
from app.services.payment_service import PaymentService
from app.services.plan_service import PlanService
from app.services.subscription_service import SubscriptionService

# --- Repositories -----------------------------------------------------


def get_plan_repo(db: Session = Depends(get_db)) -> PlanRepository:
    return PlanRepository(db)


def get_customer_repo(db: Session = Depends(get_db)) -> CustomerRepository:
    return CustomerRepository(db)


def get_subscription_repo(db: Session = Depends(get_db)) -> SubscriptionRepository:
    return SubscriptionRepository(db)


def get_invoice_repo(db: Session = Depends(get_db)) -> InvoiceRepository:
    return InvoiceRepository(db)


def get_payment_attempt_repo(db: Session = Depends(get_db)) -> PaymentAttemptRepository:
    return PaymentAttemptRepository(db)


def get_ledger_repo(db: Session = Depends(get_db)) -> LedgerRepository:
    return LedgerRepository(db)


# --- Services -----------------------------------------------------
# Every dependency is injected, never constructed inline inside a service.


def get_ledger_service(ledger_repo: LedgerRepository = Depends(get_ledger_repo)) -> LedgerService:
    return LedgerService(ledger_repo)


def get_plan_service(plan_repo: PlanRepository = Depends(get_plan_repo)) -> PlanService:
    return PlanService(plan_repo)


def get_customer_service(
    customer_repo: CustomerRepository = Depends(get_customer_repo),
) -> CustomerService:
    return CustomerService(customer_repo)


def get_subscription_service(
    subscription_repo: SubscriptionRepository = Depends(get_subscription_repo),
    plan_repo: PlanRepository = Depends(get_plan_repo),
    customer_repo: CustomerRepository = Depends(get_customer_repo),
) -> SubscriptionService:
    return SubscriptionService(subscription_repo, plan_repo, customer_repo)


def get_invoice_service(
    subscription_repo: SubscriptionRepository = Depends(get_subscription_repo),
    plan_repo: PlanRepository = Depends(get_plan_repo),
    invoice_repo: InvoiceRepository = Depends(get_invoice_repo),
    ledger_service: LedgerService = Depends(get_ledger_service),
) -> InvoiceService:
    return InvoiceService(subscription_repo, plan_repo, invoice_repo, ledger_service)


def get_payment_service(
    invoice_repo: InvoiceRepository = Depends(get_invoice_repo),
    payment_attempt_repo: PaymentAttemptRepository = Depends(get_payment_attempt_repo),
    ledger_service: LedgerService = Depends(get_ledger_service),
) -> PaymentService:
    return PaymentService(invoice_repo, payment_attempt_repo, ledger_service)
