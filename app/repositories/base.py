from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Owns reads/writes for one table. Services own business rules and
    never touch the DB session directly — they go through a repository."""

    model: type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> ModelType | None:
        return self.db.get(self.model, id)

    def list(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return list(self.db.query(self.model).offset(skip).limit(limit).all())

    def add(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance
