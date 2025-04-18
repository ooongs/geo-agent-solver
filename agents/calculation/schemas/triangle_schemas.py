"""
Triangle calculation input schema module

This module defines input schemas used in triangle calculation tools.
These schemas specify the required parameters and their formats for various geometric calculations involving triangles.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class TriangleVerticesInput(BaseModel):
    """Input schema for triangle calculations using vertices.
    The triangle is specified by the coordinates of its three vertices."""
    vertices: List[List[float]] = Field(
        description="Coordinates of the three vertices of the triangle, format [[x1,y1], [x2,y2], [x3,y3]]",
        min_items=3,
        max_items=3
    )

class TriangleSidesInput(BaseModel):
    """Input schema for triangle calculations using side lengths.
    The triangle is specified by the lengths of its three sides."""
    side1: float = Field(..., description="Length of the first side of the triangle")
    side2: float = Field(..., description="Length of the second side of the triangle")
    side3: float = Field(..., description="Length of the third side of the triangle")

class TriangleAngleInput(BaseModel):
    """Input schema for calculating angles in a triangle.
    The triangle is specified by its three side lengths and the type of angle to calculate."""
    side1: float = Field(..., description="Length of the first side of the triangle")
    side2: float = Field(..., description="Length of the second side of the triangle")
    side3: float = Field(..., description="Length of the third side of the triangle")
    angle_type: str = Field(..., description="Type of angle to calculate: 'A' (opposite to side1), 'B' (opposite to side2), or 'C' (opposite to side3)")

class PointTrianglePositionInput(BaseModel):
    """Input schema for determining the position of a point relative to a triangle.
    The triangle is specified by the coordinates of its three vertices, and the point by its coordinates."""
    point: List[float] = Field(..., description="Coordinates of the point to check [x, y]", min_items=2, max_items=2)
    vertices: List[List[float]] = Field(
        description="Coordinates of the three vertices of the triangle, format [[x1,y1], [x2,y2], [x3,y3]]",
        min_items=3,
        max_items=3
    ) 