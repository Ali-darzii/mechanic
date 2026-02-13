from typing import List
from fastapi import APIRouter, status, Depends, Query

from src.models.user import User as UserModel, UserRole
from src.services.mechanic_car_reqquest import MechanicCarRequstService
from src.schemas.mechanic_car_request import CreateMechanicCarRequest, UpdateMechanicCarRequestByMechanic, UpdateMechanicCarRequestByUser, MechanicCarRequestOut
from src.utils.auth import get_current_user, get_current_user_with_permission


rotuer = APIRouter(
    prefix="/mechanic/car/request",
    tags=["v1 - mechanic - car - request"]
)

@rotuer.post("", response_model=MechanicCarRequestOut, status_code=status.HTTP_201_CREATED)
async def create_mechanic_car_request(
    mechanic_request: CreateMechanicCarRequest,
    service: MechanicCarRequstService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> MechanicCarRequestOut:
    return await service.create(mechanic_request, user)


@rotuer.patch("/user/{mechanic_request_id}", response_model=MechanicCarRequestOut, status_code=status.HTTP_200_OK)
async def update_mechanic_car_request_by_user(
    mechanic_request_id: int,
    mechanic_request: UpdateMechanicCarRequestByUser,
    service: MechanicCarRequstService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> MechanicCarRequestOut:
    return await service.update_by_user(mechanic_request_id, mechanic_request, user)


@rotuer.patch("/mechanic-user/{mechanic_request_id}", response_model=MechanicCarRequestOut, status_code=status.HTTP_200_OK)
async def update_mechanic_car_request_by_mechanic_user(
    mechanic_request_id: int,
    mechanic_request: UpdateMechanicCarRequestByMechanic,
    service: MechanicCarRequstService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.mechanic]))
) -> MechanicCarRequestOut:
    return await service.update_by_mechanic(mechanic_request_id, mechanic_request, user)


@rotuer.get("", response_model=List[MechanicCarRequestOut], status_code=status.HTTP_200_OK)
async def list_mechanic_car_request(
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    service: MechanicCarRequstService = Depends(),
    user: UserModel = Depends(get_current_user)
) -> List[MechanicCarRequestOut]:
    return await service.list_mechanic_reqeusts(user, limit, offset)


