from fastapi import Depends, HTTPException, status

from src.models.mechanic_car_request import MechanicCarRequestStatus
from src.models.mechanic_comments import MechanicComment as MechanicCommentModel
from src.models.user import User as UserModel
from src.repositories.mechanic_car_reqquest import MechanicCarRequestRepository
from src.repositories.mechanic_comment import MechanicCommentRepository  
from src.schemas.mechanic_comment import CreateMechanicComment


class MechanicCommnetService:
    def __init__(self, repository: MechanicCommentRepository = Depends(), mechanic_request_repository: MechanicCarRequestRepository = Depends()):
        self._repository = repository
        self._mechanic_request_repository = mechanic_request_repository

    async def create(self, comment: CreateMechanicComment, user: UserModel) -> MechanicCommentModel:
        comment.user_id = user.id

        mechanic_request = await self._mechanic_request_repository.get_by_user_id_and_mechanic_request_id(comment.mechanic_request_id, user.id)
        if mechanic_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mechanic request wiht id: {comment.mechanic_request_id} not found."
            )
        
        if mechanic_request.status != MechanicCarRequestStatus.delivered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Car should delivered to you can inesrt a comment."
            )
        
        db_obj = await self._repository.create(comment)
        
        return db_obj
    
    async def list_mechanic_comments(self, mechanic_id: int, limit: int, offset: int):
        return await self._repository.get_mechanic_comments_by_mechanic_id(mechanic_id, limit, offset)

    async def delete(self, user, commentd_id: int) -> None:
        db_obj = await self._repository.get_by_id(commentd_id)
        if db_obj is None or db_obj.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with id: {commentd_id} not found."
            )

        await self._repository.delete(db_obj)
