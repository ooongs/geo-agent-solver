"""
좌표 계산 래퍼 함수 모듈

이 모듈은 좌표 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import CoordinateTools

def calculate_midpoint_wrapper(point1: List[float], point2: List[float]) -> dict:
    """
    두 점의 중점을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        
    Returns:
        중점 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        midpoint = CoordinateTools.calculate_midpoint(p1, p2)
        return {
            "midpoint": midpoint,
            "midpoint_explanation": f"点 {p1} 和 {p2} 的中点是 {midpoint}"
        }
    except Exception as e:
        raise ToolException(f"计算中点时出错：{str(e)}")

def calculate_slope_wrapper(point1: List[float], point2: List[float]) -> dict:
    """
    두 점의 기울기를 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        
    Returns:
        기울기 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
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

def calculate_line_equation_wrapper(point1: List[float], point2: List[float]) -> dict:
    """
    두 점을 지나는 직선 방정식을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        
    Returns:
        직선 방정식 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        a, b, c = CoordinateTools.calculate_line_equation(p1, p2)
        equation = f"{a}x + {b}y + {c} = 0"
        return {
            "line_equation": [a, b, c],
            "equation_string": equation,
            "equation_explanation": f"通过点 {p1} 和 {p2} 的直线方程是 {equation}"
        }
    except Exception as e:
        raise ToolException(f"计算直线方程时出错：{str(e)}")

def are_points_collinear_wrapper(point1: List[float], point2: List[float], point3: List[float]) -> dict:
    """
    세 점의 공선성을 확인하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        point3: 세 번째 점 좌표 [x3, y3]
        
    Returns:
        공선성 확인 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        p3 = tuple(point3)
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

def are_lines_parallel_wrapper(line1: List[float], line2: List[float]) -> dict:
    """
    두 직선의 평행 여부를 확인하는 래퍼 함수
    
    Args:
        line1: 첫 번째 직선의 방정식 계수 [a1, b1, c1] (a1x + b1y + c1 = 0)
        line2: 두 번째 직선의 방정식 계수 [a2, b2, c2] (a2x + b2y + c2 = 0)
        
    Returns:
        평행 여부 확인 결과와 설명
    """
    try:
        l1 = tuple(line1)
        l2 = tuple(line2)
        parallel = CoordinateTools.are_lines_parallel(l1, l2)
        if parallel:
            return {
                "parallel": True,
                "parallel_explanation": f"直线 {l1} 和 {l2} 是平行的"
            }
        else:
            # 교점 계산
            a1, b1, c1 = l1
            a2, b2, c2 = l2
            det = a1*b2 - a2*b1
            if abs(det) < 1e-10:
                return {
                    "parallel": True,
                    "parallel_explanation": f"直线 {l1} 和 {l2} 重合或平行"
                }
            x = (b1*c2 - b2*c1) / det
            y = (a2*c1 - a1*c2) / det
            intersection = (x, y)
            return {
                "parallel": False,
                "parallel_explanation": f"直线 {l1} 和 {l2} 不是平行的",
                "intersection": intersection,
                "intersection_explanation": f"两直线的交点是 {intersection}"
            }
    except Exception as e:
        raise ToolException(f"检查直线平行性时出错：{str(e)}")

def calculate_segment_division_wrapper(point1: List[float], point2: List[float], ratio: float) -> dict:
    """
    선분 분할점을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        ratio: 분할 비율
        
    Returns:
        분할점 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        division_point = CoordinateTools.calculate_segment_division(p1, p2, ratio)
        return {
            "division_point": division_point,
            "division_explanation": f"线段 {p1} 到 {p2} 按比例 {ratio} 分割的点是 {division_point}"
        }
    except Exception as e:
        raise ToolException(f"计算分割点时出错：{str(e)}")

def calculate_internal_division_point_wrapper(point1: List[float], point2: List[float], m: float, n: float) -> dict:
    """
    내분점을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        m: 첫 번째 비율
        n: 두 번째 비율
        
    Returns:
        내분점 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        
        if m <= 0 or n <= 0:
            raise ToolException("内分比的两个数值必须为正数")
            
        division_point = CoordinateTools.calculate_internal_division_point(p1, p2, m, n)
        return {
            "internal_division_point": division_point,
            "division_explanation": f"线段 {p1} 到 {p2} 的内分点（比例 {m}:{n}）是 {division_point}"
        }
    except Exception as e:
        raise ToolException(f"计算内分点时出错：{str(e)}")

def calculate_external_division_point_wrapper(point1: List[float], point2: List[float], m: float, n: float) -> dict:
    """
    외분점을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        point2: 두 번째 점 좌표 [x2, y2]
        m: 첫 번째 비율
        n: 두 번째 비율
        
    Returns:
        외분점 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(point2)
        
        if m <= 0 or n <= 0 or m == n:
            raise ToolException("外分比的两个数值必须为正数且不相等")
            
        division_point = CoordinateTools.calculate_external_division_point(p1, p2, m, n)
        return {
            "external_division_point": division_point,
            "division_explanation": f"线段 {p1} 到 {p2} 的外分点（比例 {m}:{n}）是 {division_point}"
        }
    except Exception as e:
        raise ToolException(f"计算外分点时出错：{str(e)}")

def is_point_on_segment_wrapper(point: List[float], segment_start: List[float], segment_end: List[float]) -> dict:
    """
    점이 선분 위에 있는지 확인하는 래퍼 함수
    
    Args:
        point: 확인할 점의 좌표 [x, y]
        segment_start: 선분의 시작점 좌표 [x1, y1]
        segment_end: 선분의 끝점 좌표 [x2, y2]
        
    Returns:
        확인 결과와 설명
    """
    try:
        p = tuple(point)
        p1 = tuple(segment_start)
        p2 = tuple(segment_end)
        
        is_on_segment = CoordinateTools.is_point_on_segment(p, p1, p2)
        if is_on_segment:
            return {
                "is_on_segment": True,
                "explanation": f"点 {p} 在线段 {p1} 到 {p2} 上"
            }
        else:
            return {
                "is_on_segment": False,
                "explanation": f"点 {p} 不在线段 {p1} 到 {p2} 上"
            }
    except Exception as e:
        raise ToolException(f"判断点是否在线段上时出错：{str(e)}") 