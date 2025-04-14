"""
면적 계산 입력 스키마 모듈

이 모듈은 면적 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class AreaInput(BaseModel):
    """면적 계산 도구 입력 스키마"""
    triangle: Optional[Dict[str, Any]] = Field(
        default=None,
        description="三角形相关信息，可包含vertices（顶点坐标）, sides（三边长）或base和height（底和高）"
    )
    rectangle: Optional[Dict[str, Any]] = Field(
        default=None,
        description="矩形相关信息，可包含width和height（宽和高）或vertices（顶点坐标）"
    )
    square: Optional[Dict[str, Any]] = Field(
        default=None,
        description="正方形相关信息，包含side（边长）"
    )
    parallelogram: Optional[Dict[str, Any]] = Field(
        default=None,
        description="平行四边形相关信息，可包含base和height（底和高）或vertices（顶点坐标）"
    )
    rhombus: Optional[Dict[str, Any]] = Field(
        default=None,
        description="菱形相关信息，可包含diagonal1和diagonal2（两对角线）或vertices（顶点坐标）"
    )
    trapezoid: Optional[Dict[str, Any]] = Field(
        default=None,
        description="梯形相关信息，可包含base1、base2和height（两底和高）或vertices（顶点坐标）"
    )
    regular_polygon: Optional[Dict[str, Any]] = Field(
        default=None,
        description="正多边形相关信息，包含side（边长）和n（边数）"
    )
    polygon: Optional[Dict[str, Any]] = Field(
        default=None,
        description="多边形相关信息，包含vertices（顶点坐标）"
    )
    circle: Optional[Dict[str, Any]] = Field(
        default=None,
        description="圆相关信息，包含radius（半径）"
    )
    angle: Optional[float] = Field(
        default=None,
        description="角度（弧度），用于计算扇形面积和弓形面积"
    )
    degrees: Optional[bool] = Field(
        default=None,
        description="如果为true，表示angle是以度为单位，需要转换为弧度"
    )


class RectangleAreaInput(BaseModel):
    """직사각형 면적 계산 입력 스키마"""
    length: float = Field(..., description="矩形的长")
    width: float = Field(..., description="矩形的宽")

class CircleAreaInput(BaseModel):
    """원 면적 계산 입력 스키마"""
    radius: float = Field(..., description="圆的半径")

class TriangleAreaInput(BaseModel):
    """삼각형 면적 계산 입력 스키마"""
    base: float = Field(..., description="三角形的底边")
    height: float = Field(..., description="三角形的高")

class PolygonAreaInput(BaseModel):
    """다각형 면적 계산 입력 스키마"""
    points: List[List[float]] = Field(..., description="多边形的顶点坐标，格式为[[x1,y1], [x2,y2], ...]") 