"""
Area calculation input schema module

This module defines input schemas used in area calculation tools.
These schemas specify the required parameters and their formats for calculating areas of various geometric shapes.
"""

from typing import List, Optional, Union, Dict, Any, Tuple
from pydantic import BaseModel, Field

class TriangleAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a triangle from its vertices.
    The triangle is specified by the coordinates of its three vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of three vertices [[x1, y1], [x2, y2], [x3, y3]]")

class TriangleAreaFromSidesInput(BaseModel):
    """Input schema for calculating the area of a triangle using Heron's formula.
    The triangle is specified by the lengths of its three sides."""
    a: float = Field(..., description="Length of first side")
    b: float = Field(..., description="Length of second side")
    c: float = Field(..., description="Length of third side")

class TriangleAreaFromBaseHeightInput(BaseModel):
    """Input schema for calculating the area of a triangle using base and height.
    The triangle is specified by its base length and the corresponding height."""
    base: float = Field(..., description="Length of the base")
    height: float = Field(..., description="Height perpendicular to the base")

class RectangleAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a rectangle from its vertices.
    The rectangle is specified by the coordinates of its four vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of four vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")

class RectangleAreaFromWidthHeightInput(BaseModel):
    """Input schema for calculating the area of a rectangle from its width and height.
    The rectangle is specified by its width and height dimensions."""
    width: float = Field(..., description="Width of the rectangle")
    height: float = Field(..., description="Height of the rectangle")

class SquareAreaFromSideInput(BaseModel):
    """Input schema for calculating the area of a square from its side length.
    The square is specified by the length of one of its sides."""
    side: float = Field(..., description="Length of a side of the square")

class ParallelogramAreaFromBaseHeightInput(BaseModel):
    """Input schema for calculating the area of a parallelogram from its base and height.
    The parallelogram is specified by its base length and the corresponding height."""
    base: float = Field(..., description="Length of the base")
    height: float = Field(..., description="Height perpendicular to the base")

class ParallelogramAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a parallelogram from its vertices.
    The parallelogram is specified by the coordinates of its four vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of four vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")
    
class RhombusAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a rhombus from its vertices.
    The rhombus is specified by the coordinates of its four vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of four vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")

class RhombusAreaFromDiagonalsInput(BaseModel):
    """Input schema for calculating the area of a rhombus from its diagonals.
    The rhombus is specified by the lengths of its two diagonals."""
    diagonal1: float = Field(..., description="Length of first diagonal")
    diagonal2: float = Field(..., description="Length of second diagonal")

class TrapezoidAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a trapezoid from its vertices.
    The trapezoid is specified by the coordinates of its four vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of four vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")

class TrapezoidAreaFromBaseHeightInput(BaseModel):
    """Input schema for calculating the area of a trapezoid from its bases and height.
    The trapezoid is specified by the lengths of its parallel sides (bases) and the height between them."""
    base1: float = Field(..., description="Length of first parallel side")
    base2: float = Field(..., description="Length of second parallel side")
    height: float = Field(..., description="Height between parallel sides")

class RegularPolygonAreaFromSideInput(BaseModel):
    """Input schema for calculating the area of a regular polygon from its side length.
    The polygon is specified by the number of sides and the length of one side."""
    side: float = Field(..., description="Length of a side of the regular polygon")
    n: int = Field(..., description="Number of sides of the regular polygon")

class PolygonAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a polygon from its vertices.
    The polygon is specified by the coordinates of its vertices in order."""
    vertices: List[List[float]] = Field(..., description="Coordinates of vertices [[x1, y1], [x2, y2], ..., [xn, yn]]")

class CircleAreaFromRadiusInput(BaseModel):
    """Input schema for calculating the area of a circle from its radius.
    The circle is specified by its radius."""
    radius: float = Field(..., description="Radius of the circle")

class SectorAreaFromRadiusAngleInput(BaseModel):
    """Input schema for calculating the area of a circular sector.
    The sector is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle_rad: float = Field(..., description="Central angle in radians")
    degrees: Optional[bool] = Field(False, description="Whether the angle is in degrees instead of radians")

class SegmentAreaFromRadiusAngleInput(BaseModel):
    """Input schema for calculating the area of a circular segment.
    The segment is specified by the circle's radius and the central angle it subtends."""
    radius: float = Field(..., description="Radius of the circle")
    angle_rad: float = Field(..., description="Central angle in radians")
    degrees: Optional[bool] = Field(False, description="Whether the angle is in degrees instead of radians")

class QuadrilateralAreaFromPointsInput(BaseModel):
    """Input schema for calculating the area of a quadrilateral from its vertices.
    The quadrilateral is specified by the coordinates of its four vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of four vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")