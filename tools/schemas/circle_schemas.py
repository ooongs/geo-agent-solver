"""
원 계산 입력 스키마 모듈

이 모듈은 원 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class CircleInput(BaseModel):
    """원 계산 도구 입력 스키마"""
    radius: Optional[float] = Field(
        default=None,
        description="圆的半径"
    )
    diameter: Optional[float] = Field(
        default=None,
        description="圆的直径"
    )
    center: Optional[List[float]] = Field(
        default=None,
        description="圆心坐标 [x, y]"
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

class CircleAreaInput(BaseModel):
    """원 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")

class CircleCircumferenceInput(BaseModel):
    """원 둘레 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")

class CircleDiameterInput(BaseModel):
    """원 지름 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")

class CircleRadiusInput(BaseModel):
    """원 반지름 계산 입력 스키마"""
    diameter: float = Field(..., description="圆的直径")

class ChordLengthInput(BaseModel):
    """현의 길이 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度）")

class SectorAreaInput(BaseModel):
    """부채꼴 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度）")

class SegmentAreaInput(BaseModel):
    """활꼴 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度）")

class PointCirclePositionInput(BaseModel):
    """점과 원의 위치 관계 확인 입력 스키마"""
    center: List[float] = Field(..., description="圆心坐标 [x, y]")
    radius: float = Field(..., description="圆的半径")
    point: List[float] = Field(..., description="需要检查的点坐标 [x, y]")

class TangentPointsInput(BaseModel):
    """외부 점에서 원에 그은 접선의 접점 계산 입력 스키마"""
    center: List[float] = Field(..., description="圆心坐标 [x, y]")
    radius: float = Field(..., description="圆的半径")
    external_point: List[float] = Field(..., description="圆外一点坐标 [x, y]")

class CircleIntersectionInput(BaseModel):
    """두 원의 교점 계산 입력 스키마"""
    center1: List[float] = Field(..., description="第一个圆的圆心坐标 [x1, y1]")
    radius1: float = Field(..., description="第一个圆的半径")
    center2: List[float] = Field(..., description="第二个圆的圆心坐标 [x2, y2]")
    radius2: float = Field(..., description="第二个圆的半径")

class CircleFromThreePointsInput(BaseModel):
    """세 점으로부터 원 계산 입력 스키마"""
    points: List[List[float]] = Field(..., description="三个点的坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]") 