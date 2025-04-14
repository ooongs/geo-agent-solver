"""
면적 관련 계산 도구

이 모듈은 중국 중학교 수준의 면적 관련 기하학 문제를 해결하기 위한 도구를 제공합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase


class AreaTools(GeometryToolBase):
    """면적 관련 계산 도구"""
    
    @staticmethod
    def calculate_area_triangle(vertices: List[Tuple[float, float]]) -> float:
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
    def calculate_area_triangle_from_sides(a: float, b: float, c: float) -> float:
        """삼각형의 면적 계산 (세 변의 길이 사용, 헤론의 공식)"""
        # 헤론의 공식
        s = (a + b + c) / 2  # 반둘레
        if s <= a or s <= b or s <= c:  # 삼각형 부등식 검사
            return 0
        
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        return area
    
    @staticmethod
    def calculate_area_triangle_from_base_height(base: float, height: float) -> float:
        """삼각형의 면적 계산 (밑변과 높이 사용)"""
        return 0.5 * base * height
    
    @staticmethod
    def calculate_area_rectangle(width: float, height: float) -> float:
        """직사각형의 면적 계산"""
        return width * height
    
    @staticmethod
    def calculate_area_rectangle_from_points(vertices: List[Tuple[float, float]]) -> float:
        """직사각형의 면적 계산 (네 꼭짓점 좌표 사용)"""
        if len(vertices) != 4:
            return 0
        
        # 변들의 길이 계산
        sides = []
        for i in range(4):
            sides.append(AreaTools.calculate_distance(vertices[i], vertices[(i + 1) % 4]))
        
        # 직사각형은 마주보는 변이 같아야 함
        if abs(sides[0] - sides[2]) > 1e-10 or abs(sides[1] - sides[3]) > 1e-10:
            return 0  # 직사각형이 아님
        
        return sides[0] * sides[1]
    
    @staticmethod
    def calculate_area_square(side: float) -> float:
        """정사각형의 면적 계산"""
        return side * side
    
    @staticmethod
    def calculate_area_parallelogram(base: float, height: float) -> float:
        """평행사변형의 면적 계산"""
        return base * height
    
    @staticmethod
    def calculate_area_parallelogram_from_points(vertices: List[Tuple[float, float]]) -> float:
        """평행사변형의 면적 계산 (네 꼭짓점 좌표 사용)"""
        if len(vertices) != 4:
            return 0
        
        # 네 개의 점이 평행사변형을 이루는지 확인
        # 대각선이 서로를 이등분하는지 확인
        p1, p2, p3, p4 = vertices
        mid1 = AreaTools.calculate_midpoint(p1, p3)
        mid2 = AreaTools.calculate_midpoint(p2, p4)
        
        if abs(mid1[0] - mid2[0]) > 1e-10 or abs(mid1[1] - mid2[1]) > 1e-10:
            return 0  # 평행사변형이 아님
        
        # 넓이 계산 (두 삼각형의 합으로 계산)
        return AreaTools.calculate_area_triangle([p1, p2, p3]) + AreaTools.calculate_area_triangle([p1, p3, p4])
    
    @staticmethod
    def calculate_area_rhombus(diagonal1: float, diagonal2: float) -> float:
        """마름모의 면적 계산 (두 대각선 사용)"""
        return 0.5 * diagonal1 * diagonal2
    
    @staticmethod
    def calculate_area_rhombus_from_points(vertices: List[Tuple[float, float]]) -> float:
        """마름모의 면적 계산 (네 꼭짓점 좌표 사용)"""
        if len(vertices) != 4:
            return 0
        
        # 네 변의 길이가 같은지 확인
        p1, p2, p3, p4 = vertices
        side1 = AreaTools.calculate_distance(p1, p2)
        side2 = AreaTools.calculate_distance(p2, p3)
        side3 = AreaTools.calculate_distance(p3, p4)
        side4 = AreaTools.calculate_distance(p4, p1)
        
        if abs(side1 - side2) > 1e-10 or abs(side2 - side3) > 1e-10 or abs(side3 - side4) > 1e-10:
            return 0  # 마름모가 아님
        
        # 대각선 길이 계산
        diagonal1 = AreaTools.calculate_distance(p1, p3)
        diagonal2 = AreaTools.calculate_distance(p2, p4)
        
        return 0.5 * diagonal1 * diagonal2
    
    @staticmethod
    def calculate_area_trapezoid(base1: float, base2: float, height: float) -> float:
        """사다리꼴의 면적 계산"""
        return 0.5 * (base1 + base2) * height
    
    @staticmethod
    def calculate_area_trapezoid_from_points(vertices: List[Tuple[float, float]]) -> float:
        """사다리꼴의 면적 계산 (네 꼭짓점 좌표 사용)"""
        if len(vertices) != 4:
            return 0
        
        # 사다리꼴은 두 변이 평행해야 함
        # 이 구현에서는 단순하게 주어진 점들을 사용하여 면적을 계산
        # 실제로는 각 점의 순서와 배치에 따라 다를 수 있음
        return AreaTools.calculate_area_polygon(vertices)
    
    @staticmethod
    def calculate_area_regular_polygon(side: float, n: int) -> float:
        """정다각형의 면적 계산"""
        return 0.25 * n * side**2 * (1 / np.tan(np.pi / n))
    
    @staticmethod
    def calculate_area_polygon(vertices: List[Tuple[float, float]]) -> float:
        """다각형의 면적 계산 (신발끈 공식)"""
        if len(vertices) < 3:
            return 0
        
        n = len(vertices)
        area = 0
        
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        
        return abs(area) / 2
    
    @staticmethod
    def calculate_area_circle(radius: float) -> float:
        """원의 면적 계산"""
        return np.pi * radius**2
    
    @staticmethod
    def calculate_area_sector(radius: float, angle: float) -> float:
        """부채꼴의 면적 계산 (각도는 라디안)"""
        return 0.5 * radius**2 * angle
    
    @staticmethod
    def calculate_area_segment(radius: float, angle: float) -> float:
        """활꼴의 면적 계산 (각도는 라디안)"""
        sector_area = AreaTools.calculate_area_sector(radius, angle)
        triangle_area = 0.5 * radius**2 * np.sin(angle)
        return sector_area - triangle_area
    
    @staticmethod
    def calculate_midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
        """두 점의 중점 계산 (내부 계산용)"""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    