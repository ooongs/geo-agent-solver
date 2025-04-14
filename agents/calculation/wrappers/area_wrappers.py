"""
면적 계산 래퍼 함수 모듈

이 모듈은 면적 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import AreaTools

def calculate_area_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 면적을 계산하는 래퍼 함수 (좌표 사용)
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        area = AreaTools.calculate_area_triangle(vertex_tuples)
        
        return {
            "area": area,
            "explanation": f"三角形 {vertex_tuples} 的面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_triangle_from_sides_wrapper(side1: float, side2: float, side3: float) -> dict:
    """
    삼각형 면적을 계산하는 래퍼 함수 (세 변의 길이 사용)
    
    Args:
        side1: 첫 번째 변의 길이
        side2: 두 번째 변의 길이
        side3: 세 번째 변의 길이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_triangle_from_sides(side1, side2, side3)
        
        return {
            "area": area,
            "explanation": f"边长为 {side1}, {side2}, {side3} 的三角形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_triangle_from_base_height_wrapper(base: float, height: float) -> dict:
    """
    삼각형 면적을 계산하는 래퍼 함수 (밑변과 높이 사용)
    
    Args:
        base: 밑변 길이
        height: 높이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_triangle_from_base_height(base, height)
        
        return {
            "area": area,
            "explanation": f"底为 {base}，高为 {height} 的三角形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_rectangle_wrapper(width: float, height: float) -> dict:
    """
    직사각형 면적을 계산하는 래퍼 함수
    
    Args:
        width: 너비
        height: 높이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_rectangle(width, height)
        
        return {
            "area": area,
            "explanation": f"宽为 {width}，高为 {height} 的矩形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算矩形面积时出错：{str(e)}")

def calculate_area_rectangle_from_points_wrapper(vertices: List[List[float]]) -> dict:
    """
    직사각형 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        vertices: 직사각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 4:
            raise ToolException("矩形必须有四个顶点")
            
        area = AreaTools.calculate_area_rectangle_from_points(vertex_tuples)
        
        if area == 0:
            raise ToolException("提供的点不构成矩形")
        
        return {
            "area": area,
            "explanation": f"由点 {vertex_tuples} 构成的矩形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算矩形面积时出错：{str(e)}")

def calculate_area_square_wrapper(side: float) -> dict:
    """
    정사각형 면적을 계산하는 래퍼 함수
    
    Args:
        side: 정사각형의 한 변의 길이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_square(side)
        
        return {
            "area": area,
            "explanation": f"边长为 {side} 的正方形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算正方形面积时出错：{str(e)}")

def calculate_area_parallelogram_wrapper(base: float, height: float) -> dict:
    """
    평행사변형 면적을 계산하는 래퍼 함수
    
    Args:
        base: 밑변의 길이
        height: 높이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_parallelogram(base, height)
        
        return {
            "area": area,
            "explanation": f"底为 {base}，高为 {height} 的平行四边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算平行四边形面积时出错：{str(e)}")

def calculate_area_parallelogram_from_points_wrapper(vertices: List[List[float]]) -> dict:
    """
    평행사변형 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        vertices: 평행사변형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 4:
            raise ToolException("平行四边形必须有四个顶点")
            
        area = AreaTools.calculate_area_parallelogram_from_points(vertex_tuples)
        
        if area == 0:
            raise ToolException("提供的点不构成平行四边形")
        
        return {
            "area": area,
            "explanation": f"由点 {vertex_tuples} 构成的平行四边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算平行四边形面积时出错：{str(e)}")

def calculate_area_rhombus_wrapper(diagonal1: float, diagonal2: float) -> dict:
    """
    마름모 면적을 계산하는 래퍼 함수 (두 대각선 사용)
    
    Args:
        diagonal1: 첫 번째 대각선의 길이
        diagonal2: 두 번째 대각선의 길이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_rhombus(diagonal1, diagonal2)
        
        return {
            "area": area,
            "explanation": f"对角线长为 {diagonal1} 和 {diagonal2} 的菱形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算菱形面积时出错：{str(e)}")

def calculate_area_rhombus_from_points_wrapper(vertices: List[List[float]]) -> dict:
    """
    마름모 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        vertices: 마름모 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 4:
            raise ToolException("菱形必须有四个顶点")
            
        area = AreaTools.calculate_area_rhombus_from_points(vertex_tuples)
        
        if area == 0:
            raise ToolException("提供的点不构成菱形")
        
        return {
            "area": area,
            "explanation": f"由点 {vertex_tuples} 构成的菱形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算菱形面积时出错：{str(e)}")

def calculate_area_trapezoid_wrapper(base1: float, base2: float, height: float) -> dict:
    """
    사다리꼴 면적을 계산하는 래퍼 함수
    
    Args:
        base1: 첫 번째 평행변의 길이
        base2: 두 번째 평행변의 길이
        height: 높이
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_trapezoid(base1, base2, height)
        
        return {
            "area": area,
            "explanation": f"上底为 {base1}，下底为 {base2}，高为 {height} 的梯形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算梯形面积时出错：{str(e)}")

def calculate_area_trapezoid_from_points_wrapper(vertices: List[List[float]]) -> dict:
    """
    사다리꼴 면적을 계산하는 래퍼 함수 (네 꼭짓점 좌표 사용)
    
    Args:
        vertices: 사다리꼴 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 4:
            raise ToolException("梯形必须有四个顶点")
            
        area = AreaTools.calculate_area_trapezoid_from_points(vertex_tuples)
        
        return {
            "area": area,
            "explanation": f"由点 {vertex_tuples} 构成的梯形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算梯形面积时出错：{str(e)}")

def calculate_area_regular_polygon_wrapper(side: float, n: int) -> dict:
    """
    정다각형 면적을 계산하는 래퍼 함수
    
    Args:
        side: 변의 길이
        n: 변의 개수
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        if n < 3:
            raise ToolException("正多边形的边数必须大于等于3")
        
        area = AreaTools.calculate_area_regular_polygon(side, n)
        
        return {
            "area": area,
            "explanation": f"{n}边形，边长为 {side} 的正多边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算正多边形面积时出错：{str(e)}")

def calculate_area_polygon_wrapper(vertices: List[List[float]]) -> dict:
    """
    다각형 면적을 계산하는 래퍼 함수
    
    Args:
        vertices: 다각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], ..., [xn, yn]]
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) < 3:
            raise ToolException("多边形必须至少有三个顶点")
            
        area = AreaTools.calculate_area_polygon(vertex_tuples)
        
        return {
            "area": area,
            "explanation": f"由点 {vertex_tuples} 构成的 {len(vertex_tuples)}边形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算多边形面积时出错：{str(e)}")

def calculate_area_circle_wrapper(radius: float) -> dict:
    """
    원 면적을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        area = AreaTools.calculate_area_circle(radius)
        
        return {
            "area": area,
            "explanation": f"半径为 {radius} 的圆面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算圆面积时出错：{str(e)}")

def calculate_area_sector_wrapper(radius: float, angle: float, degrees: bool = False) -> dict:
    """
    부채꼴 면적을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 중심각 (라디안 또는 도)
        degrees: angle이 도 단위인지 여부 (True면 도, False면 라디안)
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        angle_rad = angle
        if degrees:
            angle_rad = AreaTools.degrees_to_radians(angle)
        
        area = AreaTools.calculate_area_sector(radius, angle_rad)
        angle_deg = AreaTools.radians_to_degrees(angle_rad)
        
        return {
            "area": area,
            "explanation": f"半径为 {radius}，圆心角为 {angle_deg}° 的扇形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算扇形面积时出错：{str(e)}")

def calculate_area_segment_wrapper(radius: float, angle: float, degrees: bool = False) -> dict:
    """
    활꼴 면적을 계산하는 래퍼 함수
    
    Args:
        radius: 원의 반지름
        angle: 중심각 (라디안 또는 도)
        degrees: angle이 도 단위인지 여부 (True면 도, False면 라디안)
        
    Returns:
        면적 계산 결과와 설명
    """
    try:
        angle_rad = angle
        if degrees:
            angle_rad = AreaTools.degrees_to_radians(angle)
        
        area = AreaTools.calculate_area_segment(radius, angle_rad)
        angle_deg = AreaTools.radians_to_degrees(angle_rad)
        
        return {
            "area": area,
            "explanation": f"半径为 {radius}，圆心角为 {angle_deg}° 的弓形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算弓形面积时出错：{str(e)}") 