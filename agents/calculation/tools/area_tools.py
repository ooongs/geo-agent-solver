"""
Area-related calculation tools

This module provides tools for calculating areas of various geometric shapes at the middle school level.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase


class AreaTools(GeometryToolBase):
    """Tools for area-related calculations"""
    
    @staticmethod
    def calculate_quadrilateral_area(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a quadrilateral from its vertices
        
        Args:
            vertices: List of four vertices [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            
        Returns:
            Area of the quadrilateral
        """
        if len(vertices) != 4:
            raise ToolException("A quadrilateral must have exactly 4 vertices")
        
        # Using the Shoelace formula
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        area = abs(area) / 2.0
        
        return area
    
    @staticmethod
    def calculate_polygon_area(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of any polygon from its vertices
        
        Args:
            vertices: List of vertices [(x1, y1), (x2, y2), ..., (xn, yn)]
            
        Returns:
            Area of the polygon
        """
        if len(vertices) < 3:
            raise ToolException("A polygon must have at least 3 vertices")
        
        # Using the Shoelace formula
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        area = abs(area) / 2.0
        
        return area
    
    @staticmethod
    def calculate_rectangle_area(length: float, width: float) -> float:
        """Calculate the area of a rectangle
        
        Args:
            length: Length of the rectangle
            width: Width of the rectangle
            
        Returns:
            Area of the rectangle
        """
        if length <= 0 or width <= 0:
            raise ToolException("Length and width must be positive")
        
        return length * width
    
    @staticmethod
    def calculate_square_area(side: float) -> float:
        """Calculate the area of a square
        
        Args:
            side: Length of a side of the square
            
        Returns:
            Area of the square
        """
        if side <= 0:
            raise ToolException("Side length must be positive")
        
        return side * side
    
    @staticmethod
    def calculate_parallelogram_area(base: float, height: float) -> float:
        """Calculate the area of a parallelogram
        
        Args:
            base: Length of the base of the parallelogram
            height: Height of the parallelogram
            
        Returns:
            Area of the parallelogram
        """
        if base <= 0 or height <= 0:
            raise ToolException("Base and height must be positive")
        
        return base * height
    
    @staticmethod
    def calculate_trapezoid_area(a: float, b: float, height: float) -> float:
        """Calculate the area of a trapezoid
        
        Args:
            a: Length of one parallel side
            b: Length of the other parallel side
            height: Height between the parallel sides
            
        Returns:
            Area of the trapezoid
        """
        if a <= 0 or b <= 0 or height <= 0:
            raise ToolException("Sides and height must be positive")
        
        return 0.5 * (a + b) * height
    
    @staticmethod
    def calculate_regular_polygon_area(side_length: float, num_sides: int) -> float:
        """Calculate the area of a regular polygon
        
        Args:
            side_length: Length of a side of the regular polygon
            num_sides: Number of sides of the regular polygon
            
        Returns:
            Area of the regular polygon
        """
        if side_length <= 0:
            raise ToolException("Side length must be positive")
        
        if num_sides < 3:
            raise ToolException("Number of sides must be at least 3")
        
        # Calculate the area using the formula A = (n * s^2) / (4 * tan(π/n))
        area = (num_sides * side_length**2) / (4 * np.tan(np.pi / num_sides))
        
        return area
    
    @staticmethod
    def calculate_area_triangle(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a triangle from its vertices
        
        Args:
            vertices: List of three vertices [(x1, y1), (x2, y2), (x3, y3)]
            
        Returns:
            Area of the triangle
        """
        if len(vertices) != 3:
            raise ToolException("A triangle must have exactly 3 vertices")
        
        # Using the Shoelace formula (determinant method)
        x1, y1 = vertices[0]
        x2, y2 = vertices[1]
        x3, y3 = vertices[2]
        
        area = 0.5 * abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)))
        
        return area
    
    @staticmethod
    def calculate_area_triangle_from_sides(a: float, b: float, c: float) -> float:
        """Calculate the area of a triangle from its three sides using Heron's formula
        
        Args:
            a: Length of first side
            b: Length of second side
            c: Length of third side
            
        Returns:
            Area of the triangle
        """
        if a <= 0 or b <= 0 or c <= 0:
            raise ToolException("Side lengths must be positive")
            
        # Check triangle inequality
        if a + b <= c or a + c <= b or b + c <= a:
            raise ToolException("The given side lengths do not form a valid triangle")
        
        # Semi-perimeter
        s = (a + b + c) / 2
        
        # Heron's formula
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        
        return area
    
    @staticmethod
    def calculate_area_triangle_from_base_height(base: float, height: float) -> float:
        """Calculate the area of a triangle from its base and height
        
        Args:
            base: Length of the base
            height: Height to the base
            
        Returns:
            Area of the triangle
        """
        if base <= 0 or height <= 0:
            raise ToolException("Base and height must be positive")
        
        return 0.5 * base * height
    
    @staticmethod
    def calculate_area_circle(radius: float) -> float:
        """Calculate the area of a circle
        
        Args:
            radius: Radius of the circle
            
        Returns:
            Area of the circle
        """
        if radius <= 0:
            raise ToolException("Radius must be positive")
        
        return math.pi * radius * radius
    
    @staticmethod
    def calculate_area_sector(radius: float, angle_rad: float) -> float:
        """Calculate the area of a sector of a circle
        
        Args:
            radius: Radius of the circle
            angle_rad: Central angle in radians
            
        Returns:
            Area of the sector
        """
        if radius <= 0:
            raise ToolException("Radius must be positive")
        
        if angle_rad <= 0 or angle_rad > 2 * math.pi:
            raise ToolException("Angle must be positive and at most 2π radians")
        
        return 0.5 * radius * radius * angle_rad
    
    @staticmethod
    def calculate_area_segment(radius: float, angle_rad: float) -> float:
        """Calculate the area of a segment of a circle
        
        Args:
            radius: Radius of the circle
            angle_rad: Central angle in radians
            
        Returns:
            Area of the segment
        """
        if radius <= 0:
            raise ToolException("Radius must be positive")
        
        if angle_rad <= 0 or angle_rad > 2 * math.pi:
            raise ToolException("Angle must be positive and at most 2π radians")
        
        # Area of sector - area of triangle formed by center and the two points on the circle
        sector_area = AreaTools.calculate_area_sector(radius, angle_rad)
        triangle_area = 0.5 * radius * radius * math.sin(angle_rad)
        
        return sector_area - triangle_area
    
    @staticmethod
    def calculate_area_rectangle_from_points(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a rectangle from its vertices
        
        Args:
            vertices: List of four vertices [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            
        Returns:
            Area of the rectangle
        """
        if len(vertices) != 4:
            raise ToolException("A rectangle must have exactly 4 vertices")
        
        # Calculate the lengths of all sides
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        sides = [
            distance(vertices[0], vertices[1]),
            distance(vertices[1], vertices[2]),
            distance(vertices[2], vertices[3]),
            distance(vertices[3], vertices[0])
        ]
        
        # In a rectangle, opposite sides are equal
        # Check if the shape is approximately a rectangle
        if abs(sides[0] - sides[2]) > 1e-10 or abs(sides[1] - sides[3]) > 1e-10:
            raise ToolException("The given vertices do not form a rectangle")
        
        return sides[0] * sides[1]
    
    @staticmethod
    def calculate_area_rhombus(diagonal1: float, diagonal2: float) -> float:
        """Calculate the area of a rhombus given its diagonals
        
        Args:
            diagonal1: Length of first diagonal
            diagonal2: Length of second diagonal
            
        Returns:
            Area of the rhombus
        """
        if diagonal1 <= 0 or diagonal2 <= 0:
            raise ToolException("Diagonals must be positive")
        
        return 0.5 * diagonal1 * diagonal2
    
    @staticmethod
    def calculate_area_rhombus_from_points(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a rhombus from its vertices
        
        Args:
            vertices: List of four vertices [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            
        Returns:
            Area of the rhombus
        """
        if len(vertices) != 4:
            raise ToolException("A rhombus must have exactly 4 vertices")
        
        # For a rhombus, we can use the same formula as any quadrilateral
        return AreaTools.calculate_quadrilateral_area(vertices)
    
    @staticmethod
    def calculate_area_parallelogram_from_points(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a parallelogram from its vertices
        
        Args:
            vertices: List of four vertices [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            
        Returns:
            Area of the parallelogram
        """
        if len(vertices) != 4:
            raise ToolException("A parallelogram must have exactly 4 vertices")
        
        # For a parallelogram, we can use the same formula as any quadrilateral
        return AreaTools.calculate_quadrilateral_area(vertices)
    
    @staticmethod
    def calculate_area_trapezoid_from_points(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the area of a trapezoid from its vertices
        
        Args:
            vertices: List of four vertices [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            
        Returns:
            Area of the trapezoid
        """
        if len(vertices) != 4:
            raise ToolException("A trapezoid must have exactly 4 vertices")
        
        # For a trapezoid, we can use the same formula as any quadrilateral
        return AreaTools.calculate_quadrilateral_area(vertices)
    