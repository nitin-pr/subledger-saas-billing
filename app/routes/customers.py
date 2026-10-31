from fastapi import APIRouter, Depends, status

from app.dependencies import get_customer_service, get_ledger_service
from app.schemas import CustomerCreate, CustomerOut, LedgerEntryOut
from app.services.customer_service import CustomerService
from app.services.ledger_service import LedgerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate, service: CustomerService = Depends(get_customer_service)
):
    return service.create_customer(data)


@router.get("", response_model=list[CustomerOut])
def list_customers(service: CustomerService = Depends(get_customer_service)):
    return service.list_customers()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    return service.get_customer(customer_id)


@router.get("/{customer_id}/ledger", response_model=list[LedgerEntryOut])
def get_customer_ledger(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
    ledger_service: LedgerService = Depends(get_ledger_service),
):
    customer_service.get_customer(customer_id)  # raises 404 if the customer doesn't exist
    return ledger_service.list_for_customer(customer_id)
