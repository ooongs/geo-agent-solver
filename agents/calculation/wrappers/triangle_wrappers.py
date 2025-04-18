"""
Triangle calculation wrapper module

This module provides wrapper functions for triangle calculation tools.
Each function validates the input and explains the result in English.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import TriangleTools

def calculate_area_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the area of a triangle (using coordinates)
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Area calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        area = TriangleTools.calculate_area(vertex_tuples)
        
        return {
            "area": area,
            "explanation": f"The area of triangle {vertex_tuples} is {area}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle area: {str(e)}")

def calculate_area_from_sides_wrapper(side1: float, side2: float, side3: float) -> dict:
    """
    Wrapper function for calculating the area of a triangle (using three side lengths)
    
    Args:
        side1: Length of the first side
        side2: Length of the second side
        side3: Length of the third side
        
    Returns:
        Area calculation result with explanation
    """
    try:
        area = TriangleTools.calculate_area_from_sides(side1, side2, side3)
        
        return {
            "area": area,
            "explanation": f"The area of the triangle with sides {side1}, {side2}, {side3} is {area}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle area: {str(e)}")

def calculate_perimeter_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the perimeter of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Perimeter calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        perimeter = TriangleTools.calculate_perimeter(vertex_tuples)
        
        return {
            "perimeter": perimeter,
            "explanation": f"The perimeter of triangle {vertex_tuples} is {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle perimeter: {str(e)}")

def is_right_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for checking if a triangle is a right triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Verification result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        is_right = TriangleTools.is_right_triangle(vertex_tuples)
        
        if is_right:
            return {
                "is_right": True,
                "explanation": f"Triangle {vertex_tuples} is a right triangle"
            }
        else:
            return {
                "is_right": False,
                "explanation": f"Triangle {vertex_tuples} is not a right triangle"
            }
    except Exception as e:
        raise ToolException(f"Error determining if triangle is right: {str(e)}")

def is_isosceles_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for checking if a triangle is an isosceles triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Verification result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        is_isosceles = TriangleTools.is_isosceles_triangle(vertex_tuples)
        
        if is_isosceles:
            return {
                "is_isosceles": True,
                "explanation": f"Triangle {vertex_tuples} is an isosceles triangle"
            }
        else:
            return {
                "is_isosceles": False,
                "explanation": f"Triangle {vertex_tuples} is not an isosceles triangle"
            }
    except Exception as e:
        raise ToolException(f"Error determining if triangle is isosceles: {str(e)}")

def is_equilateral_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for checking if a triangle is an equilateral triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Verification result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        is_equilateral = TriangleTools.is_equilateral_triangle(vertex_tuples)
        
        if is_equilateral:
            return {
                "is_equilateral": True,
                "explanation": f"Triangle {vertex_tuples} is an equilateral triangle"
            }
        else:
            return {
                "is_equilateral": False,
                "explanation": f"Triangle {vertex_tuples} is not an equilateral triangle"
            }
    except Exception as e:
        raise ToolException(f"Error determining if triangle is equilateral: {str(e)}")

def calculate_angles_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the three angles of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Angle calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        angles_rad = TriangleTools.calculate_angles(vertex_tuples)
        angles_deg = [TriangleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"The interior angles of triangle {vertex_tuples} are {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle angles: {str(e)}")

def calculate_centroid_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the centroid of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Centroid calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        centroid = TriangleTools.calculate_centroid(vertex_tuples)
        
        return {
            "centroid": centroid,
            "explanation": f"The centroid of triangle {vertex_tuples} is {centroid}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle centroid: {str(e)}")

def calculate_circumcenter_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the circumcenter of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Circumcenter calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        circumcenter = TriangleTools.calculate_circumcenter(vertex_tuples)
        circumradius = TriangleTools.calculate_circumradius(vertex_tuples)
        
        return {
            "circumcenter": circumcenter,
            "circumradius": circumradius,
            "explanation": f"The circumcenter of triangle {vertex_tuples} is {circumcenter} with radius {circumradius}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle circumcenter: {str(e)}")

def calculate_incenter_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the incenter of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Incenter calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        incenter = TriangleTools.calculate_incenter(vertex_tuples)
        inradius = TriangleTools.calculate_inradius(vertex_tuples)
        
        return {
            "incenter": incenter,
            "inradius": inradius,
            "explanation": f"The incenter of triangle {vertex_tuples} is {incenter} with inradius {inradius}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle incenter: {str(e)}")

def calculate_orthocenter_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the orthocenter of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Orthocenter calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        orthocenter = TriangleTools.calculate_orthocenter(vertex_tuples)
        
        # Check if the orthocenter is one of the vertices (in case of right triangle)
        is_right = TriangleTools.is_right_triangle(vertex_tuples)
        right_vertex_info = ""
        if is_right:
            right_vertex_info = " (this triangle is a right triangle, so the orthocenter is at one of the vertices)"
        
        return {
            "orthocenter": orthocenter,
            "explanation": f"The orthocenter of triangle {vertex_tuples} is {orthocenter}{right_vertex_info}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle orthocenter: {str(e)}")

def calculate_triangle_centers_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating all centers of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        All centers calculation results with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        centroid = TriangleTools.calculate_centroid(vertex_tuples)
        circumcenter = TriangleTools.calculate_circumcenter(vertex_tuples)
        incenter = TriangleTools.calculate_incenter(vertex_tuples)
        orthocenter = TriangleTools.calculate_orthocenter(vertex_tuples)
        
        return {
            "centroid": centroid,
            "circumcenter": circumcenter,
            "incenter": incenter,
            "orthocenter": orthocenter,
            "explanation": f"The centers of triangle {vertex_tuples} are:\n- Centroid: {centroid}\n- Circumcenter: {circumcenter}\n- Incenter: {incenter}\n- Orthocenter: {orthocenter}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle centers: {str(e)}")

def triangle_classification_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for classifying a triangle by its sides and angles
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Triangle classification result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        is_equilateral = TriangleTools.is_equilateral_triangle(vertex_tuples)
        is_isosceles = TriangleTools.is_isosceles_triangle(vertex_tuples)
        is_right = TriangleTools.is_right_triangle(vertex_tuples)
        angles_rad = TriangleTools.calculate_angles(vertex_tuples)
        angles_deg = [TriangleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        # Classify by angles
        angle_type = "acute"
        for angle in angles_rad:
            if angle > TriangleTools.HALF_PI + 1e-6:  # With tolerance for floating point errors
                angle_type = "obtuse"
                break
            elif abs(angle - TriangleTools.HALF_PI) < 1e-6:  # Right angle with tolerance
                angle_type = "right"
                break
                
        # Classify by sides
        side_type = "scalene"
        if is_equilateral:
            side_type = "equilateral"
        elif is_isosceles:
            side_type = "isosceles"
            
        classification = f"{side_type} {angle_type} triangle"
        if side_type == "equilateral":
            classification = "equilateral triangle (all angles are 60°)"
            
        return {
            "side_classification": side_type,
            "angle_classification": angle_type,
            "classification": classification,
            "angles_deg": angles_deg,
            "explanation": f"Triangle {vertex_tuples} is classified as a {classification} with angles {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"Error classifying triangle: {str(e)}")

def calculate_inradius_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the inradius of a triangle (radius of the inscribed circle)
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Inradius calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        inradius = TriangleTools.calculate_inradius(vertex_tuples)
        
        return {
            "inradius": inradius,
            "explanation": f"The inradius (radius of the inscribed circle) of triangle {vertex_tuples} is {inradius}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle inradius: {str(e)}")

def calculate_circumradius_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the circumradius of a triangle (radius of the circumscribed circle)
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Circumradius calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        circumradius = TriangleTools.calculate_circumradius(vertex_tuples)
        
        return {
            "circumradius": circumradius,
            "explanation": f"The circumradius (radius of the circumscribed circle) of triangle {vertex_tuples} is {circumradius}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle circumradius: {str(e)}")

def calculate_median_lengths_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the median lengths of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Median lengths calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        median_lengths = TriangleTools.calculate_median_lengths(vertex_tuples)
        
        return {
            "median_lengths": median_lengths,
            "explanation": f"The lengths of the three medians of triangle {vertex_tuples} are {median_lengths[0]}, {median_lengths[1]}, and {median_lengths[2]}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle median lengths: {str(e)}")

def calculate_altitude_lengths_wrapper(vertices: List[List[float]]) -> dict:
    """
    Wrapper function for calculating the altitude lengths of a triangle
    
    Args:
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Altitude lengths calculation result with explanation
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        altitude_lengths = TriangleTools.calculate_altitude_lengths(vertex_tuples)
        
        return {
            "altitude_lengths": altitude_lengths,
            "explanation": f"The lengths of the three altitudes of triangle {vertex_tuples} are {altitude_lengths[0]}, {altitude_lengths[1]}, and {altitude_lengths[2]}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle altitude lengths: {str(e)}")

def is_point_inside_triangle_wrapper(point: List[float], vertices: List[List[float]]) -> dict:
    """
    Wrapper function for checking if a point is inside a triangle
    
    Args:
        point: Coordinates of the point [x, y]
        vertices: List of triangle vertex coordinates [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Check result with explanation
    """
    try:
        point_tuple = tuple(point)
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("A triangle must have three vertices")
            
        is_inside = TriangleTools.is_point_inside_triangle(point_tuple, vertex_tuples)
        
        if is_inside:
            return {
                "is_inside": True,
                "explanation": f"Point {point_tuple} is inside triangle {vertex_tuples}"
            }
        else:
            return {
                "is_inside": False,
                "explanation": f"Point {point_tuple} is not inside triangle {vertex_tuples}"
            }
    except Exception as e:
        raise ToolException(f"Error checking if point is inside triangle: {str(e)}") 