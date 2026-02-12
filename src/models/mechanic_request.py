from enum import Enum

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as AlchemyEnum

from src.models.base import Base


class MechanicRequestStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    under_repair = "under repair"
    repired = "repaired"
    delivered = "delivered"

class MechanicRequest(Base):
    __tablename__ = "mechanic_request"

    id = Column(primary_key=True, index=True, autoincrement=True, nullable=False)

    mechanic_id = Column(Integer, ForeignKey("mechanic.id", ondelete="CASCADE"), nullable=False, index=True)
    mechanic = relationship("Mechanic", back_populates="requests")

    car_id = Column(Integer, ForeignKey("car.id", ondelete="CASCADE"), nullable=False, index=True)
    car = relationship("Car", back_populates="mechanic_requests")

    status = Column(
        AlchemyEnum(
            MechanicRequestStatus, name="mechanic_request_status", native_enum=True
        ),
        nullable=False,
        default=MechanicRequestStatus.pending,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
