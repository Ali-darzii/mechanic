from typing import List

from fastapi import Depends, HTTPException, status

from src.repositories.car import CarRepository
from src.models.user import User as UserModel
from src.models.car import Car as CarModel
from src.schemas.car import CreateCar, UpdateCar


class CarService:
    def __init__(self, repository: CarRepository = Depends()):
        self._repository = repository

    async def create(self, car: CreateCar, user: UserModel) -> CarModel:
        car.user_id = user.id

        db_obj = await self._repository.create(car)
        return db_obj

    async def update(self, car_id: int, car: UpdateCar, user: UserModel) -> CarModel:
        db_obj = await self._repository.get_by_id_and_user_id(car_id, user.id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id: {car_id} not found.",
            )

        db_obj = await self._repository.update(db_obj, car, True)

        return db_obj

    async def list_user_cars(self, user: UserModel) -> List[CarModel]:
        return await self._repository.list_user_cars(user.id)

    async def get_by_car_id_and_user_id(self, car_id: int, user: UserModel) -> CarModel:
        db_obj = await self._repository.get_by_id_and_user_id_with_mechanic_requests_relation(
            car_id, user.id
        )
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id: {car_id} not found.",
            )

        return db_obj

    async def delete(self, car_id:int , user: UserModel) -> None:
        db_obj = await self._repository.get_by_id_and_user_id(car_id, user.id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id: {car_id} not found.",
            )
        
        await self._repository.delete(db_obj)