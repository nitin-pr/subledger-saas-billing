from app.models import PaymentAttempt
from app.repositories.base import BaseRepository


class PaymentAttemptRepository(BaseRepository[PaymentAttempt]):
    model = PaymentAttempt

    def list_for_invoice(self, invoice_id: int) -> list[PaymentAttempt]:
        return list(
            self.db.query(PaymentAttempt).filter(PaymentAttempt.invoice_id == invoice_id).all()
        )
