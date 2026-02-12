from typing import List
from fastapi import APIRouter, Depends, Query, status

from src.models.user import User as UserModel, UserRole
from src.schemas.permission import CreateMechanicPermission, MechanicPermissionOut
from src.services.permission import MechanicPermissionService
from src.utils.auth import get_current_user_with_permission


router = APIRouter(
    prefix="/permission",
    tags=["v1 - permission"]
)

@router.post("/mechanic", response_model=MechanicPermissionOut, status_code=status.HTTP_201_CREATED)
async def create_mechenic_permission(
    mechanic_permission: CreateMechanicPermission,
    service: MechanicPermissionService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.admin])),
) -> MechanicPermissionOut:
    return await service.create(mechanic_permission)


@router.get("/mechanic", response_model=List[MechanicPermissionOut], status_code=status.HTTP_200_OK)
async def list_all_mechanic_permission(
    limit: int = Query(100, ge=0),
    offset: int = Query(0, ge=0),
    service: MechanicPermissionService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.admin])),
) -> List[MechanicPermissionOut]:
    return await service.list_all(limit, offset)


@router.get("/mechanic/{key}", response_model=MechanicPermissionOut, status_code=status.HTTP_200_OK)
async def get_mechanic_permission_by_key(
    key: str,
    service: MechanicPermissionService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.admin])),
) -> MechanicPermissionOut:
    return await service.get_by_key(key)