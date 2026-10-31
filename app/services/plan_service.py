from app.exceptions import NotFoundError
from app.models import Plan
from app.repositories.plan_repository import PlanRepository
from app.schemas import PlanCreate, PlanUpdate


class PlanService:
    """Owns: price, billing cycle, and plan status changes."""

    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, data: PlanCreate) -> Plan:
        plan = Plan(
            name=data.name,
            description=data.description,
            billing_cycle=data.billing_cycle,
            price=data.price,
            currency=data.currency,
        )
        return self.plan_repo.add(plan)

    def list_plans(self) -> list[Plan]:
        return self.plan_repo.list()

    def get_plan(self, plan_id: int) -> Plan:
        plan = self.plan_repo.get(plan_id)
        if plan is None:
            raise NotFoundError(f"Plan {plan_id} not found.")
        return plan

    def update_plan(self, plan_id: int, data: PlanUpdate) -> Plan:
        plan = self.get_plan(plan_id)
        if data.name is not None:
            plan.name = data.name
        if data.description is not None:
            plan.description = data.description
        if data.price is not None:
            plan.price = data.price
        if data.status is not None:
            plan.status = data.status
        self.plan_repo.db.flush()
        self.plan_repo.db.refresh(plan)
        return plan
