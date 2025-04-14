"""
길이 계산 입력 스키마 모듈

이 모듈은 길이 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Tuple, Dict, Any
from pydantic import BaseModel, Field


class LengthInput(BaseModel):
    """길이 계산 도구 입력 스키마"""
    points: Optional[List[List[float]]] = Field(
        default=None,
        description="需要计算距离的点坐标，格式为[[x1,y1], [x2,y2]]"
    )
    point: Optional[List[float]] = Field(
        default=None,
        description="用于计算到直线距离的点坐标，格式为[x, y]"
    )
    line: Optional[List[float]] = Field(
        default=None,
        description="直线参数，格式为[a, b, c]，表示ax + by + c = 0"
    )
    polygon: Optional[List[List[float]]] = Field(
        default=None,
        description="多边形的顶点坐标，格式为[[x1,y1], [x2,y2], ...]"
    )
    circle: Optional[Dict[str, Any]] = Field(
        default=None,
        description="圆的信息，格式为{\"radius\": r}，其中r为圆的半径"
    )
    angle: Optional[float] = Field(
        default=None,
        description="角度（以弧度为单位），用于计算弦长和弧长"
    )
    segment: Optional[List[List[float]]] = Field(
        default=None,
        description="线段的两个端点坐标，格式为[[x1,y1], [x2,y2]]"
    )
    division_ratio: Optional[float] = Field(
        default=None,
        description="线段分割比例"
    )
    internal_ratio: Optional[List[float]] = Field(
        default=None,
        description="内分比，格式为[m, n]"
    )
    external_ratio: Optional[List[float]] = Field(
        default=None,
        description="外分比，格式为[m, n]"
    )
    check_point: Optional[List[float]] = Field(
        default=None,
        description="需要检查是否在线段上的点坐标，格式为[x, y]"
    )


class DistanceBetweenPointsInput(BaseModel):
    """두 점 사이의 거리를 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x2, y2]")

class DistancePointToLineInput(BaseModel):
    """점과 직선 사이의 거리를 계산하는 입력 스키마"""
    point: List[float] = Field(..., description="点的坐标 [x, y]")
    line: List[float] = Field(..., description="直线的参数 [a, b, c]，表示 ax + by + c = 0")
    
class DistanceParallelLinesInput(BaseModel):
    """두 평행선 사이의 거리를 계산하는 입력 스키마"""
    line1: List[float] = Field(..., description="第一条直线的参数 [a1, b1, c1]，表示 a1x + b1y + c1 = 0")
    line2: List[float] = Field(..., description="第二条直线的参数 [a2, b2, c2]，表示 a2x + b2y + c2 = 0")
    
class PerimeterTriangleInput(BaseModel):
    """삼각형 둘레를 계산하는 입력 스키마"""
    points: List[List[float]] = Field(..., description="三角形三个顶点的坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]")
    
class PerimeterQuadrilateralInput(BaseModel):
    """사각형 둘레를 계산하는 입력 스키마"""
    points: List[List[float]] = Field(..., description="四边形四个顶点的坐标，格式为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")
    
class PerimeterPolygonInput(BaseModel):
    """다각형 둘레를 계산하는 입력 스키마"""
    points: List[List[float]] = Field(..., description="多边形顶点的坐标，格式为[[x1,y1], [x2,y2], ...]")
    
class CircumferenceInput(BaseModel):
    """원 둘레를 계산하는 입력 스키마"""
    radius: float = Field(..., description="圆的半径")

class ChordLengthInput(BaseModel):
    """현의 길이를 계산하는 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度或角度）")
    degrees: Optional[bool] = Field(False, description="角度是否以度为单位，True表示度，False表示弧度")
    
class ArcLengthInput(BaseModel):
    """호의 길이를 계산하는 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度或角度）")
    degrees: Optional[bool] = Field(False, description="角度是否以度为单位，True表示度，False表示弧度")
    
class MidpointInput(BaseModel):
    """두 점의 중점을 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x2, y2]")
    
class SegmentDivisionInput(BaseModel):
    """선분 분할점을 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="线段起点坐标 [x1, y1]")
    point2: List[float] = Field(..., description="线段终点坐标 [x2, y2]")
    ratio: float = Field(..., description="分割比例，表示从起点到分割点的距离与线段长度的比值")
    
class InternalDivisionPointInput(BaseModel):
    """내분점을 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="线段起点坐标 [x1, y1]")
    point2: List[float] = Field(..., description="线段终点坐标 [x2, y2]")
    m: float = Field(..., description="内分比的第一个值")
    n: float = Field(..., description="内分比的第二个值")
    
class ExternalDivisionPointInput(BaseModel):
    """외분점을 계산하는 입력 스키마"""
    point1: List[float] = Field(..., description="线段起点坐标 [x1, y1]")
    point2: List[float] = Field(..., description="线段终点坐标 [x2, y2]")
    m: float = Field(..., description="外分比的第一个值")
    n: float = Field(..., description="外分比的第二个值")
    
class PointOnSegmentInput(BaseModel):
    """점이 선분 위에 있는지 확인하는 입력 스키마"""
    point: List[float] = Field(..., description="需要检查的点的坐标 [x, y]")
    segment_start: List[float] = Field(..., description="线段起点坐标 [x1, y1]")
    segment_end: List[float] = Field(..., description="线段终点坐标 [x2, y2]")

class UnitConversionInput(BaseModel):
    """단위 변환 입력 스키마"""
    value: float = Field(..., description="要转换的值")
    from_unit: str = Field(..., description="原始单位：'m', 'cm', 'mm', 'km' 等")
    to_unit: str = Field(..., description="目标单位：'m', 'cm', 'mm', 'km' 等") 