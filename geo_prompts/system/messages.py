"""
시스템 메시지 관리 모듈

이 모듈은 다국어 시스템 메시지를 관리합니다.
"""

from ..config import get_language

# 계산 유형 목록
CALCULATION_TYPES = [
    "default", "triangle", "circle", "angle", 
    "length", "area", "coordinate", "manager", "merger"
]

# 시스템 메시지 유형 목록
SYSTEM_MESSAGE_TYPES = [
    "calculation", "planner", "geogebra", "parsing",
    "explanation", "validation", "command_selection"
]

def get_calculation_system_message(calc_type="default"):
    """
    계산 유형에 맞는 시스템 메시지를 반환합니다.
    
    Args:
        calc_type (str): 계산 유형 (default, triangle, circle, angle, length, area, coordinate, manager, merger)
        
    Returns:
        str: 해당 계산 유형의 시스템 메시지
    """
    language = get_language()
    
    if calc_type not in CALCULATION_TYPES:
        print(f"경고: 알 수 없는 계산 유형 '{calc_type}'입니다. 기본값을 사용합니다.")
        calc_type = "default"
    
    if language == "en":
        from ..i18n.en.system_text import CALCULATION_SYSTEM_MESSAGES
    else:  # 기본값은 중국어
        from ..i18n.zh.system_text import CALCULATION_SYSTEM_MESSAGES
    
    return CALCULATION_SYSTEM_MESSAGES.get(calc_type, CALCULATION_SYSTEM_MESSAGES["default"])

def get_system_message(message_type="default"):
    """
    메시지 유형에 맞는 시스템 메시지를 반환합니다.
    
    Args:
        message_type (str): 메시지 유형 (calculation, planner, geogebra, parsing, explanation, validation, command_selection)
        
    Returns:
        str: 해당 메시지 유형의 시스템 메시지
    """
    language = get_language()
    
    if language == "en":
        from ..i18n.en.system_text import SYSTEM_MESSAGES, DEFAULT_SYSTEM_MESSAGE
    else:  # 기본값은 중국어
        from ..i18n.zh.system_text import SYSTEM_MESSAGES, DEFAULT_SYSTEM_MESSAGE
    
    if message_type == "default":
        return DEFAULT_SYSTEM_MESSAGE
        
    return SYSTEM_MESSAGES.get(message_type, DEFAULT_SYSTEM_MESSAGE) 