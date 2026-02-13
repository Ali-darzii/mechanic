from sqlalchemy import Boolean, Column, DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.orm import relationship

from src.models.base import Base



class MechanicComment(Base):
    __tablename__ = "mechanic_comment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)

    comment = Column(Text, nullable=False)
    rate = Column(Integer, nullable=False)
    anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="mechanic_comments")

    mechanic_request_id = Column(Integer, ForeignKey("mechanic_car_request.id", ondelete="CASCADE"), nullable=False, index=True)
    mechanic_request = relationship("MechanicCarRequest", back_populates="comments")

    parent_id = Column(Integer, ForeignKey(f"mechanic_comment.id", ondelete="SET NULL"), nullable=True, index=True)
    parent = relationship("MechanicComment", remote_side=[id], back_populates="childs")
    childs = relationship("MechanicComment", back_populates="parent", passive_deletes=True)