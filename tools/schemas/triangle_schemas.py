"""
삼각형 계산 입력 스키마 모듈

이 모듈은 삼각형 계산 도구에서 사용하는 입력 스키마들을 정의합니다.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class TriangleInput(BaseModel):
    """삼각형 계산 도구 입력 스키마"""
    vertices: List[List[float]] = Field(
        description="三角形的三个顶点坐标，格式为[[x1,y1], [x2,y2], [x3,y3]]",
        min_items=3,
        max_items=3
    )
    calculate: Optional[List[str]] = Field(
        default=None,
        description="需要计算的特殊项目，可选值：centroid（质心）, circumcenter（外心）, incenter（内心）, orthocenter（垂心）"
    )

class TriangleAreaInput(BaseModel):
    """삼각형 면적 계산 입력 스키마"""
    base: float = Field(..., description="三角形的底边长度")
    height: float = Field(..., description="三角形的高")

class TrianglePerimeterInput(BaseModel):
    """삼각형 둘레 계산 입력 스키마"""
    side1: float = Field(..., description="三角形的第一条边长度")
    side2: float = Field(..., description="三角形的第二条边长度")
    side3: float = Field(..., description="三角形的第三条边长度")

class TriangleAngleInput(BaseModel):
    """삼각형 각도 계산 입력 스키마"""
    side1: float = Field(..., description="三角形的第一条边长度")
    side2: float = Field(..., description="三角形的第二条边长度")
    side3: float = Field(..., description="三角形的第三条边长度")
    angle_type: str = Field(..., description="要计算的角类型：'A'（对边为side1）, 'B'（对边为side2）, 'C'（对边为side3）") 