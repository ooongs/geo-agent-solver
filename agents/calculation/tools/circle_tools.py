"""
Circle-related calculation tools

This module provides tools for solving geometry problems related to circles at the middle school level.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase


class CircleTools(GeometryToolBase):
    """Tools for circle-related calculations"""
    
    @staticmethod
    def calculate_area(radius: float) -> float:
        """Calculate the area of a circle"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        return np.pi * radius**2
    
    @staticmethod
    def calculate_circumference(radius: float) -> float:
        """Calculate the circumference of a circle"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        return 2 * np.pi * radius
    
    @staticmethod
    def calculate_chord_length(radius: float, angle: float) -> float:
        """Calculate the length of a chord (angle in radians)"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        return 2 * radius * np.sin(angle / 2)
    
    @staticmethod
    def calculate_sector_area(radius: float, angle: float) -> float:
        """Calculate the area of a sector (angle in radians)"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        return 0.5 * radius**2 * angle
    
    @staticmethod
    def calculate_segment_area(radius: float, angle: float) -> float:
        """Calculate the area of a segment (angle in radians)"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        sector_area = CircleTools.calculate_sector_area(radius, angle)
        triangle_area = 0.5 * radius**2 * np.sin(angle)
        return sector_area - triangle_area
    
    @staticmethod
    def is_point_inside_circle(center: Tuple[float, float], radius: float, point: Tuple[float, float]) -> bool:
        """Check if a point is inside a circle"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        distance = CircleTools.calculate_distance(center, point)
        return distance < radius
    
    @staticmethod
    def is_point_on_circle(center: Tuple[float, float], radius: float, point: Tuple[float, float]) -> bool:
        """Check if a point is on a circle"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        distance = CircleTools.calculate_distance(center, point)
        return abs(distance - radius) < 1e-10
    
    @staticmethod
    def calculate_tangent_points(center: Tuple[float, float], radius: float, external_point: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Calculate tangent points from an external point to a circle"""
        if radius <= 0:
            raise ToolException("Radius must be positive")
        
        # Distance between center and external point
        distance = CircleTools.calculate_distance(center, external_point)
        
        # If external point is inside the circle, no tangent points exist
        if distance < radius:
            return []
        
        # If external point is on the circle, the point itself is the tangent point
        if abs(distance - radius) < 1e-10:
            return [external_point]
        
        # Vector from center to external point
        dx = external_point[0] - center[0]
        dy = external_point[1] - center[1]
        
        # Length of the tangent (using Pythagorean theorem)
        tangent_length = np.sqrt(distance**2 - radius**2)
        
        # Angle of tangent points
        angle = np.arccos(radius / distance)
        
        # Base angle of the vector
        base_angle = np.arctan2(dy, dx)
        angle1 = base_angle + angle
        angle2 = base_angle - angle
        
        # Calculate tangent points
        tangent_point1 = (
            center[0] + radius * np.cos(angle1),
            center[1] + radius * np.sin(angle1)
        )
        
        tangent_point2 = (
            center[0] + radius * np.cos(angle2),
            center[1] + radius * np.sin(angle2)
        )
        
        return [tangent_point1, tangent_point2]
    
    @staticmethod
    def calculate_circle_intersection(center1: Tuple[float, float], radius1: float, 
                                     center2: Tuple[float, float], radius2: float) -> List[Tuple[float, float]]:
        """Calculate the intersection points of two circles"""
        if radius1 <= 0 or radius2 <= 0:
            raise ToolException("Radii must be positive")
        
        # Distance between circle centers
        d = CircleTools.calculate_distance(center1, center2)
        
        # Check if circles have no intersection
        if d > radius1 + radius2 or d < abs(radius1 - radius2):
            return []
        
        # Check if circles are identical (infinite intersection points)
        if d < 1e-10 and abs(radius1 - radius2) < 1e-10:
            return []
        
        # Check if circles are tangent (one intersection point)
        if abs(d - (radius1 + radius2)) < 1e-10 or abs(d - abs(radius1 - radius2)) < 1e-10:
            # Calculate point on the line between centers
            t = radius1 / d
            return [(
                center1[0] + t * (center2[0] - center1[0]),
                center1[1] + t * (center2[1] - center1[1])
            )]
        
        # Calculate intersection points when circles intersect at two points
        a = (radius1**2 - radius2**2 + d**2) / (2 * d)
        h = np.sqrt(radius1**2 - a**2)
        
        # Calculate midpoint
        x2 = center1[0] + a * (center2[0] - center1[0]) / d
        y2 = center1[1] + a * (center2[1] - center1[1]) / d
        
        # Calculate intersection points
        x3 = x2 + h * (center2[1] - center1[1]) / d
        y3 = y2 - h * (center2[0] - center1[0]) / d
        
        x4 = x2 - h * (center2[1] - center1[1]) / d
        y4 = y2 + h * (center2[0] - center1[0]) / d
        
        return [(x3, y3), (x4, y4)]
    
    @staticmethod
    def calculate_circle_from_three_points(p1: Tuple[float, float], p2: Tuple[float, float], 
                                          p3: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
        """Calculate the center and radius of a circle passing through three points"""
        # Check if points are collinear
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Check determinant to see if points are collinear
        if abs((y2 - y1) * (x3 - x2) - (y3 - y2) * (x2 - x1)) < 1e-10:
            raise ToolException("The three points are collinear, no circle can be formed")
        
        # The center of the circle is the intersection of the perpendicular bisectors of the sides
        # First, find the midpoints of the sides
        mx1 = (x1 + x2) / 2
        my1 = (y1 + y2) / 2
        
        mx2 = (x2 + x3) / 2
        my2 = (y2 + y3) / 2
        
        # Calculate slopes of the perpendicular bisectors
        if abs(x2 - x1) < 1e-10:
            # First segment is vertical, perpendicular bisector is horizontal
            s1 = 0
        else:
            s1 = -1 / ((y2 - y1) / (x2 - x1))
        
        if abs(x3 - x2) < 1e-10:
            # Second segment is vertical, perpendicular bisector is horizontal
            s2 = 0
        else:
            s2 = -1 / ((y3 - y2) / (x3 - x2))
        
        # Check if perpendicular bisectors are parallel
        if abs(s1 - s2) < 1e-10:
            raise ToolException("Cannot determine the circle, perpendicular bisectors are parallel")
        
        # Find the intersection of the perpendicular bisectors (circle center)
        cx = 0
        cy = 0
        
        if abs(s1) < 1e-10:  # First perpendicular bisector is horizontal
            cx = mx1
            cy = s2 * (cx - mx2) + my2
        elif abs(s2) < 1e-10:  # Second perpendicular bisector is horizontal
            cx = mx2
            cy = s1 * (cx - mx1) + my1
        else:
            cx = (s1 * mx1 - s2 * mx2 + my2 - my1) / (s1 - s2)
            cy = s1 * (cx - mx1) + my1
        
        # Calculate radius as distance from center to any of the points
        radius = CircleTools.calculate_distance((cx, cy), p1)
        
        return ((cx, cy), radius)
    
    @staticmethod
    def calculate_circle_from_center_and_point(center: Tuple[float, float], point: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
        """Calculate the center and radius of a circle given the center and a point on the circle"""
        radius = CircleTools.calculate_distance(center, point)
        if radius <= 0:
            raise ToolException("Calculated radius must be positive")
        return (center, radius)
    
    @staticmethod
    def calculate_central_angle(center: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate the central angle formed by two points on a circle (in radians)"""
        # Calculate vectors from center to points
        v1 = (p1[0] - center[0], p1[1] - center[1])
        v2 = (p2[0] - center[0], p2[1] - center[1])
        
        # Calculate dot product
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        
        # Calculate magnitudes
        mag1 = np.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = np.sqrt(v2[0]**2 + v2[1]**2)
        
        # Calculate angle using dot product formula
        # Handle floating point errors
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(min(cos_angle, 1.0), -1.0)  # Clamp to [-1, 1]
        
        return np.arccos(cos_angle)
    
    @staticmethod
    def calculate_inscribed_angle(center: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """Calculate the inscribed angle in a circle (in radians)
        
        p1, p2, p3 are points on the circle, with p2 as the vertex of the angle
        """
        # Check if points are on the circle
        if not (CircleTools.is_point_on_circle(center, CircleTools.calculate_distance(center, p1), p1) and
                CircleTools.is_point_on_circle(center, CircleTools.calculate_distance(center, p2), p2) and
                CircleTools.is_point_on_circle(center, CircleTools.calculate_distance(center, p3), p3)):
            raise ToolException("All points must be on the circle")
        
        # Calculate the angle formed by p1, p2, p3
        return CircleTools.calculate_angle(p1, p2, p3)
    
    @staticmethod
    def calculate_power_of_point(external_point: Tuple[float, float], center: Tuple[float, float], radius: float) -> float:
        """Calculate the power of a point with respect to a circle
        
        The power of a point P with respect to a circle is defined as:
        power = OP^2 - r^2 where O is the center of the circle, r is the radius
        """
        distance_squared = CircleTools.calculate_distance(external_point, center)**2
        return distance_squared - radius**2
    
    @staticmethod
    def circle_tool(input_json: str) -> str:
        """Main function for the circle calculation tool"""
        try:
            data = CircleTools.parse_input(input_json)
            
            result = {}
            
            # Handle circle defined by center and radius
            if "center" in data and "radius" in data:
                center = data["center"]
                radius = data["radius"]
                
                result["area"] = CircleTools.calculate_area(radius)
                result["circumference"] = CircleTools.calculate_circumference(radius)
                
                # Additional calculations
                if "point" in data:
                    point = data["point"]
                    result["is_inside"] = CircleTools.is_point_inside_circle(center, radius, point)
                    result["is_on_circle"] = CircleTools.is_point_on_circle(center, radius, point)
                    
                    if not result["is_inside"] and not result["is_on_circle"]:
                        result["tangent_points"] = CircleTools.calculate_tangent_points(center, radius, point)
                
                if "angle" in data:
                    angle = data["angle"]
                    result["chord_length"] = CircleTools.calculate_chord_length(radius, angle)
                    result["sector_area"] = CircleTools.calculate_sector_area(radius, angle)
                    result["segment_area"] = CircleTools.calculate_segment_area(radius, angle)
            
            # Handle circle defined by three points
            elif "points" in data and len(data["points"]) == 3:
                p1, p2, p3 = data["points"]
                center, radius = CircleTools.calculate_circle_from_three_points(p1, p2, p3)
                
                result["center"] = center
                result["radius"] = radius
                result["area"] = CircleTools.calculate_area(radius)
                result["circumference"] = CircleTools.calculate_circumference(radius)
            
            # Handle intersection of two circles
            elif "circle1" in data and "circle2" in data:
                circle1 = data["circle1"]
                circle2 = data["circle2"]
                
                center1 = circle1.get("center")
                radius1 = circle1.get("radius")
                center2 = circle2.get("center")
                radius2 = circle2.get("radius")
                
                if not all([center1, radius1, center2, radius2]):
                    raise ToolException("Both circles must have a center and radius")
                
                result["intersection_points"] = CircleTools.calculate_circle_intersection(center1, radius1, center2, radius2)
            
            else:
                raise ToolException("Invalid input: required parameters missing")
            
            return CircleTools.format_output(result)
        except ToolException as e:
            return CircleTools.format_output({"error": str(e)})
        except Exception as e:
            return CircleTools.format_output({"error": f"Error calculating circle properties: {str(e)}"})
   