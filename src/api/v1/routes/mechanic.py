from typing import List
from fastapi import APIRouter, Depends, Query, status

from src.models.user import User as UserModel, UserRole
from src.services.mechanic import MechanicService
from src.schemas.mechanic import CreateMechanic, UpdateMechanic, MechanicOut
from src.utils.auth import get_current_user, get_current_user_with_permission

router = APIRouter(
    prefix="/mechanic",
    tags=["v1 - mechanic"]
)

@router.post("", response_model=MechanicOut, status_code=status.HTTP_201_CREATED)
async def create_mechanic(
    mechanic: CreateMechanic,
    service: MechanicService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> MechanicOut:
    return await service.create(mechanic, user)


@router.patch("", response_model=MechanicOut, status_code=status.HTTP_201_CREATED)
async def partial_update_mechanic(
    mechanic: UpdateMechanic,
    service: MechanicService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.mechanic]))
) -> MechanicOut:
    return await service.update(mechanic, user, True)


@router.get("", response_model=List[MechanicOut], status_code=status.HTTP_200_OK)
async def list_all_mechanic(
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    service: MechanicService = Depends(),
    user: UserModel = Depends(get_current_user)
) -> List[MechanicOut]:
    return await service.list_all(limit, offset)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mechanic(
    service: MechanicService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.mechanic]))
):
    await service.delete(user)
