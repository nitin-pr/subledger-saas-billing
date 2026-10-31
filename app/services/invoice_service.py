from app.exceptions import InactiveSubscriptionError, NotFoundError
from app.models import Invoice, InvoiceStatus, SubscriptionStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas import InvoiceGenerateRequest
from app.services.ledger_service import LedgerService


class InvoiceService:
    """Owns: generating invoices, computing amount_due from the plan price
    at generation time, updating invoice status after payment."""

    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
        invoice_repo: InvoiceRepository,
        ledger_service: LedgerService,
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.ledger_service = ledger_service

    def generate_invoice(self, data: InvoiceGenerateRequest) -> Invoice:
        subscription = self.subscription_repo.get(data.subscription_id)
        if subscription is None:
            raise NotFoundError(f"Subscription {data.subscription_id} not found.")
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise InactiveSubscriptionError(
                f"Subscription {subscription.id} is not active; cannot generate an invoice."
            )

        # Plan price snapshot — the invoice amount is fixed at generation
        # time, independent of later plan price changes.
        plan = self.plan_repo.get(subscription.plan_id)

        period_start = data.period_start or subscription.current_period_start
        period_end = data.period_end or subscription.current_period_end

        invoice = Invoice(
            subscription_id=subscription.id,
            customer_id=subscription.customer_id,
            amount_due=plan.price,
            amount_paid=0,
            currency=plan.currency,
            status=InvoiceStatus.ISSUED,
            period_start=period_start,
            period_end=period_end,
            due_date=period_end,
        )
        invoice = self.invoice_repo.add(invoice)

        self.ledger_service.record_invoice_created(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            amount=invoice.amount_due,
            currency=invoice.currency,
        )
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.invoice_repo.get(invoice_id)
        if invoice is None:
            raise NotFoundError(f"Invoice {invoice_id} not found.")
        return invoice
