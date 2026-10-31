from fastapi import APIRouter, Depends, status

from app.dependencies import get_plan_service
from app.schemas import PlanCreate, PlanOut, PlanUpdate
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
def create_plan(data: PlanCreate, service: PlanService = Depends(get_plan_service)):
    return service.create_plan(data)


@router.get("", response_model=list[PlanOut])
def list_plans(service: PlanService = Depends(get_plan_service)):
    return service.list_plans()


@router.patch("/{plan_id}", response_model=PlanOut)
def update_plan(
    plan_id: int, data: PlanUpdate, service: PlanService = Depends(get_plan_service)
):
    return service.update_plan(plan_id, data)
