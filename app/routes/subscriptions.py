from fastapi import APIRouter, Depends, status

from app.dependencies import get_subscription_service
from app.schemas import SubscriptionCreate, SubscriptionOut
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    data: SubscriptionCreate, service: SubscriptionService = Depends(get_subscription_service)
):
    return service.create_subscription(data)


@router.get("", response_model=list[SubscriptionOut])
def list_subscriptions(service: SubscriptionService = Depends(get_subscription_service)):
    return service.list_subscriptions()


@router.patch("/{subscription_id}/cancel", response_model=SubscriptionOut)
def cancel_subscription(
    subscription_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    return service.cancel_subscription(subscription_id)
