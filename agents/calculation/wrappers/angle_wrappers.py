"""
Angle calculation wrapper module

This module provides wrapper functions for angle calculations.
Each function validates input and returns the result with explanation.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from langchain_core.tools import ToolException
from agents.calculation.tools import AngleTools
import math

# === Math Tool Wrappers ===

def calculate_angle_three_points_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the angle formed by three points
    """
    try:
        # Convert lists to tuples
        point1_tuple = tuple(point1)
        vertex_tuple = tuple(vertex)
        point2_tuple = tuple(point2)
        
        angle_rad = AngleTools.calculate_angle_three_points(point1_tuple, vertex_tuple, point2_tuple)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"The angle formed by points {point1}, {vertex} (vertex), and {point2} is {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle between three points: {str(e)}")

def calculate_angle_two_lines_wrapper(
    line1_a: float, 
    line1_b: float, 
    line1_c: float, 
    line2_a: float, 
    line2_b: float, 
    line2_c: float
) -> Dict[str, Any]:
    """
    Wrapper function to calculate the angle between two lines
    """
    try:
        line1_tuple = (line1_a, line1_b, line1_c)
        line2_tuple = (line2_a, line2_b, line2_c)
        
        angle_rad = AngleTools.calculate_angle_two_lines(line1_tuple, line2_tuple)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"The angle between lines {line1_tuple} and {line2_tuple} is {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle between two lines: {str(e)}")

def calculate_angle_two_vectors_wrapper(vector1: List[float], vector2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the angle between two vectors
    """
    try:
        # Convert lists to tuples
        vector1_tuple = tuple(vector1)
        vector2_tuple = tuple(vector2)
        
        angle_rad = AngleTools.calculate_angle_two_vectors(vector1_tuple, vector2_tuple)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"The angle between vectors {vector1} and {vector2} is {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle between two vectors: {str(e)}")

def calculate_interior_angles_triangle_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the interior angles of a triangle
    """
    try:
        if len(vertices) != 3:
            raise ToolException("Error: A triangle must have exactly 3 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertices_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"The interior angles of the triangle are {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, and {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle interior angles: {str(e)}")

def calculate_exterior_angles_triangle_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the exterior angles of a triangle
    """
    try:
        if len(vertices) != 3:
            raise ToolException("Error: A triangle must have exactly 3 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        angles_rad = AngleTools.calculate_exterior_angles_triangle(vertices_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"The exterior angles of the triangle are {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, and {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle exterior angles: {str(e)}")

def calculate_inscribed_angle_wrapper(center: List[float], point1: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the inscribed angle in a circle
    """
    try:
        # Convert lists to tuples
        center_tuple = tuple(center)
        point1_tuple = tuple(point1)
        point2_tuple = tuple(point2)
        
        inscribed_angle_rad = AngleTools.calculate_inscribed_angle(center_tuple, point1_tuple, point2_tuple)
        inscribed_angle_deg = AngleTools.radians_to_degrees(inscribed_angle_rad)
        central_angle_rad = 2 * inscribed_angle_rad
        central_angle_deg = AngleTools.radians_to_degrees(central_angle_rad)
        
        return {
            "inscribed_angle_rad": inscribed_angle_rad,
            "inscribed_angle_deg": inscribed_angle_deg,
            "central_angle_rad": central_angle_rad,
            "central_angle_deg": central_angle_deg,
            "explanation": f"The inscribed angle with center {center}, and points {point1} and {point2} is {inscribed_angle_deg:.2f}°, with corresponding central angle {central_angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating inscribed angle: {str(e)}")

def calculate_angle_bisector_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the angle bisector
    """
    try:
        # Convert lists to tuples
        point1_tuple = tuple(point1)
        vertex_tuple = tuple(vertex)
        point2_tuple = tuple(point2)
        
        bisector = AngleTools.calculate_angle_bisector(point1_tuple, vertex_tuple, point2_tuple)
        
        return {
            "angle_bisector": bisector,
            "equation": f"{bisector[0]}x + {bisector[1]}y + {bisector[2]} = 0",
            "explanation": f"The angle bisector of points {point1}, {vertex} (vertex), and {point2} has the equation {bisector[0]:.2f}x + {bisector[1]:.2f}y + {bisector[2]:.2f} = 0"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle bisector: {str(e)}")
    
def calculate_angle_trisection_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to trisect an angle
    """
    try:
        # Convert lists to tuples
        point1_tuple = tuple(point1)
        vertex_tuple = tuple(vertex)
        point2_tuple = tuple(point2)
        
        trisection = AngleTools.calculate_angle_trisection(point1_tuple, vertex_tuple, point2_tuple)
        trisection_equations = [f"{t[0]:.2f}x + {t[1]:.2f}y + {t[2]:.2f} = 0" for t in trisection]
        
        return {
            "trisection_lines": trisection,
            "equations": trisection_equations,
            "explanation": f"The trisectors of the angle formed by points {point1}, {vertex} (vertex), and {point2} have the equations: {', '.join(trisection_equations)}",
            "geometric_elements": {
                "rays": [
                    {"name": "trisector1", "angle": AngleTools.calculate_angle_two_vectors((1, 0), (trisection[0][1], -trisection[0][0])), "direction_vector": (trisection[0][1], -trisection[0][0])},
                    {"name": "trisector2", "angle": AngleTools.calculate_angle_two_vectors((1, 0), (trisection[1][1], -trisection[1][0])), "direction_vector": (trisection[1][1], -trisection[1][0])},
                    {"name": "trisector3", "angle": AngleTools.calculate_angle_two_vectors((1, 0), (trisection[2][1], -trisection[2][0])), "direction_vector": (trisection[2][1], -trisection[2][0])}
                ]
            }
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle trisection: {str(e)}")

def calculate_angle_complement_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate the complement of an angle (in radians, 90° - angle)
    """
    try:
        complement_rad = AngleTools.calculate_angle_complement(angle_rad)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        complement_deg = AngleTools.radians_to_degrees(complement_rad)
        
        return {
            "original_angle_rad": angle_rad,
            "original_angle_deg": angle_deg,
            "complement_rad": complement_rad,
            "complement_deg": complement_deg,
            "explanation": f"The complement of {angle_deg:.2f}° is {complement_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle complement: {str(e)}")

def calculate_angle_supplement_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate the supplement of an angle (in radians, 180° - angle)
    """
    try:
        supplement_rad = AngleTools.calculate_angle_supplement(angle_rad)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        supplement_deg = AngleTools.radians_to_degrees(supplement_rad)
        
        return {
            "original_angle_rad": angle_rad,
            "original_angle_deg": angle_deg,
            "supplement_rad": supplement_rad,
            "supplement_deg": supplement_deg,
            "explanation": f"The supplement of {angle_deg:.2f}° is {supplement_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle supplement: {str(e)}")

def calculate_regular_polygon_angle_wrapper(sides: int) -> Dict[str, Any]:
    """
    Wrapper function to calculate the interior and exterior angles of a regular polygon
    """
    try:
        if sides < 3:
            raise ToolException("A polygon must have at least 3 sides")
            
        interior_angle_rad = AngleTools.calculate_regular_polygon_angle(sides)
        interior_angle_deg = AngleTools.radians_to_degrees(interior_angle_rad)
        
        exterior_angle_rad = 2 * math.pi / sides
        exterior_angle_deg = AngleTools.radians_to_degrees(exterior_angle_rad)
        
        return {
            "interior_angle_rad": interior_angle_rad,
            "interior_angle_deg": interior_angle_deg,
            "exterior_angle_rad": exterior_angle_rad,
            "exterior_angle_deg": exterior_angle_deg,
            "explanation": f"A regular polygon with {sides} sides has interior angles of {interior_angle_deg:.2f}° and exterior angles of {exterior_angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating regular polygon angle: {str(e)}")

def normalize_angle_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to normalize an angle to the range [0, 2π)
    """
    try:
        normalized_angle_rad = AngleTools.normalize_angle(angle_rad)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        normalized_angle_deg = AngleTools.radians_to_degrees(normalized_angle_rad)
        
        return {
            "original_angle_rad": angle_rad,
            "original_angle_deg": angle_deg,
            "normalized_angle_rad": normalized_angle_rad,
            "normalized_angle_deg": normalized_angle_deg,
            "explanation": f"The angle {angle_deg:.2f}° normalized to the range [0°, 360°) is {normalized_angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error normalizing angle: {str(e)}")

def calculate_angle_with_direction_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> Dict[str, Any]:
    """
    Wrapper function to calculate the angle formed by three points with direction (counter-clockwise is positive)
    """
    try:
        # Convert lists to tuples
        point1_tuple = tuple(point1)
        vertex_tuple = tuple(vertex)
        point2_tuple = tuple(point2)
        
        angle_rad = AngleTools.calculate_angle_with_direction(point1_tuple, vertex_tuple, point2_tuple)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        direction = "counter-clockwise" if angle_rad > 0 else "clockwise"
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "direction": direction,
            "explanation": f"The angle formed by points {point1}, {vertex} (vertex), and {point2} is {abs(angle_deg):.2f}° in the {direction} direction"
        }
    except Exception as e:
        raise ToolException(f"Error calculating angle with direction: {str(e)}")

# === Validation Tool Wrappers ===

def angle_classification_wrapper(angle_deg: float) -> Dict[str, Any]:
    """
    Wrapper function to classify an angle
    """
    try:
        classification = AngleTools.classify_angle(angle_deg)
        
        explanation_map = {
            "zero": "zero angle (0° or 360°)",
            "right": "right angle (90°)",
            "obtuse": "obtuse angle (between 90° and 180°)",
            "straight": "straight angle (180°)",
            "reflex": "reflex angle (between 180° and 360°)",
            "reflex_right": "reflex right angle (270°)",
            "acute": "acute angle (between 0° and 90°)"
        }
        
        explanation = f"{angle_deg}° is a {explanation_map.get(classification, 'unknown angle type')}"
        
        return {
            "angle_deg": angle_deg,
            "classification": classification,
            "explanation": explanation
        }
    except Exception as e:
        raise ToolException(f"Error classifying angle: {str(e)}")

def is_angle_acute_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to check if an angle is acute
    """
    try:
        is_acute = AngleTools.is_angle_acute(angle_rad)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "is_acute": is_acute,
            "explanation": f"The angle {angle_deg:.2f}° is{' ' if is_acute else ' not '}an acute angle"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angle is acute: {str(e)}")

def is_angle_right_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to check if an angle is right
    """
    try:
        is_right = AngleTools.is_angle_right(angle_rad)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "is_right": is_right,
            "explanation": f"The angle {angle_deg:.2f}° is{' ' if is_right else ' not '}a right angle"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angle is a right angle: {str(e)}")

def is_angle_obtuse_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to check if an angle is obtuse (greater than 90° but less than 180°)
    """
    try:
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        is_obtuse = AngleTools.is_angle_obtuse(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "is_obtuse": is_obtuse,
            "explanation": f"The angle of {angle_deg:.2f}° is {'obtuse' if is_obtuse else 'not obtuse'}"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angle is obtuse: {str(e)}")

def is_triangle_acute_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to check if a triangle is acute
    """
    try:
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        is_acute = AngleTools.is_triangle_acute(vertices_tuples)
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertices_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "vertices": vertices,
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "is_acute_triangle": is_acute,
            "explanation": f"The triangle with angles {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, and {angles_deg[2]:.2f}° is{' ' if is_acute else ' not '}an acute triangle"
        }
    except Exception as e:
        raise ToolException(f"Error checking if triangle is acute: {str(e)}")

def is_triangle_right_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to check if a triangle is right
    """
    try:
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        is_right = AngleTools.is_triangle_right(vertices_tuples)
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertices_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "vertices": vertices,
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "is_right_triangle": is_right,
            "explanation": f"The triangle with angles {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, and {angles_deg[2]:.2f}° is{' ' if is_right else ' not '}a right triangle"
        }
    except Exception as e:
        raise ToolException(f"Error checking if triangle is a right triangle: {str(e)}")

def is_triangle_obtuse_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to check if a triangle is obtuse (one angle is greater than 90°)
    """
    try:
        if len(vertices) != 3:
            raise ToolException("A triangle must have exactly 3 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        is_obtuse = AngleTools.is_triangle_obtuse(vertices_tuples)
        
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertices_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "vertices": vertices,
            "is_obtuse": is_obtuse,
            "angles_deg": angles_deg,
            "explanation": f"The triangle with vertices {vertices} {'is' if is_obtuse else 'is not'} obtuse. Its angles are {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, and {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error checking if triangle is obtuse: {str(e)}")

def is_triangle_equiangular_wrapper(vertices: List[List[float]], tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Wrapper function to check if a triangle is equiangular (all angles are equal)
    """
    try:
        if len(vertices) != 3:
            raise ToolException("A triangle must have exactly 3 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        is_equiangular = AngleTools.is_triangle_equiangular(vertices_tuples, tolerance)
        
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertices_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "vertices": vertices,
            "is_equiangular": is_equiangular,
            "angles_deg": angles_deg,
            "explanation": f"The triangle with vertices {vertices} {'is' if is_equiangular else 'is not'} equiangular. Its angles are {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, and {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error checking if triangle is equiangular: {str(e)}")

def are_angles_equal_wrapper(angle1_rad: float, angle2_rad: float, tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Wrapper function to check if two angles are equal
    """
    try:
        are_equal = AngleTools.are_angles_equal(angle1_rad, angle2_rad, tolerance)
        angle1_deg = AngleTools.radians_to_degrees(angle1_rad)
        angle2_deg = AngleTools.radians_to_degrees(angle2_rad)
        
        return {
            "angle1_rad": angle1_rad,
            "angle1_deg": angle1_deg,
            "angle2_rad": angle2_rad,
            "angle2_deg": angle2_deg,
            "tolerance_rad": tolerance,
            "tolerance_deg": AngleTools.radians_to_degrees(tolerance),
            "are_equal": are_equal,
            "explanation": f"The angles {angle1_deg:.2f}° and {angle2_deg:.2f}° are{' ' if are_equal else ' not '}equal (within tolerance)"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angles are equal: {str(e)}")

def are_angles_complementary_wrapper(angle1_rad: float, angle2_rad: float, tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Wrapper function to check if two angles are complementary
    """
    try:
        are_complementary = AngleTools.are_angles_complementary(angle1_rad, angle2_rad, tolerance)
        angle1_deg = AngleTools.radians_to_degrees(angle1_rad)
        angle2_deg = AngleTools.radians_to_degrees(angle2_rad)
        sum_deg = angle1_deg + angle2_deg
        
        return {
            "angle1_rad": angle1_rad,
            "angle1_deg": angle1_deg,
            "angle2_rad": angle2_rad,
            "angle2_deg": angle2_deg,
            "sum_rad": angle1_rad + angle2_rad,
            "sum_deg": sum_deg,
            "are_complementary": are_complementary,
            "explanation": f"The angles {angle1_deg:.2f}° and {angle2_deg:.2f}° (sum = {sum_deg:.2f}°) are{' ' if are_complementary else ' not '}complementary"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angles are complementary: {str(e)}")

def are_angles_supplementary_wrapper(angle1_rad: float, angle2_rad: float, tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Wrapper function to check if two angles are supplementary
    """
    try:
        are_supplementary = AngleTools.are_angles_supplementary(angle1_rad, angle2_rad, tolerance)
        angle1_deg = AngleTools.radians_to_degrees(angle1_rad)
        angle2_deg = AngleTools.radians_to_degrees(angle2_rad)
        sum_deg = angle1_deg + angle2_deg
        
        return {
            "angle1_rad": angle1_rad,
            "angle1_deg": angle1_deg,
            "angle2_rad": angle2_rad,
            "angle2_deg": angle2_deg,
            "sum_rad": angle1_rad + angle2_rad,
            "sum_deg": sum_deg,
            "are_supplementary": are_supplementary,
            "explanation": f"The angles {angle1_deg:.2f}° and {angle2_deg:.2f}° (sum = {sum_deg:.2f}°) are{' ' if are_supplementary else ' not '}supplementary"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angles are supplementary: {str(e)}")

# === Conversion Functions ===

def radians_to_degrees_wrapper(radians: float) -> Dict[str, Any]:
    """
    Wrapper function to convert radians to degrees
    """
    try:
        degrees = AngleTools.radians_to_degrees(radians)
        return {
            "radians": radians,
            "degrees": degrees,
            "explanation": f"{radians:.6f} radians = {degrees:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error converting radians to degrees: {str(e)}")

def degrees_to_radians_wrapper(degrees: float) -> Dict[str, Any]:
    """
    Wrapper function to convert degrees to radians
    """
    try:
        radians = AngleTools.degrees_to_radians(degrees)
        return {
            "degrees": degrees,
            "radians": radians,
            "explanation": f"{degrees:.2f}° = {radians:.6f} radians"
        }
    except Exception as e:
        raise ToolException(f"Error converting degrees to radians: {str(e)}")

def calculate_rotation_wrapper(point: List[float], center: List[float], angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to rotate a point around a center by a given angle
    """
    try:
        # Convert lists to tuples
        point_tuple = tuple(point)
        center_tuple = tuple(center)
        
        rotated_point = AngleTools.calculate_rotation(point_tuple, center_tuple, angle_rad)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "original_point": point,
            "center": center,
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "rotated_point": rotated_point,
            "explanation": f"Rotating point {point} around center {center} by {angle_deg:.2f}° gives the rotated point {rotated_point}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating point rotation: {str(e)}")

def is_angle_straight_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to check if an angle is straight (equal to 180°)
    """
    try:
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        is_straight = AngleTools.is_angle_straight(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "is_straight": is_straight,
            "explanation": f"The angle of {angle_deg:.2f}° is {'straight' if is_straight else 'not straight'}"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angle is straight: {str(e)}")

def is_angle_reflex_wrapper(angle_rad: float) -> Dict[str, Any]:
    """
    Wrapper function to check if an angle is reflex (greater than 180° but less than 360°)
    """
    try:
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        is_reflex = AngleTools.is_angle_reflex(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "is_reflex": is_reflex,
            "explanation": f"The angle of {angle_deg:.2f}° is {'reflex' if is_reflex else 'not reflex'}"
        }
    except Exception as e:
        raise ToolException(f"Error checking if angle is reflex: {str(e)}") 
