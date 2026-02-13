from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.mechanic_car_request import MechanicCarRequestOut

class CreateMechanicComment(BaseModel):
    comment: str
    rate: int = Field(..., ge=1, le=5)
    anonymous: bool = False
    mechanic_request_id: int = Field(..., ge=1)
    parent_id: int | None = Field(None, ge=1)
    
    model_config = ConfigDict(extra='allow')


class MechanicCommentOut(BaseModel):
    id: int
    comment: str
    rate: int
    user_id: int
    mechanic_request_id: int
    parent_id: int | None
    created_at: datetime


class CommentUserOut(BaseModel):
    first_name: str

class GetMechanicCommentOut(BaseModel):
    id: int
    comment: str
    rate: int
    user: CommentUserOut
    mechanic_request: MechanicCarRequestOut
    parent_id: int | None
    created_at: datetime