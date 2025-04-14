"""
길이 계산 입력 스키마 모듈

이 모듈은 길이 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


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
