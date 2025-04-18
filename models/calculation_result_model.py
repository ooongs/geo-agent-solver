from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field

class CalculationResult(BaseModel):
    """Calculation Result Generated by Calculation Agents"""
    task_id: Optional[str] = Field(None, description="Task ID")
    success: Optional[bool] = Field(True, description="Success or Failure")
    # 기본 기하학적 정보 (대부분 문제에 공통)
    coordinates: Optional[Dict[str, List[float]]] = Field(None, description="Coordinates")
    lengths: Optional[Dict[str, float]] = Field(None, description="Lengths")
    angles: Optional[Dict[str, float]] = Field(None, description="Angles")
    areas: Optional[Dict[str, float]] = Field(None, description="Areas")
    
    # 범용적 확장 필드
    geometric_elements: Optional[Dict[str, Any]] = Field(None, description="Various geometric elements")
    derived_data: Optional[Dict[str, Any]] = Field(None, description="Derived data from calculations")
    explanation: Optional[str] = Field(None, description="Calculation explanation")
    
    # 임의 확장을 위한 필드
    extras: Optional[Dict[str, Any]] = Field(None, description="Problem-specific extension data")

    def update_with(self, other: Dict) -> None:
        """Update current result with other result."""
        for key, value in other.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if current_value is None:
                    setattr(self, key, value)
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    current_value.update(value)
                else:
                    setattr(self, key, value)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, supporting both Pydantic v1 and v2."""
        try:
            # Try Pydantic v2 method
            return self.model_dump(exclude_none=True)
        except AttributeError:
            # Fallback to Pydantic v1 method
            return self.dict(exclude_none=True) 