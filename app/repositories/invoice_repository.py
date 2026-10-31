from app.models import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    model = Invoice

    def list_for_subscription(self, subscription_id: int) -> list[Invoice]:
        return list(
            self.db.query(Invoice).filter(Invoice.subscription_id == subscription_id).all()
        )
