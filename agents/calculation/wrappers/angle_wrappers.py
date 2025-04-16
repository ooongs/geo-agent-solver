"""
각도 계산 래퍼 함수 모듈

이 모듈은 각도 계산 도구의 래퍼 함수들을 제공합니다.
각 함수는 입력을 검증하고 결과를 중국어로 설명합니다.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.tools import ToolException
from agents.calculation.tools import AngleTools

def calculate_angle_three_points_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> dict:
    """
    세 점으로 이루어진 각도를 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        vertex: 각의 꼭지점 좌표 [x2, y2]
        point2: 두 번째 점 좌표 [x3, y3]
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(vertex)  # 각의 꼭지점
        p3 = tuple(point2)
        
        angle_rad = AngleTools.calculate_angle_three_points(p1, p2, p3)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"点 {p1}、{p2}（角的顶点）和 {p3} 形成的角度是 {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三点角度时出错：{str(e)}")

def calculate_angle_two_lines_wrapper(line1: List[float], line2: List[float]) -> dict:
    """
    두 직선 사이의 각도를 계산하는 래퍼 함수
    
    Args:
        line1: 첫 번째 직선의 방정식 계수 [a1, b1, c1] (a1x + b1y + c1 = 0)
        line2: 두 번째 직선의 방정식 계수 [a2, b2, c2] (a2x + b2y + c2 = 0)
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        l1 = tuple(line1)
        l2 = tuple(line2)
        
        angle_rad = AngleTools.calculate_angle_two_lines(l1, l2)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"直线 {l1} 和 {l2} 之间的角度是 {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算两直线角度时出错：{str(e)}")

def calculate_angle_two_vectors_wrapper(vector1: List[float], vector2: List[float]) -> dict:
    """
    두 벡터 사이의 각도를 계산하는 래퍼 함수
    
    Args:
        vector1: 첫 번째 벡터 [x1, y1]
        vector2: 두 번째 벡터 [x2, y2]
        
    Returns:
        각도 계산 결과와 설명
    """
    try:
        v1 = tuple(vector1)
        v2 = tuple(vector2)
        
        angle_rad = AngleTools.calculate_angle_two_vectors(v1, v2)
        angle_deg = AngleTools.radians_to_degrees(angle_rad)
        
        return {
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "explanation": f"向量 {v1} 和 {v2} 之间的角度是 {angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算两向量角度时出错：{str(e)}")

def calculate_interior_angles_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 내각을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        내각 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("必须提供三角形的三个顶点")
            
        angles_rad = AngleTools.calculate_interior_angles_triangle(vertex_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"三角形内角分别是 {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三角形内角时出错：{str(e)}")

def calculate_exterior_angles_triangle_wrapper(vertices: List[List[float]]) -> dict:
    """
    삼각형 외각을 계산하는 래퍼 함수
    
    Args:
        vertices: 삼각형 꼭지점 좌표 리스트 [[x1, y1], [x2, y2], [x3, y3]]
        
    Returns:
        외각 계산 결과와 설명
    """
    try:
        vertex_tuples = [tuple(p) for p in vertices]
        
        if len(vertex_tuples) != 3:
            raise ToolException("必须提供三角形的三个顶点")
            
        angles_rad = AngleTools.calculate_exterior_angles_triangle(vertex_tuples)
        angles_deg = [AngleTools.radians_to_degrees(angle) for angle in angles_rad]
        
        return {
            "angles_rad": angles_rad,
            "angles_deg": angles_deg,
            "explanation": f"三角形外角分别是 {angles_deg[0]:.2f}°, {angles_deg[1]:.2f}°, {angles_deg[2]:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算三角形外角时出错：{str(e)}")

def calculate_inscribed_angle_wrapper(center: List[float], point1: List[float], point2: List[float]) -> dict:
    """
    원에서의 내접각을 계산하는 래퍼 함수
    
    Args:
        center: 원의 중심 좌표 [x, y]
        point1: 원 위의 첫 번째 점 좌표 [x1, y1]
        point2: 원 위의 두 번째 점 좌표 [x2, y2]
        
    Returns:
        내접각 계산 결과와 설명
    """
    try:
        c = tuple(center)
        p1 = tuple(point1)
        p2 = tuple(point2)
        
        inscribed_angle_rad = AngleTools.calculate_inscribed_angle(c, p1, p2)
        inscribed_angle_deg = AngleTools.radians_to_degrees(inscribed_angle_rad)
        central_angle_rad = 2 * inscribed_angle_rad
        central_angle_deg = AngleTools.radians_to_degrees(central_angle_rad)
        
        return {
            "inscribed_angle_rad": inscribed_angle_rad,
            "inscribed_angle_deg": inscribed_angle_deg,
            "central_angle_rad": central_angle_rad,
            "central_angle_deg": central_angle_deg,
            "explanation": f"圆心为 {c}，点 {p1} 和 {p2} 形成的内接角是 {inscribed_angle_deg:.2f}°，对应的圆心角是 {central_angle_deg:.2f}°"
        }
    except Exception as e:
        raise ToolException(f"计算内接角时出错：{str(e)}")

def calculate_angle_bisector_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> dict:
    """
    두 점을 향하는 각의 이등분선을 계산하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        vertex: 각의 꼭지점 좌표 [x2, y2]  
        point2: 두 번째 점 좌표 [x3, y3]
        
    Returns:
        이등분선 계산 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(vertex)  # 각의 꼭지점
        p3 = tuple(point2)
        
        bisector = AngleTools.calculate_angle_bisector(p1, p2, p3)
        
        return {
            "angle_bisector": bisector,
            "explanation": f"点 {p1}、{p2}（角的顶点）和 {p3} 形成的角的角平分线方程是 {bisector[0]}x + {bisector[1]}y + {bisector[2]} = 0"
        }
    except Exception as e:
        raise ToolException(f"计算角平分线时出错：{str(e)}")
    
def calculate_angle_trisection_wrapper(point1: List[float], vertex: List[float], point2: List[float]) -> dict:
    """
    각도를 세 등분하는 래퍼 함수
    
    Args:
        point1: 첫 번째 점 좌표 [x1, y1]
        vertex: 각의 꼭지점 좌표 [x2, y2]
        point2: 두 번째 점 좌표 [x3, y3]
        
    Returns:
        세 등분 결과와 설명
    """
    try:
        p1 = tuple(point1)
        p2 = tuple(vertex)  # 각의 꼭지점
        p3 = tuple(point2)
        
        trisection = AngleTools.calculate_angle_trisection(p1, p2, p3)
        
        return {
            "trisection": trisection,
            "explanation": f"点 {p1}、{p2}（角的顶点）和 {p3} 形成的角的三等分线方程是 l1: {trisection[0][0]}x + {trisection[0][1]}y + {trisection[0][2]} = 0, l2: {trisection[1][0]}x + {trisection[1][1]}y + {trisection[1][2]} = 0, l3: {trisection[2][0]}x + {trisection[2][1]}y + {trisection[2][2]} = 0"
        }
    except Exception as e:
        raise ToolException(f"计算三等分线时出错：{str(e)}")

def angle_classification_wrapper(angle_deg: float) -> dict:
    """
    각도 분류를 수행하는 래퍼 함수
    
    Args:
        angle_deg: 각도(도)
        
    Returns:
        분류 결과와 설명
    """
    try:
        classification = AngleTools.classify_angle(angle_deg)
        
        explanation_map = {
            "acute": "锐角 (小于90°)",
            "right": "直角 (等于90°)",
            "obtuse": "钝角 (大于90°但小于180°)",
            "straight": "平角 (等于180°)",
            "reflex": "优角 (大于180°但小于360°)",
            "full": "周角 (等于360°)"
        }
        
        explanation = f"{angle_deg}° 是{explanation_map.get(classification, '')}"
        
        return {
            "angle_deg": angle_deg,
            "classification": classification,
            "explanation": explanation
        }
    except Exception as e:
        raise ToolException(f"分类角度时出错：{str(e)}") 
