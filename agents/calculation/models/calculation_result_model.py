from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

class CalculationResult(BaseModel):
    """用于存储计算结果的模型"""
    coordinates: Optional[Dict[str, List[float]]] = Field(None, description="坐标信息")
    lengths: Optional[Dict[str, float]] = Field(None, description="长度信息")
    angles: Optional[Dict[str, float]] = Field(None, description="角度信息")
    areas: Optional[Dict[str, float]] = Field(None, description="面积信息")
    perimeters: Optional[Dict[str, float]] = Field(None, description="周长信息")
    special_points: Optional[Dict[str, List[float]]] = Field(None, description="特殊点信息")
    circle_properties: Optional[Dict[str, Union[float, List[float]]]] = Field(None, description="圆的属性信息")
    ratios: Optional[Dict[str, float]] = Field(None, description="比例信息")
    other_results: Optional[Dict[str, Union[float, List[float], str]]] = Field(None, description="其他计算结果")

    def update_with(self, other: Dict) -> None:
        """用其他结果更新当前结果。"""
        for key, value in other.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if current_value is None:
                    setattr(self, key, value)
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    current_value.update(value)
                else:
                    setattr(self, key, value) 