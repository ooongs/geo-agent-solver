"""
면적 계산 래퍼 함수 모듈

이 모듈은 면적 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from tools.area_tools import AreaTools

def calculate_area_triangle_wrapper(input_data: dict) -> dict:
    """
    삼각형 면적을 계산하는 래퍼 함수 (좌표 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        area = AreaTools.calculate_area_triangle(vertices)
        
        return {
            "area": area,
            "explanation": f"三角形 {vertices} 的面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_triangle_from_sides_wrapper(input_data: dict) -> dict:
    """
    삼각형 면적을 계산하는 래퍼 함수 (세 변의 길이 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        a = input_data["a"]
        b = input_data["b"]
        c = input_data["c"]
        
        area = AreaTools.calculate_area_triangle_from_sides(a, b, c)
        
        return {
            "area": area,
            "explanation": f"边长为 {a}, {b}, {c} 的三角形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_triangle_from_base_height_wrapper(input_data: dict) -> dict:
    """
    삼각형 면적을 계산하는 래퍼 함수 (밑변과 높이 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        base = input_data["base"]
        height = input_data["height"]
        
        area = AreaTools.calculate_area_triangle_from_base_height(base, height)
        
        return {
            "area": area,
            "explanation": f"底为 {base}，高为 {height} 的三角形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_rectangle_wrapper(input_data: dict) -> dict:
    """
    직사각형 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        width = input_data["width"]
        height = input_data["height"]
        
        area = AreaTools.calculate_area_rectangle(width, height)
        
        return {
            "area": area,
            "explanation": f"宽为 {width}，高为 {height} 的矩形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算矩形面积时出错：{str(e)}")

def calculate_area_rectangle_from_points_wrapper(input_data: dict) -> dict:
    """
    직사각형 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 4:
            raise ToolException("矩形必须有四个顶点")
            
        area = AreaTools.calculate_area_rectangle_from_points(vertices)
        
        if area == 0:
            raise ToolException("提供的点不构成矩形")
        
        return {
            "area": area,
            "explanation": f"由点 {vertices} 构成的矩形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算矩形面积时出错：{str(e)}")

def calculate_area_square_wrapper(input_data: dict) -> dict:
    """
    정사각형 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        side = input_data["side"]
        
        area = AreaTools.calculate_area_square(side)
        
        return {
            "area": area,
            "explanation": f"边长为 {side} 的正方形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算正方形面积时出错：{str(e)}")

def calculate_area_parallelogram_wrapper(input_data: dict) -> dict:
    """
    평행사변형 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        base = input_data["base"]
        height = input_data["height"]
        
        area = AreaTools.calculate_area_parallelogram(base, height)
        
        return {
            "area": area,
            "explanation": f"底为 {base}，高为 {height} 的平行四边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算平行四边形面积时出错：{str(e)}")

def calculate_area_parallelogram_from_points_wrapper(input_data: dict) -> dict:
    """
    평행사변형 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 4:
            raise ToolException("平行四边形必须有四个顶点")
            
        area = AreaTools.calculate_area_parallelogram_from_points(vertices)
        
        if area == 0:
            raise ToolException("提供的点不构成平行四边形")
        
        return {
            "area": area,
            "explanation": f"由点 {vertices} 构成的平行四边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算平行四边形面积时出错：{str(e)}")

def calculate_area_rhombus_wrapper(input_data: dict) -> dict:
    """
    마름모 면적을 계산하는 래퍼 함수 (두 대각선 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        diagonal1 = input_data["diagonal1"]
        diagonal2 = input_data["diagonal2"]
        
        area = AreaTools.calculate_area_rhombus(diagonal1, diagonal2)
        
        return {
            "area": area,
            "explanation": f"对角线长为 {diagonal1} 和 {diagonal2} 的菱形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算菱形面积时出错：{str(e)}")

def calculate_area_rhombus_from_points_wrapper(input_data: dict) -> dict:
    """
    마름모 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 4:
            raise ToolException("菱形必须有四个顶点")
            
        area = AreaTools.calculate_area_rhombus_from_points(vertices)
        
        if area == 0:
            raise ToolException("提供的点不构成菱形")
        
        return {
            "area": area,
            "explanation": f"由点 {vertices} 构成的菱形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算菱形面积时出错：{str(e)}")

def calculate_area_trapezoid_wrapper(input_data: dict) -> dict:
    """
    사다리꼴 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        base1 = input_data["base1"]
        base2 = input_data["base2"]
        height = input_data["height"]
        
        area = AreaTools.calculate_area_trapezoid(base1, base2, height)
        
        return {
            "area": area,
            "explanation": f"上底为 {base1}，下底为 {base2}，高为 {height} 的梯形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算梯形面积时出错：{str(e)}")

def calculate_area_trapezoid_from_points_wrapper(input_data: dict) -> dict:
    """
    사다리꼴 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 4:
            raise ToolException("梯形必须有四个顶点")
            
        area = AreaTools.calculate_area_trapezoid_from_points(vertices)
        
        return {
            "area": area,
            "explanation": f"由点 {vertices} 构成的梯形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算梯形面积时出错：{str(e)}")

def calculate_area_regular_polygon_wrapper(input_data: dict) -> dict:
    """
    정다각형 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        side = input_data["side"]
        n = input_data["n"]
        
        if n < 3:
            raise ToolException("正多边形的边数必须大于等于3")
        
        area = AreaTools.calculate_area_regular_polygon(side, n)
        
        return {
            "area": area,
            "explanation": f"{n}边形，边长为 {side} 的正多边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算正多边形面积时出错：{str(e)}")

def calculate_area_polygon_wrapper(input_data: dict) -> dict:
    """
    다각형 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) < 3:
            raise ToolException("多边形必须至少有三个顶点")
            
        area = AreaTools.calculate_area_polygon(vertices)
        
        return {
            "area": area,
            "explanation": f"由点 {vertices} 构成的 {len(vertices)}边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算多边形面积时出错：{str(e)}")

def calculate_area_circle_wrapper(input_data: dict) -> dict:
    """
    원 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        
        area = AreaTools.calculate_area_circle(radius)
        
        return {
            "area": area,
            "explanation": f"半径为 {radius} 的圆面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算圆面积时出错：{str(e)}")

def calculate_area_sector_wrapper(input_data: dict) -> dict:
    """
    부채꼴 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        
        if "degrees" in input_data and input_data["degrees"]:
            angle = AreaTools.degrees_to_radians(angle)
        
        area = AreaTools.calculate_area_sector(radius, angle)
        angle_deg = AreaTools.radians_to_degrees(angle)
        
        return {
            "area": area,
            "explanation": f"半径为 {radius}，圆心角为 {angle_deg}° 的扇形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算扇形面积时出错：{str(e)}")

def calculate_area_segment_wrapper(input_data: dict) -> dict:
    """
    활꼴 면적을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        radius = input_data["radius"]
        angle = input_data["angle"]
        
        if "degrees" in input_data and input_data["degrees"]:
            angle = AreaTools.degrees_to_radians(angle)
        
        area = AreaTools.calculate_area_segment(radius, angle)
        angle_deg = AreaTools.radians_to_degrees(angle)
        
        return {
            "area": area,
            "explanation": f"半径为 {radius}，圆心角为 {angle_deg}° 的弓形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算弓形面积时出错：{str(e)}") 