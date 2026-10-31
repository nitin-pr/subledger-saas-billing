from app.exceptions import DuplicateEmailError, NotFoundError
from app.models import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas import CustomerCreate


class CustomerService:
    """Owns: creating customers, enforcing email uniqueness, fetching a
    customer's profile."""

    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    def create_customer(self, data: CustomerCreate) -> Customer:
        if self.customer_repo.get_by_email(data.email) is not None:
            raise DuplicateEmailError(f"A customer with email {data.email} already exists.")
        customer = Customer(name=data.name, email=data.email, company_name=data.company_name)
        return self.customer_repo.add(customer)

    def list_customers(self) -> list[Customer]:
        return self.customer_repo.list()

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.customer_repo.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Customer {customer_id} not found.")
        return customer
