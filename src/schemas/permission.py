from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException, status

class MechanicPermissionOut(BaseModel):
    id: int
    key: str
    user_id: int
    created_at: datetime
    used_at: datetime | None
    expires_at: datetime


class CreateMechanicPermission(BaseModel):
    user_id: int = Field(..., ge=1)
    expire_at: datetime

    @field_validator("expire_at", mode="after")
    @classmethod
    def validate(cls, value: datetime) -> datetime:
        now = datetime.now(timezone.utc)

        if value <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="expire_at must be in the future."
            )

        return value


class UpdateMechanicPermission(BaseModel):
    is_used: bool | None = None
    used_at: datetime | None = None

