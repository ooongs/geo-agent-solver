"""
길이 계산 래퍼 함수 모듈

이 모듈은 길이 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import LengthTools

def calculate_distance_points_wrapper(point1: List[float], point2: List[float]) -> dict:
    """
    두 점 사이의 거리를 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점의 좌표 [x1, y1]
        point2: 두 번째 점의 좌표 [x2, y2]
        
    Returns:
        거리 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        distance = LengthTools.calculate_distance_between_points(p1, p2)
        return {
            "distance": distance,
            "distance_explanation": f"点 {p1} 和 {p2} 之间的距离是 {distance}"
        }
    except Exception as e:
        raise ToolException(f"计算两点距离时出错：{str(e)}")

def calculate_distance_point_to_line_wrapper(point: List[float], line: List[float]) -> dict:
    """
    점과 직선 사이의 거리를 계산하는 래퍼 함수
    
    Args:
        point: 점의 좌표 [x, y]
        line: 직선의 파라미터 [a, b, c], ax + by + c = 0
        
    Returns:
        거리 계산 결과와 설명
    """
    try:
        point_tuple = tuple(point)
        line_tuple = tuple(line)
        distance = LengthTools.calculate_distance_point_to_line(point_tuple, line_tuple)
        return {
            "distance": distance,
            "distance_explanation": f"点 {point_tuple} 到直线 {line_tuple} 的距离是 {distance}"
        }
    except Exception as e:
        raise ToolException(f"计算点到直线距离时出错：{str(e)}")

def calculate_distance_parallel_lines_wrapper(line1: List[float], line2: List[float]) -> dict:
    """
    두 평행선 사이의 거리를 계산하는 래퍼 함수
    
    Args:
        line1: 첫 번째 직선의 파라미터 [a1, b1, c1], a1x + b1y + c1 = 0
        line2: 두 번째 직선의 파라미터 [a2, b2, c2], a2x + b2y + c2 = 0
        
    Returns:
        거리 계산 결과와 설명
    """
    try:
        line1_tuple = tuple(line1)
        line2_tuple = tuple(line2)
        distance = LengthTools.calculate_distance_between_parallel_lines(line1_tuple, line2_tuple)
        if distance == float('inf'):
            return {
                "distance": "无穷大",
                "distance_explanation": f"直线 {line1_tuple} 和 {line2_tuple} 不平行，无法计算距离"
            }
        return {
            "distance": distance,
            "distance_explanation": f"平行直线 {line1_tuple} 和 {line2_tuple} 之间的距离是 {distance}"
        }
    except Exception as e:
        raise ToolException(f"计算平行线距离时出错：{str(e)}")

def calculate_perimeter_triangle_wrapper(points: List[List[float]]) -> dict:
    """
    삼각형 둘레를 계산하는 래퍼 함수
    
    Args:
        points: 삼각형 세 꼭짓점의 좌표, 형식은 [[x1,y1], [x2,y2], [x3,y3]]
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        points_tuple = [tuple(p) for p in points]
        if len(points_tuple) != 3:
            raise ToolException("三角形需要精确的3个顶点")
        perimeter = LengthTools.calculate_perimeter_triangle(points_tuple)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"三角形 {points_tuple} 的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形周长时出错：{str(e)}")

def calculate_perimeter_quadrilateral_wrapper(points: List[List[float]]) -> dict:
    """
    사각형 둘레를 계산하는 래퍼 함수
    
    Args:
        points: 사각형 네 꼭짓점의 좌표, 형식은 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        points_tuple = [tuple(p) for p in points]
        if len(points_tuple) != 4:
            raise ToolException("四边形需要精确的4个顶点")
        perimeter = LengthTools.calculate_perimeter_quadrilateral(points_tuple)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"四边形 {points_tuple} 的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算四边形周长时出错：{str(e)}")

def calculate_perimeter_polygon_wrapper(points: List[List[float]]) -> dict:
    """
    다각형 둘레를 계산하는 래퍼 함수
    
    Args:
        points: 다각형 꼭짓점의 좌표, 형식은 [[x1,y1], [x2,y2], ...]
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        points_tuple = [tuple(p) for p in points]
        if len(points_tuple) < 3:
            raise ToolException("多边形至少需要3个顶点")
        perimeter = LengthTools.calculate_perimeter_polygon(points_tuple)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"{len(points_tuple)}边形的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算多边形周长时出错：{str(e)}")

def calculate_circumference_wrapper(radius: float) -> dict:
    """
    원 둘레를 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        if radius <= 0:
            raise ToolException("圆的半径必须为正数")
        circumference = LengthTools.calculate_circumference(radius)
        return {
            "circumference": circumference,
            "circumference_explanation": f"半径为 {radius} 的圆的周长是 {circumference}"
        }
    except Exception as e:
        raise ToolException(f"计算圆周长时出错：{str(e)}")

def calculate_chord_length_wrapper(radius: float, angle: float, degrees: bool = False) -> dict:
    """
    현의 길이를 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 원심각(라디안 또는 각도)
        degrees: 각도가 도 단위인지 여부, True는 도, False는 라디안
        
    Returns:
        현 길이 계산 결과와 설명
    """
    try:
        if degrees:
            angle = LengthTools.degrees_to_radians(angle)
        
        if radius <= 0:
            raise ToolException("圆的半径必须为正数")
            
        chord_length = LengthTools.calculate_chord_length(radius, angle)
        return {
            "chord_length": chord_length,
            "chord_length_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的弦长是 {chord_length}"
        }
    except Exception as e:
        raise ToolException(f"计算弦长时出错：{str(e)}")

def calculate_arc_length_wrapper(radius: float, angle: float, degrees: bool = False) -> dict:
    """
    호의 길이를 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 원심각(라디안 또는 각도)
        degrees: 각도가 도 단위인지 여부, True는 도, False는 라디안
        
    Returns:
        호 길이 계산 결과와 설명
    """
    try:
        if degrees:
            angle = LengthTools.degrees_to_radians(angle)
        
        if radius <= 0:
            raise ToolException("圆的半径必须为正数")
            
        arc_length = LengthTools.calculate_arc_length(radius, angle)
        return {
            "arc_length": arc_length,
            "arc_length_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的弧长是 {arc_length}"
        }
    except Exception as e:
        raise ToolException(f"计算弧长时出错：{str(e)}") 