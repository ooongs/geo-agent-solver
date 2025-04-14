"""
JSON 파싱 유틸리티 모듈

이 모듈은 LLM 출력에서 JSON을 추출하고 파싱하는 유틸리티 함수를 제공합니다.
마크다운 코드 블록, 일반 JSON 문자열 등 다양한 형식을 처리합니다.
"""

import json
import re
from typing import Any, Type, TypeVar, Optional, Union
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def parse_llm_json_output(content: Any, model_class: Type[T]) -> Union[T, dict]:
    """
    LLM 출력에서 JSON을 추출하고 지정된 Pydantic 모델로 파싱합니다.
    
    마크다운 코드 블록(```json ```) 형식, 일반 JSON 문자열 등 다양한 형식을 처리합니다.
    
    Args:
        content: LLM 출력 내용 (문자열 또는 AIMessage 객체)
        model_class: 파싱 결과를 변환할 Pydantic 모델 클래스
        
    Returns:
        파싱된 Pydantic 모델 객체 또는 dict
        
    Raises:
        ValueError: JSON 파싱에 실패한 경우
    """
    # content가 AIMessage 객체인지 확인하고 문자열 추출
    if hasattr(content, 'content'):
        content = content.content
    
    # 문자열이 아닌 경우 처리
    if not isinstance(content, str):
        raise ValueError(f"지원되지 않는 입력 유형: {type(content)}")
    
    # 마크다운 코드 블록 처리 (```json ... ```)
    if "```json" in content or "```" in content:
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1).strip()
    
    # JSON 형식 문자열 처리
    if content.strip().startswith('{'):
        try:
            parsed_json = json.loads(content)
            if model_class:
                return model_class(**parsed_json)
            return parsed_json
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {str(e)}")
        except Exception as e:
            raise ValueError(f"Pydantic 모델 변환 실패: {str(e)}")
    
    # JSON 형식이 아닌 경우
    raise ValueError("유효한 JSON 형식이 아닙니다")

def safe_parse_llm_json_output(content: Any, model_class: Type[T], output_parser=None) -> Optional[Union[T, dict]]:
    """
    LLM 출력에서 JSON을 안전하게 추출하고 파싱합니다.
    
    파싱에 실패해도 예외를 발생시키지 않고 None을 반환합니다.
    output_parser가 제공된 경우 파싱 실패 시 대체 방법으로 사용합니다.
    
    Args:
        content: LLM 출력 내용 (문자열 또는 AIMessage 객체)
        model_class: 파싱 결과를 변환할 Pydantic 모델 클래스
        output_parser: 대체 파서 (옵션)
        
    Returns:
        파싱된 Pydantic 모델 객체, dict 또는 None (파싱 실패 시)
    """
    try:
        return parse_llm_json_output(content, model_class)
    except ValueError:
        if output_parser:
            try:
                # content가 AIMessage 객체인지 확인하고 문자열 추출
                if hasattr(content, 'content'):
                    content = content.content
                return output_parser.parse(content)
            except Exception:
                pass
        return None 