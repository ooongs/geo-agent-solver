"""
Angle-related calculation tools

This module provides tools for solving angle-related geometry problems at the middle school level.
"""

import math
from typing import Dict, Any, List, Tuple, Optional, Union
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException

from .base_tools import GeometryToolBase
from .coordinate_tools import CoordinateTools

class AngleTools(GeometryToolBase):
    """Angle-related calculation tools"""
    
    # Constants
    PI = math.pi
    HALF_PI = math.pi / 2
    TWO_PI = math.pi * 2
    
    # === Math Tools ===
    
    @staticmethod
    def normalize_angle(angle_rad: float) -> float:
        """Normalize angle to [0, 2π) range"""
        return angle_rad % AngleTools.TWO_PI
    
    @staticmethod
    def degrees_to_radians(angle_deg: float) -> float:
        """Convert angle from degrees to radians"""
        return angle_deg * (math.pi / 180)
    
    @staticmethod
    def radians_to_degrees(angle_rad: float) -> float:
        """Convert angle from radians to degrees"""
        return angle_rad * (180 / math.pi)
    
    @staticmethod
    def calculate_angle_two_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """Calculate the angle between two vectors in radians"""
        v1_length = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_length = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if v1_length < 1e-10 or v2_length < 1e-10:
            raise ToolException("Cannot calculate angle with zero-length vector")
        
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        cos_angle = dot_product / (v1_length * v2_length)
        
        # Handle numerical inaccuracies
        if cos_angle > 1:
            cos_angle = 1
        elif cos_angle < -1:
            cos_angle = -1
            
        # Return the unsigned angle [0, π]
        return math.acos(cos_angle)
    
    @staticmethod
    def calculate_angle_three_points(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """Calculate the angle formed by three points with p2 as the vertex"""
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        return AngleTools.calculate_angle_two_vectors(v1, v2)
    
    @staticmethod
    def calculate_angle_with_direction(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """Calculate the angle with direction (counter-clockwise is positive)"""
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # Calculate cross product (z-component)
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        # Calculate the unsigned angle
        angle = AngleTools.calculate_angle_three_points(p1, p2, p3)
        
        # Apply sign based on the cross product
        if cross_product < 0:
            return -angle
        return angle
    
    @staticmethod
    def calculate_angle_two_lines(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> float:
        """Calculate the angle between two lines in radians"""
        if CoordinateTools.are_lines_parallel(line1, line2):
            return 0.0
        
        # For line ax + by + c = 0, the slope is -a/b
        if abs(line1[1]) < 1e-10:  # First line is vertical
            if abs(line2[0]) < 1e-10:  # Second line is horizontal
                return AngleTools.HALF_PI
            else:
                slope2 = -line2[0] / line2[1]
                return math.atan(abs(slope2))
        elif abs(line2[1]) < 1e-10:  # Second line is vertical
            if abs(line1[0]) < 1e-10:  # First line is horizontal
                return AngleTools.HALF_PI
            else:
                slope1 = -line1[0] / line1[1]
                return math.atan(abs(slope1))
        else:
            slope1 = -line1[0] / line1[1]
            slope2 = -line2[0] / line2[1]
            return math.atan(abs((slope2 - slope1) / (1 + slope1 * slope2)))
    
    @staticmethod
    def calculate_interior_angles_triangle(vertices: List[Tuple[float, float]]) -> List[float]:
        """Calculate the interior angles of a triangle"""
        if len(vertices) != 3:
            raise ToolException("A triangle must have exactly 3 vertices")
        
        angles = []
        for i in range(3):
            p1 = vertices[i]
            p2 = vertices[(i+1) % 3]
            p3 = vertices[(i+2) % 3]
            angles.append(AngleTools.calculate_angle_three_points(p1, p2, p3))
        
        return angles
    
    @staticmethod
    def calculate_exterior_angles_triangle(vertices: List[Tuple[float, float]]) -> List[float]:
        """Calculate the exterior angles of a triangle"""
        interior_angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return [math.pi - angle for angle in interior_angles]
    
    @staticmethod
    def calculate_angle_bisector(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float, float]:
        """Calculate the angle bisector line for an angle formed by three points with p2 as vertex"""
        # Normalize the two vectors
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        v1_length = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_length = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if v1_length < 1e-10 or v2_length < 1e-10:
            raise ToolException("Cannot calculate angle bisector with zero-length vector")
            
        v1_normalized = (v1[0] / v1_length, v1[1] / v1_length)
        v2_normalized = (v2[0] / v2_length, v2[1] / v2_length)
        
        # Calculate the bisector vector
        bisector = (v1_normalized[0] + v2_normalized[0], v1_normalized[1] + v2_normalized[1])
        bisector_length = math.sqrt(bisector[0]**2 + bisector[1]**2)
        
        if bisector_length < 1e-10:
            # If the vectors are in opposite directions, take perpendicular
            bisector = (-v1_normalized[1], v1_normalized[0])
        else:
            bisector = (bisector[0] / bisector_length, bisector[1] / bisector_length)
        
        # Calculate a point on the bisector line
        p_on_bisector = (p2[0] + bisector[0], p2[1] + bisector[1])
        
        # Get the line equation
        return CoordinateTools.calculate_line_equation(p2, p_on_bisector)
    
    @staticmethod
    def calculate_angle_trisection(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Calculate the two lines that trisect an angle formed by three points with p2 as vertex"""
        # Calculate the angle
        angle = AngleTools.calculate_angle_three_points(p1, p2, p3)
        trisection_angle = angle / 3
        
        # Calculate the angle between p2->p1 and positive x-axis
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        base_angle = math.atan2(v1[1], v1[0])
        
        # Calculate the two trisection angles
        first_trisection_angle = base_angle + trisection_angle
        second_trisection_angle = base_angle + 2 * trisection_angle
        
        # Calculate points on the trisection lines
        first_trisection_point = (
            p2[0] + math.cos(first_trisection_angle),
            p2[1] + math.sin(first_trisection_angle)
        )
        
        second_trisection_point = (
            p2[0] + math.cos(second_trisection_angle),
            p2[1] + math.sin(second_trisection_angle)
        )
        
        # Get the line equations
        first_trisection_line = CoordinateTools.calculate_line_equation(p2, first_trisection_point)
        second_trisection_line = CoordinateTools.calculate_line_equation(p2, second_trisection_point)
        
        return (first_trisection_line, second_trisection_line)
    
    @staticmethod
    def calculate_inscribed_angle(center: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate the inscribed angle in a circle from two points on the circle and the center"""
        v1 = (p1[0] - center[0], p1[1] - center[1])
        v2 = (p2[0] - center[0], p2[1] - center[1])
        central_angle = AngleTools.calculate_angle_two_vectors(v1, v2)
        return central_angle / 2
    
    @staticmethod
    def calculate_regular_polygon_angle(n: int) -> float:
        """Calculate the interior angle of a regular polygon with n sides"""
        if n < 3:
            raise ToolException("A polygon must have at least 3 sides")
        return (n - 2) * math.pi / n
    
    @staticmethod
    def calculate_angle_complement(angle_rad: float) -> float:
        """Calculate the complement of an angle (π/2 - angle)"""
        return AngleTools.HALF_PI - angle_rad
    
    @staticmethod
    def calculate_angle_supplement(angle_rad: float) -> float:
        """Calculate the supplement of an angle (π - angle)"""
        return math.pi - angle_rad
    
    @staticmethod
    def calculate_rotation(point: Tuple[float, float], center: Tuple[float, float], angle_rad: float) -> Tuple[float, float]:
        """Rotate a point around a center by a given angle"""
        # Translate the point so the center is at the origin
        translated = (point[0] - center[0], point[1] - center[1])
        
        # Apply rotation
        rotated = (
            translated[0] * math.cos(angle_rad) - translated[1] * math.sin(angle_rad),
            translated[0] * math.sin(angle_rad) + translated[1] * math.cos(angle_rad)
        )
        
        # Translate back
        return (rotated[0] + center[0], rotated[1] + center[1])
    
    # === Validation Tools ===
    
    @staticmethod
    def angle_classification(angle_rad: float) -> str:
        """Classify an angle as acute, right, obtuse, straight, or reflex"""
        angle_rad = AngleTools.normalize_angle(angle_rad)
        
        if abs(angle_rad) < 1e-10 or abs(angle_rad - AngleTools.TWO_PI) < 1e-10:
            return "zero"
        elif abs(angle_rad - AngleTools.HALF_PI) < 1e-10:
            return "right"
        elif angle_rad < AngleTools.HALF_PI:
            return "acute"
        elif abs(angle_rad - math.pi) < 1e-10:
            return "straight"
        elif angle_rad < math.pi:
            return "obtuse"
        else:
            return "reflex"
    
    @staticmethod
    def is_angle_acute(angle_rad: float) -> bool:
        """Check if an angle is acute (less than π/2)"""
        angle_rad = AngleTools.normalize_angle(angle_rad)
        return 0 < angle_rad < AngleTools.HALF_PI
    
    @staticmethod
    def is_angle_right(angle_rad: float) -> bool:
        """Check if an angle is right (equal to π/2)"""
        angle_rad = AngleTools.normalize_angle(angle_rad)
        return abs(angle_rad - AngleTools.HALF_PI) < 1e-10
    
    @staticmethod
    def is_angle_obtuse(angle_rad: float) -> bool:
        """Check if an angle is obtuse (between π/2 and π)"""
        angle_rad = AngleTools.normalize_angle(angle_rad)
        return AngleTools.HALF_PI < angle_rad < math.pi
    
    @staticmethod
    def is_angle_straight(angle_rad: float) -> bool:
        """Check if an angle is straight (equal to π)"""
        angle_rad = AngleTools.normalize_angle(angle_rad)
        return abs(angle_rad - math.pi) < 1e-10
    
    @staticmethod
    def is_angle_reflex(angle_rad: float) -> bool:
        """Check if an angle is reflex (between π and 2π)"""
        angle_rad = AngleTools.normalize_angle(angle_rad)
        return math.pi < angle_rad < AngleTools.TWO_PI
    
    @staticmethod
    def are_angles_equal(angle1_rad: float, angle2_rad: float, tolerance: float = 1e-10) -> bool:
        """Check if two angles are equal within the given tolerance"""
        angle1_rad = AngleTools.normalize_angle(angle1_rad)
        angle2_rad = AngleTools.normalize_angle(angle2_rad)
        return abs(angle1_rad - angle2_rad) < tolerance
    
    @staticmethod
    def is_triangle_acute(vertices: List[Tuple[float, float]]) -> bool:
        """Check if a triangle is acute (all angles are acute)"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return all(AngleTools.is_angle_acute(angle) for angle in angles)
    
    @staticmethod
    def is_triangle_right(vertices: List[Tuple[float, float]]) -> bool:
        """Check if a triangle is right (has a right angle)"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return any(AngleTools.is_angle_right(angle) for angle in angles)
    
    @staticmethod
    def is_triangle_obtuse(vertices: List[Tuple[float, float]]) -> bool:
        """Check if a triangle is obtuse (has an obtuse angle)"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return any(AngleTools.is_angle_obtuse(angle) for angle in angles)
    
    @staticmethod
    def is_triangle_equiangular(vertices: List[Tuple[float, float]], tolerance: float = 1e-10) -> bool:
        """Check if a triangle is equiangular (all angles are equal)"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return (
            abs(angles[0] - angles[1]) < tolerance and
            abs(angles[1] - angles[2]) < tolerance
        )
    
    @staticmethod
    def is_angle_complementary(angle1_rad: float, angle2_rad: float, tolerance: float = 1e-10) -> bool:
        """Check if two angles are complementary (sum to π/2)"""
        return abs(angle1_rad + angle2_rad - AngleTools.HALF_PI) < tolerance
    
    @staticmethod
    def is_angle_supplementary(angle1_rad: float, angle2_rad: float, tolerance: float = 1e-10) -> bool:
        """Check if two angles are supplementary (sum to π)"""
        return abs(angle1_rad + angle2_rad - math.pi) < tolerance
    