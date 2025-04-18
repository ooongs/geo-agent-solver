"""
Triangle-related calculation tools

This module provides tools for solving geometry problems related to triangles at the middle school level.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase


class TriangleTools(GeometryToolBase):
    """Tools for triangle-related calculations"""
    
    @staticmethod
    def calculate_area(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a triangle using coordinates"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        x1, y1 = vertices[0]
        x2, y2 = vertices[1]
        x3, y3 = vertices[2]
        
        # Calculate area using the shoelace formula
        area = 0.5 * abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)))
        return area
    
    @staticmethod
    def calculate_area_from_sides(a: float, b: float, c: float) -> float:
        """Calculate the area of a triangle using side lengths (Heron's formula)"""
        # Semi-perimeter
        s = (a + b + c) / 2
        
        # Check triangle inequality
        if s <= a or s <= b or s <= c:
            raise ToolException("Triangle inequality not satisfied: the sum of any two sides must be greater than the third side")
        
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        return area
    
    @staticmethod
    def calculate_perimeter(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the perimeter of a triangle"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        return a + b + c
    
    @staticmethod
    def is_right_triangle(vertices: List[Tuple[float, float]]) -> bool:
        """Check if a triangle is a right triangle"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        # Use Pythagorean theorem to check if it's a right triangle
        sides = sorted([a, b, c])
        return abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-10
    
    @staticmethod
    def is_isosceles_triangle(vertices: List[Tuple[float, float]]) -> bool:
        """Check if a triangle is isosceles (has two equal sides)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        # Check if any two sides are equal
        return abs(a - b) < 1e-10 or abs(b - c) < 1e-10 or abs(c - a) < 1e-10
    
    @staticmethod
    def is_equilateral_triangle(vertices: List[Tuple[float, float]]) -> bool:
        """Check if a triangle is equilateral (all sides equal)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        # Check if all sides are equal
        return abs(a - b) < 1e-10 and abs(b - c) < 1e-10
    
    @staticmethod
    def calculate_angles(vertices: List[Tuple[float, float]]) -> List[float]:
        """Calculate the three angles of a triangle (in radians)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        angle1 = TriangleTools.calculate_angle(p2, p1, p3)
        angle2 = TriangleTools.calculate_angle(p1, p2, p3)
        angle3 = TriangleTools.calculate_angle(p1, p3, p2)
        
        return [angle1, angle2, angle3]
    
    @staticmethod
    def calculate_centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the centroid of a triangle (center of mass)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        x = sum(p[0] for p in vertices) / 3
        y = sum(p[1] for p in vertices) / 3
        
        return (x, y)
    
    @staticmethod
    def calculate_circumcenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the circumcenter of a triangle (center of the circumscribed circle)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        (x1, y1), (x2, y2), (x3, y3) = vertices
        
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(D) < 1e-10:
            raise ToolException("The three points are collinear, no circumcenter exists")
        
        Ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / D
        Uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / D
        
        return (Ux, Uy)
    
    @staticmethod
    def calculate_incenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the incenter of a triangle (center of the inscribed circle)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p2, p3)
        b = TriangleTools.calculate_distance(p1, p3)
        c = TriangleTools.calculate_distance(p1, p2)
        
        # Use the side lengths as weights
        x = (a * p1[0] + b * p2[0] + c * p3[0]) / (a + b + c)
        y = (a * p1[1] + b * p2[1] + c * p3[1]) / (a + b + c)
        
        return (x, y)
    
    @staticmethod
    def calculate_orthocenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the orthocenter of a triangle (intersection of the three altitudes)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        (x1, y1), (x2, y2), (x3, y3) = vertices
        
        # Check if the points are collinear
        D = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        if abs(D) < 1e-10:
            raise ToolException("The three points are collinear, no orthocenter exists")
        
        # Calculate the slopes of each side
        m1 = float('inf') if abs(x2 - x3) < 1e-10 else (y2 - y3) / (x2 - x3)
        m2 = float('inf') if abs(x1 - x3) < 1e-10 else (y1 - y3) / (x1 - x3)
        m3 = float('inf') if abs(x1 - x2) < 1e-10 else (y1 - y2) / (x1 - x2)
        
        # Calculate slopes of the perpendicular lines (altitudes)
        m1_perp = 0 if abs(m1) == float('inf') else -1 / m1
        m2_perp = 0 if abs(m2) == float('inf') else -1 / m2
        m3_perp = 0 if abs(m3) == float('inf') else -1 / m3
        
        # Calculate the y-intercepts of the perpendicular lines
        b1 = y1 - m1_perp * x1
        b2 = y2 - m2_perp * x2
        b3 = y3 - m3_perp * x3
        
        # Calculate the intersection of two altitudes
        # (the third will pass through the same point by definition)
        if abs(m1_perp - m2_perp) < 1e-10:
            # If the first two altitudes are parallel, use the third altitude
            x = (b3 - b1) / (m1_perp - m3_perp)
            y = m1_perp * x + b1
        else:
            x = (b2 - b1) / (m1_perp - m2_perp)
            y = m1_perp * x + b1
        
        return (x, y)
    
    @staticmethod
    def calculate_triangle_centers(vertices: List[Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Calculate all centers of a triangle"""
        centers = {
            "centroid": TriangleTools.calculate_centroid(vertices),
            "circumcenter": TriangleTools.calculate_circumcenter(vertices),
            "incenter": TriangleTools.calculate_incenter(vertices),
            "orthocenter": TriangleTools.calculate_orthocenter(vertices)
        }
        return centers
    
    @staticmethod
    def calculate_inradius(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the radius of the inscribed circle (inradius)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p2, p3)
        b = TriangleTools.calculate_distance(p1, p3)
        c = TriangleTools.calculate_distance(p1, p2)
        
        # Semi-perimeter
        s = (a + b + c) / 2
        
        # Area
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        
        # Inradius = Area / Semi-perimeter
        return area / s
    
    @staticmethod
    def calculate_circumradius(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the radius of the circumscribed circle (circumradius)"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p2, p3)
        b = TriangleTools.calculate_distance(p1, p3)
        c = TriangleTools.calculate_distance(p1, p2)
        
        # Semi-perimeter
        s = (a + b + c) / 2
        
        # Area
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        
        # Circumradius = (a * b * c) / (4 * Area)
        return (a * b * c) / (4 * area)
    
    @staticmethod
    def calculate_median_lengths(vertices: List[Tuple[float, float]]) -> List[float]:
        """Calculate the lengths of the three medians of a triangle"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        
        # Calculate midpoints of each side
        mid_p2p3 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
        mid_p1p3 = ((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2)
        mid_p1p2 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        
        # Calculate lengths of medians
        median1 = TriangleTools.calculate_distance(p1, mid_p2p3)
        median2 = TriangleTools.calculate_distance(p2, mid_p1p3)
        median3 = TriangleTools.calculate_distance(p3, mid_p1p2)
        
        return [median1, median2, median3]
    
    @staticmethod
    def calculate_altitude_lengths(vertices: List[Tuple[float, float]]) -> List[float]:
        """Calculate the lengths of the three altitudes of a triangle"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        
        # Calculate side lengths
        a = TriangleTools.calculate_distance(p2, p3)
        b = TriangleTools.calculate_distance(p1, p3)
        c = TriangleTools.calculate_distance(p1, p2)
        
        # Calculate area
        s = (a + b + c) / 2  # Semi-perimeter
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        
        # Calculate altitudes (h = 2 * Area / side)
        altitude1 = 2 * area / a
        altitude2 = 2 * area / b
        altitude3 = 2 * area / c
        
        return [altitude1, altitude2, altitude3]
    
    @staticmethod
    def is_point_inside_triangle(point: Tuple[float, float], vertices: List[Tuple[float, float]]) -> bool:
        """Check if a point is inside a triangle using barycentric coordinates"""
        if len(vertices) != 3:
            raise ToolException("Triangle must have exactly 3 vertices")
        
        p1, p2, p3 = vertices
        px, py = point
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Calculate barycentric coordinates
        denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(denom) < 1e-10:
            return False  # Degenerate triangle
        
        a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / denom
        b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / denom
        c = 1 - a - b
        
        # Check if point is inside triangle
        return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1
    
    @staticmethod
    def triangle_tool(input_json: str) -> str:
        """Main function for the triangle calculation tool"""
        try:
            data = TriangleTools.parse_input(input_json)
            
            vertices = data.get("vertices", [])
            if not vertices or len(vertices) != 3:
                raise ToolException("Please provide valid triangle vertices (three points required)")
            
            # Calculate triangle information
            result = {
                "area": TriangleTools.calculate_area(vertices),
                "perimeter": TriangleTools.calculate_perimeter(vertices),
                "angles": [TriangleTools.radians_to_degrees(angle) for angle in TriangleTools.calculate_angles(vertices)],
                "is_right": TriangleTools.is_right_triangle(vertices),
                "is_isosceles": TriangleTools.is_isosceles_triangle(vertices),
                "is_equilateral": TriangleTools.is_equilateral_triangle(vertices),
                "centers": TriangleTools.calculate_triangle_centers(vertices)
            }
            
            # Handle specific calculation requests
            if "calculate" in data:
                for calc in data["calculate"]:
                    if calc == "centroid":
                        result["centroid"] = TriangleTools.calculate_centroid(vertices)
                    elif calc == "circumcenter":
                        result["circumcenter"] = TriangleTools.calculate_circumcenter(vertices)
                    elif calc == "incenter":
                        result["incenter"] = TriangleTools.calculate_incenter(vertices)
                    elif calc == "orthocenter":
                        result["orthocenter"] = TriangleTools.calculate_orthocenter(vertices)
                    elif calc == "inradius":
                        result["inradius"] = TriangleTools.calculate_inradius(vertices)
                    elif calc == "circumradius":
                        result["circumradius"] = TriangleTools.calculate_circumradius(vertices)
                    elif calc == "medians":
                        result["medians"] = TriangleTools.calculate_median_lengths(vertices)
                    elif calc == "altitudes":
                        result["altitudes"] = TriangleTools.calculate_altitude_lengths(vertices)
                    else:
                        raise ToolException(f"Unsupported calculation type: {calc}")
            
            return TriangleTools.format_output(result)
        except ToolException as e:
            return TriangleTools.format_output({"error": str(e)})
        except Exception as e:
            return TriangleTools.format_output({"error": f"Error calculating triangle properties: {str(e)}"}) 