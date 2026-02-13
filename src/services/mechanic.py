from datetime import datetime, timezone
from typing import List
from src.models.user import User as UserModel, UserRole
from src.repositories.mechanic import MechanicRepository
from src.repositories.permission import MechanicPermissionRepository
from src.repositories.user import UserRepository
from src.schemas.mechanic import CreateMechanic, UpdateMechanic, MechanicOut

from fastapi import Depends, HTTPException, status

from src.schemas.permission import UpdateMechanicPermission


class MechanicService:
    def __init__(
        self,
        repository: MechanicRepository = Depends(),
        mechanic_permission_repository: MechanicPermissionRepository = Depends(),
        user_repository: UserRepository = Depends(),
    ):
        self._repository = repository
        self._mechanic_permission_repository = mechanic_permission_repository
        self._user_repository = user_repository

    async def create(self, mechanic: CreateMechanic, user: UserModel) -> MechanicOut:
        mechanic.user_id = user.id
        now = datetime.now(timezone.utc)

        mechanic_exist = await self._repository.get_by_user_id(mechanic.user_id)
        if mechanic_exist is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Can't create more than 1 mechanic",
            )

        mechanic_permission = await self._mechanic_permission_repository.get_by_key(
            mechanic.key
        )
        
        if (
            mechanic_permission is None
            or mechanic_permission.is_used
            or mechanic_permission.user_id != mechanic.user_id
            or now >= mechanic_permission.expires_at
        ):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Permission key is not acceptable.",
            )

        delattr(mechanic, "key")
        db_obj = await self._repository.create(mechanic)

        await self._mechanic_permission_repository.update(
            mechanic_permission, UpdateMechanicPermission(is_used=True, used_at=now),
            True
        )

        await self._user_repository.change_user_role(user, UserRole.mechanic)

        return db_obj

    async def update(self, mechanic: UpdateMechanic, user: UserModel, partial: bool) -> MechanicOut:
        db_obj = await self._repository.get_by_user_id(user.id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic not found."
            )

        db_obj = await self._repository.update(db_obj, mechanic, partial=partial)

        return db_obj
    
    async def list_all(self, limit: int, offset: int) -> List[MechanicOut]:
        return await self._repository.list_all(limit, offset)

    
    async def delete(self, user: UserModel) -> None:
        db_obj = await self._repository.get_by_user_id(user.id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic not found."
            )
        
        await self._user_repository.change_user_role(user, UserRole.user)

        await self._repository.delete(db_obj)