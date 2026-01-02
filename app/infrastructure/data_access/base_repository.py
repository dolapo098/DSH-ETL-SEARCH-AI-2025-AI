from typing import Any, Generic, List, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.repositories.i_base_repository import IBaseRepository

T = TypeVar("T")


class BaseRepository(Generic[T], IBaseRepository[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def update(self, entity: T) -> T:
        return await self.session.merge(entity)

    async def get_single(self, **filters) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).filter_by(**filters)
        )
        
        return result.scalars().first()

    async def get_many(self, *filter_expressions) -> List[T]:
        result = await self.session.execute(
            select(self.model).filter(*filter_expressions)
        )
        
        return list(result.scalars().all())

