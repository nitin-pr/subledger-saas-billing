from app.models import Subscription, SubscriptionStatus
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    def find_active_for_customer_and_plan(
        self, customer_id: int, plan_id: int
    ) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .filter(
                Subscription.customer_id == customer_id,
                Subscription.plan_id == plan_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .first()
        )

    def list_for_customer(self, customer_id: int) -> list[Subscription]:
        return list(
            self.db.query(Subscription).filter(Subscription.customer_id == customer_id).all()
        )
