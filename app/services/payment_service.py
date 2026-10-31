from app.exceptions import InvalidPaymentAmountError, NotFoundError
from app.models import Invoice, InvoiceStatus, PaymentAttempt, PaymentStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.schemas import PaymentRecordRequest
from app.services.ledger_service import LedgerService


class PaymentService:
    """Owns: recording payment attempts, validating amount against the
    invoice's remaining balance, updating invoice status, triggering the
    matching ledger entry. A failed payment never touches amount_paid."""

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        payment_attempt_repo: PaymentAttemptRepository,
        ledger_service: LedgerService,
    ):
        self.invoice_repo = invoice_repo
        self.payment_attempt_repo = payment_attempt_repo
        self.ledger_service = ledger_service

    def record_payment(self, data: PaymentRecordRequest) -> tuple[PaymentAttempt, Invoice]:
        invoice = self.invoice_repo.get(data.invoice_id)
        if invoice is None:
            raise NotFoundError(f"Invoice {data.invoice_id} not found.")

        remaining = invoice.amount_due - invoice.amount_paid
        if data.status == PaymentStatus.SUCCESS and data.amount > remaining:
            raise InvalidPaymentAmountError(
                f"Payment amount {data.amount} exceeds the remaining unpaid amount "
                f"{remaining} on invoice {invoice.id}."
            )

        attempt = PaymentAttempt(
            invoice_id=invoice.id,
            amount=data.amount,
            currency=data.currency,
            status=data.status,
            provider_reference=data.provider_reference,
            failure_reason=data.failure_reason if data.status == PaymentStatus.FAILED else None,
        )
        attempt = self.payment_attempt_repo.add(attempt)

        if data.status == PaymentStatus.SUCCESS:
            invoice.amount_paid = invoice.amount_paid + data.amount
            invoice.status = (
                InvoiceStatus.PAID
                if invoice.amount_paid >= invoice.amount_due
                else InvoiceStatus.PARTIALLY_PAID
            )
            self.invoice_repo.db.flush()
            self.invoice_repo.db.refresh(invoice)

            self.ledger_service.record_payment_success(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                payment_attempt_id=attempt.id,
                amount=data.amount,
                currency=data.currency,
            )
        else:
            # Failed payment: amount_paid and invoice.status are untouched.
            self.ledger_service.record_payment_failure(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                payment_attempt_id=attempt.id,
                amount=data.amount,
                currency=data.currency,
                reason=data.failure_reason or "unspecified",
            )

        return attempt, invoice
