"""
Angle calculation input schema module

This module defines input schemas used in angle calculation tools.
These schemas specify the required parameters and their formats for various geometric angle calculations.
"""

from typing import List, Optional, Union, Dict, Any, Tuple
from pydantic import BaseModel, Field

class RadiansToDegreesInput(BaseModel):
    """Input schema for converting an angle from radians to degrees.
    The angle is specified in radians and will be converted to degrees."""
    radians: float = Field(..., description="Angle value in radians to convert to degrees")

class DegreesToRadiansInput(BaseModel):
    """Input schema for converting an angle from degrees to radians.
    The angle is specified in degrees and will be converted to radians."""
    degrees: float = Field(..., description="Angle value in degrees to convert to radians")

class AngleInput(BaseModel):
    """Input schema for operations on a single angle.
    The angle is specified in radians with an optional tolerance for floating-point comparisons."""
    angle_rad: float = Field(..., description="Angle value in radians")
    tolerance: Optional[float] = Field(1e-10, description="Tolerance for floating-point comparisons")

class TwoAnglesInput(BaseModel):
    """Input schema for operations comparing two angles.
    Both angles are specified in radians with an optional tolerance for floating-point comparisons."""
    angle1_rad: float = Field(..., description="First angle value in radians")
    angle2_rad: float = Field(..., description="Second angle value in radians")
    tolerance: Optional[float] = Field(1e-10, description="Tolerance for floating-point comparisons")

class RotationInput(BaseModel):
    """Input schema for rotating a point around a center point.
    The rotation is specified by the point to rotate, the center of rotation, and the angle of rotation in radians."""
    point: List[float] = Field(..., description="Coordinates of the point to rotate [x, y]", min_items=2, max_items=2)
    center: List[float] = Field(..., description="Coordinates of the rotation center [x, y]", min_items=2, max_items=2)
    angle_rad: float = Field(..., description="Angle of rotation in radians")

class RegularPolygonInput(BaseModel):
    """Input schema for regular polygon angle calculations.
    The polygon is specified by its number of sides."""
    sides: int = Field(..., description="Number of sides in the regular polygon")

class NormalizeAngleInput(BaseModel):
    """Input schema for normalizing an angle to the range [0, 2π).
    The angle is specified in radians and will be normalized to the standard range."""
    angle_rad: float = Field(..., description="Angle value in radians to normalize")

class AngleClassificationInput(BaseModel):
    """Input schema for classifying an angle.
    The angle is specified in radians and will be classified as acute, right, obtuse, or straight."""
    angle_rad: float = Field(..., description="Angle value in radians to classify")

class InscribedAngleInput(BaseModel):
    """Input schema for calculating inscribed angles in a circle.
    The angle is specified by the circle's center and two points on the circle."""
    center: List[float] = Field(..., description="Center coordinates of the circle [x, y]", min_items=2, max_items=2)
    point1: List[float] = Field(..., description="Coordinates of the first point on the circle [x, y]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point on the circle [x, y]", min_items=2, max_items=2)

class AngleTriangleInput(BaseModel):
    """Input schema for calculating angles in a triangle.
    The triangle is specified by the coordinates of its three vertices."""
    vertices: List[List[float]] = Field(..., description="Coordinates of three vertices [[x1, y1], [x2, y2], [x3, y3]]")

class AngleBetweenVectorsInput(BaseModel):
    """Input schema for calculating the angle between two vectors.
    The vectors are specified by their components."""
    vector1: List[float] = Field(..., description="Components of the first vector [x1, y1]", min_items=2, max_items=2)
    vector2: List[float] = Field(..., description="Components of the second vector [x2, y2]", min_items=2, max_items=2)

class AngleBetweenLinesInput(BaseModel):
    """Input schema for calculating the angle between two lines.
    Each line is specified by its coefficients in the general form ax + by + c = 0."""
    line1_a: float = Field(..., description="Coefficient 'a' of the first line for ax + by + c = 0")
    line1_b: float = Field(..., description="Coefficient 'b' of the first line for ax + by + c = 0")
    line1_c: float = Field(..., description="Coefficient 'c' of the first line for ax + by + c = 0")
    line2_a: float = Field(..., description="Coefficient 'a' of the second line for ax + by + c = 0")
    line2_b: float = Field(..., description="Coefficient 'b' of the second line for ax + by + c = 0")
    line2_c: float = Field(..., description="Coefficient 'c' of the second line for ax + by + c = 0")

class AngleBetweenPointsInput(BaseModel):
    """Input schema for calculating the angle formed by three points.
    The angle is specified by three points, with the middle point being the vertex."""
    point1: List[float] = Field(..., description="Coordinates of the first point [x1, y1]", min_items=2, max_items=2)
    vertex: List[float] = Field(..., description="Coordinates of the vertex point [x2, y2]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the third point [x3, y3]", min_items=2, max_items=2)

class AngleComplementInput(BaseModel):
    """Input schema for calculating the complement of an angle.
    The complement is the angle that, when added to the given angle, equals 90 degrees (π/2 radians)."""
    angle_rad: float = Field(..., description="Angle value in radians to find the complement of")

class AngleSupplementInput(BaseModel):
    """Input schema for calculating the supplement of an angle.
    The supplement is the angle that, when added to the given angle, equals 180 degrees (π radians)."""
    angle_rad: float = Field(..., description="Angle value in radians to find the supplement of") 