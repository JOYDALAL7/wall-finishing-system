from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ---------- Coverage Planning Schemas ----------

class Obstacle(BaseModel):
    x: float
    y: float
    width: float
    height: float


class CoverageRequest(BaseModel):
    wall_width: float = Field(..., gt=0, description="Width of the wall in meters")
    wall_height: float = Field(..., gt=0, description="Height of the wall in meters")
    obstacles: List[Obstacle] = Field(default_factory=list, description="List of rectangular obstacles")
    step: Optional[float] = Field(0.25, gt=0, description="Step size for path planning")


class Point(BaseModel):
    x: float
    y: float
    timestamp: float


class CoverageResponse(BaseModel):
    plan_id: str
    points: List[Point]


# ---------- Trajectory Schemas ----------

class TrajectoryBase(BaseModel):
    x: float
    y: float
    timestamp: float
    plan_id: str


class TrajectoryCreate(TrajectoryBase):
    pass


class TrajectoryResponse(TrajectoryBase):
    """Response schema for a single trajectory record."""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # ✅ ORM -> Pydantic support
        json_encoders = {
            # ✅ Converts datetime -> float automatically during JSON serialization
            datetime: lambda v: v.timestamp()
        }


class TrajectoryListResponse(BaseModel):
    """Response for a paginated list of trajectories."""
    total: int
    trajectories: List[TrajectoryResponse]
