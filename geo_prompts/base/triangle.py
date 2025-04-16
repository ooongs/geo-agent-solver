"""
삼각형 관련 프롬프트 템플릿 모듈

이 모듈은 삼각형 관련 문제를 해결하기 위한 프롬프트 템플릿을 제공합니다.
"""

from langchain.prompts import ChatPromptTemplate
from ..config import get_language


class TrianglePromptTemplate:
    """
    삼각형 관련 프롬프트 템플릿 클래스
    
    이 클래스는 삼각형 관련 문제를 해결하기 위한 다양한 프롬프트 템플릿을 제공합니다.
    """
    
    @staticmethod
    def get_triangle_calculation_prompt():
        """
        삼각형 계산을 위한 프롬프트 템플릿을 반환합니다.
        
        Returns:
            ChatPromptTemplate: 삼각형 계산 프롬프트 템플릿
        """
        language = get_language()
        
        if language == "en":
            from ..i18n.en.prompt_text import TRIANGLE_CALCULATION_PROMPT
        else:  # 기본값은 중국어
            from ..i18n.zh.prompt_text import TRIANGLE_CALCULATION_PROMPT
        
        return TRIANGLE_CALCULATION_PROMPT
    
    @staticmethod
    def get_triangle_json_template():
        """
        삼각형 계산 결과 JSON 템플릿을 반환합니다.
        
        Returns:
            str: 삼각형 계산 결과 JSON 템플릿
        """
        from ..templates.json_templates import TRIANGLE_JSON_TEMPLATE
        return TRIANGLE_JSON_TEMPLATE 