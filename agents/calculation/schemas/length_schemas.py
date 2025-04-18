"""
Length calculation input schema module

This module defines input schemas used in length calculation tools.
These schemas specify the required parameters and their formats for various geometric length calculations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DistanceBetweenPointsInput(BaseModel):
    """Input schema for calculating the distance between two points in a 2D coordinate system.
    The points are specified by their x,y coordinates."""
    point1: List[float] = Field(..., description="Coordinates of the first point [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point [x2, y2]", min_items=2, max_items=2)

class DistancePointToLineInput(BaseModel):
    """Input schema for calculating the perpendicular distance from a point to a line.
    The line is specified in general form ax + by + c = 0."""
    point: List[float] = Field(..., description="Coordinates of the point [x, y]", min_items=2, max_items=2)
    line_a: float = Field(..., description="Coefficient 'a' of the line for ax + by + c = 0")
    line_b: float = Field(..., description="Coefficient 'b' of the line for ax + by + c = 0")
    line_c: float = Field(..., description="Coefficient 'c' of the line for ax + by + c = 0")
    
class DistanceParallelLinesInput(BaseModel):
    """Input schema for calculating the distance between two parallel lines.
    Each line is specified in general form ax + by + c = 0."""
    line1_a: float = Field(..., description="Coefficient 'a' of the first line for ax + by + c = 0")
    line1_b: float = Field(..., description="Coefficient 'b' of the first line for ax + by + c = 0")
    line1_c: float = Field(..., description="Coefficient 'c' of the first line for ax + by + c = 0")
    line2_a: float = Field(..., description="Coefficient 'a' of the second line for ax + by + c = 0")
    line2_b: float = Field(..., description="Coefficient 'b' of the second line for ax + by + c = 0")
    line2_c: float = Field(..., description="Coefficient 'c' of the second line for ax + by + c = 0")
    
class PerimeterTriangleInput(BaseModel):
    """Input schema for calculating the perimeter of a triangle.
    The triangle is specified by the coordinates of its three vertices."""
    points: List[List[float]] = Field(..., description="Coordinates of the three vertices of the triangle, format [[x1,y1], [x2,y2], [x3,y3]]")
    
class PerimeterQuadrilateralInput(BaseModel):
    """Input schema for calculating the perimeter of a quadrilateral.
    The quadrilateral is specified by the coordinates of its four vertices."""
    points: List[List[float]] = Field(..., description="Coordinates of the four vertices of the quadrilateral, format [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")
    
class PerimeterPolygonInput(BaseModel):
    """Input schema for calculating the perimeter of a polygon.
    The polygon is specified by the coordinates of its vertices."""
    points: List[List[float]] = Field(..., description="Coordinates of the vertices of the polygon, format [[x1,y1], [x2,y2], ...]")
    
class CircumferenceInput(BaseModel):
    """Input schema for calculating the circumference of a circle.
    The circle is specified by its radius."""
    radius: float = Field(..., description="Radius of the circle")

class ChordLengthInput(BaseModel):
    """Input schema for calculating the length of a chord in a circle.
    The chord is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle: float = Field(..., description="Central angle (in radians or degrees)")
    degrees: Optional[bool] = Field(False, description="Whether the angle is in degrees, True for degrees, False for radians")
    
class ArcLengthInput(BaseModel):
    """Input schema for calculating the length of an arc in a circle.
    The arc is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle: float = Field(..., description="Central angle (in radians or degrees)")
    degrees: Optional[bool] = Field(False, description="Whether the angle is in degrees, True for degrees, False for radians")
