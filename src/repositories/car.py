from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.car import Car as CarModel
from src.repositories.base import SqlRepository

class CarRepository(SqlRepository):
    model = CarModel

    async def get_by_id_and_user_id(self, pk: int, user_id: int) -> CarModel | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == pk, self.model.user_id == user_id)
        )
        return result.scalar_one_or_none()


    async def get_by_id_and_user_id_with_mechanic_requests_relation(self, pk: int, user_id: int) -> CarModel | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == pk, self.model.user_id == user_id)
            .options(selectinload(self.model.mechanic_requests))
        )
        return result.scalar_one_or_none()
    
    async def list_user_cars(self, user_id: int) -> List[CarModel]:
        result = await self.db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()