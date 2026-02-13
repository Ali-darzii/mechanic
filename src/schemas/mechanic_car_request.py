from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, Field

from src.models.mechanic_car_request import MechanicCarRequestStatus, MechanicCarRequestIssue

class CreateMechanicCarRequest(BaseModel):
    issue: MechanicCarRequestIssue
    description: str
    mechanic_id: int = Field(..., ge=1)
    car_id: int = Field(..., ge=1)

    model_config = ConfigDict(extra='allow')

class UpdateMechanicCarRequestByUser(BaseModel):
    issue: MechanicCarRequestIssue
    description: str


class UpdateMechanicCarRequestByMechanic(BaseModel):
    status: MechanicCarRequestStatus


class MechanicCarRequestOut(BaseModel):
    id: int
    status: MechanicCarRequestStatus
    issue: MechanicCarRequestIssue
    description: str
    mechanic_id: int
    car_id: int
    created_at: datetime
    updated_at: datetime | None


class CarOut(BaseModel):
    id: int
    title: str
    car_type: str
    color: str | None
    tip: str
    model: date
    description: str | None = None
    license_plate: str
    user_id: int
    created_at: datetime
    updated_at: datetime | None

class GetMechanicCarRequestOut(BaseModel):
    id: int
    status: MechanicCarRequestStatus
    issue: MechanicCarRequestIssue
    description: str
    mechanic_id: int
    car: CarOut
    created_at: datetime
    updated_at: datetime | None