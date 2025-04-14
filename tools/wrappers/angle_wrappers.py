"""
각도 계산 래퍼 함수 모듈

이 모듈은 각도 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from tools.angle_tools import AngleTools

def calculate_angle_three_points_wrapper(input_data: dict) -> dict:
    """
    세 점으로 이루어진 각도를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])  # 각의 꼭지점
        p3 = tuple(input_data["point3"])
        
        angle_rad = AngleTools.calculate_angle_three_points(p1, p2, p3)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"点 {p1}、{p2}（角的顶点）和 {p3} 形成的角度是 {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三点角度时出错：{str(e)}")

def calculate_angle_two_lines_wrapper(input_data: dict) -> dict:
    """
    두 직선 사이의 각도를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        line1 = tuple(input_data["line1"])
        line2 = tuple(input_data["line2"])
        
        angle_rad = AngleTools.calculate_angle_two_lines(line1, line2)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"直线 {line1} 和 {line2} 之间的角度是 {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算两直线角度时出错：{str(e)}")

def calculate_angle_two_vectors_wrapper(input_data: dict) -> dict:
    """
    두 벡터 사이의 각도를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        v1 = tuple(input_data["vector1"])
        v2 = tuple(input_data["vector2"])
        
        angle_rad = AngleTools.calculate_angle_two_vectors(v1, v2)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"向量 {v1} 和 {v2} 之间的角度是 {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算两向量角度时出错：{str(e)}")

def calculate_interior_angles_triangle_wrapper(input_data: dict) -> dict:
    """
    삼각형 내각을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        내각 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("必须提供三角形的三个顶点")
            
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertices)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"三角形内角分别是 {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三角形内角时出错：{str(e)}")

def calculate_exterior_angles_triangle_wrapper(input_data: dict) -> dict:
    """
    삼각형 외각을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        외각 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("必须提供三角形的三个顶点")
            
        angles_rad = AngleTools.calculate_exterior_angles_triangle(vertices)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"三角形外角分别是 {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三角形外角时出错：{str(e)}")

def calculate_inscribed_angle_wrapper(input_data: dict) -> dict:
    """
    원에서의 내접각을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        내접각 계산 결과와 설명
    """
    try:
        center = tuple(input_data["center"])
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        
        inscribed_angle_rad = AngleTools.calculate_inscribed_angle(center, p1, p2)
        inscribed_angle_deg = AngleTools.radians_to_degrees(inscribed_angle_rad)
        central_angle_rad = 2 * inscribed_angle_rad
        central_angle_deg = AngleTools.radians_to_degrees(central_angle_rad)
        
        return {
            "inscribed_angle_rad": inscribed_angle_rad,
            "inscribed_angle_deg": inscribed_angle_deg,
            "central_angle_rad": central_angle_rad,
            "central_angle_deg": central_angle_deg,
            "explanation": f"圆心为 {center}，点 {p1} 和 {p2} 形成的内接角是 {inscribed_angle_deg:.2f}°，对应的圆心角是 {central_angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算内接角时出错：{str(e)}")

def calculate_angle_bisector_wrapper(input_data: dict) -> dict:
    """
    두 점을 향하는 각의 이등분선을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        이등분선 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])  # 각의 꼭지점
        p3 = tuple(input_data["point3"])
        
        bisector = AngleTools.calculate_angle_bisector(p1, p2, p3)
        
        return {
            "angle_bisector": bisector,
            "explanation": f"点 {p1}、{p2}（角的顶点）和 {p3} 形成的角的角平分线方程是 {bisector[0]}x + {bisector[1]}y + {bisector[2]} = 0"
        }
    except Exception as e:
        raise ToolException(f"计算角平分线时出错：{str(e)}")

def triangle_angle_classification_wrapper(input_data: dict) -> dict:
    """
    삼각형 각도 분류를 수행하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        삼각형 분류 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("必须提供三角形的三个顶点")
            
        is_acute = AngleTools.is_triangle_acute(vertices)
        is_right = AngleTools.is_triangle_right(vertices)
        is_obtuse = AngleTools.is_triangle_obtuse(vertices)
        
        if is_acute:
            triangle_type = "锐角三角形"
        elif is_right:
            triangle_type = "直角三角形"
        elif is_obtuse:
            triangle_type = "钝角三角形"
        else:
            triangle_type = "无法分类"
        
        return {
            "is_acute_triangle": is_acute,
            "is_right_triangle": is_right,
            "is_obtuse_triangle": is_obtuse,
            "triangle_type": triangle_type,
            "explanation": f"该三角形是{triangle_type}"
        }
    except Exception as e:
        raise ToolException(f"分类三角形时出错：{str(e)}")

def angle_classification_wrapper(input_data: dict) -> dict:
    """
    각도 분류를 수행하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        각도 분류 결과와 설명
    """
    try:
        if "angle_rad" in input_data:
            angle_rad = input_data["angle_rad"]
        elif "angle_deg" in input_data:
            angle_rad = AngleTools.degrees_to_radians(input_data["angle_deg"])
        else:
            raise ToolException("必须提供角度值（弧度或度）")
            
        is_acute = AngleTools.is_angle_acute(angle_rad)
        is_right = AngleTools.is_angle_right(angle_rad)
        is_obtuse = AngleTools.is_angle_obtuse(angle_rad)
        
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        if is_acute:
            angle_type = "锐角"
        elif is_right:
            angle_type = "直角"
        elif is_obtuse:
            angle_type = "钝角"
        else:
            angle_type = "其他类型的角"
        
        return {
            "is_acute": is_acute,
            "is_right": is_right,
            "is_obtuse": is_obtuse,
            "angle_type": angle_type,
            "explanation": f"{angle_deg:.2f}° 是{angle_type}"
        }
    except Exception as e:
        raise ToolException(f"分类角度时出错：{str(e)}") 