from decimal import Decimal

from app.models import LedgerEntry, LedgerEntryType
from app.repositories.ledger_repository import LedgerRepository


class LedgerService:
    """Owns: creating append-only ledger entries and fetching customer
    ledger history. Nothing else in the app writes to LedgerEntry."""

    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def record_invoice_created(
        self, customer_id: int, invoice_id: int, amount: Decimal, currency: str
    ) -> LedgerEntry:
        entry = LedgerEntry(
            customer_id=customer_id,
            invoice_id=invoice_id,
            entry_type=LedgerEntryType.INVOICE_CREATED,
            amount=amount,
            currency=currency,
            reference_id=f"invoice:{invoice_id}",
            description=f"Invoice #{invoice_id} created for {amount} {currency}",
        )
        return self.ledger_repo.add(entry)

    def record_payment_success(
        self,
        customer_id: int,
        invoice_id: int,
        payment_attempt_id: int,
        amount: Decimal,
        currency: str,
    ) -> LedgerEntry:
        entry = LedgerEntry(
            customer_id=customer_id,
            invoice_id=invoice_id,
            entry_type=LedgerEntryType.PAYMENT_SUCCESS,
            amount=amount,
            currency=currency,
            reference_id=f"payment:{payment_attempt_id}",
            description=f"Payment of {amount} {currency} succeeded for invoice #{invoice_id}",
        )
        return self.ledger_repo.add(entry)

    def record_payment_failure(
        self,
        customer_id: int,
        invoice_id: int,
        payment_attempt_id: int,
        amount: Decimal,
        currency: str,
        reason: str,
    ) -> LedgerEntry:
        entry = LedgerEntry(
            customer_id=customer_id,
            invoice_id=invoice_id,
            entry_type=LedgerEntryType.PAYMENT_FAILURE,
            amount=amount,
            currency=currency,
            reference_id=f"payment:{payment_attempt_id}",
            description=f"Payment of {amount} {currency} failed for invoice #{invoice_id}: {reason}",
        )
        return self.ledger_repo.add(entry)

    def list_for_customer(self, customer_id: int) -> list[LedgerEntry]:
        return self.ledger_repo.list_for_customer(customer_id)
