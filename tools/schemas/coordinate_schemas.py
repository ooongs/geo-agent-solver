"""
좌표 계산 입력 스키마 모듈

이 모듈은 좌표 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class CoordinateInput(BaseModel):
    """좌표 계산 도구 입력 스키마"""
    points: Optional[List[List[float]]] = Field(
        default=None,
        description="需要处理的点的坐标，格式为[[x1,y1], [x2,y2], ...] 等"
    )
    lines: Optional[List[List[float]]] = Field(
        default=None,
        description="直线的参数，每条直线格式为[a, b, c]，表示ax + by + c = 0"
    )

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