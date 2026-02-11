from datetime import datetime

from sqlalchemy import select

from src.repositories.base import SqlRepository
from src.models.permission import MechanicPermission as MechanicPermissionModel


class MechanicPermissionRepository(SqlRepository):
    model = MechanicPermissionModel

    async def create(self, key: str, user_id, expires_at: datetime) -> MechanicPermissionModel:
        db_obj = self.model(
            key=key,
            user_id=user_id,
            expires_at=expires_at
        )

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj

    async def get_by_key(self, key: str) -> MechanicPermissionModel | None:
        result = await self.db.execute(
            select(self.model).where(self.model.key == key)
        )
        return result.scalar_one_or_none()