"""
원 관련 계산 도구

이 모듈은 중국 중학교 수준의 원 관련 기하학 문제를 해결하기 위한 도구를 제공합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase

class CircleInput(BaseModel):
    """원 계산 도구 입력 스키마"""
    center: Optional[List[float]] = Field(
        default=None,
        description="圆的中心坐标，格式为[x, y]"
    )
    radius: Optional[float] = Field(
        default=None,
        description="圆的半径"
    )
    three_points: Optional[List[List[float]]] = Field(
        default=None,
        description="三个点的坐标用于确定圆，格式为[[x1,y1], [x2,y2], [x3,y3]]"
    )
    points: Optional[List[List[float]]] = Field(
        default=None,
        description="需要检查与圆的关系的点，格式为[[x1,y1], [x2,y2], ...]"
    )
    external_point: Optional[List[float]] = Field(
        default=None,
        description="圆外一点，用于计算切线，格式为[x, y]"
    )
    angle: Optional[float] = Field(
        default=None,
        description="角度值（以度为单位），用于计算弦长、扇形面积等"
    )
    second_circle: Optional[Dict[str, Any]] = Field(
        default=None,
        description="第二个圆的信息，用于计算两圆交点，格式为{\"center\": [x, y], \"radius\": r}"
    )

class CircleTools(GeometryToolBase):
    """원 관련 계산 도구"""
    
    @staticmethod
    def calculate_area(radius: float) -> float:
        """원의 면적 계산"""
        return np.pi * radius**2
    
    @staticmethod
    def calculate_circumference(radius: float) -> float:
        """원의 둘레 계산"""
        return 2 * np.pi * radius
    
    @staticmethod
    def calculate_chord_length(radius: float, angle: float) -> float:
        """현의 길이 계산 (각도는 라디안)"""
        return 2 * radius * np.sin(angle / 2)
    
    @staticmethod
    def calculate_sector_area(radius: float, angle: float) -> float:
        """부채꼴의 면적 계산 (각도는 라디안)"""
        return 0.5 * radius**2 * angle
    
    @staticmethod
    def calculate_segment_area(radius: float, angle: float) -> float:
        """활꼴의 면적 계산 (각도는 라디안)"""
        sector_area = CircleTools.calculate_sector_area(radius, angle)
        triangle_area = 0.5 * radius**2 * np.sin(angle)
        return sector_area - triangle_area
    
    @staticmethod
    def is_point_inside_circle(center: Tuple[float, float], radius: float, point: Tuple[float, float]) -> bool:
        """점이 원 내부에 있는지 확인"""
        distance = CircleTools.calculate_distance(center, point)
        return distance < radius
    
    @staticmethod
    def is_point_on_circle(center: Tuple[float, float], radius: float, point: Tuple[float, float]) -> bool:
        """점이 원 위에 있는지 확인"""
        distance = CircleTools.calculate_distance(center, point)
        return abs(distance - radius) < 1e-10
    
    @staticmethod
    def calculate_tangent_point(center: Tuple[float, float], radius: float, external_point: Tuple[float, float]) -> List[Tuple[float, float]]:
        """외부 점에서 원에 그은 접선의 접점 계산"""
        # 중심과 외부 점 사이의 거리
        distance = CircleTools.calculate_distance(center, external_point)
        
        # 외부 점이 원 내부에 있으면 접점 없음
        if distance < radius:
            return []
        
        # 외부 점이 원 위에 있으면 그 점이 접점
        if abs(distance - radius) < 1e-10:
            return [external_point]
        
        # 중심에서 외부 점으로 향하는 벡터
        dx = external_point[0] - center[0]
        dy = external_point[1] - center[1]
        
        # 접선의 길이 (피타고라스 정리 이용)
        tangent_length = np.sqrt(distance**2 - radius**2)
        
        # 접점의 각도 계산
        angle = np.arccos(radius / distance)
        
        # 벡터 회전
        base_angle = np.arctan2(dy, dx)
        angle1 = base_angle + angle
        angle2 = base_angle - angle
        
        # 접점 계산
        tangent_point1 = (
            center[0] + radius * np.cos(angle1),
            center[1] + radius * np.sin(angle1)
        )
        
        tangent_point2 = (
            center[0] + radius * np.cos(angle2),
            center[1] + radius * np.sin(angle2)
        )
        
        return [tangent_point1, tangent_point2]
    
    @staticmethod
    def calculate_circle_intersection(center1: Tuple[float, float], radius1: float, 
                                     center2: Tuple[float, float], radius2: float) -> List[Tuple[float, float]]:
        """두 원의 교점 계산"""
        # 두 원의 중심 사이의 거리
        d = CircleTools.calculate_distance(center1, center2)
        
        # 교점이 없는 경우
        if d > radius1 + radius2 or d < abs(radius1 - radius2):
            return []
        
        # 원이 같은 경우 (무한히 많은 교점)
        if d < 1e-10 and abs(radius1 - radius2) < 1e-10:
            return []
        
        # 원이 접하는 경우 (한 점에서 접함)
        if abs(d - (radius1 + radius2)) < 1e-10 or abs(d - abs(radius1 - radius2)) < 1e-10:
            # 두 중심을 잇는 선 위의 점 계산
            t = radius1 / d
            return [(
                center1[0] + t * (center2[0] - center1[0]),
                center1[1] + t * (center2[1] - center1[1])
            )]
        
        # 두 원이 두 점에서 만나는 경우
        a = (radius1**2 - radius2**2 + d**2) / (2 * d)
        h = np.sqrt(radius1**2 - a**2)
        
        # 중간 점 계산
        x2 = center1[0] + a * (center2[0] - center1[0]) / d
        y2 = center1[1] + a * (center2[1] - center1[1]) / d
        
        # 교점 계산
        x3 = x2 + h * (center2[1] - center1[1]) / d
        y3 = y2 - h * (center2[0] - center1[0]) / d
        
        x4 = x2 - h * (center2[1] - center1[1]) / d
        y4 = y2 + h * (center2[0] - center1[0]) / d
        
        return [(x3, y3), (x4, y4)]
    
    @staticmethod
    def calculate_circle_from_three_points(p1: Tuple[float, float], p2: Tuple[float, float], 
                                          p3: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
        """세 점을 지나는 원의 중심과 반지름 계산"""
        # 세 점이 일직선상에 있는지 확인
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # 세 점이 일직선상에 있으면 원을 그릴 수 없음
        if abs((y2 - y1) * (x3 - x2) - (y3 - y2) * (x2 - x1)) < 1e-10:
            return ((0, 0), 0)
        
        # 세 점을 지나는 원의 중심은 세 점의 수직이등분선의 교점
        # 첫 번째 선분의 중점
        mx1 = (x1 + x2) / 2
        my1 = (y1 + y2) / 2
        
        # 두 번째 선분의 중점
        mx2 = (x2 + x3) / 2
        my2 = (y2 + y3) / 2
        
        # 첫 번째 선분에 수직인 직선의 기울기
        if abs(x2 - x1) < 1e-10:
            # 선분이 수직선인 경우
            s1 = 0
        else:
            s1 = -1 / ((y2 - y1) / (x2 - x1))
        
        # 두 번째 선분에 수직인 직선의 기울기
        if abs(x3 - x2) < 1e-10:
            # 선분이 수직선인 경우
            s2 = 0
        else:
            s2 = -1 / ((y3 - y2) / (x3 - x2))
        
        # 두 수직이등분선의 교점 (원의 중심)
        if abs(s1 - s2) < 1e-10:
            # 기울기가 같으면 교점이 없음
            return ((0, 0), 0)
        
        cx = 0
        cy = 0
        
        if abs(s1) < 1e-10:  # 첫 번째 직선이 수평선
            cx = mx1
            cy = s2 * (cx - mx2) + my2
        elif abs(s2) < 1e-10:  # 두 번째 직선이 수평선
            cx = mx2
            cy = s1 * (cx - mx1) + my1
        else:
            cx = (s1 * mx1 - s2 * mx2 + my2 - my1) / (s1 - s2)
            cy = s1 * (cx - mx1) + my1
        
        # 중심과 첫 번째 점 사이의 거리 (원의 반지름)
        radius = CircleTools.calculate_distance((cx, cy), p1)
        
        return ((cx, cy), radius)
    
    @staticmethod
    def calculate_circle_from_center_and_point(center: Tuple[float, float], point: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
        """중심과 한 점을 알 때 원의 중심과 반지름 계산"""
        radius = CircleTools.calculate_distance(center, point)
        return (center, radius)
    
    @staticmethod
    def calculate_circle_tool(input_json: str) -> str:
        """원 계산 도구 메인 함수"""
        try:
            data = CircleTools.parse_input(input_json)
            
            # 원의 정보
            center = data.get("center")
            radius = data.get("radius")
            
            # 다른 입력 방식
            three_points = data.get("three_points")
            
            result = {}
            
            # 세 점으로부터 원 계산
            if three_points and len(three_points) == 3:
                center, radius = CircleTools.calculate_circle_from_three_points(
                    three_points[0], three_points[1], three_points[2]
                )
                if radius == 0:
                    raise ToolException("无法通过给定的三点确定一个圆，这些点可能共线")
                result["center"] = center
                result["radius"] = radius
            
            # 기본 정보가 있는 경우
            if center and radius:
                result["area"] = CircleTools.calculate_area(radius)
                result["circumference"] = CircleTools.calculate_circumference(radius)
                
                # 추가 계산
                if "points" in data:
                    result["points_status"] = []
                    for point in data["points"]:
                        if CircleTools.is_point_inside_circle(center, radius, point):
                            result["points_status"].append("inside")
                        elif CircleTools.is_point_on_circle(center, radius, point):
                            result["points_status"].append("on")
                        else:
                            result["points_status"].append("outside")
                
                if "external_point" in data:
                    ext_point = data["external_point"]
                    if CircleTools.is_point_inside_circle(center, radius, ext_point):
                        raise ToolException("给定点在圆内，无法计算切线")
                    result["tangent_points"] = CircleTools.calculate_tangent_point(center, radius, ext_point)
                
                if "angle" in data:
                    angle = CircleTools.degrees_to_radians(data["angle"])
                    result["chord_length"] = CircleTools.calculate_chord_length(radius, angle)
                    result["sector_area"] = CircleTools.calculate_sector_area(radius, angle)
                    result["segment_area"] = CircleTools.calculate_segment_area(radius, angle)
                
                if "second_circle" in data:
                    second_circle = data["second_circle"]
                    if "center" in second_circle and "radius" in second_circle:
                        result["intersection_points"] = CircleTools.calculate_circle_intersection(
                            center, radius, second_circle["center"], second_circle["radius"]
                        )
            elif not three_points:
                raise ToolException("请提供圆的基本信息（中心坐标和半径）或三个点来确定圆")
            
            return CircleTools.format_output(result)
        except ToolException as e:
            return CircleTools.format_output({"error": str(e)})
        except Exception as e:
            return CircleTools.format_output({"error": f"计算圆时出现错误：{str(e)}"}) 