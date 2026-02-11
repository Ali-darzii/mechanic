from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base

class Mechanic(Base):
    __tablename__ = "mechanic"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)

    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326))
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    user = relationship("User", back_populates="mechanic")