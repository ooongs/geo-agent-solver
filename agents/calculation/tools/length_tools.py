"""
Length-related calculation tools

This module provides tools for solving geometry problems related to lengths at the middle school level.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase

class LengthTools(GeometryToolBase):
    """Tools for length-related calculations"""
    
    @staticmethod
    def calculate_distance_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate the distance between two points"""
        return LengthTools.calculate_distance(p1, p2)
    
    @staticmethod
    def calculate_distance_point_to_line(point: Tuple[float, float], line: Tuple[float, float, float]) -> float:
        """Calculate the distance from a point to a line"""
        a, b, c = line
        return abs(a * point[0] + b * point[1] + c) / np.sqrt(a**2 + b**2)
    
    @staticmethod
    def calculate_distance_between_parallel_lines(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> float:
        """Calculate the distance between two parallel lines"""
        a1, b1, c1 = line1
        a2, b2, c2 = line2
        
        # Check if the lines are parallel
        if abs(a1 * b2 - a2 * b1) > 1e-10:
            return float('inf')  # Not parallel
        
        # Calculate distance for parallel lines
        return abs(c1 - c2 * (a1 / a2)) / np.sqrt(a1**2 + b1**2) if abs(a2) > 1e-10 else abs(c1 - c2 * (b1 / b2)) / np.sqrt(a1**2 + b1**2)
    
    @staticmethod
    def calculate_perimeter_triangle(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the perimeter of a triangle"""
        if len(vertices) != 3:
            return 0
        
        p1, p2, p3 = vertices
        a = LengthTools.calculate_distance(p1, p2)
        b = LengthTools.calculate_distance(p2, p3)
        c = LengthTools.calculate_distance(p3, p1)
        
        return a + b + c
    
    @staticmethod
    def calculate_perimeter_quadrilateral(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the perimeter of a quadrilateral"""
        if len(vertices) != 4:
            return 0
        
        p1, p2, p3, p4 = vertices
        a = LengthTools.calculate_distance(p1, p2)
        b = LengthTools.calculate_distance(p2, p3)
        c = LengthTools.calculate_distance(p3, p4)
        d = LengthTools.calculate_distance(p4, p1)
        
        return a + b + c + d
    
    @staticmethod
    def calculate_perimeter_polygon(vertices: List[Tuple[float, float]]) -> float:
        """Calculate the perimeter of a polygon"""
        if len(vertices) < 3:
            return 0
        
        perimeter = 0
        n = len(vertices)
        
        for i in range(n):
            perimeter += LengthTools.calculate_distance(vertices[i], vertices[(i + 1) % n])
        
        return perimeter
    
    @staticmethod
    def calculate_circumference(radius: float) -> float:
        """Calculate the circumference of a circle"""
        return 2 * np.pi * radius
    
    @staticmethod
    def calculate_chord_length(radius: float, angle: float) -> float:
        """Calculate the length of a chord (angle in radians)"""
        return 2 * radius * np.sin(angle / 2)
    
    @staticmethod
    def calculate_arc_length(radius: float, angle: float) -> float:
        """Calculate the length of an arc (angle in radians)"""
        return radius * angle
    
