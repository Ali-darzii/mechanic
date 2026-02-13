from typing import List
from fastapi import APIRouter, status, Depends, Query

from src.models.user import User as UserModel, UserRole
from src.utils.auth import get_current_user
from src.services.mechanic_comment import MechanicCommnetService
from src.schemas.mechanic_comment import CreateMechanicComment, MechanicCommentOut, GetMechanicCommentOut

router = APIRouter(
    prefix="/mechanic/comment",
    tags=["v1- mechanic - comment"]
)


@router.post("", response_model=MechanicCommentOut, status_code=status.HTTP_201_CREATED)
async def create_mechanic_comment(
    comment: CreateMechanicComment,
    service: MechanicCommnetService = Depends(),
    user: UserModel = Depends(get_current_user)
) -> MechanicCommentOut:
    return await service.create(comment, user)


@router.get("/{mechanic_id}", response_model=List[GetMechanicCommentOut], status_code=status.HTTP_200_OK)
async def list_by_mechanic_id(
    mechanic_id: int,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    service: MechanicCommnetService = Depends(),
    user: UserModel = Depends(get_current_user)
) -> List[GetMechanicCommentOut]:
    return await service.list_mechanic_comments(mechanic_id, limit, offset)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    service: MechanicCommnetService = Depends(),
    user: UserModel = Depends(get_current_user)
):
    await service.delete(user, comment_id)