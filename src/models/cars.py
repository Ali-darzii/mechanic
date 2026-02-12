from sqlalchemy import Column, Date, DateTime, String, Integer, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import relationship

from src.models.base import Base



class Car(Base):
    __tablename__ = "car"

    id = Column(primary_key=True, index=True, autoincrement=True, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="cars")

    car_type = Column(String(100), nullable=False)
    color = Column(String(50), nullable=True)
    tip = Column(String(100), nullable=False)
    model = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    mechanic_requests = relationship("MechanicRequest", back_populates="car")
