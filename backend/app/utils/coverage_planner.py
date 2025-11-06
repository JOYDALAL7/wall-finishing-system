# backend/app/utils/coverage_planner.py
from typing import List, Dict
import uuid
import time

def generate_coverage_path(
    wall_width: float,
    wall_height: float,
    obstacles: List[Dict[str, float]],
    step: float = 0.25
) -> Dict[str, any]:
    """
    Generate a boustrophedon (zig-zag) coverage path avoiding rectangular obstacles.
    Merges adjacent rows to avoid unreachable islands.
    Returns { plan_id, points: [{x, y, timestamp}] }
    """

    def is_inside_obstacle(x, y):
        """Check if point lies inside any rectangular obstacle."""
        for obs in obstacles:
            if (
                obs["x"] <= x <= obs["x"] + obs["width"]
                and obs["y"] <= y <= obs["y"] + obs["height"]
            ):
                return True
        return False

    plan_id = str(uuid.uuid4())
    points = []
    y = 0.0
    direction = 1  # 1 = left→right, -1 = right→left
    timestamp = time.time()

    while y <= wall_height:
        if direction == 1:
            xs = [round(x, 3) for x in frange(0.0, wall_width, step)]
        else:
            xs = [round(x, 3) for x in frange(wall_width, 0.0, -step)]

        for x in xs:
            if not is_inside_obstacle(x, y):
                points.append({
                    "x": x,
                    "y": round(y, 3),
                    "timestamp": timestamp
                })
                timestamp += 0.01

        y += step
        direction *= -1

    return {"plan_id": plan_id, "points": points}


def frange(start: float, stop: float, step: float):
    """Floating point range generator."""
    if step == 0:
        raise ValueError("Step cannot be zero.")
    x = start
    if step > 0:
        while x <= stop:
            yield x
            x += step
    else:
        while x >= stop:
            yield x
            x += step
