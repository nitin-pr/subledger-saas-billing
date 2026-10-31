from datetime import date, datetime, timezone

from app.exceptions import DuplicateActiveSubscriptionError, InactivePlanError, NotFoundError
from app.models import PlanStatus, Subscription, SubscriptionStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas import SubscriptionCreate
from app.utils import period_end_for_cycle


class SubscriptionService:
    """Owns: create/cancel subscriptions, checking active plan, preventing
    a duplicate active subscription to the same plan."""

    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
        customer_repo: CustomerRepository,
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.customer_repo = customer_repo

    def create_subscription(self, data: SubscriptionCreate) -> Subscription:
        if self.customer_repo.get(data.customer_id) is None:
            raise NotFoundError(f"Customer {data.customer_id} not found.")

        plan = self.plan_repo.get(data.plan_id)
        if plan is None:
            raise NotFoundError(f"Plan {data.plan_id} not found.")
        if plan.status != PlanStatus.ACTIVE:
            raise InactivePlanError(f"Plan {plan.id} is inactive; cannot subscribe to it.")

        existing = self.subscription_repo.find_active_for_customer_and_plan(
            data.customer_id, data.plan_id
        )
        if existing is not None:
            raise DuplicateActiveSubscriptionError(
                f"Customer {data.customer_id} already has an active subscription "
                f"to plan {data.plan_id}."
            )

        start = data.start_date or date.today()
        period_end = period_end_for_cycle(start, plan.billing_cycle)

        subscription = Subscription(
            customer_id=data.customer_id,
            plan_id=data.plan_id,
            status=SubscriptionStatus.ACTIVE,
            start_date=start,
            current_period_start=start,
            current_period_end=period_end,
        )
        return self.subscription_repo.add(subscription)

    def list_subscriptions(self) -> list[Subscription]:
        return self.subscription_repo.list()

    def get_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.subscription_repo.get(subscription_id)
        if subscription is None:
            raise NotFoundError(f"Subscription {subscription_id} not found.")
        return subscription

    def cancel_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.get_subscription(subscription_id)
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now(timezone.utc)
        self.subscription_repo.db.flush()
        self.subscription_repo.db.refresh(subscription)
        return subscription
