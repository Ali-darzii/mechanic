from typing import List
from fastapi import Depends, HTTPException, status

from src.models.user import User as UserModel, UserRole
from src.repositories.car import CarRepository
from src.repositories.mechanic import MechanicRepository
from src.repositories.mechanic_car_reqquest import MechanicCarRequestRepository
from src.models.mechanic_car_request import (
    MechanicCarRequest as MechanicCarRequestModel,
    MechanicCarRequestStatus,
)
from src.schemas.mechanic_car_request import (
    CreateMechanicCarRequest,
    UpdateMechanicCarRequestByUser,
    UpdateMechanicCarRequestByMechanic,
    MechanicCarRequestOut,
    GetMechanicCarRequestOut,
)
from src.utils.validation import validate_mechanic_car_status_transition


class MechanicCarRequstService:

    def __init__(
        self,
        repository: MechanicCarRequestRepository = Depends(),
        car_repository: CarRepository = Depends(),
        mechanic_repository: MechanicRepository = Depends(),
    ):
        self._repository = repository
        self._mechanic_repository = mechanic_repository
        self._car_repository = car_repository

    async def create(
        self, mechanic_request: CreateMechanicCarRequest, user: UserModel
    ) -> MechanicCarRequestModel:
        mechanic_request.status = MechanicCarRequestStatus.pending

        car = await self._car_repository.get_by_id_and_user_id_with_mechanic_requests_relation(
            mechanic_request.car_id, user.id
        )
        if car is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id: {mechanic_request.car_id} not found.",
            )

        for mechnic_req in car.mechanic_requests:
            if mechnic_req.status != MechanicCarRequestStatus.delivered:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Your car is not delivered. Call our supports!",
                )

        mechanic = await self._mechanic_repository.get_by_id(
            mechanic_request.mechanic_id
        )
        if mechanic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic with id: {mechanic_request.mechanic_id} not found.",
            )
        
        if user.id == mechanic.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Own mechanic can't request mechanic.",
            )


        db_obj = await self._repository.create(mechanic_request)

        return db_obj

    async def update_by_user(
        self,
        mechanic_request_id: int,
        mechanic_request: UpdateMechanicCarRequestByUser,
        user: UserModel,
    ) -> MechanicCarRequestModel:
        db_obj = await self._repository.get_by_id(mechanic_request_id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic request with id: {mechanic_request_id} not found.",
            )

        car = await self._car_repository.get_by_id(db_obj.car_id)
        if car is None or car.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id: {mechanic_request.car_id} not found.",
            )

        if db_obj.status != MechanicCarRequestStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mechanic approved your request, you need to cancel it or call mechanic.",
            )

        db_obj = await self._repository.update(db_obj, mechanic_request, True)

        return db_obj


    async def update_by_mechanic(
        self,
        mechanic_request_id: int,
        mechanic_request: UpdateMechanicCarRequestByMechanic,
        mechanic_user: UserModel,
    ) -> MechanicCarRequestModel:
        db_obj = await self._repository.get_by_id(mechanic_request_id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic Request with id: {mechanic_request_id} not found."
            )
        
        mechanic = await self._mechanic_repository.get_by_id(db_obj.mechanic_id)
        if mechanic.user_id != mechanic_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission Denied."
            )

        validate_mechanic_car_status_transition(db_obj.status, mechanic_request.status)

        db_obj = await self._repository.update(db_obj, mechanic_request, True)

        return db_obj
    

    async def list_mechanic_reqeusts(self, user: UserModel, limit: int, offset: int) -> List[MechanicCarRequestModel]:
        if user.role == UserRole.user:
            return await self._repository.list_all_by_user_id(user.id)

        else:
            return await self._repository.list_all_by_user_mechanic_id(user.id)

    async def delete(self, mechanic_request_id: int, user: UserModel) -> None:
        db_obj = await self._repository.get_by_id(mechanic_request_id)
        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic Request with id: {mechanic_request_id} not found."
            )
        
        if user.role  == UserRole.user:
            car = await self._car_repository.get_by_id(db_obj.car_id)
            if car is None or car.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Car with id: {db_obj.car_id} not found."
                )
            
        else:
            mechanic = await self._mechanic_repository.get_by_id(db_obj.mechanic_id)
            if mechanic is None or mechanic.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mechanic with id {db_obj.mechanic_id} not found."
                )
            
        await self._repository.delete(db_obj)



        