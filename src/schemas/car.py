from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.mechanic_car_request import MechanicCarRequestOut


class CreateCar(BaseModel):
    title: str = Field(..., max_length=100)
    car_type: str = Field(..., max_length=100)
    color: str | None = Field(None, max_length=50)
    tip: str = Field(..., max_length=100)
    model: date
    description: str | None = None
    license_plate: str = Field(..., max_length=8)

    model_config = ConfigDict(extra='allow')

class UpdateCar(BaseModel):
    title: str | None = Field(None, max_length=100)
    car_type: str | None = Field(None, max_length=100)
    color: str | None = Field(None, max_length=50)
    tip: str | None = Field(None, max_length=100)
    model: date | None = None
    description: str | None = None
    license_plate: str | None = Field(None, max_length=8)

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


class GetCarOut(CarOut):
    mechanic_requests: List[MechanicCarRequestOut]