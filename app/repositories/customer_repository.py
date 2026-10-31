from app.models import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.email == email).first()
