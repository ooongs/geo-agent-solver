"""
검증 결과 관련 모델 정의

이 모듈은 GeoGebra 명령어 검증 결과를 표현하는 Pydantic 모델을 정의합니다.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    """검증 결과 모델"""
    analysis: str = Field(description="对验证结果的分析（用 Markdown 格式，详细分析）")
    is_valid: bool = Field(description="验证是否成功")
    errors: List[str] = Field(default_factory=list, description="从验证结果中提取的错误信息")
    warnings: List[str] = Field(default_factory=list, description="从验证结果中提取的警告信息")
    suggestions: List[str] = Field(default_factory=list, description="从验证结果中提取的建议信息")
    
class RegenerationResult(BaseModel):
    """명령어 재생성 결과 모델"""
    analysis: str = Field(description="对验证失败原因的分析（用 Markdown 格式，详细分析）")
    fixed_issues: List[str] = Field(default_factory=list, description="从验证结果中提取的修复的问题")
    commands: List[str] = Field(default_factory=list, description="从验证结果中提取的GeoGebra命令") 