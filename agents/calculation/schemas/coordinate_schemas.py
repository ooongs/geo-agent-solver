"""
Coordinate calculation input schema module

This module defines input schemas used in coordinate calculation tools.
These schemas specify the required parameters and their formats for various geometric coordinate calculations.
"""

from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field


class MidpointInput(BaseModel):
    """Input schema for calculating the midpoint between two points.
    The midpoint is the point that is equidistant from both input points."""
    point1: List[float] = Field(..., description="Coordinates of the first point [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point [x2, y2]", min_items=2, max_items=2)

class SlopeInput(BaseModel):
    """Input schema for calculating the slope of a line passing through two points.
    The slope is calculated as the ratio of the change in y to the change in x."""
    point1: List[float] = Field(..., description="Coordinates of the first point [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point [x2, y2]", min_items=2, max_items=2)

class LineEquationInput(BaseModel):
    """Input schema for calculating the equation of a line passing through two points.
    The line equation will be in the form ax + by + c = 0."""
    point1: List[float] = Field(..., description="Coordinates of the first point [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point [x2, y2]", min_items=2, max_items=2)

class CollinearInput(BaseModel):
    """Input schema for checking if three points are collinear.
    Points are collinear if they lie on the same straight line."""
    point1: List[float] = Field(..., description="Coordinates of the first point [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second point [x2, y2]", min_items=2, max_items=2)
    point3: List[float] = Field(..., description="Coordinates of the third point [x3, y3]", min_items=2, max_items=2)

class LinesParallelInput(BaseModel):
    """Input schema for checking if two lines are parallel.
    Each line is specified by its coefficients in the general form ax + by + c = 0."""
    line1_a: float = Field(..., description="Coefficient 'a' of the first line for ax + by + c = 0")
    line1_b: float = Field(..., description="Coefficient 'b' of the first line for ax + by + c = 0")
    line1_c: float = Field(..., description="Coefficient 'c' of the first line for ax + by + c = 0")
    line2_a: float = Field(..., description="Coefficient 'a' of the second line for ax + by + c = 0")
    line2_b: float = Field(..., description="Coefficient 'b' of the second line for ax + by + c = 0")
    line2_c: float = Field(..., description="Coefficient 'c' of the second line for ax + by + c = 0")

class SegmentDivisionInput(BaseModel):
    """Input schema for calculating a point that divides a line segment in a given ratio.
    The division point is specified by the ratio of its distances from the endpoints."""
    point1: List[float] = Field(..., description="Coordinates of the first endpoint [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second endpoint [x2, y2]", min_items=2, max_items=2)
    ratio: float = Field(..., description="Ratio of division (distance from point1 to division point) / (total segment length)")
    
class InternalDivisionPointInput(BaseModel):
    """Input schema for calculating a point that internally divides a line segment.
    The division point is specified by the ratio m:n of its distances from the endpoints."""
    point1: List[float] = Field(..., description="Coordinates of the first endpoint [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second endpoint [x2, y2]", min_items=2, max_items=2)
    m: float = Field(..., description="First part of the ratio (distance from point1)")
    n: float = Field(..., description="Second part of the ratio (distance from point2)")
    
class ExternalDivisionPointInput(BaseModel):
    """Input schema for calculating a point that externally divides a line segment.
    The division point is specified by the ratio m:n of its distances from the endpoints."""
    point1: List[float] = Field(..., description="Coordinates of the first endpoint [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the second endpoint [x2, y2]", min_items=2, max_items=2)
    m: float = Field(..., description="First part of the ratio (distance from point1)")
    n: float = Field(..., description="Second part of the ratio (distance from point2)")
    
class PointOnSegmentInput(BaseModel):
    """Input schema for checking if a point lies on a line segment.
    The check determines if the point is between the segment's endpoints."""
    point: List[float] = Field(..., description="Coordinates of the point to check [x, y]", min_items=2, max_items=2)
    segment_start: List[float] = Field(..., description="Coordinates of the segment's start point [x1, y1]", min_items=2, max_items=2)
    segment_end: List[float] = Field(..., description="Coordinates of the segment's end point [x2, y2]", min_items=2, max_items=2)


# Newly added schemas

class VectorInput(BaseModel):
    """Input schema for vector calculations.
    The vector is specified by its start and end points."""
    point1: List[float] = Field(..., description="Coordinates of the vector's start point [x1, y1]", min_items=2, max_items=2)
    point2: List[float] = Field(..., description="Coordinates of the vector's end point [x2, y2]", min_items=2, max_items=2)

class DotProductInput(BaseModel):
    """Input schema for calculating the dot product of two vectors.
    The vectors are specified by their components."""
    vector1: List[float] = Field(..., description="Components of the first vector [x1, y1]", min_items=2, max_items=2)
    vector2: List[float] = Field(..., description="Components of the second vector [x2, y2]", min_items=2, max_items=2)

class CrossProductInput(BaseModel):
    """Input schema for calculating the cross product of two vectors.
    The vectors are specified by their components."""
    vector1: List[float] = Field(..., description="Components of the first vector [x1, y1]", min_items=2, max_items=2)
    vector2: List[float] = Field(..., description="Components of the second vector [x2, y2]", min_items=2, max_items=2)

class NormalizeVectorInput(BaseModel):
    """Input schema for normalizing a vector to unit length.
    The vector is specified by its components."""
    vector: List[float] = Field(..., description="Components of the vector to normalize [x, y]", min_items=2, max_items=2)

class PointToLineInput(BaseModel):
    """Input schema for calculating the distance from a point to a line.
    The line is specified by its coefficients in the general form ax + by + c = 0."""
    point: List[float] = Field(..., description="Coordinates of the point [x, y]", min_items=2, max_items=2)
    line_a: float = Field(..., description="Coefficient 'a' of the line for ax + by + c = 0")
    line_b: float = Field(..., description="Coefficient 'b' of the line for ax + by + c = 0")
    line_c: float = Field(..., description="Coefficient 'c' of the line for ax + by + c = 0")

class LineIntersectionInput(BaseModel):
    """Input schema for calculating the intersection point of two lines.
    Each line is specified by its coefficients in the general form ax + by + c = 0."""
    line1_a: float = Field(..., description="Coefficient 'a' of the first line for ax + by + c = 0")
    line1_b: float = Field(..., description="Coefficient 'b' of the first line for ax + by + c = 0")
    line1_c: float = Field(..., description="Coefficient 'c' of the first line for ax + by + c = 0")
    line2_a: float = Field(..., description="Coefficient 'a' of the second line for ax + by + c = 0")
    line2_b: float = Field(..., description="Coefficient 'b' of the second line for ax + by + c = 0")
    line2_c: float = Field(..., description="Coefficient 'c' of the second line for ax + by + c = 0")

class RayIntersectionInput(BaseModel):
    """Input schema for calculating the intersection of a ray and a line segment.
    The ray is specified by its start point and angle, and the segment by its endpoints."""
    ray_start: List[float] = Field(..., description="Coordinates of the ray's start point [x, y]", min_items=2, max_items=2)
    ray_angle: float = Field(..., description="Angle of the ray in radians")
    segment_start: List[float] = Field(..., description="Coordinates of the segment's start point [x1, y1]", min_items=2, max_items=2)
    segment_end: List[float] = Field(..., description="Coordinates of the segment's end point [x2, y2]", min_items=2, max_items=2)

class LinesPerpendicularInput(BaseModel):
    """Input schema for checking if two lines are perpendicular.
    Each line is specified by its coefficients in the general form ax + by + c = 0."""
    line1_a: float = Field(..., description="Coefficient 'a' of the first line for ax + by + c = 0")
    line1_b: float = Field(..., description="Coefficient 'b' of the first line for ax + by + c = 0")
    line1_c: float = Field(..., description="Coefficient 'c' of the first line for ax + by + c = 0")
    line2_a: float = Field(..., description="Coefficient 'a' of the second line for ax + by + c = 0")
    line2_b: float = Field(..., description="Coefficient 'b' of the second line for ax + by + c = 0")
    line2_c: float = Field(..., description="Coefficient 'c' of the second line for ax + by + c = 0")

class PointInTriangleInput(BaseModel):
    """Input schema for checking if a point lies inside a triangle.
    The triangle is specified by the coordinates of its three vertices."""
    point: List[float] = Field(..., description="Coordinates of the point to check [x, y]", min_items=2, max_items=2)
    triangle_point1: List[float] = Field(..., description="Coordinates of the first triangle vertex [x1, y1]", min_items=2, max_items=2)
    triangle_point2: List[float] = Field(..., description="Coordinates of the second triangle vertex [x2, y2]", min_items=2, max_items=2)
    triangle_point3: List[float] = Field(..., description="Coordinates of the third triangle vertex [x3, y3]", min_items=2, max_items=2) 