"""
원 계산 래퍼 함수 모듈

이 모듈은 원 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import CircleTools

def calculate_circle_area_wrapper(radius: float) -> dict:
    """
    원의 면적을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        
    Returns:
        원의 면적 계산 결과와 설명
    """
    try:
        area = CircleTools.calculate_area(radius)
        return {
            "area": area,
            "area_explanation": f"半径为 {radius} 的圆的面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的面积时出错：{str(e)}")

def calculate_circle_circumference_wrapper(radius: float) -> dict:
    """
    원의 둘레를 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        
    Returns:
        원의 둘레 계산 결과와 설명
    """
    try:
        circumference = CircleTools.calculate_circumference(radius)
        return {
            "circumference": circumference,
            "circumference_explanation": f"半径为 {radius} 的圆的周长是 {circumference}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的周长时出错：{str(e)}")

def calculate_circle_diameter_wrapper(radius: float) -> dict:
    """
    원의 지름을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        
    Returns:
        원의 지름 계산 결과와 설명
    """
    try:
        diameter = radius * 2
        return {
            "diameter": diameter,
            "diameter_explanation": f"半径为 {radius} 的圆的直径是 {diameter}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的直径时出错：{str(e)}")

def calculate_circle_radius_wrapper(diameter: float) -> dict:
    """
    원의 반지름을 계산하는 래퍼 함수
    
    Args:
        diameter: 원의 지름
        
    Returns:
        원의 반지름 계산 결과와 설명
    """
    try:
        radius = diameter / 2
        return {
            "radius": radius,
            "radius_explanation": f"直径为 {diameter} 的圆的半径是 {radius}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的半径时出错：{str(e)}")


def calculate_chord_length_wrapper(radius: float, angle: float) -> dict:
    """
    현의 길이를 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 중심각 (라디안)
        
    Returns:
        현의 길이 계산 결과와 설명
    """
    try:
        chord_length = CircleTools.calculate_chord_length(radius, angle)
        return {
            "chord_length": chord_length,
            "chord_length_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的弦长是 {chord_length}"
        }
    except Exception as e:
        raise ToolException(f"计算弦长时出错：{str(e)}")

def calculate_sector_area_wrapper(radius: float, angle: float) -> dict:
    """
    부채꼴의 면적을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 중심각 (라디안)
        
    Returns:
        부채꼴 면적 계산 결과와 설명
    """
    try:
        sector_area = CircleTools.calculate_sector_area(radius, angle)
        return {
            "sector_area": sector_area,
            "sector_area_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的扇形面积是 {sector_area}"
        }
    except Exception as e:
        raise ToolException(f"计算扇形面积时出错：{str(e)}")

def calculate_segment_area_wrapper(radius: float, angle: float) -> dict:
    """
    활꼴의 면적을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 중심각 (라디안)
        
    Returns:
        활꼴 면적 계산 결과와 설명
    """
    try:
        segment_area = CircleTools.calculate_segment_area(radius, angle)
        return {
            "segment_area": segment_area,
            "segment_area_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的弓形面积是 {segment_area}"
        }
    except Exception as e:
        raise ToolException(f"计算弓形面积时出错：{str(e)}")

def check_point_circle_position_wrapper(center: List[float], radius: float, point: List[float]) -> dict:
    """
    점과 원의 위치 관계를 확인하는 래퍼 함수
    
    Args:
        center: 원의 중심 좌표 [x, y]
        radius: 원의 반지름
        point: 점의 좌표 [x, y]
        
    Returns:
        위치 관계 확인 결과와 설명
    """
    try:
        center_tuple = tuple(center)
        point_tuple = tuple(point)
        position = CircleTools.check_point_circle_position(center_tuple, radius, point_tuple)
        
        if position == "inside":
            explanation = f"点 {point_tuple} 在圆 (圆心 {center_tuple}, 半径 {radius}) 内部"
        elif position == "on":
            explanation = f"点 {point_tuple} 在圆 (圆心 {center_tuple}, 半径 {radius}) 上"
        else:  # position == "outside"
            explanation = f"点 {point_tuple} 在圆 (圆心 {center_tuple}, 半径 {radius}) 外部"
            
        # 거리 계산
        distance = CircleTools.calculate_distance(center_tuple, point_tuple)
        distance_info = f"点到圆心的距离是 {distance}，半径是 {radius}"
            
        return {
            "position": position,
            "distance": distance,
            "explanation": f"{explanation}。{distance_info}"
        }
    except Exception as e:
        raise ToolException(f"检查点与圆的位置关系时出错：{str(e)}")

def calculate_tangent_points_wrapper(center: List[float], radius: float, point: List[float]) -> dict:
    """
    외부 점에서 원에 그은 접선의 접점을 계산하는 래퍼 함수
    
    Args:
        center: 원의 중심 좌표 [x, y]
        radius: 원의 반지름
        point: 외부 점의 좌표 [x, y]
        
    Returns:
        접점 계산 결과와 설명
    """
    try:
        center_tuple = tuple(center)
        point_tuple = tuple(point)
        
        # 외부 점인지 확인
        position = CircleTools.check_point_circle_position(center_tuple, radius, point_tuple)
        if position != "outside":
            raise ToolException(f"点 {point_tuple} 不在圆 (圆心 {center_tuple}, 半径 {radius}) 的外部，无法计算切点")
            
        tangent_points = CircleTools.calculate_tangent_points(center_tuple, radius, point_tuple)
        
        return {
            "tangent_points": tangent_points,
            "explanation": f"从点 {point_tuple} 到圆 (圆心 {center_tuple}, 半径 {radius}) 的切点是 {tangent_points[0]} 和 {tangent_points[1]}"
        }
    except Exception as e:
        raise ToolException(f"计算切点时出错：{str(e)}")

def calculate_circle_intersection_wrapper(center1: List[float], radius1: float, center2: List[float], radius2: float) -> dict:
    """
    두 원의 교점을 계산하는 래퍼 함수
    
    Args:
        center1: 첫 번째 원의 중심 좌표 [x1, y1]
        radius1: 첫 번째 원의 반지름
        center2: 두 번째 원의 중심 좌표 [x2, y2]
        radius2: 두 번째 원의 반지름
        
    Returns:
        교점 계산 결과와 설명
    """
    try:
        center1_tuple = tuple(center1)
        center2_tuple = tuple(center2)
        
        intersection_points = CircleTools.calculate_circle_intersection(center1_tuple, radius1, center2_tuple, radius2)
        
        if not intersection_points:
            explanation = f"圆 (圆心 {center1_tuple}, 半径 {radius1}) 和圆 (圆心 {center2_tuple}, 半径 {radius2}) 没有交点"
        elif len(intersection_points) == 1:
            explanation = f"圆 (圆心 {center1_tuple}, 半径 {radius1}) 和圆 (圆心 {center2_tuple}, 半径 {radius2}) 相切于点 {intersection_points[0]}"
        else:  # len(intersection_points) == 2
            explanation = f"圆 (圆心 {center1_tuple}, 半径 {radius1}) 和圆 (圆心 {center2_tuple}, 半径 {radius2}) 相交于点 {intersection_points[0]} 和 {intersection_points[1]}"
            
        return {
            "intersection_points": intersection_points,
            "explanation": explanation
        }
    except Exception as e:
        raise ToolException(f"计算两圆交点时出错：{str(e)}")

def calculate_circle_from_three_points_wrapper(point1: List[float], point2: List[float], point3: List[float]) -> dict:
    """
    세 점을 지나는 원을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점의 좌표 [x1, y1]
        point2: 두 번째 점의 좌표 [x2, y2]
        point3: 세 번째 점의 좌표 [x3, y3]
        
    Returns:
        원 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        p3 = tuple(point3)
        
        center, radius = CircleTools.calculate_circle_from_three_points(p1, p2, p3)
        
        if center is None:
            raise ToolException(f"点 {p1}, {p2}, {p3} 共线，无法确定一个唯一的圆")
            
        return {
            "center": center,
            "radius": radius,
            "explanation": f"过点 {p1}, {p2}, {p3} 的圆的圆心是 {center}，半径是 {radius}"
        }
    except Exception as e:
        raise ToolException(f"从三点确定圆时出错：{str(e)}") 