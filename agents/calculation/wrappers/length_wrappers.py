"""
Length calculation wrapper module

This module provides wrapper functions for length calculation tools.
Each function validates the input and explains the result in English.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import LengthTools

def calculate_distance_points_wrapper(point1: List[float], point2: List[float]) -> dict:
    """
    Wrapper function for calculating the distance between two points
    
    Args:
        point1: Coordinates of the first point [x1, y1]
        point2: Coordinates of the second point [x2, y2]
        
    Returns:
        Distance calculation result with explanation
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        distance = LengthTools.calculate_distance_between_points(p1, p2)
        return {
            "distance": distance,
            "distance_explanation": f"The distance between points {p1} and {p2} is {distance}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating distance between points: {str(e)}")

def calculate_distance_point_to_line_wrapper(
    point: List[float], 
    line_a: float, 
    line_b: float, 
    line_c: float
) -> dict:
    """
    Wrapper function for calculating the distance from a point to a line
    
    Args:
        point: Coordinates of the point [x, y]
        line_a: Coefficient 'a' of the line for ax + by + c = 0
        line_b: Coefficient 'b' of the line for ax + by + c = 0
        line_c: Coefficient 'c' of the line for ax + by + c = 0
        
    Returns:
        Distance calculation result with explanation
    """
    try:
        point_tuple = tuple(point)
        line_tuple = (line_a, line_b, line_c)
        distance = LengthTools.calculate_distance_point_to_line(point_tuple, line_tuple)
        return {
            "distance": distance,
            "distance_explanation": f"The distance from point {point_tuple} to line {line_tuple} is {distance}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating distance from point to line: {str(e)}")

def calculate_distance_parallel_lines_wrapper(
    line1_a: float, 
    line1_b: float, 
    line1_c: float, 
    line2_a: float, 
    line2_b: float, 
    line2_c: float
) -> dict:
    """
    Wrapper function for calculating the distance between two parallel lines
    
    Args:
        line1_a: Coefficient 'a' of the first line for ax + by + c = 0
        line1_b: Coefficient 'b' of the first line for ax + by + c = 0
        line1_c: Coefficient 'c' of the first line for ax + by + c = 0
        line2_a: Coefficient 'a' of the second line for ax + by + c = 0
        line2_b: Coefficient 'b' of the second line for ax + by + c = 0
        line2_c: Coefficient 'c' of the second line for ax + by + c = 0
        
    Returns:
        Distance calculation result with explanation
    """
    try:
        line1_tuple = (line1_a, line1_b, line1_c)
        line2_tuple = (line2_a, line2_b, line2_c)
        distance = LengthTools.calculate_distance_between_parallel_lines(line1_tuple, line2_tuple)
        if distance == float('inf'):
            return {
                "distance": "infinity",
                "distance_explanation": f"Lines {line1_tuple} and {line2_tuple} are not parallel, cannot calculate distance"
            }
        return {
            "distance": distance,
            "distance_explanation": f"The distance between parallel lines {line1_tuple} and {line2_tuple} is {distance}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating distance between parallel lines: {str(e)}")

def calculate_perimeter_triangle_wrapper(points: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the perimeter of a triangle
    
    Args:
        points: Coordinates of the three vertices of the triangle, format [[x1,y1], [x2,y2], [x3,y3]]
        
    Returns:
        Perimeter calculation result with explanation
    """
    try:
        points_tuple = [tuple(p) for p in points]
        if len(points_tuple) != 3:
            raise ToolException("A triangle requires exactly 3 vertices")
        perimeter = LengthTools.calculate_perimeter_triangle(points_tuple)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"The perimeter of the triangle {points_tuple} is {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle perimeter: {str(e)}")

def calculate_perimeter_quadrilateral_wrapper(points: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the perimeter of a quadrilateral
    
    Args:
        points: Coordinates of the four vertices of the quadrilateral, format [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        
    Returns:
        Perimeter calculation result with explanation
    """
    try:
        points_tuple = [tuple(p) for p in points]
        if len(points_tuple) != 4:
            raise ToolException("A quadrilateral requires exactly 4 vertices")
        perimeter = LengthTools.calculate_perimeter_quadrilateral(points_tuple)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"The perimeter of the quadrilateral {points_tuple} is {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating quadrilateral perimeter: {str(e)}")

def calculate_perimeter_polygon_wrapper(points: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the perimeter of a polygon
    
    Args:
        points: Coordinates of the vertices of the polygon, format [[x1,y1], [x2,y2], ...]
        
    Returns:
        Perimeter calculation result with explanation
    """
    try:
        points_tuple = [tuple(p) for p in points]
        if len(points_tuple) < 3:
            raise ToolException("A polygon requires at least 3 vertices")
        perimeter = LengthTools.calculate_perimeter_polygon(points_tuple)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"The perimeter of the {len(points_tuple)}-sided polygon is {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating polygon perimeter: {str(e)}")

def calculate_circumference_wrapper(radius: float) -> dict:
    """
    Wrapper function for calculating the circumference of a circle
    
    Args:
        radius: Radius of the circle
        
    Returns:
        Circumference calculation result with explanation
    """
    try:
        if radius <= 0:
            raise ToolException("The radius of a circle must be positive")
        circumference = LengthTools.calculate_circumference(radius)
        return {
            "circumference": circumference,
            "circumference_explanation": f"The circumference of a circle with radius {radius} is {circumference}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating circle circumference: {str(e)}")

def calculate_chord_length_wrapper(radius: float, angle: float, degrees: bool = False) -> dict:
    """
    Wrapper function for calculating the length of a chord
    
    Args:
        radius: Radius of the circle
        angle: Central angle (in radians or degrees)
        degrees: Whether the angle is in degrees, True for degrees, False for radians
        
    Returns:
        Chord length calculation result with explanation
    """
    try:
        if degrees:
            angle = LengthTools.degrees_to_radians(angle)
        
        if radius <= 0:
            raise ToolException("The radius of a circle must be positive")
            
        chord_length = LengthTools.calculate_chord_length(radius, angle)
        return {
            "chord_length": chord_length,
            "chord_length_explanation": f"The chord length for a circle with radius {radius} and central angle {angle} radians is {chord_length}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating chord length: {str(e)}")

def calculate_arc_length_wrapper(radius: float, angle: float, degrees: bool = False) -> dict:
    """
    Wrapper function for calculating the length of an arc
    
    Args:
        radius: Radius of the circle
        angle: Central angle (in radians or degrees)
        degrees: Whether the angle is in degrees, True for degrees, False for radians
        
    Returns:
        Arc length calculation result with explanation
    """
    try:
        if degrees:
            angle = LengthTools.degrees_to_radians(angle)
        
        if radius <= 0:
            raise ToolException("The radius of a circle must be positive")
            
        arc_length = LengthTools.calculate_arc_length(radius, angle)
        return {
            "arc_length": arc_length,
            "arc_length_explanation": f"The arc length for a circle with radius {radius} and central angle {angle} radians is {arc_length}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating arc length: {str(e)}") 