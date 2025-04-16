"""
각도 관련 프롬프트 템플릿 모듈

이 모듈은 각도 관련 문제를 해결하기 위한 프롬프트 템플릿을 제공합니다.
"""

from langchain.prompts import ChatPromptTemplate
from ..config import get_language


class AnglePromptTemplate:
    """
    각도 관련 프롬프트 템플릿 클래스
    
    이 클래스는 각도 관련 문제를 해결하기 위한 다양한 프롬프트 템플릿을 제공합니다.
    """
    
    @staticmethod
    def get_angle_calculation_prompt():
        """
        각도 계산을 위한 프롬프트 템플릿을 반환합니다.
        
        Returns:
            ChatPromptTemplate: 각도 계산 프롬프트 템플릿
        """
        language = get_language()
        
        if language == "en":
            from ..i18n.en.prompt_text import ANGLE_CALCULATION_PROMPT
        else:  # 기본값은 중국어
            from ..i18n.zh.prompt_text import ANGLE_CALCULATION_PROMPT
        
        return ANGLE_CALCULATION_PROMPT
    
    @staticmethod
    def get_angle_json_template():
        """
        각도 계산 결과 JSON 템플릿을 반환합니다.
        
        Returns:
            str: 각도 계산 결과 JSON 템플릿
        """
        from ..templates.json_templates import ANGLE_JSON_TEMPLATE
        return ANGLE_JSON_TEMPLATE 