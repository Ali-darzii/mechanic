from sqlalchemy import select

from src.repositories.base import SqlRepository
from src.models.mechanic import Mechanic as MechanicModel



class MechanicRepository(SqlRepository):
    model  = MechanicModel

    
    async def get_by_user_id(self, user_id: int) -> MechanicModel | None:
        result = await self.db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalar_one_or_none()