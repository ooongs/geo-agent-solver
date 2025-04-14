"""
계산 관리자 프롬프트 패키지

이 패키지는 계산 관리자 에이전트에서 사용하는 프롬프트를 제공합니다.
"""

from agents.calculation.prompts.manager_prompt import CALCULATION_MANAGER_PROMPT
from agents.calculation.prompts.area_prompt import AREA_CALCULATION_PROMPT
from agents.calculation.prompts.angle_prompt import ANGLE_CALCULATION_PROMPT
from agents.calculation.prompts.coordinate_prompt import COORDINATE_CALCULATION_PROMPT
from agents.calculation.prompts.length_prompt import LENGTH_CALCULATION_PROMPT
from agents.calculation.prompts.triangle_prompt import TRIANGLE_CALCULATION_PROMPT
from agents.calculation.prompts.manager_prompt import MANAGER_JSON_TEMPLATE
from agents.calculation.prompts.area_prompt import AREA_JSON_TEMPLATE
from agents.calculation.prompts.angle_prompt import ANGLE_JSON_TEMPLATE
from agents.calculation.prompts.coordinate_prompt import COORDINATE_JSON_TEMPLATE
from agents.calculation.prompts.length_prompt import LENGTH_JSON_TEMPLATE
from agents.calculation.prompts.triangle_prompt import TRIANGLE_JSON_TEMPLATE

__all__ = [
    "CALCULATION_MANAGER_PROMPT", 
    "AREA_CALCULATION_PROMPT", 
    "ANGLE_CALCULATION_PROMPT", 
    "COORDINATE_CALCULATION_PROMPT", 
    "LENGTH_CALCULATION_PROMPT", 
    "TRIANGLE_CALCULATION_PROMPT",
    "MANAGER_JSON_TEMPLATE",
    "AREA_JSON_TEMPLATE",
    "ANGLE_JSON_TEMPLATE",
    "COORDINATE_JSON_TEMPLATE",
    "LENGTH_JSON_TEMPLATE",
    "TRIANGLE_JSON_TEMPLATE"
] 