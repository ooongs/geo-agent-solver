"""
면적 계산 입력 스키마 모듈

이 모듈은 면적 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class TriangleAreaFromPointsInput(BaseModel):
    """삼각형 면적 계산 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="三角形的三个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]")

class TriangleAreaFromSidesInput(BaseModel):
    """삼각형 면적 계산 입력 스키마"""
    side1: float = Field(..., description="三角形的一条边长")
    side2: float = Field(..., description="三角形的另一条边长")
    side3: float = Field(..., description="三角形的第三条边长")

class TriangleAreaFromBaseHeightInput(BaseModel):
    """삼각형 면적 계산 입력 스키마"""
    base: float = Field(..., description="三角形的底边")
    height: float = Field(..., description="三角形的高")

class RectangleAreaFromPointsInput(BaseModel):
    """직사각형 면적 계산 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="矩形的四个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")

class RectangleAreaFromWidthHeightInput(BaseModel):
    """직사각형 면적 계산 입력 스키마"""
    width: float = Field(..., description="矩形的宽")
    height: float = Field(..., description="矩形的高")

class SquareAreaFromSideInput(BaseModel):
    """정사각형 면적 계산 입력 스키마"""
    side: float = Field(..., description="正方形的边长")

class ParallelogramAreaFromBaseHeightInput(BaseModel):
    """평행사변형 면적 계산 입력 스키마"""
    base: float = Field(..., description="平行四边形的底边")
    height: float = Field(..., description="平行四边形的高")

class ParallelogramAreaFromPointsInput(BaseModel):
    """평행사변형 면적 계산 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="平行四边形的四个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")
    
class RhombusAreaFromPointsInput(BaseModel):
    """마름모 면적 계산 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="菱形的四个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")

class RhombusAreaFromDiagonalsInput(BaseModel):
    diagonal1: float = Field(..., description="菱形的一条对角线")
    diagonal2: float = Field(..., description="菱形的另一条对角线")

class TrapezoidAreaFromPointsInput(BaseModel):
    """평행사변형 면적 계산 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="梯形的四个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")

class TrapezoidAreaFromBaseHeightInput(BaseModel):
    """평행사변형 면적 계산 입력 스키마"""
    base1: float = Field(..., description="梯形的上底")
    base2: float = Field(..., description="梯形的下底")
    height: float = Field(..., description="梯形的高")

class RegularPolygonAreaFromSideInput(BaseModel):
    """정다각형 면적 계산 입력 스키마"""
    side: float = Field(..., description="正多边形的边长")
    n: int = Field(..., description="正多边形的边数")

class PolygonAreaFromPointsInput(BaseModel):
    """다각형 면적 계산 입력 스키마"""
    vertices: List[List[float]] = Field(..., description="多边形的顶点坐标，格式为[[x1,y1], [x2,y2], ...]")

class CircleAreaFromRadiusInput(BaseModel):
    """원 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")


class SectorAreaFromRadiusAngleInput(BaseModel):
    """부채꼴 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度）")

class SegmentAreaFromRadiusAngleInput(BaseModel):
    """호 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")
    angle: float = Field(..., description="圆心角（弧度）")