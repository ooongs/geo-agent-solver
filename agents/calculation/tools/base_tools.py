"""
Base class for geometry tools

This module defines the base class that all geometry tools inherit from.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
import json
from langchain_core.tools import ToolException

class GeometryToolBase:
    """Base class for geometry tools"""
    
    @staticmethod
    def parse_input(input_json: str) -> Dict[str, Any]:
        """Parse input JSON string"""
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            try:
                return json.loads(input_json)
            except json.JSONDecodeError:
                raise ToolException("Invalid JSON format, please ensure the input is a valid JSON string")
        elif isinstance(input_json, dict):
            return input_json
        else:
            raise ToolException("Invalid input format, please provide a valid JSON string or dictionary")
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate distance between two points"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    @staticmethod
    def format_result(result: Any) -> str:
        """Format calculation result as JSON string"""
        if isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False)
        else:
            return json.dumps({"result": result}, ensure_ascii=False)
    
    @staticmethod
    def validate_point(point: Any) -> Tuple[float, float]:
        """Validate and convert point data to tuple format"""
        if isinstance(point, (list, tuple)) and len(point) == 2:
            try:
                return (float(point[0]), float(point[1]))
            except (ValueError, TypeError):
                raise ToolException("Point coordinates must be numeric values")
        else:
            raise ToolException("Invalid point format. Point must be a tuple or list of two numeric values")
    
    @staticmethod
    def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """세 점으로 이루어진 각도 계산 (라디안)"""
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        
        # 벡터 정규화
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        
        if v1_norm == 0 or v2_norm == 0:
            return 0
        
        # 코사인 값 계산
        cos_angle = np.dot(v1, v2) / (v1_norm * v2_norm)
        
        # 부동소수점 오차 처리
        cos_angle = max(min(cos_angle, 1.0), -1.0)
        
        # 각도 계산 (라디안)
        return np.arccos(cos_angle)
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """각도를 라디안으로 변환"""
        return degrees * math.pi / 180
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """라디안을 각도로 변환"""
        return radians * 180 / math.pi 