"""
Coordinate calculation wrapper module

This module provides wrapper functions for coordinate calculation tools.
Each function validates input and provides the result with explanation.
"""

from typing import Dict, Any, List, Tuple, Optional
from langchain_core.tools import ToolException
from agents.calculation.tools import CoordinateTools
import numpy as np

def calculate_midpoint_wrapper(point1: List[float], point2: List[float]) -> Tuple[float, float]:
    """
    Wrapper function to calculate the midpoint between two points
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        return CoordinateTools.calculate_midpoint(point1_tuple, point2_tuple)
    except Exception as e:
        raise ToolException(f"Midpoint calculation error: {str(e)}")

def calculate_slope_wrapper(point1: List[float], point2: List[float]) -> float:
    """
    Wrapper function to calculate the slope of a line passing through two points
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        result = CoordinateTools.calculate_slope(point1_tuple, point2_tuple)
        if result == float('inf'):
            return "Infinity (vertical line)"
        return result
    except Exception as e:
        raise ToolException(f"Slope calculation error: {str(e)}")

def calculate_line_equation_wrapper(point1: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the equation of a line passing through two points (in the form ax + by + c = 0)
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        a, b, c = CoordinateTools.calculate_line_equation(point1_tuple, point2_tuple)
        return {"a": a, "b": b, "c": c, "equation": f"{a}x + {b}y + {c} = 0"}
    except Exception as e:
        raise ToolException(f"Line equation calculation error: {str(e)}")

def are_points_collinear_wrapper(point1: List[float], point2: List[float], point3: List[float]) -> bool:
    """
    Wrapper function to check if three points are collinear
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        point3_tuple = tuple(point3)
        return CoordinateTools.are_points_collinear(point1_tuple, point2_tuple, point3_tuple)
    except Exception as e:
        raise ToolException(f"Collinearity check error: {str(e)}")

def are_lines_parallel_wrapper(
    line1_a: float, 
    line1_b: float, 
    line1_c: float, 
    line2_a: float, 
    line2_b: float, 
    line2_c: float
) -> bool:
    """
    Wrapper function to check if two lines are parallel
    Input is the a, b, c values for each line (in the form ax + by + c = 0)
    """
    try:
        line1_tuple = (line1_a, line1_b, line1_c)
        line2_tuple = (line2_a, line2_b, line2_c)
        return CoordinateTools.are_lines_parallel(line1_tuple, line2_tuple)
    except Exception as e:
        raise ToolException(f"Lines parallel check error: {str(e)}")

def calculate_segment_division_wrapper(point1: List[float], point2: List[float], ratio: float) -> Tuple[float, float]:
    """
    Wrapper function to calculate a point that divides a line segment by a specific ratio
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        return CoordinateTools.calculate_segment_division(point1_tuple, point2_tuple, ratio)
    except Exception as e:
        raise ToolException(f"Segment division calculation error: {str(e)}")

def calculate_internal_division_point_wrapper(point1: List[float], point2: List[float], m: float, n: float) -> Tuple[float, float]:
    """
    Wrapper function to calculate the internal division point of a line segment (ratio m:n)
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        return CoordinateTools.calculate_internal_division_point(point1_tuple, point2_tuple, m, n)
    except Exception as e:
        raise ToolException(f"Internal division point calculation error: {str(e)}")

def calculate_external_division_point_wrapper(point1: List[float], point2: List[float], m: float, n: float) -> Tuple[float, float]:
    """
    Wrapper function to calculate the external division point of a line segment (ratio m:n)
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        return CoordinateTools.calculate_external_division_point(point1_tuple, point2_tuple, m, n)
    except Exception as e:
        raise ToolException(f"External division point calculation error: {str(e)}")

def is_point_on_segment_wrapper(point: List[float], segment_start: List[float], segment_end: List[float]) -> bool:
    """
    Wrapper function to check if a point is on a line segment
    """
    try:
        # Convert list to tuple
        point_tuple = tuple(point)
        segment_start_tuple = tuple(segment_start)
        segment_end_tuple = tuple(segment_end)
        return CoordinateTools.is_point_on_segment(point_tuple, segment_start_tuple, segment_end_tuple)
    except Exception as e:
        raise ToolException(f"Point on segment check error: {str(e)}")

# Additional wrapper functions

def calculate_vector_wrapper(point1: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the vector between two points
    """
    try:
        # Convert list to tuple
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        vector = CoordinateTools.calculate_vector(point1_tuple, point2_tuple)
        length = CoordinateTools.calculate_vector_length(vector)
        return {
            "vector": vector,
            "length": length,
            "unit_vector": CoordinateTools.normalize_vector(vector) if length > 1e-10 else None
        }
    except Exception as e:
        raise ToolException(f"Vector calculation error: {str(e)}")

def calculate_dot_product_wrapper(vector1: List[float], vector2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the dot product of two vectors
    """
    try:
        # Convert list to tuple
        vector1_tuple = tuple(vector1)
        vector2_tuple = tuple(vector2)
        dot_product = CoordinateTools.calculate_dot_product(vector1_tuple, vector2_tuple)
        length1 = CoordinateTools.calculate_vector_length(vector1_tuple)
        length2 = CoordinateTools.calculate_vector_length(vector2_tuple)
        
        # cos(θ) = dot_product / (|v1| * |v2|)
        cos_theta = dot_product / (length1 * length2) if length1 > 1e-10 and length2 > 1e-10 else 0
        # Handle floating-point errors
        cos_theta = max(min(cos_theta, 1.0), -1.0)
        angle_radians = np.arccos(cos_theta)
        angle_degrees = np.degrees(angle_radians)
        
        return {
            "dot_product": dot_product,
            "angle_radians": angle_radians,
            "angle_degrees": angle_degrees
        }
    except Exception as e:
        raise ToolException(f"Dot product calculation error: {str(e)}")

def calculate_cross_product_wrapper(vector1: List[float], vector2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the cross product of two vectors (z component)
    """
    try:
        # Convert list to tuple
        vector1_tuple = tuple(vector1)
        vector2_tuple = tuple(vector2)
        cross_product = CoordinateTools.calculate_cross_product(vector1_tuple, vector2_tuple)
        # The magnitude of the cross product is the area of the parallelogram formed by the two vectors
        area = abs(cross_product)
        return {
            "cross_product": cross_product,
            "area": area
        }
    except Exception as e:
        raise ToolException(f"Cross product calculation error: {str(e)}")

def normalize_vector_wrapper(vector: List[float]) -> Tuple[float, float]:
    """
    Wrapper function to normalize a vector
    """
    try:
        # Convert list to tuple
        vector_tuple = tuple(vector)
        return CoordinateTools.normalize_vector(vector_tuple)
    except Exception as e:
        raise ToolException(f"Vector normalization error: {str(e)}")

def calculate_distance_point_to_line_wrapper(
    point: List[float], 
    line_a: float, 
    line_b: float, 
    line_c: float
) -> float:
    """
    Wrapper function to calculate the distance from a point to a line
    Input is the point coordinates and the a, b, c values for the line (in the form ax + by + c = 0)
    """
    try:
        line_tuple = (line_a, line_b, line_c)
        return CoordinateTools.calculate_distance_point_to_line(point, line_tuple)
    except Exception as e:
        raise ToolException(f"Distance from point to line calculation error: {str(e)}")

def calculate_line_intersection_wrapper(
    line1_a: float, 
    line1_b: float, 
    line1_c: float, 
    line2_a: float, 
    line2_b: float, 
    line2_c: float
) -> Optional[Tuple[float, float]]:
    """
    Wrapper function to calculate the intersection point of two lines
    Input is the a, b, c values for each line (in the form ax + by + c = 0)
    """
    try:
        line1_tuple = (line1_a, line1_b, line1_c)
        line2_tuple = (line2_a, line2_b, line2_c)
        intersection = CoordinateTools.calculate_line_intersection(line1_tuple, line2_tuple)
        return intersection
    except Exception as e:
        raise ToolException(f"Line intersection calculation error: {str(e)}")

def calculate_ray_intersection_wrapper(
    ray_start: List[float], 
    ray_angle: float, 
    segment_start: List[float], 
    segment_end: List[float]
) -> Optional[Tuple[float, float]]:
    """
    Wrapper function to calculate the intersection between a ray and a line segment
    """
    try:
        # Convert list to tuple
        ray_start_tuple = tuple(ray_start)
        segment_start_tuple = tuple(segment_start)
        segment_end_tuple = tuple(segment_end)
        return CoordinateTools.calculate_ray_intersection_with_segment(
            ray_start_tuple, ray_angle, segment_start_tuple, segment_end_tuple
        )
    except Exception as e:
        raise ToolException(f"Ray intersection calculation error: {str(e)}")

def are_lines_perpendicular_wrapper(
    line1_a: float, 
    line1_b: float, 
    line1_c: float, 
    line2_a: float, 
    line2_b: float, 
    line2_c: float
) -> bool:
    """
    Wrapper function to check if two lines are perpendicular
    Input is the a, b, c values for each line (in the form ax + by + c = 0)
    """
    try:
        line1_tuple = (line1_a, line1_b, line1_c)
        line2_tuple = (line2_a, line2_b, line2_c)
        return CoordinateTools.are_lines_perpendicular(line1_tuple, line2_tuple)
    except Exception as e:
        raise ToolException(f"Lines perpendicular check error: {str(e)}")

def is_point_inside_triangle_wrapper(
    point: List[float], 
    triangle_point1: List[float], 
    triangle_point2: List[float], 
    triangle_point3: List[float]
) -> bool:
    """
    Wrapper function to check if a point is inside a triangle
    """
    try:
        # Convert list to tuple
        point_tuple = tuple(point)
        triangle_point1_tuple = tuple(triangle_point1)
        triangle_point2_tuple = tuple(triangle_point2)
        triangle_point3_tuple = tuple(triangle_point3)
        return CoordinateTools.is_point_inside_triangle(
            point_tuple, triangle_point1_tuple, triangle_point2_tuple, triangle_point3_tuple
        )
    except Exception as e:
        raise ToolException(f"Point inside triangle check error: {str(e)}") 