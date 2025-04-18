"""
Circle calculation input schema module

This module defines input schemas used in circle calculation tools.
These schemas specify the required parameters and their formats for various geometric calculations involving circles.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class CircleRadiusInput(BaseModel):
    """Input schema for calculating circle area.
    The circle is specified by its radius."""
    radius: float = Field(..., description="Radius of the circle")

class CircleDiameterInput(BaseModel):
    """Input schema for calculating circle diameter.
    The circle is specified by its diameter."""
    diameter: float = Field(..., description="Diameter of the circle")

class CircleRadiusAngleInput(BaseModel):
    """Input schema for calculating chord length.
    The chord is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle: float = Field(..., description="Central angle (in radians)")

class CircleChordLengthInput(BaseModel):
    """Input schema for calculating chord length.
    The chord is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle: float = Field(..., description="Central angle (in radians)")

class CircleSectorAreaInput(BaseModel):
    """Input schema for calculating sector area.
    The sector is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle: float = Field(..., description="Central angle (in radians)")

class CircleSegmentAreaInput(BaseModel):
    """Input schema for calculating segment area.
    The segment is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle: float = Field(..., description="Central angle (in radians)")

class PointCirclePositionInput(BaseModel):
    """Input schema for determining the position of a point relative to a circle.
    The circle is specified by its center coordinates and radius, and the point by its coordinates."""
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    radius: float = Field(..., description="Radius of the circle")
    point: List[float] = Field(..., description="Coordinates of the point to check [x, y]", min_items=2, max_items=2)

class CircleTangentPointsInput(BaseModel):
    """Input schema for calculating tangent points from an external point to a circle.
    The circle is specified by its center coordinates and radius, and the external point by its coordinates."""
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    radius: float = Field(..., description="Radius of the circle")
    external_point: List[float] = Field(..., description="Coordinates of the external point [x, y]", min_items=2, max_items=2)

class CircleIntersectionInput(BaseModel):
    """Input schema for calculating intersection points of two circles.
    Each circle is specified by its center coordinates and radius."""
    center1: List[float] = Field(..., description="Center coordinates of the first circle [x1, y1]", min_items=2, max_items=2)
    radius1: float = Field(..., description="Radius of the first circle")
    center2: List[float] = Field(..., description="Center coordinates of the second circle [x2, y2]", min_items=2, max_items=2)
    radius2: float = Field(..., description="Radius of the second circle")

class CircleFromThreePointsInput(BaseModel):
    """Input schema for determining a circle from three points.
    The circle is specified by the coordinates of three points that lie on it."""
    points: List[List[float]] = Field(..., description="Coordinates of three points on the circle, format [[x1,y1], [x2,y2], [x3,y3]]")

class CircleFromCenterPointInput(BaseModel):
    """Input schema for determining a circle from its center and a point on it.
    The circle is specified by its center coordinates and a point that lies on it."""
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    point: List[float] = Field(..., description="Coordinates of a point on the circle [x, y]", min_items=2, max_items=2)

class CentralAngleInput(BaseModel):
    """Input schema for calculating the central angle of a circle.
    The angle is specified by the circle's center and two points on the circle."""
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    point1: List[float] = Field(..., description="Coordinates of the first point on the circle [x, y]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point on the circle [x, y]", min_items=2, max_items=2)

class InscribedAngleInput(BaseModel):
    """Input schema for calculating the inscribed angle of a circle.
    The angle is specified by the circle's center and three points on the circle."""
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    point1: List[float] = Field(..., description="Coordinates of the first point on the circle [x, y]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the vertex point on the circle [x, y]", min_items=2, max_items=2)
    point3: List[float] = Field(..., description="Coordinates of the third point on the circle [x, y]", min_items=2, max_items=2)

class PowerOfPointInput(BaseModel):
    """Input schema for calculating the power of a point with respect to a circle.
    The calculation is specified by the point coordinates, circle center, and radius."""
    point: List[float] = Field(..., description="Coordinates of the point [x, y]", min_items=2, max_items=2)
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    radius: float = Field(..., description="Radius of the circle") 