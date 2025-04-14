"""
좌표 계산 래퍼 함수 모듈

이 모듈은 좌표 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from tools.coordinate_tools import CoordinateTools

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
        midpoint = CoordinateTools.calculate_midpoint(p1, p2)
        return {
            "midpoint": midpoint,
            "midpoint_explanation": f"点 {p1} 和 {p2} 的中点是 {midpoint}"
        }
    except Exception as e:
        raise ToolException(f"计算中点时出错：{str(e)}")

def calculate_slope_wrapper(input_data: dict) -> dict:
    """
    두 점의 기울기를 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        기울기 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        slope = CoordinateTools.calculate_slope(p1, p2)
        if slope == float('inf'):
            return {
                "slope": "无穷大",
                "slope_explanation": f"点 {p1} 和 {p2} 连线的斜率是无穷大（垂直线）"
            }
        return {
            "slope": slope,
            "slope_explanation": f"点 {p1} 和 {p2} 连线的斜率是 {slope}"
        }
    except Exception as e:
        raise ToolException(f"计算斜率时出错：{str(e)}")

def calculate_line_equation_wrapper(input_data: dict) -> dict:
    """
    두 점을 지나는 직선 방정식을 계산하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        직선 방정식 계산 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        a, b, c = CoordinateTools.calculate_line_equation(p1, p2)
        equation = f"{a}x + {b}y + {c} = 0"
        return {
            "line_equation": [a, b, c],
            "equation_string": equation,
            "equation_explanation": f"通过点 {p1} 和 {p2} 的直线方程是 {equation}"
        }
    except Exception as e:
        raise ToolException(f"计算直线方程时出错：{str(e)}")

def are_points_collinear_wrapper(input_data: dict) -> dict:
    """
    세 점의 공선성을 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        공선성 확인 결과와 설명
    """
    try:
        p1 = tuple(input_data["point1"])
        p2 = tuple(input_data["point2"])
        p3 = tuple(input_data["point3"])
        collinear = CoordinateTools.are_points_collinear(p1, p2, p3)
        if collinear:
            return {
                "collinear": True,
                "collinear_explanation": f"点 {p1}、{p2} 和 {p3} 在同一直线上"
            }
        else:
            # 삼각형 면적 계산
            area = 0.5 * abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])))
            return {
                "collinear": False,
                "collinear_explanation": f"点 {p1}、{p2} 和 {p3} 不在同一直线上",
                "triangle_area": area,
                "area_explanation": f"这三点形成的三角形面积是 {area}"
            }
    except Exception as e:
        raise ToolException(f"检查点共线性时出错：{str(e)}")

def are_lines_parallel_wrapper(input_data: dict) -> dict:
    """
    두 직선의 평행 여부를 확인하는 래퍼 함수
    
    Args:
        input_data: 입력 데이터 딕셔너리
        
    Returns:
        평행 여부 확인 결과와 설명
    """
    try:
        line1 = tuple(input_data["line1"])
        line2 = tuple(input_data["line2"])
        parallel = CoordinateTools.are_lines_parallel(line1, line2)
        if parallel:
            return {
                "parallel": True,
                "parallel_explanation": f"直线 {line1} 和 {line2} 是平行的"
            }
        else:
            # 교점 계산
            a1, b1, c1 = line1
            a2, b2, c2 = line2
            det = a1*b2 - a2*b1
            if abs(det) < 1e-10:
                return {
                    "parallel": True,
                    "parallel_explanation": f"直线 {line1} 和 {line2} 重合或平行"
                }
            x = (b1*c2 - b2*c1) / det
            y = (a2*c1 - a1*c2) / det
            intersection = (x, y)
            return {
                "parallel": False,
                "parallel_explanation": f"直线 {line1} 和 {line2} 不是平行的",
                "intersection": intersection,
                "intersection_explanation": f"两直线的交点是 {intersection}"
            }
    except Exception as e:
        raise ToolException(f"检查直线平行性时出错：{str(e)}") 