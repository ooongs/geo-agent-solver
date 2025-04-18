"""
Coordinate-related calculation tools

This module provides tools for solving coordinate geometry problems at the middle school level.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase

class CoordinateTools(GeometryToolBase):
    """Coordinate-related calculation tools"""
    
    # === Math Tools ===
    
    @staticmethod
    def calculate_midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate the midpoint of two points"""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    
    @staticmethod
    def calculate_slope(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate the slope of a line passing through two points"""
        if abs(p2[0] - p1[0]) < 1e-10:
            return float('inf')  # Infinity (vertical line)
        return (p2[1] - p1[1]) / (p2[0] - p1[0])
    
    @staticmethod
    def calculate_line_equation(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float, float]:
        """Calculate the equation of a line passing through two points (in the form ax + by + c = 0)"""
        if abs(p2[0] - p1[0]) < 1e-10:
            # Vertical line: x = p1[0]
            return (1, 0, -p1[0])
        
        slope = CoordinateTools.calculate_slope(p1, p2)
        if abs(slope) < 1e-10:
            # Horizontal line: y = p1[1]
            return (0, 1, -p1[1])
        
        # General case: y = slope * x + intercept
        intercept = p1[1] - slope * p1[0]
        return (-slope, 1, -intercept)  # Convert to ax + by + c = 0 form
    
    @staticmethod
    def calculate_segment_division(p1: Tuple[float, float], p2: Tuple[float, float], ratio: float) -> Tuple[float, float]:
        """Calculate a point that divides a line segment by a given ratio"""
        return (
            p1[0] + ratio * (p2[0] - p1[0]),
            p1[1] + ratio * (p2[1] - p1[1])
        )
    
    @staticmethod
    def calculate_internal_division_point(p1: Tuple[float, float], p2: Tuple[float, float], m: float, n: float) -> Tuple[float, float]:
        """Calculate a point that internally divides a line segment in the ratio m:n"""
        if abs(m + n) < 1e-10:
            return p1  # Invalid ratio
        
        return (
            (m * p2[0] + n * p1[0]) / (m + n),
            (m * p2[1] + n * p1[1]) / (m + n)
        )
    
    @staticmethod
    def calculate_external_division_point(p1: Tuple[float, float], p2: Tuple[float, float], m: float, n: float) -> Tuple[float, float]:
        """Calculate a point that externally divides a line segment in the ratio m:n"""
        if abs(m - n) < 1e-10:
            return p1  # Invalid ratio
        
        return (
            (m * p2[0] - n * p1[0]) / (m - n),
            (m * p2[1] - n * p1[1]) / (m - n)
        )
    
    @staticmethod
    def calculate_vector(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate the vector between two points"""
        return (p2[0] - p1[0], p2[1] - p1[1])
    
    @staticmethod
    def calculate_vector_length(vector: Tuple[float, float]) -> float:
        """Calculate the length of a vector"""
        return np.sqrt(vector[0]**2 + vector[1]**2)
    
    @staticmethod
    def calculate_dot_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """Calculate the dot product of two vectors"""
        return v1[0] * v2[0] + v1[1] * v2[1]
    
    @staticmethod
    def calculate_cross_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """Calculate the cross product of two vectors (z component)"""
        return v1[0] * v2[1] - v1[1] * v2[0]
    
    @staticmethod
    def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
        """Normalize a vector"""
        length = CoordinateTools.calculate_vector_length(vector)
        if abs(length) < 1e-10:
            raise ToolException("Cannot normalize zero vector")
        return (vector[0] / length, vector[1] / length)
    
    @staticmethod
    def calculate_distance_point_to_line(point: Tuple[float, float], line: Tuple[float, float, float]) -> float:
        """Calculate the distance from a point to a line"""
        a, b, c = line
        return abs(a * point[0] + b * point[1] + c) / np.sqrt(a**2 + b**2)
    
    @staticmethod
    def calculate_reflection_point(point: Tuple[float, float], line: Tuple[float, float, float]) -> Tuple[float, float]:
        """Calculate the reflection of a point across a line"""
        a, b, c = line
        # Normal vector from a point on the line
        normal = (a, b)
        normal_length = np.sqrt(a**2 + b**2)
        unit_normal = (a / normal_length, b / normal_length)
        
        # Distance from point to line
        distance = CoordinateTools.calculate_distance_point_to_line(point, line)
        
        # Vector perpendicular from the point to the line
        d = a * point[0] + b * point[1] + c
        direction = 1 if d > 0 else -1
        
        # Calculate the reflection point
        return (
            point[0] - 2 * direction * unit_normal[0] * distance,
            point[1] - 2 * direction * unit_normal[1] * distance
        )
    
    @staticmethod
    def calculate_line_intersection(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> Optional[Tuple[float, float]]:
        """Calculate the intersection point of two lines"""
        a1, b1, c1 = line1
        a2, b2, c2 = line2
        
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-10:  # Parallel or coincident
            return None
        
        x = (b1 * c2 - b2 * c1) / det
        y = (a2 * c1 - a1 * c2) / det
        return (x, y)
    
    @staticmethod
    def calculate_ray_intersection_with_segment(
        ray_start: Tuple[float, float], 
        ray_angle: float, 
        segment_start: Tuple[float, float], 
        segment_end: Tuple[float, float]
    ) -> Optional[Tuple[float, float]]:
        """Calculate the intersection of a ray and a line segment"""
        # Direction vector of the ray
        ray_direction = (np.cos(ray_angle), np.sin(ray_angle))
        
        # Vector of the segment
        segment_vector = (segment_end[0] - segment_start[0], segment_end[1] - segment_start[1])
        
        # Vector from ray start to segment start
        start_vector = (segment_start[0] - ray_start[0], segment_start[1] - ray_start[1])
        
        # Normal vector to the segment direction (rotated 90 degrees)
        normal = (-segment_vector[1], segment_vector[0])
        
        # Dot product of ray and normal vector
        dot_product = ray_direction[0] * normal[0] + ray_direction[1] * normal[1]
        
        # Check if parallel
        if abs(dot_product) < 1e-10:
            return None
        
        # Calculate intersection ratio
        t = (start_vector[0] * normal[0] + start_vector[1] * normal[1]) / dot_product
        
        # Check ray direction
        if t < 0:
            return None
        
        # Calculate intersection point
        intersection = (ray_start[0] + t * ray_direction[0], ray_start[1] + t * ray_direction[1])
        
        # Check if intersection point is on the segment
        if CoordinateTools.is_point_on_segment(intersection, segment_start, segment_end):
            return intersection
            
        return None
    
    # === Validation Tools ===
    
    @staticmethod
    def are_points_collinear(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
        """Check if three points are collinear"""
        return abs((p2[1] - p1[1]) * (p3[0] - p2[0]) - (p3[1] - p2[1]) * (p2[0] - p1[0])) < 1e-10
    
    @staticmethod
    def are_lines_parallel(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> bool:
        """Check if two lines are parallel"""
        # In the form ax + by + c = 0, the slope is -a/b
        if abs(line1[1]) < 1e-10 and abs(line2[1]) < 1e-10:
            return True  # Both lines are vertical
        if abs(line1[1]) < 1e-10 or abs(line2[1]) < 1e-10:
            return False  # Only one line is vertical
        return abs(line1[0] / line1[1] - line2[0] / line2[1]) < 1e-10
    
    @staticmethod
    def are_lines_perpendicular(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> bool:
        """Check if two lines are perpendicular"""
        # In the form ax + by + c = 0, the slope is -a/b
        if abs(line1[1]) < 1e-10:  # First line is vertical
            return abs(line2[0]) < 1e-10  # Perpendicular if second line is horizontal
        if abs(line2[1]) < 1e-10:  # Second line is vertical
            return abs(line1[0]) < 1e-10  # Perpendicular if first line is horizontal
            
        # General case: product of slopes is -1 if perpendicular
        return abs(line1[0] / line1[1] * line2[0] / line2[1] + 1) < 1e-10
    
    @staticmethod
    def is_point_on_segment(p: Tuple[float, float], segment_start: Tuple[float, float], segment_end: Tuple[float, float]) -> bool:
        """Check if a point is on a line segment"""
        # Check if the point is on the line
        if abs((p[1] - segment_start[1]) * (segment_end[0] - segment_start[0]) - 
               (p[0] - segment_start[0]) * (segment_end[1] - segment_start[1])) > 1e-10:
            return False
        
        # Check if the point is within the segment bounds
        if min(segment_start[0], segment_end[0]) <= p[0] <= max(segment_start[0], segment_end[0]) and \
           min(segment_start[1], segment_end[1]) <= p[1] <= max(segment_start[1], segment_end[1]):
            return True
        
        return False
    
    @staticmethod
    def is_point_inside_triangle(p: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
        """Check if a point is inside a triangle"""
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
            
        d1 = sign(p, p1, p2)
        d2 = sign(p, p2, p3)
        d3 = sign(p, p3, p1)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        # Inside triangle if all signs are the same
        return not (has_neg and has_pos)
    