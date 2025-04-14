"""
각도 계산 입력 스키마 모듈

이 모듈은 각도 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class AngleInput(BaseModel):
    """각도 계산 도구 입력 스키마"""
    points: Optional[List[List[float]]] = Field(
        default=None,
        description="用于计算角度的点坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]，其中x2,y2是角的顶点"
    )
    lines: Optional[List[List[float]]] = Field(
        default=None,
        description="用于计算角度的直线参数，每条直线格式为[a, b, c]，表示ax + by + c = 0"
    )
    triangle: Optional[List[List[float]]] = Field(
        default=None,
        description="三角形的三个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]"
    )
    circle: Optional[Dict[str, Any]] = Field(
        default=None,
        description="圆的信息，格式为{\"center\": [x, y], \"radius\": r}"
    )

class RadiansToDegreesInput(BaseModel):
    """라디안을 도로 변환하는 입력 스키마"""
    radians: float = Field(..., description="要转换的弧度值")

class DegreesToRadiansInput(BaseModel):
    """도를 라디안으로 변환하는 입력 스키마"""
    degrees: float = Field(..., description="要转换的角度值")

class AngleBetweenPointsInput(BaseModel):
    """세 점 사이의 각도를 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    vertex: List[float] = Field(..., description="角的顶点坐标 [x2, y2]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x3, y3]") 