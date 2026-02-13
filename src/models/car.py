from sqlalchemy import Column, Date, DateTime, String, Integer, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from src.models.base import Base



class Car(Base):
    __tablename__ = "car"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100),nullable=False)
    car_type = Column(String(100), nullable=False)
    color = Column(String(50), nullable=True)
    tip = Column(String(100), nullable=False)
    model = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    license_plate = Column(String(8), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="cars")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    mechanic_requests = relationship("MechanicCarRequest", back_populates="car", cascade="all, delete-orphan")
