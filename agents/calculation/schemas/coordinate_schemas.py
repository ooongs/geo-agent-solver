"""
좌표 계산 입력 스키마 모듈

이 모듈은 좌표 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MidpointInput(BaseModel):
    """중점 계산 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x2, y2]")

class SlopeInput(BaseModel):
    """기울기 계산 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x2, y2]")

class LineEquationInput(BaseModel):
    """직선 방정식 계산 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x2, y2]")

class CollinearInput(BaseModel):
    """공선성 확인 입력 스키마"""
    point1: List[float] = Field(..., description="第一个点的坐标 [x1, y1]")
    point2: List[float] = Field(..., description="第二个点的坐标 [x2, y2]")
    point3: List[float] = Field(..., description="第三个点的坐标 [x3, y3]")

class LinesParallelInput(BaseModel):
    """평행선 확인 입력 스키마"""
    line1: List[float] = Field(..., description="第一条直线的方程参数 [a1, b1, c1]，表示a1x + b1y + c1 = 0")
    line2: List[float] = Field(..., description="第二条直线的方程参数 [a2, b2, c2]，表示a2x + b2y + c2 = 0")

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