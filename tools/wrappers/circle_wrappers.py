"""
원 계산 래퍼 함수 모듈

이 모듈은 원 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from tools.circle_tools import CircleTools

def calculate_circle_area_wrapper(input_data: dict) -> dict:
    """
    원의 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        원의 면적 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        area = CircleTools.calculate_area(radius)
        return {
            "area": area,
            "area_explanation": f"半径为 {radius} 的圆的面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的面积时出错：{str(e)}")

def calculate_circle_circumference_wrapper(input_data: dict) -> dict:
    """
    원의 둘레를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        원의 둘레 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        circumference = CircleTools.calculate_circumference(radius)
        return {
            "circumference": circumference,
            "circumference_explanation": f"半径为 {radius} 的圆的周长是 {circumference}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的周长时出错：{str(e)}")

def calculate_circle_diameter_wrapper(input_data: dict) -> dict:
    """
    원의 지름을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        원의 지름 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        diameter = radius * 2
        return {
            "diameter": diameter,
            "diameter_explanation": f"半径为 {radius} 的圆的直径是 {diameter}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的直径时出错：{str(e)}")

def calculate_circle_radius_wrapper(input_data: dict) -> dict:
    """
    원의 반지름을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        원의 반지름 계산 결과와 설명
    """
    try:
        diameter = input_data["diameter"]
        radius = diameter / 2
        return {
            "radius": radius,
            "radius_explanation": f"直径为 {diameter} 的圆的半径是 {radius}"
        }
    except Exception as e:
        raise ToolException(f"计算圆的半径时出错：{str(e)}")

def calculate_circle_wrapper(input_data: dict) -> dict:
    """
    원 계산 도구 메인 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        원 계산 결과와 설명
    """
    try:
        result = {}
        
        # 반지름이 주어진 경우
        if "radius" in input_data and input_data["radius"] is not None:
            radius = input_data["radius"]
            
            # 면적 계산
            area = CircleTools.calculate_area(radius)
            result["area"] = area
            result["area_explanation"] = f"半径为 {radius} 的圆的面积是 {area}"
            
            # 둘레 계산
            circumference = CircleTools.calculate_circumference(radius)
            result["circumference"] = circumference
            result["circumference_explanation"] = f"半径为 {radius} 的圆的周长是 {circumference}"
            
            # 지름 계산
            diameter = radius * 2
            result["diameter"] = diameter
            result["diameter_explanation"] = f"半径为 {radius} 的圆的直径是 {diameter}"
        
        # 지름이 주어진 경우
        elif "diameter" in input_data and input_data["diameter"] is not None:
            diameter = input_data["diameter"]
            radius = diameter / 2
            
            # 면적 계산
            area = CircleTools.calculate_area(radius)
            result["area"] = area
            result["area_explanation"] = f"直径为 {diameter} 的圆的面积是 {area}"
            
            # 둘레 계산
            circumference = CircleTools.calculate_circumference(radius)
            result["circumference"] = circumference
            result["circumference_explanation"] = f"直径为 {diameter} 的圆的周长是 {circumference}"
            
            # 반지름 계산
            result["radius"] = radius
            result["radius_explanation"] = f"直径为 {diameter} 的圆的半径是 {radius}"
        
        else:
            raise ToolException("请提供圆的半径或直径")
        
        return result
    except ToolException as e:
        raise ToolException(str(e))
    except Exception as e:
        raise ToolException(f"计算圆时出错：{str(e)}")

def calculate_chord_length_wrapper(input_data: dict) -> dict:
    """
    현의 길이를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        현의 길이 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        chord_length = CircleTools.calculate_chord_length(radius, angle)
        return {
            "chord_length": chord_length,
            "chord_length_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的弦长是 {chord_length}"
        }
    except Exception as e:
        raise ToolException(f"计算弦长时出错：{str(e)}")

def calculate_sector_area_wrapper(input_data: dict) -> dict:
    """
    부채꼴의 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        부채꼴 면적 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        sector_area = CircleTools.calculate_sector_area(radius, angle)
        return {
            "sector_area": sector_area,
            "sector_area_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的扇形面积是 {sector_area}"
        }
    except Exception as e:
        raise ToolException(f"计算扇形面积时出错：{str(e)}")

def calculate_segment_area_wrapper(input_data: dict) -> dict:
    """
    활꼴의 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        활꼴 면적 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        segment_area = CircleTools.calculate_segment_area(radius, angle)
        return {
            "segment_area": segment_area,
            "segment_area_explanation": f"半径为 {radius}，圆心角为 {angle} 弧度的弓形面积是 {segment_area}"
        }
    except Exception as e:
        raise ToolException(f"计算弓形面积时出错：{str(e)}")

def check_point_circle_position_wrapper(input_data: dict) -> dict:
    """
    점과 원의 위치 관계를 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        위치 관계 확인 결과와 설명
    """
    try:
        center = tuple(input_data["center"])
        radius = input_data["radius"]
        point = tuple(input_data["point"])
        
        is_inside = CircleTools.is_point_inside_circle(center, radius, point)
        is_on = CircleTools.is_point_on_circle(center, radius, point)
        
        if is_on:
            return {
                "position": "on",
                "position_explanation": f"点 {point} 在圆上"
            }
        elif is_inside:
            return {
                "position": "inside",
                "position_explanation": f"点 {point} 在圆内"
            }
        else:
            return {
                "position": "outside",
                "position_explanation": f"点 {point} 在圆外"
            }
    except Exception as e:
        raise ToolException(f"判断点与圆位置关系时出错：{str(e)}")

def calculate_tangent_points_wrapper(input_data: dict) -> dict:
    """
    외부 점에서 원에 그은 접선의 접점을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        접점 계산 결과와 설명
    """
    try:
        center = tuple(input_data["center"])
        radius = input_data["radius"]
        external_point = tuple(input_data["external_point"])
        
        tangent_points = CircleTools.calculate_tangent_point(center, radius, external_point)
        
        if not tangent_points:
            return {
                "tangent_points": [],
                "tangent_explanation": f"点 {external_point} 在圆内，无法计算切点"
            }
        elif len(tangent_points) == 1:
            return {
                "tangent_points": tangent_points,
                "tangent_explanation": f"点 {external_point} 在圆上，切点就是该点 {tangent_points[0]}"
            }
        else:
            return {
                "tangent_points": tangent_points,
                "tangent_explanation": f"从点 {external_point} 到圆的切点是 {tangent_points[0]} 和 {tangent_points[1]}"
            }
    except Exception as e:
        raise ToolException(f"计算切点时出错：{str(e)}")

def calculate_circle_intersection_wrapper(input_data: dict) -> dict:
    """
    두 원의 교점을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        교점 계산 결과와 설명
    """
    try:
        center1 = tuple(input_data["center1"])
        radius1 = input_data["radius1"]
        center2 = tuple(input_data["center2"])
        radius2 = input_data["radius2"]
        
        intersection_points = CircleTools.calculate_circle_intersection(center1, radius1, center2, radius2)
        
        if not intersection_points:
            return {
                "intersection_points": [],
                "intersection_explanation": f"两个圆没有交点，可能是两圆相离或者重合"
            }
        elif len(intersection_points) == 1:
            return {
                "intersection_points": intersection_points,
                "intersection_explanation": f"两个圆相切，交点是 {intersection_points[0]}"
            }
        else:
            return {
                "intersection_points": intersection_points,
                "intersection_explanation": f"两个圆相交，交点是 {intersection_points[0]} 和 {intersection_points[1]}"
            }
    except Exception as e:
        raise ToolException(f"计算圆的交点时出错：{str(e)}")

def calculate_circle_from_three_points_wrapper(input_data: dict) -> dict:
    """
    세 점으로부터 원을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        원 계산 결과와 설명
    """
    try:
        points = [tuple(p) for p in input_data["points"]]
        if len(points) != 3:
            raise ToolException("需要提供恰好三个点的坐标")
            
        center, radius = CircleTools.calculate_circle_from_three_points(points[0], points[1], points[2])
        
        if radius == 0:
            raise ToolException("无法通过给定的三点确定一个圆，这些点可能共线")
            
        return {
            "center": center,
            "radius": radius,
            "circle_explanation": f"通过点 {points[0]}、{points[1]} 和 {points[2]} 确定的圆的中心是 {center}，半径是 {radius}"
        }
    except ToolException as e:
        raise ToolException(str(e))
    except Exception as e:
        raise ToolException(f"通过三点计算圆时出错：{str(e)}") 