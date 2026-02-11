from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.orm import relationship

from src.models.base import Base

class UserRole(int, Enum):
    user = 0
    mechanic = 1
    admin = 2


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)

    phone_number = Column(String(11), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    avatar = Column(String(200), nullable=True)
    role = Column(AlchemyEnum(UserRole, name="user_role", native_enum=True), nullable=False, default=UserRole.user)
    is_active = Column(Boolean, default=False)
    is_delete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    mechanic_keys = relationship("MechanicPermission", back_populates="user")
    mechanic = relationship("Mechanic", back_populates="user")