from fastapi import APIRouter, Depends, status

from app.dependencies import get_payment_service
from app.schemas import PaymentRecordRequest, PaymentRecordResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/record", response_model=PaymentRecordResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    data: PaymentRecordRequest, service: PaymentService = Depends(get_payment_service)
):
    attempt, invoice = service.record_payment(data)
    return PaymentRecordResponse(payment_attempt=attempt, invoice=invoice)
