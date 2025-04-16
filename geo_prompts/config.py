"""
언어 및 환경 설정 관리 모듈

이 모듈은 geo_prompts 패키지에서 사용할 언어 및 환경 설정을 관리합니다.
환경 변수 LANGUAGE를 통해 언어 설정을 변경할 수 있습니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지원되는 언어 목록
SUPPORTED_LANGUAGES = ['en', 'zh']

# 환경 변수에서 언어 설정 가져오기 (기본값은 중국어)
LANGUAGE = os.getenv("LANGUAGE", "zh").lower()

# 유효한 언어인지 확인
if LANGUAGE not in SUPPORTED_LANGUAGES:
    print(f"경고: 지원되지 않는 언어 '{LANGUAGE}'입니다. 기본값 'zh'로 설정합니다.")
    LANGUAGE = "zh"

def get_language():
    """현재 설정된 언어를 반환합니다."""
    return LANGUAGE

def set_language(language):
    """
    언어 설정을 변경합니다.
    
    Args:
        language (str): 설정할 언어 코드 ('en' 또는 'zh')
        
    Returns:
        bool: 설정 성공 여부
    """
    global LANGUAGE
    language = language.lower()
    
    if language in SUPPORTED_LANGUAGES:
        LANGUAGE = language
        return True
    else:
        print(f"오류: 지원되지 않는 언어 '{language}'입니다. 'en' 또는 'zh'만 사용 가능합니다.")
        return False 