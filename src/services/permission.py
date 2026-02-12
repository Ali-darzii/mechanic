from datetime import datetime
import secrets
import string


from fastapi import Depends, HTTPException, status

from src.repositories.permission import MechanicPermissionRepository
from src.repositories.user import UserRepository
from src.schemas.permission import CreateMechanicPermission, MechanicPermissionOut

class MechanicPermissionService:

    def __init__(self, repository: MechanicPermissionRepository = Depends(), user_repository: UserRepository = Depends()):
        self._repository = repository
        self._user_repository = user_repository


    def generate_random_string(self, length: int = 50) -> str:
        """ with string.punctuation gonna be too complicated"""
        punctuation = "@#$%"
        characters = string.digits + string.ascii_letters + punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))


    async def create(self, mechanic_permission: CreateMechanicPermission) -> MechanicPermissionOut:
        if self._user_repository.get_by_id(mechanic_permission.user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {mechanic_permission.user_id} not found."
            )
        
        key = self.generate_random_string()

        return await self._repository.create(
            key,
            mechanic_permission.user_id,
            mechanic_permission.expire_at
        )


    async def list_all(self, limit: int, offset: int):
        return await self._repository.list_all(limit, offset)


    async def get_by_key(self, key: str) -> MechanicPermissionOut:
        db_obj = await self._repository.get_by_key(key)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic permission with key: {key} not found."
            )
        
        return db_obj