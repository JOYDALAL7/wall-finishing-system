from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
import datetime


class Trajectory(Base):
    __tablename__ = "trajectories"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
