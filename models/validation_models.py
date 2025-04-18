"""
검증 결과 관련 모델 정의

이 모듈은 GeoGebra 명령어 검증 결과를 표현하는 Pydantic 모델을 정의합니다.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from models.state_models import ConstructionPlan

class CommandAnalysis(BaseModel):
    command: str = Field(description="GeoGebra command")
    analysis: str = Field(description="Analysis of the command")

class ValidationResult(BaseModel):
    """검증 결과 모델"""
    analysis: str = Field(description="Extremely detailed analysis of the validation results, analyzing the correctness of each command line by line, clearly pointing out all issues (in Markdown format)")
    is_valid: bool = Field(description="Whether the commands are completely correct")
    errors: List[str] = Field(default_factory=list, description="All discovered errors, precisely described")
    warnings: List[str] = Field(default_factory=list, description="Potential issues or inelegant implementations")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions, can be provided even if the commands are correct")
    command_by_command_analysis: List[CommandAnalysis] = Field(default_factory=list, description="Detailed analysis of each command")
    construction_plan: Optional[ConstructionPlan] = Field(default=None, description="Re-planned construction plan")
    
class RegenerationResult(BaseModel):
    """명령어 재생성 결과 모델"""
    analysis: str = Field(description="Analysis of the reasons for validation failure (in Markdown format, detailed analysis)")
    fixed_issues: List[str] = Field(default_factory=list, description="Fixed issues extracted from the validation results")
    commands: List[str] = Field(default_factory=list, description="GeoGebra commands extracted from the validation results") 