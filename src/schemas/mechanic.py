from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point


class CreateMechanic(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    geom: List[float]
    key: str
    
    model_config = ConfigDict(extra='allow')

    @field_validator("geom", mode="after")
    def validate_geom(cls, v):
        if len(v) != 2:
            raise ValueError("Geom length must be 2.")
        try:
            return from_shape(Point(v[0], v[1]), srid=4326)
        except Exception:
            raise ValueError("Geom is in bad format.")


class UpdateMechanic(BaseModel):
    name: str | None  = Field(None, max_length=150)
    description: str | None = None
    geom: List[float] | None = None

    @field_validator("geom", mode="after")
    def validate_geom(cls, v):
        if v:
            if len(v) != 2:
                raise ValueError("Geom length must be 2.")
            try:
                return from_shape(Point(v[0], v[1]), srid=4326)
            except Exception:
                raise ValueError("Geom is in bad format.")
        return v
    

class MechanicOut(BaseModel):
    id: int
    name: str
    description: str 
    geom: List[float]

    @field_validator("geom", mode="before")
    def serialize_geom(cls, geom):
        try:
            point = to_shape(geom)
            return [point.x, point.y]
        except Exception:
            raise ValueError("Serializing geom went wrong.")