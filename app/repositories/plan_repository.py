from app.models import Plan
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    model = Plan
