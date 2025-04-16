"""
각도 관련 계산 도구

이 모듈은 중국 중학교 수준의 각도 관련 기하학 문제를 해결하기 위한 도구를 제공합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from .base_tools import GeometryToolBase



class AngleTools(GeometryToolBase):
    """각도 관련 계산 도구"""
    
    @staticmethod
    def calculate_angle_three_points(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """세 점으로 이루어진 각도 계산 (라디안, p2가 각의 꼭지점)"""
        return AngleTools.calculate_angle(p1, p2, p3)
    
    @staticmethod
    def calculate_angle_two_lines(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> float:
        """두 직선 사이의 각도 계산 (라디안)"""
        # ax + by + c = 0 형태에서 직선의 법선 벡터는 (a, b)
        a1, b1, _ = line1
        a2, b2, _ = line2
        
        # 두 법선 벡터 사이의 각도 계산
        dot_product = a1 * a2 + b1 * b2
        norm1 = np.sqrt(a1**2 + b1**2)
        norm2 = np.sqrt(a2**2 + b2**2)
        
        # 코사인 값 계산
        cos_angle = dot_product / (norm1 * norm2)
        
        # 부동소수점 오차 처리
        cos_angle = max(min(cos_angle, 1.0), -1.0)
        
        # 각도 계산 (라디안)
        angle = np.arccos(cos_angle)
        
        # 항상 예각 또는 직각 반환 (0 ~ pi/2)
        return min(angle, np.pi - angle)
    
    @staticmethod
    def calculate_angle_two_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """두 벡터 사이의 각도 계산 (라디안)"""
        # 두 벡터의 내적 계산
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        norm1 = np.sqrt(v1[0]**2 + v1[1]**2)
        norm2 = np.sqrt(v2[0]**2 + v2[1]**2)
        
        # 코사인 값 계산
        cos_angle = dot_product / (norm1 * norm2)
        
        # 부동소수점 오차 처리
        cos_angle = max(min(cos_angle, 1.0), -1.0)
        
        # 각도 계산 (라디안)
        return np.arccos(cos_angle)
    
    @staticmethod
    def calculate_interior_angles_triangle(vertices: List[Tuple[float, float]]) -> List[float]:
        """삼각형 내각 계산 (라디안)"""
        if len(vertices) != 3:
            return [0, 0, 0]
        
        p1, p2, p3 = vertices
        angle1 = AngleTools.calculate_angle(p2, p1, p3)
        angle2 = AngleTools.calculate_angle(p1, p2, p3)
        angle3 = AngleTools.calculate_angle(p1, p3, p2)
        
        return [angle1, angle2, angle3]
    
    @staticmethod
    def calculate_exterior_angles_triangle(vertices: List[Tuple[float, float]]) -> List[float]:
        """삼각형 외각 계산 (라디안)"""
        interior_angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return [np.pi - angle for angle in interior_angles]
    
    @staticmethod
    def calculate_inscribed_angle(center: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """원에서의 내접각 계산 (라디안)"""
        # 중심각 계산
        central_angle = AngleTools.calculate_angle_two_vectors(
            (p1[0] - center[0], p1[1] - center[1]),
            (p2[0] - center[0], p2[1] - center[1])
        )
        
        # 내접각은 중심각의 절반
        return central_angle / 2
    
    @staticmethod
    def calculate_angle_bisector(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float, float]:
        """두 점을 향하는 각의 이등분선 직선 방정식 계산"""
        # 두 벡터 계산
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v3 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # 벡터 정규화
        norm1 = np.sqrt(v1[0]**2 + v1[1]**2)
        norm3 = np.sqrt(v3[0]**2 + v3[1]**2)
        
        v1_unit = (v1[0] / norm1, v1[1] / norm1)
        v3_unit = (v3[0] / norm3, v3[1] / norm3)
        
        # 이등분선 벡터 (두 단위 벡터의 합)
        bisector = (v1_unit[0] + v3_unit[0], v1_unit[1] + v3_unit[1])
        
        # 이등분선 벡터가 영벡터인 경우
        if abs(bisector[0]) < 1e-10 and abs(bisector[1]) < 1e-10:
            # 두 벡터가 정반대 방향인 경우, 수직 벡터 사용
            bisector = (-v1_unit[1], v1_unit[0])
        
        # 이등분선이 지나는 한 점 (각의 꼭지점)
        point = p2
        
        # 직선의 방정식 계산 (ax + by + c = 0)
        if abs(bisector[1]) < 1e-10:
            # 수평선
            return (0, 1, -point[1])
        
        slope = bisector[0] / bisector[1]
        intercept = point[1] - slope * point[0]
        
        return (-slope, 1, -intercept)
    
    @staticmethod
    def calculate_angle_trisection(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> List[Tuple[float, float, float]]:
        """각도를 세 등분하는 두 직선의 방정식 계산 (p1-p2-p3 각도 제외)"""
        # 두 벡터 계산
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v3 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # 벡터 정규화
        norm1 = np.sqrt(v1[0]**2 + v1[1]**2)
        norm3 = np.sqrt(v3[0]**2 + v3[1]**2)
        
        v1_unit = (v1[0] / norm1, v1[1] / norm1)
        v3_unit = (v3[0] / norm3, v3[1] / norm3)
        
        # 두 벡터 사이의 각도 계산
        dot_product = v1_unit[0] * v3_unit[0] + v1_unit[1] * v3_unit[1]
        angle = np.arccos(max(min(dot_product, 1.0), -1.0))
        
        # 각도를 삼등분하여 두 개의 새로운 벡터 계산
        trisection_lines = []
        for i in range(1, 3):  # 1/3, 2/3 위치에 직선 생성
            # 회전 각도 계산 (v1에서 시작하여 v3 방향으로)
            rotation_angle = angle * i / 3
            
            # 단위 벡터 v1을 회전
            cos_theta = np.cos(rotation_angle)
            sin_theta = np.sin(rotation_angle)
            
            # v1을 기준으로 회전 변환 적용
            # 2D 회전 변환: [cos θ, -sin θ; sin θ, cos θ] * [x; y]
            rotated_x = v1_unit[0] * cos_theta - v1_unit[1] * sin_theta
            rotated_y = v1_unit[0] * sin_theta + v1_unit[1] * cos_theta
            
            # 회전된 벡터
            trisect_vector = (rotated_x, rotated_y)
            
            # 직선의 방정식 계산 (ax + by + c = 0)
            # 방향 벡터가 (dx, dy)일 때, 직선의 법선 벡터는 (-dy, dx)
            a = -trisect_vector[1]
            b = trisect_vector[0]
            c = trisect_vector[1] * p2[0] - trisect_vector[0] * p2[1]
            
            trisection_lines.append((a, b, c))
        
        return trisection_lines
    
    @staticmethod
    def is_angle_acute(angle: float) -> bool:
        """예각인지 확인"""
        return 0 < angle < np.pi / 2
    
    @staticmethod
    def is_angle_right(angle: float) -> bool:
        """직각인지 확인"""
        return abs(angle - np.pi / 2) < 1e-10
    
    @staticmethod
    def is_angle_obtuse(angle: float) -> bool:
        """둔각인지 확인"""
        return np.pi / 2 < angle < np.pi
    
    @staticmethod
    def is_triangle_acute(vertices: List[Tuple[float, float]]) -> bool:
        """예각삼각형인지 확인"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return all(AngleTools.is_angle_acute(angle) for angle in angles)
    
    @staticmethod
    def is_triangle_right(vertices: List[Tuple[float, float]]) -> bool:
        """직각삼각형인지 확인"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return any(AngleTools.is_angle_right(angle) for angle in angles)
    
    @staticmethod
    def is_triangle_obtuse(vertices: List[Tuple[float, float]]) -> bool:
        """둔각삼각형인지 확인"""
        angles = AngleTools.calculate_interior_angles_triangle(vertices)
        return any(AngleTools.is_angle_obtuse(angle) for angle in angles)
    