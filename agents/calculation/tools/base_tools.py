"""
기하학 도구의 기본 클래스

이 모듈은 모든 기하학 도구가 상속받는 기본 클래스를 정의합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math
import json
from langchain_core.tools import ToolException

class GeometryToolBase:
    """기하학 도구 기본 클래스"""
    
    @staticmethod
    def parse_input(input_json: str) -> Dict[str, Any]:
        """입력 JSON 문자열을 파싱"""
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            try:
                return json.loads(input_json)
            except json.JSONDecodeError:
                raise ToolException("无效的JSON格式，请确保输入是有效的JSON字符串")
        elif isinstance(input_json, dict):
            return input_json
        else:
            raise ToolException("无效的输入格式，请提供有效的JSON字符串或字典")
    
    @staticmethod
    def format_output(result: Dict[str, Any]) -> str:
        """출력을 JSON 문자열로 변환"""
        return json.dumps(result, ensure_ascii=False)
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """두 점 사이의 거리 계산"""
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
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