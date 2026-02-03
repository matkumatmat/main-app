from __future__ import annotations
from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlmodel import SQLModel
import uuid

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing CRUD operations for SQLModel entities.
    Services should extend this for domain-specific queries.
    """

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def getById(self, id: uuid.UUID) -> ModelType | None:
        """Retrieve single entity by primary key"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def getAll(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Retrieve all entities with pagination"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def getByField(self, field_name: str, value: any) -> list[ModelType]:
        """Retrieve entities matching a field value"""
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name) == value)
        )
        return list(result.scalars().all())

    async def getOneByField(self, field_name: str, value: any) -> ModelType | None:
        """Retrieve single entity by field value"""
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name) == value)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: ModelType) -> ModelType:
        """Persist new entity to database"""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, id: uuid.UUID, data: dict) -> ModelType | None:
        """Update entity by ID with partial data"""
        entity = await self.getById(id)
        if entity is None:
            return None

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: uuid.UUID) -> bool:
        """Delete entity by primary key, returns success status"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def exists(self, id: uuid.UUID) -> bool:
        """Check if entity exists by primary key"""
        result = await self.session.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        """Count total entities"""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
