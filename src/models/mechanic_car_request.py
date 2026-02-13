from enum import Enum

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as AlchemyEnum

from src.models.base import Base


class MechanicCarRequestStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    under_repair = "under repair"
    repaired = "repaired"
    delivered = "delivered"

class MechanicCarRequestIssue(str, Enum):
    motor = "motor"
    gear_box = "gear box"
    electronic = "electronic"
    suspension_system = "suspension system"
    other = "other"


class MechanicCarRequest(Base):
    __tablename__ = "mechanic_car_request"

    id = Column(Integer, primary_key=True, index=True)

    status = Column(
        AlchemyEnum(
            MechanicCarRequestStatus, name="mechanic_car_request_status", native_enum=True
        ),
        nullable=False,
        default=MechanicCarRequestStatus.pending,
    )
    issue = Column(
        AlchemyEnum(
            MechanicCarRequestIssue, name="mechanic_car_request_issue", native_enum=True
        ),
        nullable=False,
    )
    description = Column(Text, nullable=False)

    mechanic_id = Column(Integer, ForeignKey("mechanic.id", ondelete="CASCADE"), nullable=False, index=True)
    mechanic = relationship("Mechanic", back_populates="requests")

    car_id = Column(Integer, ForeignKey("car.id", ondelete="CASCADE"), nullable=False, index=True)
    car = relationship("Car", back_populates="mechanic_requests")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    comments = relationship("MechanicComment", back_populates="mechanic_request", cascade="all, delete-orphan")