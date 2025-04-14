"""
각도 계산 입력 스키마 모듈

이 모듈은 각도 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class RadiansToDegreesInput(BaseModel):
    """라디안을 도로 변환하는 입력 스키마"""
    radians: float = Field(..., description="要转换的弧度值")

class DegreesToRadiansInput(BaseModel):
    """도를 라디안으로 변환하는 입력 스키마"""
    degrees: float = Field(..., description="要转换的角度值")

class AngleClassificationInput(BaseModel):
    """각도 분류를 수행하는 입력 스키마"""
    angle_rad: float = Field(..., description="要分类的角度值（弧度）")
    angle_deg: float = Field(..., description="要分类的角度值（度）")

class InscribedAngleInput(BaseModel):
    """원에서의 내접각을 계산하는 입력 스키마"""
    center: List[float] = Field(..., description="圆的中心坐标，格式为[x, y]")
    point1: List[float] = Field(..., description="第一个点的坐标，格式为[x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标，格式为[x2, y2]")

class AngleTriangleInput(BaseModel):
    """삼각형 내각을 계산하는 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="三角形的三个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]")

class AngleBetweenVectorsInput(BaseModel):
    vector1: List[float] = Field(..., description="第一个向量的坐标，格式为[x1, y1]")
    vector2: List[float] = Field(..., description="第二个向量的坐标，格式为[x2, y2]")

class AngleBetweenLinesInput(BaseModel):
    line1: List[float] = Field(..., description="第一条直线的参数，格式为[a, b, c]，表示ax + by + c = 0")
    line2: List[float] = Field(..., description="第二条直线的参数，格式为[a, b, c]，表示ax + by + c = 0")

class AngleBetweenPointsInput(BaseModel):
    """세 점 사이의 각도를 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    vertex: List[float] = Field(..., description="角的顶点坐标 [x2, y2]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x3, y3]") 