from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from src.models.base import Base

class RevokedToken(Base):
    __tablename__ = "revoked_token"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    jti = Column(String(128), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)