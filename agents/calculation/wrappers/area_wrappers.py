"""
Area calculation wrapper module

This module provides wrapper functions for area calculation tools.
Each function validates input and returns the result with explanation.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import AreaTools

def calculate_area_triangle_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate triangle area from vertices
    
    Args:
        vertices: List of triangle vertices [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) != 3:
            raise ToolException("A triangle must have exactly 3 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_area_triangle(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the triangle with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle area: {str(e)}")

def calculate_area_triangle_from_sides_wrapper(a: float, b: float, c: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate triangle area from three sides using Heron's formula
    
    Args:
        a: Length of first side
        b: Length of second side
        c: Length of third side
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_area_triangle_from_sides(a, b, c)
        
        return {
            "area": area,
            "lengths": {"side1": a, "side2": b, "side3": c},
            "explanation": f"The area of the triangle with sides {a}, {b}, and {c} is {area:.4f} square units (using Heron's formula)"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle area from sides: {str(e)}")

def calculate_area_triangle_from_base_height_wrapper(base: float, height: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate triangle area from base and height
    
    Args:
        base: Length of the base
        height: Height to the base
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_area_triangle_from_base_height(base, height)
        
        return {
            "area": area,
            "lengths": {"base": base, "height": height},
            "explanation": f"The area of the triangle with base {base} and height {height} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating triangle area from base and height: {str(e)}")

def calculate_area_rectangle_wrapper(width: float, height: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate rectangle area from width and height
    
    Args:
        width: Width of the rectangle
        height: Height of the rectangle
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_rectangle_area(width, height)
        
        return {
            "area": area,
            "lengths": {"width": width, "height": height},
            "explanation": f"The area of the rectangle with width {width} and height {height} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating rectangle area: {str(e)}")

def calculate_area_rectangle_from_points_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate rectangle area from vertices
    
    Args:
        vertices: List of rectangle vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) != 4:
            raise ToolException("A rectangle must have exactly 4 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_area_rectangle_from_points(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the rectangle with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating rectangle area from vertices: {str(e)}")

def calculate_area_square_wrapper(side: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate square area from side length
    
    Args:
        side: Length of a side of the square
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_square_area(side)
        
        return {
            "area": area,
            "lengths": {"side": side},
            "explanation": f"The area of the square with side length {side} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating square area: {str(e)}")

def calculate_area_parallelogram_wrapper(base: float, height: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate parallelogram area from base and height
    
    Args:
        base: Length of the base
        height: Height to the base
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_parallelogram_area(base, height)
        
        return {
            "area": area,
            "lengths": {"base": base, "height": height},
            "explanation": f"The area of the parallelogram with base {base} and height {height} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating parallelogram area: {str(e)}")

def calculate_area_parallelogram_from_points_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate parallelogram area from vertices
    
    Args:
        vertices: List of parallelogram vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) != 4:
            raise ToolException("A parallelogram must have exactly 4 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_area_parallelogram_from_points(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the parallelogram with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating parallelogram area from vertices: {str(e)}")

def calculate_area_rhombus_wrapper(diagonal1: float, diagonal2: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate rhombus area from diagonals
    
    Args:
        diagonal1: Length of first diagonal
        diagonal2: Length of second diagonal
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_area_rhombus(diagonal1, diagonal2)
        
        return {
            "area": area,
            "lengths": {"diagonal1": diagonal1, "diagonal2": diagonal2},
            "explanation": f"The area of the rhombus with diagonals {diagonal1} and {diagonal2} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating rhombus area: {str(e)}")

def calculate_area_rhombus_from_points_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate rhombus area from vertices
    
    Args:
        vertices: List of rhombus vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) != 4:
            raise ToolException("A rhombus must have exactly 4 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_area_rhombus_from_points(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the rhombus with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating rhombus area from vertices: {str(e)}")

def calculate_area_trapezoid_wrapper(base1: float, base2: float, height: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate trapezoid area from parallel sides and height
    
    Args:
        base1: Length of first parallel side
        base2: Length of second parallel side
        height: Height between parallel sides
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_trapezoid_area(base1, base2, height)
        
        return {
            "area": area,
            "lengths": {"base1": base1, "base2": base2, "height": height},
            "explanation": f"The area of the trapezoid with parallel sides {base1} and {base2}, and height {height} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating trapezoid area: {str(e)}")

def calculate_area_trapezoid_from_points_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate trapezoid area from vertices
    
    Args:
        vertices: List of trapezoid vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) != 4:
            raise ToolException("A trapezoid must have exactly 4 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_area_trapezoid_from_points(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the trapezoid with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating trapezoid area from vertices: {str(e)}")

def calculate_area_regular_polygon_wrapper(side: float, n: int) -> Dict[str, Any]:
    """
    Wrapper function to calculate regular polygon area
    
    Args:
        side: Length of a side of the regular polygon
        n: Number of sides
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if n < 3:
            raise ToolException("A polygon must have at least 3 sides")
        
        area = AreaTools.calculate_regular_polygon_area(side, n)
        
        return {
            "area": area,
            "parameters": {"side_length": side, "num_sides": n},
            "explanation": f"The area of the regular {n}-sided polygon with side length {side} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating regular polygon area: {str(e)}")

def calculate_area_polygon_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate polygon area from vertices
    
    Args:
        vertices: List of polygon vertices [[x1, y1], [x2, y2], ..., [xn, yn]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) < 3:
            raise ToolException("A polygon must have at least 3 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_area_polygon(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the {len(vertices)}-sided polygon with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating polygon area: {str(e)}")

def calculate_area_circle_wrapper(radius: float) -> Dict[str, Any]:
    """
    Wrapper function to calculate circle area
    
    Args:
        radius: Radius of the circle
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        area = AreaTools.calculate_area_circle(radius)
        
        return {
            "area": area,
            "parameters": {"radius": radius},
            "explanation": f"The area of the circle with radius {radius} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating circle area: {str(e)}")

def calculate_area_sector_wrapper(radius: float, angle_rad: float, degrees: bool = False) -> Dict[str, Any]:
    """
    Wrapper function to calculate sector area
    
    Args:
        radius: Radius of the circle
        angle_rad: Central angle in radians
        degrees: Whether the angle is in degrees instead of radians
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        angle_to_use = angle_rad
        if degrees:
            # Convert to radians if needed
            from math import pi
            angle_to_use = angle_rad * (pi / 180)
        
        area = AreaTools.calculate_area_sector(radius, angle_to_use)
        
        angle_display = angle_rad
        unit = "radians"
        if degrees:
            unit = "degrees"
        
        return {
            "area": area,
            "parameters": {"radius": radius, "angle": angle_display, "angle_unit": unit},
            "explanation": f"The area of the sector with radius {radius} and central angle {angle_display} {unit} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating sector area: {str(e)}")

def calculate_area_segment_wrapper(radius: float, angle_rad: float, degrees: bool = False) -> Dict[str, Any]:
    """
    Wrapper function to calculate segment area
    
    Args:
        radius: Radius of the circle
        angle_rad: Central angle in radians
        degrees: Whether the angle is in degrees instead of radians
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        angle_to_use = angle_rad
        if degrees:
            # Convert to radians if needed
            from math import pi
            angle_to_use = angle_rad * (pi / 180)
        
        area = AreaTools.calculate_area_segment(radius, angle_to_use)
        
        angle_display = angle_rad
        unit = "radians"
        if degrees:
            unit = "degrees"
        
        return {
            "area": area,
            "parameters": {"radius": radius, "angle": angle_display, "angle_unit": unit},
            "explanation": f"The area of the segment with radius {radius} and central angle {angle_display} {unit} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating segment area: {str(e)}")

def calculate_area_quadrilateral_wrapper(vertices: List[List[float]]) -> Dict[str, Any]:
    """
    Wrapper function to calculate quadrilateral area from vertices
    
    Args:
        vertices: List of quadrilateral vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        Dictionary with area calculation result and explanation
    """
    try:
        if len(vertices) != 4:
            raise ToolException("A quadrilateral must have exactly 4 vertices")
            
        # Convert list of lists to list of tuples
        vertices_tuples = [tuple(vertex) for vertex in vertices]
        
        area = AreaTools.calculate_quadrilateral_area(vertices_tuples)
        
        return {
            "area": area,
            "coordinates": {f"point{i+1}": vertices[i] for i in range(len(vertices))},
            "explanation": f"The area of the quadrilateral with vertices {vertices} is {area:.4f} square units"
        }
    except Exception as e:
        raise ToolException(f"Error calculating quadrilateral area: {str(e)}") 