"""
삼각형 계산 래퍼 함수 모듈

이 모듈은 삼각형 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import TriangleTools

def calculate_area_wrapper(vertices: List[List[float]]) -> dict:
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
            
        area = TriangleTools.calculate_area(vertex_tuples)
        
        return {
            "area": area,
            "explanation": f"三角形 {vertex_tuples} 的面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_from_sides_wrapper(side1: float, side2: float, side3: float) -> dict:
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
        area = TriangleTools.calculate_area_from_sides(side1, side2, side3)
        
        return {
            "area": area,
            "explanation": f"边长为 {side1}, {side2}, {side3} 的三角形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_perimeter_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 둘레를 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        perimeter = TriangleTools.calculate_perimeter(vertex_tuples)
        
        return {
            "perimeter": perimeter,
            "explanation": f"三角形 {vertex_tuples} 的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形周长时出错：{str(e)}")

def is_right_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    직각삼각형 여부를 확인하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        확인 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_right = TriangleTools.is_right_triangle(vertex_tuples)
        
        if is_right:
            return {
                "is_right": True,
                "explanation": f"三角形 {vertex_tuples} 是直角三角形"
            }
        else:
            return {
                "is_right": False,
                "explanation": f"三角形 {vertex_tuples} 不是直角三角形"
            }
    except Exception as e:
        raise ToolException(f"判断直角三角形时出错：{str(e)}")

def is_isosceles_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    이등변삼각형 여부를 확인하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        확인 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_isosceles = TriangleTools.is_isosceles_triangle(vertex_tuples)
        
        if is_isosceles:
            return {
                "is_isosceles": True,
                "explanation": f"三角形 {vertex_tuples} 是等腰三角形"
            }
        else:
            return {
                "is_isosceles": False,
                "explanation": f"三角形 {vertex_tuples} 不是等腰三角形"
            }
    except Exception as e:
        raise ToolException(f"判断等腰三角形时出错：{str(e)}")

def is_equilateral_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    정삼각형 여부를 확인하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        확인 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_equilateral = TriangleTools.is_equilateral_triangle(vertex_tuples)
        
        if is_equilateral:
            return {
                "is_equilateral": True,
                "explanation": f"三角形 {vertex_tuples} 是等边三角形"
            }
        else:
            return {
                "is_equilateral": False,
                "explanation": f"三角形 {vertex_tuples} 不是等边三角形"
            }
    except Exception as e:
        raise ToolException(f"判断等边三角形时出错：{str(e)}")

def calculate_angles_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형의 세 각을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        angles_rad = TriangleTools.calculate_angles(vertex_tuples)
        angles_deg = [TriangleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"三角形 {vertex_tuples} 的内角分别是 {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三角形角度时出错：{str(e)}")

def calculate_centroid_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 무게중심을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        무게중심 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        centroid = TriangleTools.calculate_centroid(vertex_tuples)
        
        return {
            "centroid": centroid,
            "explanation": f"三角形 {vertex_tuples} 的重心是 {centroid}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形重心时出错：{str(e)}")

def calculate_circumcenter_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 외심을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        외심 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        circumcenter = TriangleTools.calculate_circumcenter(vertex_tuples)
        circumradius = TriangleTools.calculate_circumradius(vertex_tuples)
        
        return {
            "circumcenter": circumcenter,
            "circumradius": circumradius,
            "explanation": f"三角形 {vertex_tuples} 的外心是 {circumcenter}，外接圆半径是 {circumradius}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形外心时出错：{str(e)}")

def calculate_incenter_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 내심을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        내심 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        incenter = TriangleTools.calculate_incenter(vertex_tuples)
        inradius = TriangleTools.calculate_inradius(vertex_tuples)
        
        return {
            "incenter": incenter,
            "inradius": inradius,
            "explanation": f"三角形 {vertex_tuples} 的内心是 {incenter}，内切圆半径是 {inradius}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形内心时出错：{str(e)}")

def calculate_orthocenter_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 수심을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        수심 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        orthocenter = TriangleTools.calculate_orthocenter(vertex_tuples)
        
        # 고도 계산 (각 꼭지점에서 반대 변에 내린 수선)
        heights = []
        for i in range(3):
            p1 = vertex_tuples[i]
            p2 = vertex_tuples[(i+1)%3]
            p3 = vertex_tuples[(i+2)%3]
            height = TriangleTools.calculate_triangle_height(vertex_tuples, i)
            heights.append(height)
        
        return {
            "orthocenter": orthocenter,
            "heights": heights,
            "explanation": f"三角形 {vertex_tuples} 的垂心是 {orthocenter}，三个高分别是 {heights[0]:.2f}, {heights[1]:.2f}, {heights[2]:.2f}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形垂心时出错：{str(e)}")

def calculate_triangle_centers_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형의 모든 중심을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        모든 중심 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        centroid = TriangleTools.calculate_centroid(vertex_tuples)
        circumcenter = TriangleTools.calculate_circumcenter(vertex_tuples)
        incenter = TriangleTools.calculate_incenter(vertex_tuples)
        orthocenter = TriangleTools.calculate_orthocenter(vertex_tuples)
        
        return {
            "centroid": centroid,
            "circumcenter": circumcenter,
            "incenter": incenter,
            "orthocenter": orthocenter,
            "explanation": f"三角形 {vertex_tuples} 的重心是 {centroid}，外心是 {circumcenter}，内心是 {incenter}，垂心是 {orthocenter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形中心时出错：{str(e)}")

def triangle_classification_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 분류를 수행하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        분류 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_right = TriangleTools.is_right_triangle(vertex_tuples)
        is_isosceles = TriangleTools.is_isosceles_triangle(vertex_tuples)
        is_equilateral = TriangleTools.is_equilateral_triangle(vertex_tuples)
        is_acute = TriangleTools.is_acute_triangle(vertex_tuples)
        is_obtuse = TriangleTools.is_obtuse_triangle(vertex_tuples)
        
        classifications = []
        if is_equilateral:
            classifications.append("等边三角形")
        elif is_isosceles:
            classifications.append("等腰三角形")
            
        if is_right:
            classifications.append("直角三角形")
        elif is_acute:
            classifications.append("锐角三角形")
        elif is_obtuse:
            classifications.append("钝角三角形")
            
        triangle_type = "、".join(classifications) if classifications else "普通三角形"
        
        return {
            "is_right": is_right,
            "is_isosceles": is_isosceles,
            "is_equilateral": is_equilateral,
            "is_acute": is_acute,
            "is_obtuse": is_obtuse,
            "triangle_type": triangle_type,
            "explanation": f"三角形 {vertex_tuples} 是{triangle_type}"
        }
    except Exception as e:
        raise ToolException(f"分类三角形时出错：{str(e)}") 