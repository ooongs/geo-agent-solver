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
    
    @staticmethod
    def calculate_midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
        """두 점의 중점 계산"""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    
    @staticmethod
    def calculate_segment_division(p1: Tuple[float, float], p2: Tuple[float, float], ratio: float) -> Tuple[float, float]:
        """선분을 특정 비율로 나누는 점 계산"""
        return (
            p1[0] + ratio * (p2[0] - p1[0]),
            p1[1] + ratio * (p2[1] - p1[1])
        )
    
    @staticmethod
    def calculate_internal_division_point(p1: Tuple[float, float], p2: Tuple[float, float], m: float, n: float) -> Tuple[float, float]:
        """선분을 내분하는 점 계산 (m:n 비율)"""
        if abs(m + n) < 1e-10:
            return p1  # 비율이 잘못된 경우
        
        return (
            (m * p2[0] + n * p1[0]) / (m + n),
            (m * p2[1] + n * p1[1]) / (m + n)
        )
    
    @staticmethod
    def calculate_external_division_point(p1: Tuple[float, float], p2: Tuple[float, float], m: float, n: float) -> Tuple[float, float]:
        """선분을 외분하는 점 계산 (m:n 비율)"""
        if abs(m - n) < 1e-10:
            return p1  # 비율이 잘못된 경우
        
        return (
            (m * p2[0] - n * p1[0]) / (m - n),
            (m * p2[1] - n * p1[1]) / (m - n)
        )
    
    @staticmethod
    def is_point_on_segment(p: Tuple[float, float], segment_start: Tuple[float, float], segment_end: Tuple[float, float]) -> bool:
        """점이 선분 위에 있는지 확인"""
        # 점이 직선 위에 있는지 확인
        if abs((p[1] - segment_start[1]) * (segment_end[0] - segment_start[0]) - 
               (p[0] - segment_start[0]) * (segment_end[1] - segment_start[1])) > 1e-10:
            return False
        
        # 점이 선분의 범위 내에 있는지 확인
        if min(segment_start[0], segment_end[0]) <= p[0] <= max(segment_start[0], segment_end[0]) and \
           min(segment_start[1], segment_end[1]) <= p[1] <= max(segment_start[1], segment_end[1]):
            return True
        
        return False
    
    @staticmethod
    def calculate_length_tool(input_json: str) -> str:
        """길이 계산 도구 메인 함수"""
        try:
            data = LengthTools.parse_input(input_json)
            
            result = {}
            
            # 두 점 사이의 거리 계산
            if "points" in data and len(data["points"]) == 2:
                p1, p2 = data["points"]
                result["distance"] = LengthTools.calculate_distance_between_points(p1, p2)
                result["midpoint"] = LengthTools.calculate_midpoint(p1, p2)
            
            # 점과 직선 사이의 거리 계산
            if "point" in data and "line" in data:
                point = data["point"]
                line = data["line"]
                result["distance_to_line"] = LengthTools.calculate_distance_point_to_line(point, line)
            
            # 다각형의 둘레 계산
            if "polygon" in data:
                vertices = data["polygon"]
                if len(vertices) < 3:
                    raise ToolException("多边形至少需要3个顶点")
                    
                if len(vertices) == 3:
                    result["perimeter"] = LengthTools.calculate_perimeter_triangle(vertices)
                elif len(vertices) == 4:
                    result["perimeter"] = LengthTools.calculate_perimeter_quadrilateral(vertices)
                else:
                    result["perimeter"] = LengthTools.calculate_perimeter_polygon(vertices)
            
            # 원의 둘레 계산
            if "circle" in data and "radius" in data["circle"]:
                radius = data["circle"]["radius"]
                if radius <= 0:
                    raise ToolException("圆的半径必须为正数")
                    
                result["circumference"] = LengthTools.calculate_circumference(radius)
                
                # 현과 호의 길이 계산
                if "angle" in data:
                    angle = LengthTools.degrees_to_radians(data["angle"]) if "degrees" in data else data["angle"]
                    result["chord_length"] = LengthTools.calculate_chord_length(radius, angle)
                    result["arc_length"] = LengthTools.calculate_arc_length(radius, angle)
            
            # 선분 분할 계산
            if "segment" in data and len(data["segment"]) == 2:
                p1, p2 = data["segment"]
                
                if "division_ratio" in data:
                    ratio = data["division_ratio"]
                    result["division_point"] = LengthTools.calculate_segment_division(p1, p2, ratio)
                
                if "internal_ratio" in data:
                    m, n = data["internal_ratio"]
                    if m <= 0 or n <= 0:
                        raise ToolException("内分比的两个数值必须为正数")
                    result["internal_division_point"] = LengthTools.calculate_internal_division_point(p1, p2, m, n)
                
                if "external_ratio" in data:
                    m, n = data["external_ratio"]
                    if m <= 0 or n <= 0 or m == n:
                        raise ToolException("外分比的两个数值必须为正数且不相等")
                    result["external_division_point"] = LengthTools.calculate_external_division_point(p1, p2, m, n)
            
            # 점이 선분 위에 있는지 확인
            if "check_point" in data and "segment" in data and len(data["segment"]) == 2:
                p = data["check_point"]
                p1, p2 = data["segment"]
                result["is_on_segment"] = LengthTools.is_point_on_segment(p, p1, p2)
            
            if not result:
                raise ToolException("请提供有效的计算参数，例如两点（计算距离）、点和线（计算点到线的距离）或多边形（计算周长）")
                
            return LengthTools.format_output(result)
        except ToolException as e:
            return LengthTools.format_output({"error": str(e)})
        except Exception as e:
            return LengthTools.format_output({"error": f"计算长度时出现错误：{str(e)}"}) 