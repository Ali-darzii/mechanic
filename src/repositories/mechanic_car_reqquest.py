from typing import List

from sqlalchemy import select

from src.models.car import Car as CarModel
from src.models.mechanic import Mechanic as MechanicModel
from src.models.mechanic_car_request import MechanicCarRequest as MechanicCarRequestModel
from src.repositories.base import SqlRepository


class MechanicCarRequestRepository(SqlRepository):
    model = MechanicCarRequestModel

    async def list_all_by_user_id(self, user_id: int) -> List[MechanicCarRequestModel]:
        result = await self.db.execute(
            select(self.model)
            .join(self.model.car)
            .where(CarModel.user_id == user_id)
        )
        return result.scalars().all()
    
    async def list_all_by_user_mechanic_id(self, mechaic_user_id: int) -> List[MechanicCarRequestModel]:
        result = await self.db.execute(
            select(self.model)
            .join(self.model.mechanic)
            .where(MechanicModel.user_id == mechaic_user_id)
        )
        return result.scalars().all()

    async def get_by_user_id_and_mechanic_request_id(self, mechanic_request_id: int, user_id: int) -> List[MechanicCarRequestModel]:
        result = await self.db.execute(
            select(self.model)
            .join(self.model.car)
            .where(self.model.id == mechanic_request_id, CarModel.user_id == user_id)
        )

        return result.scalar_one_or_none()

    