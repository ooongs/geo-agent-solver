"""
길이 관련 계산 도구

이 모듈은 중국 중학교 수준의 길이 관련 기하학 문제를 해결하기 위한 도구를 제공합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase

class LengthTools(GeometryToolBase):
    """길이 관련 계산 도구"""
    
    @staticmethod
    def calculate_distance_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """두 점 사이의 거리 계산"""
        return LengthTools.calculate_distance(p1, p2)
    
    @staticmethod
    def calculate_distance_point_to_line(point: Tuple[float, float], line: Tuple[float, float, float]) -> float:
        """점에서 직선까지의 거리 계산"""
        a, b, c = line
        return abs(a * point[0] + b * point[1] + c) / np.sqrt(a**2 + b**2)
    
    @staticmethod
    def calculate_distance_between_parallel_lines(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> float:
        """두 평행선 사이의 거리 계산"""
        a1, b1, c1 = line1
        a2, b2, c2 = line2
        
        # 두 직선이 평행한지 확인
        if abs(a1 * b2 - a2 * b1) > 1e-10:
            return float('inf')  # 평행하지 않은 경우
        
        # 평행한 경우 거리 계산
        return abs(c1 - c2 * (a1 / a2)) / np.sqrt(a1**2 + b1**2) if abs(a2) > 1e-10 else abs(c1 - c2 * (b1 / b2)) / np.sqrt(a1**2 + b1**2)
    
    @staticmethod
    def calculate_perimeter_triangle(vertices: List[Tuple[float, float]]) -> float:
        """삼각형의 둘레 계산"""
        if len(vertices) != 3:
            return 0
        
        p1, p2, p3 = vertices
        a = LengthTools.calculate_distance(p1, p2)
        b = LengthTools.calculate_distance(p2, p3)
        c = LengthTools.calculate_distance(p3, p1)
        
        return a + b + c
    
    @staticmethod
    def calculate_perimeter_quadrilateral(vertices: List[Tuple[float, float]]) -> float:
        """사각형의 둘레 계산"""
        if len(vertices) != 4:
            return 0
        
        p1, p2, p3, p4 = vertices
        a = LengthTools.calculate_distance(p1, p2)
        b = LengthTools.calculate_distance(p2, p3)
        c = LengthTools.calculate_distance(p3, p4)
        d = LengthTools.calculate_distance(p4, p1)
        
        return a + b + c + d
    
    @staticmethod
    def calculate_perimeter_polygon(vertices: List[Tuple[float, float]]) -> float:
        """다각형의 둘레 계산"""
        if len(vertices) < 3:
            return 0
        
        perimeter = 0
        n = len(vertices)
        
        for i in range(n):
            perimeter += LengthTools.calculate_distance(vertices[i], vertices[(i + 1) % n])
        
        return perimeter
    
    @staticmethod
    def calculate_circumference(radius: float) -> float:
        """원의 둘레 계산"""
        return 2 * np.pi * radius
    
    @staticmethod
    def calculate_chord_length(radius: float, angle: float) -> float:
        """현의 길이 계산 (각도는 라디안)"""
        return 2 * radius * np.sin(angle / 2)
    
    @staticmethod
    def calculate_arc_length(radius: float, angle: float) -> float:
        """호의 길이 계산 (각도는 라디안)"""
        return radius * angle
    
