from app.models import LedgerEntry
from app.repositories.base import BaseRepository


class LedgerRepository(BaseRepository[LedgerEntry]):
    """Deliberately exposes no update()/delete() — ledger entries are
    append-only. Only add() (inherited) and the reads below are available."""

    model = LedgerEntry

    def list_for_customer(self, customer_id: int) -> list[LedgerEntry]:
        return list(
            self.db.query(LedgerEntry)
            .filter(LedgerEntry.customer_id == customer_id)
            .order_by(LedgerEntry.created_at.asc())
            .all()
        )
