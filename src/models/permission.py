from sqlalchemy import Column, Boolean, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship

from src.models.base import Base

class MechanicPermission(Base):
    __tablename__ = "mechanic_permission"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)

    key = Column(String(100), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="mechanic_keys")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

