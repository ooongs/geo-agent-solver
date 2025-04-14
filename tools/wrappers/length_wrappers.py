"""
길이 계산 래퍼 함수 모듈

이 모듈은 길이 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from tools.length_tools import LengthTools

def calculate_distance_points_wrapper(input_data: dict) -> dict:
    """
    두 점 사이의 거리를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        거리 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        distance = LengthTools.calculate_distance_between_points(p1, p2)
        return {
            "distance": distance,
            "distance_explanation": f"点 {p1} 和 {p2} 之间的距离是 {distance}"
        }
    except Exception as e:
        raise ToolException(f"计算两点距离时出错：{str(e)}")

def calculate_distance_point_to_line_wrapper(input_data: dict) -> dict:
    """
    점과 직선 사이의 거리를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        거리 계산 결과와 설명
    """
    try:
        point = tuple(input_data["point"])
        line = tuple(input_data["line"])
        distance = LengthTools.calculate_distance_point_to_line(point, line)
        return {
            "distance": distance,
            "distance_explanation": f"点 {point} 到直线 {line} 的距离是 {distance}"
        }
    except Exception as e:
        raise ToolException(f"计算点到直线距离时出错：{str(e)}")

def calculate_distance_parallel_lines_wrapper(input_data: dict) -> dict:
    """
    두 평행선 사이의 거리를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        거리 계산 결과와 설명
    """
    try:
        line1 = tuple(input_data["line1"])
        line2 = tuple(input_data["line2"])
        distance = LengthTools.calculate_distance_between_parallel_lines(line1, line2)
        if distance == float('inf'):
            return {
                "distance": "无穷大",
                "distance_explanation": f"直线 {line1} 和 {line2} 不平行，无法计算距离"
            }
        return {
            "distance": distance,
            "distance_explanation": f"平行直线 {line1} 和 {line2} 之间的距离是 {distance}"
        }
    except Exception as e:
        raise ToolException(f"计算平行线距离时出错：{str(e)}")

def calculate_perimeter_triangle_wrapper(input_data: dict) -> dict:
    """
    삼각형 둘레를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        points = [tuple(p) for p in input_data["points"]]
        if len(points) != 3:
            raise ToolException("三角形需要精确的3个顶点")
        perimeter = LengthTools.calculate_perimeter_triangle(points)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"三角形 {points} 的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形周长时出错：{str(e)}")

def calculate_perimeter_quadrilateral_wrapper(input_data: dict) -> dict:
    """
    사각형 둘레를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        points = [tuple(p) for p in input_data["points"]]
        if len(points) != 4:
            raise ToolException("四边形需要精确的4个顶点")
        perimeter = LengthTools.calculate_perimeter_quadrilateral(points)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"四边形 {points} 的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算四边形周长时出错：{str(e)}")

def calculate_perimeter_polygon_wrapper(input_data: dict) -> dict:
    """
    다각형 둘레를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        points = [tuple(p) for p in input_data["points"]]
        if len(points) < 3:
            raise ToolException("多边形至少需要3个顶点")
        perimeter = LengthTools.calculate_perimeter_polygon(points)
        return {
            "perimeter": perimeter,
            "perimeter_explanation": f"{len(points)}边形的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算多边形周长时出错：{str(e)}")

def calculate_circumference_wrapper(input_data: dict) -> dict:
    """
    원 둘레를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        if radius <= 0:
            raise ToolException("圆的半径必须为正数")
        circumference = LengthTools.calculate_circumference(radius)
        return {
            "circumference": circumference,
            "circumference_explanation": f"半径为 {radius} 的圆的周长是 {circumference}"
        }
    except Exception as e:
        raise ToolException(f"计算圆周长时出错：{str(e)}")

def calculate_chord_length_wrapper(input_data: dict) -> dict:
    """
    현의 길이를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        현 길이 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        if "degrees" in input_data and input_data["degrees"]:
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

def calculate_arc_length_wrapper(input_data: dict) -> dict:
    """
    호의 길이를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        호 길이 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        if "degrees" in input_data and input_data["degrees"]:
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

def calculate_midpoint_wrapper(input_data: dict) -> dict:
    """
    두 점의 중점을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        중점 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        midpoint = LengthTools.calculate_midpoint(p1, p2)
        return {
            "midpoint": midpoint,
            "midpoint_explanation": f"点 {p1} 和 {p2} 的中点是 {midpoint}"
        }
    except Exception as e:
        raise ToolException(f"计算中点时出错：{str(e)}")

def calculate_segment_division_wrapper(input_data: dict) -> dict:
    """
    선분 분할점을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        분할점 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        ratio = input_data["ratio"]
        division_point = LengthTools.calculate_segment_division(p1, p2, ratio)
        return {
            "division_point": division_point,
            "division_explanation": f"线段 {p1} 到 {p2} 按比例 {ratio} 分割的点是 {division_point}"
        }
    except Exception as e:
        raise ToolException(f"计算分割点时出错：{str(e)}")

def calculate_internal_division_point_wrapper(input_data: dict) -> dict:
    """
    내분점을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        내분점 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        m = input_data["m"]
        n = input_data["n"]
        
        if m <= 0 or n <= 0:
            raise ToolException("内分比的两个数值必须为正数")
            
        division_point = LengthTools.calculate_internal_division_point(p1, p2, m, n)
        return {
            "internal_division_point": division_point,
            "division_explanation": f"线段 {p1} 到 {p2} 的内分点（比例 {m}:{n}）是 {division_point}"
        }
    except Exception as e:
        raise ToolException(f"计算内分点时出错：{str(e)}")

def calculate_external_division_point_wrapper(input_data: dict) -> dict:
    """
    외분점을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        외분점 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        m = input_data["m"]
        n = input_data["n"]
        
        if m <= 0 or n <= 0 or m == n:
            raise ToolException("外分比的两个数值必须为正数且不相等")
            
        division_point = LengthTools.calculate_external_division_point(p1, p2, m, n)
        return {
            "external_division_point": division_point,
            "division_explanation": f"线段 {p1} 到 {p2} 的外分点（比例 {m}:{n}）是 {division_point}"
        }
    except Exception as e:
        raise ToolException(f"计算外分点时出错：{str(e)}")

def is_point_on_segment_wrapper(input_data: dict) -> dict:
    """
    점이 선분 위에 있는지 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        확인 결과와 설명
    """
    try:
        point = tuple(input_data["point"])
        p1 = tuple(input_data["segment_start"])
        p2 = tuple(input_data["segment_end"])
        
        is_on_segment = LengthTools.is_point_on_segment(point, p1, p2)
        if is_on_segment:
            return {
                "is_on_segment": True,
                "explanation": f"点 {point} 在线段 {p1} 到 {p2} 上"
            }
        else:
            return {
                "is_on_segment": False,
                "explanation": f"点 {point} 不在线段 {p1} 到 {p2} 上"
            }
    except Exception as e:
        raise ToolException(f"判断点是否在线段上时出错：{str(e)}") 