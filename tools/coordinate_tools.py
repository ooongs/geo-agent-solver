"""
좌표 관련 계산 도구

이 모듈은 중국 중학교 수준의 좌표 기하학 문제를 해결하기 위한 도구를 제공합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from .base_tools import GeometryToolBase
from .schemas.coordinate_schemas import CoordinateInput

class CoordinateTools(GeometryToolBase):
    """좌표 관련 계산 도구"""
    
    @staticmethod
    def calculate_midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
        """두 점의 중점 계산"""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    
    @staticmethod
    def calculate_slope(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """두 점을 지나는 직선의 기울기 계산"""
        if abs(p2[0] - p1[0]) < 1e-10:
            return float('inf')  # 무한대 (수직선)
        return (p2[1] - p1[1]) / (p2[0] - p1[0])
    
    @staticmethod
    def calculate_line_equation(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float, float]:
        """두 점을 지나는 직선의 방정식 계산 (ax + by + c = 0 형태)"""
        if abs(p2[0] - p1[0]) < 1e-10:
            # 수직선: x = p1[0]
            return (1, 0, -p1[0])
        
        slope = CoordinateTools.calculate_slope(p1, p2)
        if abs(slope) < 1e-10:
            # 수평선: y = p1[1]
            return (0, 1, -p1[1])
        
        # 일반적인 경우: y = slope * x + intercept
        intercept = p1[1] - slope * p1[0]
        return (-slope, 1, -intercept)  # ax + by + c = 0 형태로 변환
    
    @staticmethod
    def are_points_collinear(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
        """세 점이 일직선 위에 있는지 확인"""
        return abs((p2[1] - p1[1]) * (p3[0] - p2[0]) - (p3[1] - p2[1]) * (p2[0] - p1[0])) < 1e-10
    
    @staticmethod
    def are_lines_parallel(line1: Tuple[float, float, float], line2: Tuple[float, float, float]) -> bool:
        """두 직선이 평행한지 확인"""
        # ax + by + c = 0 형태에서 기울기는 -a/b
        if abs(line1[1]) < 1e-10 and abs(line2[1]) < 1e-10:
            return True  # 두 직선 모두 수직선
        if abs(line1[1]) < 1e-10 or abs(line2[1]) < 1e-10:
            return False  # 한 직선만 수직선
        return abs(line1[0] / line1[1] - line2[0] / line2[1]) < 1e-10
    
    @staticmethod
    def calculate_coordinate_tool(input_json: str) -> str:
        """좌표 계산 도구 메인 함수"""
        try:
            data = CoordinateTools.parse_input(input_json)
            
            result = {}
            
            # 중점 계산
            if "points" in data and len(data["points"]) == 2:
                p1, p2 = data["points"]
                result["midpoint"] = CoordinateTools.calculate_midpoint(p1, p2)
                result["distance"] = CoordinateTools.calculate_distance(p1, p2)
                
                try:
                    result["slope"] = CoordinateTools.calculate_slope(p1, p2)
                    if result["slope"] == float('inf'):
                        result["slope"] = "无穷大（垂直线）"
                except:
                    result["slope"] = "无穷大（垂直线）"
                
                result["line_equation"] = CoordinateTools.calculate_line_equation(p1, p2)
            
            # 세 점이 일직선 위에 있는지 확인
            if "points" in data and len(data["points"]) == 3:
                p1, p2, p3 = data["points"]
                result["collinear"] = CoordinateTools.are_points_collinear(p1, p2, p3)
                if not result["collinear"]:
                    # 세 점이 일직선 상에 없으면 삼각형 정보 추가
                    result["triangle_area"] = 0.5 * abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])))
            
            # 두 직선의 관계 확인
            if "lines" in data and len(data["lines"]) == 2:
                line1, line2 = data["lines"]
                result["parallel"] = CoordinateTools.are_lines_parallel(line1, line2)
                if not result["parallel"]:
                    # 교점 계산
                    a1, b1, c1 = line1
                    a2, b2, c2 = line2
                    det = a1*b2 - a2*b1
                    if abs(det) < 1e-10:
                        raise ToolException("两条直线平行或重合，无法计算交点")
                    x = (b1*c2 - b2*c1) / det
                    y = (a2*c1 - a1*c2) / det
                    result["intersection"] = (x, y)
            
            if not result:
                raise ToolException("请提供有效的坐标数据，可以是两点（计算中点、距离等）或三点（检查共线性）或两条直线（检查平行性）")
                
            return CoordinateTools.format_output(result)
        except ToolException as e:
            return CoordinateTools.format_output({"error": str(e)})
        except Exception as e:
            return CoordinateTools.format_output({"error": f"坐标计算时出现错误：{str(e)}"}) 