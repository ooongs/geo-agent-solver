"""
GeoGebra 프롬프트 패키지

이 패키지는 GeoGebra 명령어 생성 및 검증에 사용되는 프롬프트 템플릿을 제공합니다.
환경 변수 LANGUAGE에 따라 언어별 프롬프트가 로드됩니다.
"""

from .config import get_language, set_language

# 현재 설정된 언어 가져오기
language = get_language()

# 언어 설정에 따라 적절한 프롬프트 모듈 가져오기
if language == "en":
    from .i18n.en.prompt_text import (
        PARSING_PROMPT,
        PLANNER_PROMPT,
        GEOGEBRA_COMMAND_PROMPT,
        VALIDATION_PROMPT,
        COMMAND_REGENERATION_PROMPT,
        EXPLANATION_PROMPT,
        COMMAND_SELECTION_PROMPT,
        # Calculation Prompts ------------------------------------------------------------
        CALCULATION_MANAGER_PROMPT,
        AREA_CALCULATION_PROMPT,
        ANGLE_CALCULATION_PROMPT,
        COORDINATE_CALCULATION_PROMPT,
        LENGTH_CALCULATION_PROMPT,
        TRIANGLE_CALCULATION_PROMPT,
        RESULT_MERGER_PROMPT,
        CIRCLE_CALCULATION_PROMPT,
    )
    # 시스템 메시지 가져오기
    from .i18n.en.system_text import (
        CALCULATION_SYSTEM_MESSAGES,
        SYSTEM_MESSAGES,
        DEFAULT_SYSTEM_MESSAGE
    )
else:  # 기본값은 중국어
    from .i18n.zh.prompt_text import (
        PARSING_PROMPT,
        PLANNER_PROMPT,
        GEOGEBRA_COMMAND_PROMPT,
        VALIDATION_PROMPT,
        COMMAND_REGENERATION_PROMPT,
        EXPLANATION_PROMPT,
        COMMAND_SELECTION_PROMPT,
        # Calculation Prompts ------------------------------------------------------------
        CALCULATION_MANAGER_PROMPT,
        AREA_CALCULATION_PROMPT,
        ANGLE_CALCULATION_PROMPT,
        COORDINATE_CALCULATION_PROMPT,
        LENGTH_CALCULATION_PROMPT,
        TRIANGLE_CALCULATION_PROMPT,
        CIRCLE_CALCULATION_PROMPT,
        RESULT_MERGER_PROMPT,
    )
    # 시스템 메시지 가져오기
    from .i18n.zh.system_text import (
        CALCULATION_SYSTEM_MESSAGES,
        SYSTEM_MESSAGES,
        DEFAULT_SYSTEM_MESSAGE
    )

# 시스템 메시지 함수 가져오기
from .system import get_system_message, get_calculation_system_message, CALCULATION_TYPES

# 템플릿 임포트
from geo_prompts.templates.json_templates import (
    PLANNER_CALCULATION_JSON_TEMPLATE,
    PLANNER_NO_CALCULATION_JSON_TEMPLATE,
    VALIDATION_JSON_TEMPLATE,
    COMMAND_SELECTION_TEMPLATE,
    COMMAND_GENERATION_TEMPLATE,
    COMMAND_REGENERATION_JSON_TEMPLATE,
    MANAGER_JSON_TEMPLATE,  # calculation_manager_agent에서 사용하는 JSON 템플릿
    TRIANGLE_JSON_TEMPLATE,
    ANGLE_JSON_TEMPLATE,
    COORDINATE_JSON_TEMPLATE,
    LENGTH_JSON_TEMPLATE,
    AREA_JSON_TEMPLATE,
    CIRCLE_JSON_TEMPLATE,
    MERGER_JSON_TEMPLATE
)

# 패키지 레벨에서 노출되는 변수와 함수
__all__ = [
    # 언어 설정 함수
    "get_language",
    "set_language",
    
    # 기본 프롬프트
    "PARSING_PROMPT",
    "PLANNER_PROMPT",
    "GEOGEBRA_COMMAND_PROMPT",
    "VALIDATION_PROMPT",
    "COMMAND_REGENERATION_PROMPT",
    "EXPLANATION_PROMPT",
    "COMMAND_SELECTION_PROMPT",
    
    # 계산 에이전트 프롬프트
    "CALCULATION_MANAGER_PROMPT", 
    "AREA_CALCULATION_PROMPT", 
    "ANGLE_CALCULATION_PROMPT", 
    "COORDINATE_CALCULATION_PROMPT", 
    "LENGTH_CALCULATION_PROMPT", 
    "TRIANGLE_CALCULATION_PROMPT",
    "CIRCLE_CALCULATION_PROMPT",
    "RESULT_MERGER_PROMPT",

    # JSON 템플릿
    "PLANNER_CALCULATION_JSON_TEMPLATE",
    "PLANNER_NO_CALCULATION_JSON_TEMPLATE",
    "COMMAND_SELECTION_TEMPLATE",
    "COMMAND_GENERATION_TEMPLATE",
    "VALIDATION_JSON_TEMPLATE",
    "COMMAND_REGENERATION_JSON_TEMPLATE",
    "MANAGER_JSON_TEMPLATE",
    "TRIANGLE_JSON_TEMPLATE",
    "ANGLE_JSON_TEMPLATE",
    "COORDINATE_JSON_TEMPLATE",
    "LENGTH_JSON_TEMPLATE",
    "AREA_JSON_TEMPLATE",
    "CIRCLE_JSON_TEMPLATE",
    "MERGER_JSON_TEMPLATE",
    
    # 시스템 메시지 관련
    "get_system_message",
    "get_calculation_system_message", 
    "CALCULATION_TYPES",
    "CALCULATION_SYSTEM_MESSAGES",
    "SYSTEM_MESSAGES",
    "DEFAULT_SYSTEM_MESSAGE"
]
