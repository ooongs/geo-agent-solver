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
    
    @staticmethod
    def calculate_area_tool(input_json: str) -> str:
        """면적 계산 도구 메인 함수"""
        try:
            data = AreaTools.parse_input(input_json)
            
            result = {}
            
            # 삼각형 면적 계산
            if "triangle" in data:
                # 꼭짓점으로 계산
                if "vertices" in data["triangle"]:
                    vertices = data["triangle"]["vertices"]
                    if len(vertices) != 3:
                        raise ToolException("三角形必须有三个顶点")
                    result["triangle_area"] = AreaTools.calculate_area_triangle(vertices)
                
                # 세 변의 길이로 계산
                if "sides" in data["triangle"]:
                    if len(data["triangle"]["sides"]) != 3:
                        raise ToolException("三角形必须有三条边")
                    a, b, c = data["triangle"]["sides"]
                    # 삼각형 부등식 검증
                    if a + b <= c or a + c <= b or b + c <= a:
                        raise ToolException("三角形三边长不满足三角不等式，无法构成三角形")
                    result["triangle_area"] = AreaTools.calculate_area_triangle_from_sides(a, b, c)
                
                # 밑변과 높이로 계산
                if "base" in data["triangle"] and "height" in data["triangle"]:
                    base = data["triangle"]["base"]
                    height = data["triangle"]["height"]
                    if base <= 0 or height <= 0:
                        raise ToolException("三角形的底和高必须为正数")
                    result["triangle_area"] = AreaTools.calculate_area_triangle_from_base_height(base, height)
            
            # 사각형 면적 계산
            if "rectangle" in data:
                # 가로, 세로로 계산
                if "width" in data["rectangle"] and "height" in data["rectangle"]:
                    width = data["rectangle"]["width"]
                    height = data["rectangle"]["height"]
                    if width <= 0 or height <= 0:
                        raise ToolException("矩形的宽和高必须为正数")
                    result["rectangle_area"] = AreaTools.calculate_area_rectangle(width, height)
                
                # 꼭짓점으로 계산
                if "vertices" in data["rectangle"]:
                    vertices = data["rectangle"]["vertices"]
                    if len(vertices) != 4:
                        raise ToolException("矩形必须有四个顶点")
                    area = AreaTools.calculate_area_rectangle_from_points(vertices)
                    if area == 0:
                        raise ToolException("给定的四个点不能构成矩形")
                    result["rectangle_area"] = area
            
            # 정사각형 면적 계산
            if "square" in data and "side" in data["square"]:
                side = data["square"]["side"]
                if side <= 0:
                    raise ToolException("正方形的边长必须为正数")
                result["square_area"] = AreaTools.calculate_area_square(side)
            
            # 평행사변형 면적 계산
            if "parallelogram" in data:
                # 밑변과 높이로 계산
                if "base" in data["parallelogram"] and "height" in data["parallelogram"]:
                    base = data["parallelogram"]["base"]
                    height = data["parallelogram"]["height"]
                    if base <= 0 or height <= 0:
                        raise ToolException("平行四边形的底和高必须为正数")
                    result["parallelogram_area"] = AreaTools.calculate_area_parallelogram(base, height)
                
                # 꼭짓점으로 계산
                if "vertices" in data["parallelogram"]:
                    vertices = data["parallelogram"]["vertices"]
                    if len(vertices) != 4:
                        raise ToolException("平行四边形必须有四个顶点")
                    area = AreaTools.calculate_area_parallelogram_from_points(vertices)
                    if area == 0:
                        raise ToolException("给定的四个点不能构成平行四边形")
                    result["parallelogram_area"] = area
            
            # 마름모 면적 계산
            if "rhombus" in data:
                # 두 대각선으로 계산
                if "diagonal1" in data["rhombus"] and "diagonal2" in data["rhombus"]:
                    diagonal1 = data["rhombus"]["diagonal1"]
                    diagonal2 = data["rhombus"]["diagonal2"]
                    if diagonal1 <= 0 or diagonal2 <= 0:
                        raise ToolException("菱形的对角线长度必须为正数")
                    result["rhombus_area"] = AreaTools.calculate_area_rhombus(diagonal1, diagonal2)
                
                # 꼭짓점으로 계산
                if "vertices" in data["rhombus"]:
                    vertices = data["rhombus"]["vertices"]
                    if len(vertices) != 4:
                        raise ToolException("菱形必须有四个顶点")
                    area = AreaTools.calculate_area_rhombus_from_points(vertices)
                    if area == 0:
                        raise ToolException("给定的四个点不能构成菱形")
                    result["rhombus_area"] = area
            
            # 사다리꼴 면적 계산
            if "trapezoid" in data:
                # 평행한 두 변과 높이로 계산
                if "base1" in data["trapezoid"] and "base2" in data["trapezoid"] and "height" in data["trapezoid"]:
                    base1 = data["trapezoid"]["base1"]
                    base2 = data["trapezoid"]["base2"]
                    height = data["trapezoid"]["height"]
                    if base1 <= 0 or base2 <= 0 or height <= 0:
                        raise ToolException("梯形的两底和高必须为正数")
                    result["trapezoid_area"] = AreaTools.calculate_area_trapezoid(base1, base2, height)
                
                # 꼭짓점으로 계산
                if "vertices" in data["trapezoid"]:
                    vertices = data["trapezoid"]["vertices"]
                    if len(vertices) != 4:
                        raise ToolException("梯形必须有四个顶点")
                    result["trapezoid_area"] = AreaTools.calculate_area_trapezoid_from_points(vertices)
            
            # 정다각형 면적 계산
            if "regular_polygon" in data and "side" in data["regular_polygon"] and "n" in data["regular_polygon"]:
                side = data["regular_polygon"]["side"]
                n = data["regular_polygon"]["n"]
                if side <= 0:
                    raise ToolException("正多边形的边长必须为正数")
                if n < 3:
                    raise ToolException("正多边形的边数必须大于等于3")
                result["regular_polygon_area"] = AreaTools.calculate_area_regular_polygon(side, n)
            
            # 일반 다각형 면적 계산
            if "polygon" in data and "vertices" in data["polygon"]:
                vertices = data["polygon"]["vertices"]
                if len(vertices) < 3:
                    raise ToolException("多边形至少需要3个顶点")
                result["polygon_area"] = AreaTools.calculate_area_polygon(vertices)
            
            # 원 면적 계산
            if "circle" in data and "radius" in data["circle"]:
                radius = data["circle"]["radius"]
                if radius <= 0:
                    raise ToolException("圆的半径必须为正数")
                result["circle_area"] = AreaTools.calculate_area_circle(radius)
                
                # 부채꼴 면적 계산
                if "angle" in data:
                    angle = AreaTools.degrees_to_radians(data["angle"]) if "degrees" in data else data["angle"]
                    if angle <= 0 or angle > 2 * np.pi:
                        raise ToolException("扇形的角度必须为正数且不大于2π")
                    result["sector_area"] = AreaTools.calculate_area_sector(radius, angle)
                    result["segment_area"] = AreaTools.calculate_area_segment(radius, angle)
            
            if not result:
                raise ToolException("请提供有效的面积计算参数，例如三角形、矩形、圆等几何图形的必要信息")
                
            return AreaTools.format_output(result)
        except ToolException as e:
            return AreaTools.format_output({"error": str(e)})
        except Exception as e:
            return AreaTools.format_output({"error": f"计算面积时出现错误：{str(e)}"}) 