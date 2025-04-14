"""
삼각형 계산 래퍼 함수 모듈

이 모듈은 삼각형 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from tools.triangle_tools import TriangleTools

def calculate_area_wrapper(input_data: dict) -> dict:
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
            
        area = TriangleTools.calculate_area(vertices)
        
        return {
            "area": area,
            "explanation": f"三角形 {vertices} 的面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_area_from_sides_wrapper(input_data: dict) -> dict:
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
        
        area = TriangleTools.calculate_area_from_sides(a, b, c)
        
        return {
            "area": area,
            "explanation": f"边长为 {a}, {b}, {c} 的三角形面积是 {area}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形面积时出错：{str(e)}")

def calculate_perimeter_wrapper(input_data: dict) -> dict:
    """
    삼각형 둘레를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        둘레 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        perimeter = TriangleTools.calculate_perimeter(vertices)
        
        return {
            "perimeter": perimeter,
            "explanation": f"三角形 {vertices} 的周长是 {perimeter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形周长时出错：{str(e)}")

def is_right_triangle_wrapper(input_data: dict) -> dict:
    """
    직각삼각형 여부를 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        확인 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_right = TriangleTools.is_right_triangle(vertices)
        
        if is_right:
            return {
                "is_right": True,
                "explanation": f"三角形 {vertices} 是直角三角形"
            }
        else:
            return {
                "is_right": False,
                "explanation": f"三角形 {vertices} 不是直角三角形"
            }
    except Exception as e:
        raise ToolException(f"判断直角三角形时出错：{str(e)}")

def is_isosceles_triangle_wrapper(input_data: dict) -> dict:
    """
    이등변삼각형 여부를 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        확인 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_isosceles = TriangleTools.is_isosceles_triangle(vertices)
        
        if is_isosceles:
            return {
                "is_isosceles": True,
                "explanation": f"三角形 {vertices} 是等腰三角形"
            }
        else:
            return {
                "is_isosceles": False,
                "explanation": f"三角形 {vertices} 不是等腰三角形"
            }
    except Exception as e:
        raise ToolException(f"判断等腰三角形时出错：{str(e)}")

def is_equilateral_triangle_wrapper(input_data: dict) -> dict:
    """
    정삼각형 여부를 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        확인 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_equilateral = TriangleTools.is_equilateral_triangle(vertices)
        
        if is_equilateral:
            return {
                "is_equilateral": True,
                "explanation": f"三角形 {vertices} 是等边三角形"
            }
        else:
            return {
                "is_equilateral": False,
                "explanation": f"三角形 {vertices} 不是等边三角形"
            }
    except Exception as e:
        raise ToolException(f"判断等边三角形时出错：{str(e)}")

def calculate_angles_wrapper(input_data: dict) -> dict:
    """
    삼각형의 세 각을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        angles_rad = TriangleTools.calculate_angles(vertices)
        angles_deg = [TriangleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"三角形的三个角度分别是 {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三角形角度时出错：{str(e)}")

def calculate_centroid_wrapper(input_data: dict) -> dict:
    """
    삼각형의 무게중심을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        무게중심 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        centroid = TriangleTools.calculate_centroid(vertices)
        
        return {
            "centroid": centroid,
            "explanation": f"三角形 {vertices} 的质心是 {centroid}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形质心时出错：{str(e)}")

def calculate_circumcenter_wrapper(input_data: dict) -> dict:
    """
    삼각형의 외심을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        외심 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        circumcenter = TriangleTools.calculate_circumcenter(vertices)
        
        if circumcenter == (0, 0) and not (vertices[0] == (0, 0) or vertices[1] == (0, 0) or vertices[2] == (0, 0)):
            raise ToolException("无法计算三角形的外心，可能是三点共线")
        
        return {
            "circumcenter": circumcenter,
            "explanation": f"三角形 {vertices} 的外心是 {circumcenter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形外心时出错：{str(e)}")

def calculate_incenter_wrapper(input_data: dict) -> dict:
    """
    삼각형의 내심을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        내심 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        incenter = TriangleTools.calculate_incenter(vertices)
        
        return {
            "incenter": incenter,
            "explanation": f"三角形 {vertices} 的内心是 {incenter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形内心时出错：{str(e)}")

def calculate_orthocenter_wrapper(input_data: dict) -> dict:
    """
    삼각형의 수심을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        수심 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        orthocenter = TriangleTools.calculate_orthocenter(vertices)
        
        if orthocenter == (0, 0) and not (vertices[0] == (0, 0) or vertices[1] == (0, 0) or vertices[2] == (0, 0)):
            raise ToolException("无法计算三角形的垂心，可能是三点共线")
        
        return {
            "orthocenter": orthocenter,
            "explanation": f"三角形 {vertices} 的垂心是 {orthocenter}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形垂心时出错：{str(e)}")

def calculate_triangle_centers_wrapper(input_data: dict) -> dict:
    """
    삼각형의 모든 중심을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        중심 계산 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        centers = TriangleTools.calculate_triangle_centers(vertices)
        
        return {
            "centers": centers,
            "explanation": f"三角形 {vertices} 的各个中心点如下：质心 {centers['centroid']}，外心 {centers['circumcenter']}，内心 {centers['incenter']}，垂心 {centers['orthocenter']}"
        }
    except Exception as e:
        raise ToolException(f"计算三角形中心点时出错：{str(e)}")

def triangle_classification_wrapper(input_data: dict) -> dict:
    """
    삼각형 분류를 수행하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        삼각형 분류 결과와 설명
    """
    try:
        vertices = [tuple(p) for p in input_data["vertices"]]
        
        if len(vertices) != 3:
            raise ToolException("三角形必须有三个顶点")
            
        is_right = TriangleTools.is_right_triangle(vertices)
        is_isosceles = TriangleTools.is_isosceles_triangle(vertices)
        is_equilateral = TriangleTools.is_equilateral_triangle(vertices)
        
        triangle_type = ""
        if is_equilateral:
            triangle_type = "等边三角形"
        elif is_isosceles and is_right:
            triangle_type = "等腰直角三角形"
        elif is_isosceles:
            triangle_type = "等腰三角形"
        elif is_right:
            triangle_type = "直角三角形"
        else:
            triangle_type = "普通三角形"
        
        return {
            "is_right": is_right,
            "is_isosceles": is_isosceles,
            "is_equilateral": is_equilateral,
            "triangle_type": triangle_type,
            "explanation": f"三角形 {vertices} 是{triangle_type}"
        }
    except Exception as e:
        raise ToolException(f"分类三角形时出错：{str(e)}") 