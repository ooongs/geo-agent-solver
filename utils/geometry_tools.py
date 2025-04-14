import numpy as np
import sympy
from typing import Tuple, List, Dict, Any

class GeometryTools:
    """기하학적 계산을 위한 도구 클래스"""
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """두 점 사이의 거리 계산"""
        return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    @staticmethod
    def calculate_angle(point1: Tuple[float, float], point2: Tuple[float, float], point3: Tuple[float, float]) -> float:
        """세 점으로 이루어진 각도 계산 (라디안)"""
        vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)
        
        cos_angle = dot_product / (norm1 * norm2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # 수치적 안정성을 위한 클리핑
        
        return np.arccos(cos_angle)
    
    @staticmethod
    def calculate_circle_center(point1: Tuple[float, float], point2: Tuple[float, float], point3: Tuple[float, float]) -> Tuple[float, float]:
        """세 점을 지나는 원의 중심점 계산"""
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3
        
        # 중점 계산
        mid1 = ((x1 + x2) / 2, (y1 + y2) / 2)
        mid2 = ((x2 + x3) / 2, (y2 + y3) / 2)
        
        # 수직선의 기울기 계산
        slope1 = -(x2 - x1) / (y2 - y1) if y2 != y1 else float('inf')
        slope2 = -(x3 - x2) / (y3 - y2) if y3 != y2 else float('inf')
        
        # 중심점 계산
        if slope1 == float('inf'):
            center_x = mid1[0]
            center_y = slope2 * (center_x - mid2[0]) + mid2[1]
        elif slope2 == float('inf'):
            center_x = mid2[0]
            center_y = slope1 * (center_x - mid1[0]) + mid1[1]
        else:
            center_x = (mid2[1] - mid1[1] + slope1 * mid1[0] - slope2 * mid2[0]) / (slope1 - slope2)
            center_y = slope1 * (center_x - mid1[0]) + mid1[1]
        
        return (center_x, center_y)
    
    @staticmethod
    def calculate_triangle_centers(vertices: List[Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """삼각형의 중심점들 계산 (무게중심, 외심, 내심, 수심)"""
        if len(vertices) != 3:
            raise ValueError("삼각형은 정확히 3개의 꼭지점이 필요합니다.")
        
        # 무게중심 계산
        centroid = (
            sum(v[0] for v in vertices) / 3,
            sum(v[1] for v in vertices) / 3
        )
        
        # 외심 계산
        circumcenter = GeometryTools.calculate_circle_center(*vertices)
        
        # 내심 계산
        a = GeometryTools.calculate_distance(vertices[1], vertices[2])
        b = GeometryTools.calculate_distance(vertices[0], vertices[2])
        c = GeometryTools.calculate_distance(vertices[0], vertices[1])
        
        incenter = (
            (a * vertices[0][0] + b * vertices[1][0] + c * vertices[2][0]) / (a + b + c),
            (a * vertices[0][1] + b * vertices[1][1] + c * vertices[2][1]) / (a + b + c)
        )
        
        # 수심 계산
        orthocenter = GeometryTools.find_orthocenter(vertices)
        
        return {
            "centroid": centroid,
            "circumcenter": circumcenter,
            "incenter": incenter,
            "orthocenter": orthocenter
        }
    
    @staticmethod
    def check_congruent_triangles(triangle1: List[Tuple[float, float]], triangle2: List[Tuple[float, float]]) -> bool:
        """두 삼각형의 합동 여부 확인"""
        if len(triangle1) != 3 or len(triangle2) != 3:
            raise ValueError("삼각형은 정확히 3개의 꼭지점이 필요합니다.")
        
        # 각 변의 길이 계산
        sides1 = [
            GeometryTools.calculate_distance(triangle1[0], triangle1[1]),
            GeometryTools.calculate_distance(triangle1[1], triangle1[2]),
            GeometryTools.calculate_distance(triangle1[2], triangle1[0])
        ]
        sides2 = [
            GeometryTools.calculate_distance(triangle2[0], triangle2[1]),
            GeometryTools.calculate_distance(triangle2[1], triangle2[2]),
            GeometryTools.calculate_distance(triangle2[2], triangle2[0])
        ]
        
        # 변의 길이 정렬
        sides1.sort()
        sides2.sort()
        
        # SSS 합동 조건 확인
        return all(abs(s1 - s2) < 1e-10 for s1, s2 in zip(sides1, sides2))
    
    @staticmethod
    def check_similar_triangles(triangle1: List[Tuple[float, float]], triangle2: List[Tuple[float, float]]) -> bool:
        """두 삼각형의 닮음 여부 확인"""
        if len(triangle1) != 3 or len(triangle2) != 3:
            raise ValueError("삼각형은 정확히 3개의 꼭지점이 필요합니다.")
        
        # 각 변의 길이 계산
        sides1 = [
            GeometryTools.calculate_distance(triangle1[0], triangle1[1]),
            GeometryTools.calculate_distance(triangle1[1], triangle1[2]),
            GeometryTools.calculate_distance(triangle1[2], triangle1[0])
        ]
        sides2 = [
            GeometryTools.calculate_distance(triangle2[0], triangle2[1]),
            GeometryTools.calculate_distance(triangle2[1], triangle2[2]),
            GeometryTools.calculate_distance(triangle2[2], triangle2[0])
        ]
        
        # 변의 길이 정렬
        sides1.sort()
        sides2.sort()
        
        # 비율 계산
        ratios = [s1 / s2 for s1, s2 in zip(sides1, sides2)]
        
        # 모든 비율이 같은지 확인 (오차 허용)
        return all(abs(r - ratios[0]) < 1e-10 for r in ratios)
    
    @staticmethod
    def line_from_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float, float]:
        """두 점으로부터 직선의 방정식 계수 반환 (ax + by + c = 0 형태)"""
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = p2[0] * p1[1] - p1[0] * p2[1]
        return (a, b, c)
    
    @staticmethod
    def intersection_lines(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> Tuple[float, float]:
        """두 직선의 교점 계산"""
        a1, b1, c1 = line1
        a2, b2, c2 = line2
        
        # 평행한 경우 처리
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-10:
            return None
        
        x = (b1 * c2 - b2 * c1) / det
        y = (a2 * c1 - a1 * c2) / det
        return (x, y)
    
    @staticmethod
    def point_on_line_segment(p: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        """점 p가 선분 p1p2 위에 있는지 확인"""
        # 거리가 일치하는지 확인
        d1 = np.sqrt((p[0] - p1[0])**2 + (p[1] - p1[1])**2)
        d2 = np.sqrt((p[0] - p2[0])**2 + (p[1] - p2[1])**2)
        d = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
        # 부동소수점 오차 허용
        return abs(d1 + d2 - d) < 1e-10
    
    @staticmethod
    def perpendicular_line(line: Tuple[float, float, float], p: Tuple[float, float]) -> Tuple[float, float, float]:
        """점 p를 지나고 주어진 직선에 수직인 직선 계산"""
        a, b, _ = line
        # 수직 직선의 기울기는 원래 직선 기울기의 음의 역수
        return (b, -a, a * p[1] - b * p[0])
    
    @staticmethod
    def circle_from_center_radius(center: Tuple[float, float], radius: float) -> Dict[str, Any]:
        """중심과 반지름으로부터 원 정보 반환"""
        return {
            "center": center,
            "radius": radius,
            "equation": f"(x - {center[0]})^2 + (y - {center[1]})^2 = {radius}^2"
        }
    
    @staticmethod
    def triangle_area(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """세 점으로 이루어진 삼각형의 넓이 계산"""
        return 0.5 * abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1]))
    
    @staticmethod
    def calculate_triangle_area(vertices: List[Tuple[float, float]]) -> float:
        """삼각형 넓이 계산 (꼭지점 리스트 입력)"""
        if len(vertices) != 3:
            raise ValueError("삼각형은 정확히 3개의 꼭지점이 필요합니다.")
            
        return GeometryTools.triangle_area(vertices[0], vertices[1], vertices[2])
    
    @staticmethod
    def calculate_polygon_area(vertices: List[Tuple[float, float]]) -> float:
        """다각형 면적 계산 (신발끈 공식)"""
        n = len(vertices)
        if n < 3:
            return 0.0
            
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
            
        return abs(area) / 2.0
    
    @staticmethod
    def find_orthocenter(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """직각 삼각형의 수심 계산"""
        if len(vertices) != 3:
            raise ValueError("삼각형은 정확히 3개의 꼭지점이 필요합니다.")
            
        # 각 변의 방정식 계산
        lines = [
            GeometryTools.line_from_points(vertices[1], vertices[2]),
            GeometryTools.line_from_points(vertices[0], vertices[2]),
            GeometryTools.line_from_points(vertices[0], vertices[1])
        ]
        
        # 각 꼭지점에서 마주보는 변에 수직선 계산
        perp_lines = [
            GeometryTools.perpendicular_line(lines[0], vertices[0]),
            GeometryTools.perpendicular_line(lines[1], vertices[1]),
            GeometryTools.perpendicular_line(lines[2], vertices[2])
        ]
        
        # 두 수선의 교점(수심) 계산
        orthocenter = GeometryTools.intersection_lines(perp_lines[0], perp_lines[1])
        return orthocenter
    
    @staticmethod
    def is_collinear(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
        """세 점이 일직선 상에 있는지 확인"""
        area = GeometryTools.triangle_area(p1, p2, p3)
        return abs(area) < 1e-10
    
    @staticmethod
    def angle_bisector(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float, float]:
        """각 p1p2p3의 이등분선 계산"""
        # p2가 꼭지점
        d1 = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        d3 = np.sqrt((p3[0] - p2[0])**2 + (p3[1] - p2[1])**2)
        
        # 각 변을 길이로 정규화
        v1x = (p1[0] - p2[0]) / d1
        v1y = (p1[1] - p2[1]) / d1
        v3x = (p3[0] - p2[0]) / d3
        v3y = (p3[1] - p2[1]) / d3
        
        # 합벡터 계산
        bx = v1x + v3x
        by = v1y + v3y
        
        # 이등분선 방정식 계수 (ax + by + c = 0)
        a = -by
        b = bx
        c = by * p2[0] - bx * p2[1]
        
        return (a, b, c) 