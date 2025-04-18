"""
Circle calculation wrapper module

This module provides wrapper functions for circle calculation tools.
Each function validates the input and explains the result in English.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import CircleTools

def calculate_circle_area_wrapper(radius: float) -> dict:
    """
    Wrapper function for calculating the area of a circle
    
    Args:
        radius: Radius of the circle
        
    Returns:
        Result of circle area calculation with explanation
    """
    try:
        area = CircleTools.calculate_area(radius)
        return {
            "area": area,
            "area_explanation": f"The area of a circle with radius {radius} is {area}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the area of the circle: {str(e)}")

def calculate_circle_circumference_wrapper(radius: float) -> dict:
    """
    Wrapper function for calculating the circumference of a circle
    
    Args:
        radius: Radius of the circle
        
    Returns:
        Result of circle circumference calculation with explanation
    """
    try:
        circumference = CircleTools.calculate_circumference(radius)
        return {
            "circumference": circumference,
            "circumference_explanation": f"The circumference of a circle with radius {radius} is {circumference}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the circumference of the circle: {str(e)}")

def calculate_circle_diameter_wrapper(radius: float) -> dict:
    """
    Wrapper function for calculating the diameter of a circle
    
    Args:
        radius: Radius of the circle
        
    Returns:
        Result of circle diameter calculation with explanation
    """
    try:
        diameter = radius * 2
        return {
            "diameter": diameter,
            "diameter_explanation": f"The diameter of a circle with radius {radius} is {diameter}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the diameter of the circle: {str(e)}")

def calculate_circle_radius_wrapper(diameter: float) -> dict:
    """
    Wrapper function for calculating the radius of a circle from its diameter
    
    Args:
        diameter: Diameter of the circle
        
    Returns:
        Result of circle radius calculation with explanation
    """
    try:
        radius = diameter / 2
        return {
            "radius": radius,
            "radius_explanation": f"The radius of a circle with diameter {diameter} is {radius}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the radius of the circle: {str(e)}")

def calculate_chord_length_wrapper(radius: float, angle: float) -> dict:
    """
    Wrapper function for calculating the length of a chord in a circle
    
    Args:
        radius: Radius of the circle
        angle: Central angle in radians
        
    Returns:
        Result of chord length calculation with explanation
    """
    try:
        chord_length = CircleTools.calculate_chord_length(radius, angle)
        return {
            "chord_length": chord_length,
            "chord_length_explanation": f"The length of a chord in a circle with radius {radius} and central angle {angle} radians is {chord_length}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the chord length: {str(e)}")

def calculate_sector_area_wrapper(radius: float, angle: float) -> dict:
    """
    Wrapper function for calculating the area of a sector in a circle
    
    Args:
        radius: Radius of the circle
        angle: Central angle in radians
        
    Returns:
        Result of sector area calculation with explanation
    """
    try:
        sector_area = CircleTools.calculate_sector_area(radius, angle)
        return {
            "sector_area": sector_area,
            "sector_area_explanation": f"The area of a sector in a circle with radius {radius} and central angle {angle} radians is {sector_area}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the sector area: {str(e)}")

def calculate_segment_area_wrapper(radius: float, angle: float) -> dict:
    """
    Wrapper function for calculating the area of a segment in a circle
    
    Args:
        radius: Radius of the circle
        angle: Central angle in radians
        
    Returns:
        Result of segment area calculation with explanation
    """
    try:
        segment_area = CircleTools.calculate_segment_area(radius, angle)
        return {
            "segment_area": segment_area,
            "segment_area_explanation": f"The area of a segment in a circle with radius {radius} and central angle {angle} radians is {segment_area}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating the segment area: {str(e)}")

def check_point_circle_position_wrapper(center: List[float], radius: float, point: List[float]) -> dict:
    """
    Wrapper function for checking the position of a point relative to a circle
    
    Args:
        center: Coordinates of the circle center [x, y]
        radius: Radius of the circle
        point: Coordinates of the point [x, y]
        
    Returns:
        Result of position check with explanation
    """
    try:
        center_tuple = tuple(center)
        point_tuple = tuple(point)
        position = CircleTools.check_point_circle_position(center_tuple, radius, point_tuple)
        
        if position == "inside":
            explanation = f"Point {point_tuple} is inside the circle (center {center_tuple}, radius {radius})"
        elif position == "on":
            explanation = f"Point {point_tuple} is on the circle (center {center_tuple}, radius {radius})"
        else:  # position == "outside"
            explanation = f"Point {point_tuple} is outside the circle (center {center_tuple}, radius {radius})"
            
        # Distance calculation
        distance = CircleTools.calculate_distance(center_tuple, point_tuple)
        distance_info = f"Distance from center to point is {distance}, radius is {radius}"
            
        return {
            "position": position,
            "distance": distance,
            "explanation": f"{explanation}. {distance_info}"
        }
    except Exception as e:
        raise ToolException(f"Error checking point-circle position: {str(e)}")

def calculate_tangent_points_wrapper(center: List[float], radius: float, point: List[float]) -> dict:
    """
    Wrapper function for calculating the tangent points from an external point to a circle
    
    Args:
        center: Coordinates of the circle center [x, y]
        radius: Radius of the circle
        point: Coordinates of the external point [x, y]
        
    Returns:
        Result of tangent point calculation with explanation
    """
    try:
        center_tuple = tuple(center)
        point_tuple = tuple(point)
        
        # Check if the point is outside the circle
        position = CircleTools.check_point_circle_position(center_tuple, radius, point_tuple)
        if position != "outside":
            raise ToolException(f"Point {point_tuple} is not outside the circle (center {center_tuple}, radius {radius}), cannot calculate tangent points")
            
        tangent_points = CircleTools.calculate_tangent_points(center_tuple, radius, point_tuple)
        
        return {
            "tangent_points": tangent_points,
            "explanation": f"Tangent points from point {point_tuple} to circle (center {center_tuple}, radius {radius}) are {tangent_points[0]} and {tangent_points[1]}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating tangent points: {str(e)}")

def calculate_circle_intersection_wrapper(center1: List[float], radius1: float, center2: List[float], radius2: float) -> dict:
    """
    Wrapper function for calculating the intersection points of two circles
    
    Args:
        center1: Coordinates of the center of the first circle [x1, y1]
        radius1: Radius of the first circle
        center2: Coordinates of the center of the second circle [x2, y2]
        radius2: Radius of the second circle
        
    Returns:
        Result of intersection point calculation with explanation
    """
    try:
        center1_tuple = tuple(center1)
        center2_tuple = tuple(center2)
        
        intersection_points = CircleTools.calculate_circle_intersection(center1_tuple, radius1, center2_tuple, radius2)
        
        if not intersection_points:
            explanation = f"Circles (center {center1_tuple}, radius {radius1}) and (center {center2_tuple}, radius {radius2}) do not intersect"
        elif len(intersection_points) == 1:
            explanation = f"Circles (center {center1_tuple}, radius {radius1}) and (center {center2_tuple}, radius {radius2}) are tangent at point {intersection_points[0]}"
        else:  # len(intersection_points) == 2
            explanation = f"Circles (center {center1_tuple}, radius {radius1}) and (center {center2_tuple}, radius {radius2}) intersect at points {intersection_points[0]} and {intersection_points[1]}"
            
        return {
            "intersection_points": intersection_points,
            "explanation": explanation
        }
    except Exception as e:
        raise ToolException(f"Error calculating circle intersections: {str(e)}")

def calculate_circle_from_three_points_wrapper(point1: List[float], point2: List[float], point3: List[float]) -> dict:
    """
    Wrapper function for calculating a circle from three points
    
    Args:
        point1: Coordinates of first point [x1, y1]
        point2: Coordinates of second point [x2, y2]
        point3: Coordinates of third point [x3, y3]
        
    Returns:
        Result of circle calculation with explanation
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        p3 = tuple(point3)
        
        center, radius = CircleTools.calculate_circle_from_three_points(p1, p2, p3)
        
        if center is None:
            raise ToolException(f"Points {p1}, {p2}, {p3} are collinear, cannot determine a unique circle")
            
        return {
            "center": center,
            "radius": radius,
            "explanation": f"The circle passing through points {p1}, {p2}, {p3} has center at {center} and radius {radius}"
        }
    except Exception as e:
        raise ToolException(f"Error determining circle from three points: {str(e)}")

def calculate_circle_from_center_and_point_wrapper(center: List[float], point: List[float]) -> dict:
    """
    Wrapper function for calculating a circle from center and a point on the circle
    
    Args:
        center: Coordinates of the circle center [x, y]
        point: Coordinates of a point on the circle [x, y]
        
    Returns:
        Result of circle calculation with explanation
    """
    try:
        center_tuple = tuple(center)
        point_tuple = tuple(point)
        
        center_result, radius = CircleTools.calculate_circle_from_center_and_point(center_tuple, point_tuple)
        
        return {
            "center": center_result,
            "radius": radius,
            "explanation": f"The circle with center at {center_tuple} passing through point {point_tuple} has radius {radius}"
        }
    except Exception as e:
        raise ToolException(f"Error determining circle from center and point: {str(e)}")

def calculate_central_angle_wrapper(center: List[float], point1: List[float], point2: List[float]) -> dict:
    """
    Wrapper function for calculating the central angle formed by two points on a circle
    
    Args:
        center: Coordinates of the circle center [x, y]
        point1: Coordinates of the first point on the circle [x, y]
        point2: Coordinates of the second point on the circle [x, y]
        
    Returns:
        Result of central angle calculation with explanation
    """
    try:
        center_tuple = tuple(center)
        p1_tuple = tuple(point1)
        p2_tuple = tuple(point2)
        
        central_angle = CircleTools.calculate_central_angle(center_tuple, p1_tuple, p2_tuple)
        
        # Convert to degrees for explanation
        angle_degrees = central_angle * 180 / 3.14159
        
        return {
            "central_angle": central_angle,
            "central_angle_degrees": angle_degrees,
            "explanation": f"The central angle formed by points {p1_tuple} and {p2_tuple} from center {center_tuple} is {central_angle} radians (approximately {angle_degrees:.2f} degrees)"
        }
    except Exception as e:
        raise ToolException(f"Error calculating central angle: {str(e)}")

def calculate_inscribed_angle_wrapper(center: List[float], point1: List[float], point2: List[float], point3: List[float]) -> dict:
    """
    Wrapper function for calculating the inscribed angle in a circle
    
    Args:
        center: Coordinates of the circle center [x, y]
        point1: Coordinates of the first point on the circle [x, y]
        point2: Coordinates of the vertex point on the circle [x, y]
        point3: Coordinates of the third point on the circle [x, y]
        
    Returns:
        Result of inscribed angle calculation with explanation
    """
    try:
        center_tuple = tuple(center)
        p1_tuple = tuple(point1)
        p2_tuple = tuple(point2)
        p3_tuple = tuple(point3)
        
        inscribed_angle = CircleTools.calculate_inscribed_angle(center_tuple, p1_tuple, p2_tuple, p3_tuple)
        
        # Convert to degrees for explanation
        angle_degrees = inscribed_angle * 180 / 3.14159
        
        return {
            "inscribed_angle": inscribed_angle,
            "inscribed_angle_degrees": angle_degrees,
            "explanation": f"The inscribed angle formed by points {p1_tuple}, {p2_tuple} (vertex), and {p3_tuple} on the circle (center {center_tuple}) is {inscribed_angle} radians (approximately {angle_degrees:.2f} degrees)"
        }
    except Exception as e:
        raise ToolException(f"Error calculating inscribed angle: {str(e)}")

def calculate_power_of_point_wrapper(point: List[float], center: List[float], radius: float) -> dict:
    """
    Wrapper function for calculating the power of a point with respect to a circle
    
    Args:
        point: Coordinates of the point [x, y]
        center: Coordinates of the circle center [x, y]
        radius: Radius of the circle
        
    Returns:
        Result of power of point calculation with explanation
    """
    try:
        point_tuple = tuple(point)
        center_tuple = tuple(center)
        
        power = CircleTools.calculate_power_of_point(point_tuple, center_tuple, radius)
        
        return {
            "power": power,
            "explanation": f"The power of point {point_tuple} with respect to the circle (center {center_tuple}, radius {radius}) is {power}"
        }
    except Exception as e:
        raise ToolException(f"Error calculating power of point: {str(e)}") 