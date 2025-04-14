"""
삼각형 관련 계산 도구

이 모듈은 중국 중학교 수준의 삼각형 관련 기하학 문제를 해결하기 위한 도구를 제공합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase



class TriangleTools(GeometryToolBase):
    """삼각형 관련 계산 도구"""
    
    @staticmethod
    def calculate_area(vertices: List[Tuple[float, float]]) -> float:
        """삼각형의 면적 계산 (좌표 사용)"""
        if len(vertices) != 3:
            return 0
        
        x1, y1 = vertices[0]
        x2, y2 = vertices[1]
        x3, y3 = vertices[2]
        
        # 삼각형의 면적 계산 (신발끈 공식)
        area = 0.5 * abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)))
        return area
    
    @staticmethod
    def calculate_area_from_sides(a: float, b: float, c: float) -> float:
        """삼각형의 면적 계산 (세 변의 길이 사용, 헤론의 공식)"""
        # 헤론의 공식
        s = (a + b + c) / 2  # 반둘레
        if s <= a or s <= b or s <= c:  # 삼각형 부등식 검사
            return 0
        
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        return area
    
    @staticmethod
    def calculate_perimeter(vertices: List[Tuple[float, float]]) -> float:
        """삼각형의 둘레 계산"""
        if len(vertices) != 3:
            return 0
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        return a + b + c
    
    @staticmethod
    def is_right_triangle(vertices: List[Tuple[float, float]]) -> bool:
        """직각삼각형 여부 확인"""
        if len(vertices) != 3:
            return False
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        # 피타고라스 정리를 이용한 직각삼각형 판별
        sides = sorted([a, b, c])
        return abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-10
    
    @staticmethod
    def is_isosceles_triangle(vertices: List[Tuple[float, float]]) -> bool:
        """이등변삼각형 여부 확인"""
        if len(vertices) != 3:
            return False
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        # 두 변의 길이가 같은지 확인
        return abs(a - b) < 1e-10 or abs(b - c) < 1e-10 or abs(c - a) < 1e-10
    
    @staticmethod
    def is_equilateral_triangle(vertices: List[Tuple[float, float]]) -> bool:
        """정삼각형 여부 확인"""
        if len(vertices) != 3:
            return False
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p1, p2)
        b = TriangleTools.calculate_distance(p2, p3)
        c = TriangleTools.calculate_distance(p3, p1)
        
        # 세 변의 길이가 모두 같은지 확인
        return abs(a - b) < 1e-10 and abs(b - c) < 1e-10
    
    @staticmethod
    def calculate_angles(vertices: List[Tuple[float, float]]) -> List[float]:
        """삼각형의 세 각 계산 (라디안)"""
        if len(vertices) != 3:
            return [0, 0, 0]
        
        p1, p2, p3 = vertices
        angle1 = TriangleTools.calculate_angle(p2, p1, p3)
        angle2 = TriangleTools.calculate_angle(p1, p2, p3)
        angle3 = TriangleTools.calculate_angle(p1, p3, p2)
        
        return [angle1, angle2, angle3]
    
    @staticmethod
    def calculate_centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """삼각형의 무게중심 계산"""
        if len(vertices) != 3:
            return (0, 0)
        
        x = sum(p[0] for p in vertices) / 3
        y = sum(p[1] for p in vertices) / 3
        
        return (x, y)
    
    @staticmethod
    def calculate_circumcenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """삼각형의 외심 계산"""
        if len(vertices) != 3:
            return (0, 0)
        
        (x1, y1), (x2, y2), (x3, y3) = vertices
        
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(D) < 1e-10:
            return (0, 0)  # 세 점이 일직선 상에 있는 경우
        
        Ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / D
        Uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / D
        
        return (Ux, Uy)
    
    @staticmethod
    def calculate_incenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """삼각형의 내심 계산"""
        if len(vertices) != 3:
            return (0, 0)
        
        p1, p2, p3 = vertices
        a = TriangleTools.calculate_distance(p2, p3)
        b = TriangleTools.calculate_distance(p1, p3)
        c = TriangleTools.calculate_distance(p1, p2)
        
        # 변들의 길이를 가중치로 사용
        x = (a * p1[0] + b * p2[0] + c * p3[0]) / (a + b + c)
        y = (a * p1[1] + b * p2[1] + c * p3[1]) / (a + b + c)
        
        return (x, y)
    
    @staticmethod
    def calculate_orthocenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """삼각형의 수심 계산"""
        if len(vertices) != 3:
            return (0, 0)
        
        (x1, y1), (x2, y2), (x3, y3) = vertices
        
        # 세 점이 일직선 상에 있는지 확인
        D = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        if abs(D) < 1e-10:
            return (0, 0)
        
        # 각 변의 기울기 계산
        m1 = float('inf') if abs(x2 - x3) < 1e-10 else (y2 - y3) / (x2 - x3)
        m2 = float('inf') if abs(x1 - x3) < 1e-10 else (y1 - y3) / (x1 - x3)
        m3 = float('inf') if abs(x1 - x2) < 1e-10 else (y1 - y2) / (x1 - x2)
        
        # 각 변에 수직인 직선의 기울기
        m1_perp = 0 if abs(m1) == float('inf') else -1 / m1
        m2_perp = 0 if abs(m2) == float('inf') else -1 / m2
        m3_perp = 0 if abs(m3) == float('inf') else -1 / m3
        
        # 수선의 방정식 계산
        b1 = y1 - m1_perp * x1
        b2 = y2 - m2_perp * x2
        b3 = y3 - m3_perp * x3
        
        # 두 수선의 교점 계산
        if abs(m1_perp - m2_perp) < 1e-10:
            # 첫 번째와 두 번째 수선이 평행하면 다른 두 수선의 교점 계산
            x = (b3 - b1) / (m1_perp - m3_perp)
            y = m1_perp * x + b1
        else:
            x = (b2 - b1) / (m1_perp - m2_perp)
            y = m1_perp * x + b1
        
        return (x, y)
    
    @staticmethod
    def calculate_triangle_centers(vertices: List[Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """삼각형의 모든 중심 계산"""
        centers = {
            "centroid": TriangleTools.calculate_centroid(vertices),
            "circumcenter": TriangleTools.calculate_circumcenter(vertices),
            "incenter": TriangleTools.calculate_incenter(vertices),
            "orthocenter": TriangleTools.calculate_orthocenter(vertices)
        }
        return centers
    
    @staticmethod
    def calculate_triangle_tool(input_json: str) -> str:
        """삼각형 계산 도구 메인 함수"""
        try:
            data = TriangleTools.parse_input(input_json)
            
            vertices = data.get("vertices", [])
            if not vertices or len(vertices) != 3:
                raise ToolException("请提供有效的三角形顶点坐标，需要三个点")
            
            # 삼각형 정보 계산
            result = {
                "area": TriangleTools.calculate_area(vertices),
                "perimeter": TriangleTools.calculate_perimeter(vertices),
                "angles": [TriangleTools.radians_to_degrees(angle) for angle in TriangleTools.calculate_angles(vertices)],
                "is_right": TriangleTools.is_right_triangle(vertices),
                "is_isosceles": TriangleTools.is_isosceles_triangle(vertices),
                "is_equilateral": TriangleTools.is_equilateral_triangle(vertices),
                "centers": TriangleTools.calculate_triangle_centers(vertices)
            }
            
            # 특별한 계산 요청 처리
            if "calculate" in data:
                for calc in data["calculate"]:
                    if calc == "centroid":
                        result["centroid"] = TriangleTools.calculate_centroid(vertices)
                    elif calc == "circumcenter":
                        result["circumcenter"] = TriangleTools.calculate_circumcenter(vertices)
                    elif calc == "incenter":
                        result["incenter"] = TriangleTools.calculate_incenter(vertices)
                    elif calc == "orthocenter":
                        result["orthocenter"] = TriangleTools.calculate_orthocenter(vertices)
                    else:
                        raise ToolException(f"不支持的计算类型：{calc}，可用选项：centroid, circumcenter, incenter, orthocenter")
            
            return TriangleTools.format_output(result)
        except ToolException as e:
            return TriangleTools.format_output({"error": str(e)})
        except Exception as e:
            return TriangleTools.format_output({"error": f"计算三角形时出现错误：{str(e)}"}) 