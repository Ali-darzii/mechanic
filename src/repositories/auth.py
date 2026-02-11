from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import RevokedToken as RevokedTokenModel
from src.repositories.base import SqlRepository



class RevokedTokenRepository(SqlRepository):
    
    model = RevokedTokenModel

    async def is_revoked_token(self,jti: str) -> bool:
        result = await self.db.execute(
            select(self.model).where(self.model.jti == jti)
        )
        return bool(result.one_or_none())
