from typing import List
from fastapi import APIRouter, Depends, status

from src.models.user import User as UserModel
from src.models.user import UserRole
from src.services.car import CarService
from src.schemas.car import CreateCar, UpdateCar, CarOut, GetCarOut
from src.utils.auth import get_current_user_with_permission


router = APIRouter(
    prefix="/car",
    tags=["v1 - car"]
)


@router.post("", response_model=CarOut, status_code=status.HTTP_201_CREATED)
async def create_car(
    car: CreateCar,
    service: CarService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> CarOut:
    return await service.create(car, user)


@router.patch("/{car_id}", response_model=CarOut, status_code=status.HTTP_200_OK)
async def update_car(
    car_id: int,
    car: UpdateCar,
    service: CarService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> CarOut:
    return await service.update(car_id, car, user)


@router.get("", response_model=List[CarOut], status_code=status.HTTP_200_OK)
async def list_user_cars(
    service: CarService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> List[CarOut]:
    return await service.list_user_cars(user)

@router.get("/{car_id}", response_model=GetCarOut, status_code=status.HTTP_200_OK)
async def retrieve_car(
    car_id: int,
    service: CarService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
) -> GetCarOut:
    return await service.get_by_car_id_and_user_id(car_id, user)

@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    service: CarService = Depends(),
    user: UserModel = Depends(get_current_user_with_permission([UserRole.user]))
):
    await service.delete(car_id, user)