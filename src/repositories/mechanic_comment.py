from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.user import User as UserModel
from src.models.mechanic_comments import MechanicComment as MechanicCommentModel
from src.models.mechanic_car_request import MechanicCarRequest as MechanicCarRequestModel
from src.repositories.base import SqlRepository


class MechanicCommentRepository(SqlRepository):
    model = MechanicCommentModel

    async def get_mechanic_comments_by_mechanic_id(
        self, mechanic_id: int, limit:int, offset:int
    ) -> List[MechanicCommentModel]:
        result = await self.db.execute(
            select(self.model)
            .join(
                MechanicCarRequestModel,
                self.model.mechanic_request_id == MechanicCarRequestModel.id
            )
            .where(MechanicCarRequestModel.mechanic_id == mechanic_id)
            .options(
                selectinload(self.model.mechanic_request),
                selectinload(self.model.user)
            )
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()