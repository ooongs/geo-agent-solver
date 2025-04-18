"""
고급 JSON 파싱 유틸리티 모듈

이 모듈은 LLM 출력에서 JSON을 추출하고 파싱하는 다양한 유틸리티 함수를 제공합니다.
여러 형식(마크다운 코드 블록, 일반 JSON 문자열 등)을 처리하고
강력한 오류 처리와 복구 메커니즘을 포함합니다.
"""

import json
import re
from typing import Any, Type, TypeVar, Optional, Union, Dict, List, Callable
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

class ParseError(Exception):
    """JSON 파싱 중 발생하는 오류를 위한 기본 예외 클래스"""
    pass

class ContentExtractionError(ParseError):
    """콘텐츠 추출 중 발생하는 오류"""
    pass

class JSONParseError(ParseError):
    """JSON 파싱 중 발생하는 오류"""
    pass

class ModelConversionError(ParseError):
    """모델 변환 중 발생하는 오류"""
    pass


class JSONExtractor:
    """
    다양한 형식의 텍스트에서 JSON 데이터를 추출하는 클래스
    """
    
    @staticmethod
    def extract_from_markdown(text: str) -> Optional[str]:
        """마크다운 코드 블록에서 JSON 추출"""
        try:
            json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
            json_match = re.search(json_pattern, text)
            if json_match:
                return json_match.group(1).strip()
            return None
        except Exception as e:
            print(f"[WARNING] 마크다운에서 JSON 추출 실패: {e}")
            return None
    
    @staticmethod
    def extract_json_object(text: str) -> Optional[str]:
        """텍스트에서 JSON 객체 추출 (가장 바깥쪽 중괄호 기준)"""
        try:
            json_block_pattern = r'(\{[\s\S]*\})'
            json_block_match = re.search(json_block_pattern, text)
            if json_block_match:
                return json_block_match.group(1).strip()
            return None
        except Exception as e:
            print(f"[WARNING] JSON 객체 추출 실패: {e}")
            return None
    
    @staticmethod
    def extract_json_array(text: str) -> Optional[str]:
        """텍스트에서 JSON 배열 추출"""
        try:
            array_pattern = r'(\[[\s\S]*\])'
            array_match = re.search(array_pattern, text)
            if array_match:
                return array_match.group(1).strip()
            return None
        except Exception as e:
            print(f"[WARNING] JSON 배열 추출 실패: {e}")
            return None
    
    @staticmethod
    def extract_all_potential_json(text: str) -> List[str]:
        """텍스트에서 모든 잠재적 JSON 구조 추출"""
        json_structures = []
        
        # JSON 객체 패턴 (중괄호)
        obj_pattern = r'(\{[\s\S]*?\})'
        # JSON 배열 패턴 (대괄호)
        arr_pattern = r'(\[[\s\S]*?\])'
        
        try:
            # 객체 추출
            for match in re.finditer(obj_pattern, text):
                json_structures.append(match.group(1))
            
            # 배열 추출
            for match in re.finditer(arr_pattern, text):
                json_structures.append(match.group(1))
                
            return json_structures
        except Exception as e:
            print(f"[WARNING] 잠재적 JSON 구조 추출 실패: {e}")
            return []
    
    @staticmethod
    def extract_possible_json_block(text: str) -> Optional[str]:
        """
        텍스트에서 JSON일 가능성이 높은 블록 추출
        특히 LLM 출력에서 방해요소를 제거하고 JSON 형식만 추출
        """
        if not text or not isinstance(text, str):
            return None
            
        # 텍스트 내에서 '{' 또는 '[' 시작하는 부분 찾기
        json_start_idx = -1
        for i, char in enumerate(text):
            if char in ['{', '[']:
                json_start_idx = i
                break
                
        if json_start_idx == -1:
            return None
            
        # 괄호 균형 맞추기
        bracket_stack = []
        end_idx = -1
        
        for i in range(json_start_idx, len(text)):
            if text[i] in ['{', '[']:
                bracket_stack.append(text[i])
            elif text[i] == '}' and bracket_stack and bracket_stack[-1] == '{':
                bracket_stack.pop()
                if not bracket_stack:  # 괄호 짝이 맞음
                    end_idx = i + 1
                    break
            elif text[i] == ']' and bracket_stack and bracket_stack[-1] == '[':
                bracket_stack.pop()
                if not bracket_stack:  # 괄호 짝이 맞음
                    end_idx = i + 1
                    break
        
        if end_idx > json_start_idx:
            possible_json = text[json_start_idx:end_idx]
            return possible_json
        
        return None
    
    @staticmethod
    def clean_text(text: str) -> str:
        """JSON 파싱을 위해 텍스트 정리"""
        # 줄바꿈 및 특수 공백 제거
        cleaned = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        # 연속된 공백을 하나로 변경
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # 따옴표 관련 이스케이프 문제 처리
        cleaned = cleaned.replace('\\"', '"').replace("\\'", "'")
        return cleaned


class JSONParser:
    """
    추출된, 또는 직접 주어진 JSON 문자열을 파싱하는 클래스
    """
    
    @staticmethod
    def parse_json(text: str) -> Any:
        """JSON 문자열을 파싱"""
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"[WARNING] JSON 파싱 실패: {e}")
            raise JSONParseError(f"JSON 파싱 오류: {e}")
    
    @staticmethod
    def parse_to_model(data: Dict[str, Any], model_class: Type[T]) -> T:
        """파싱된 데이터를 지정된 Pydantic 모델로 변환"""
        try:
            return model_class(**data)
        except ValidationError as e:
            print(f"[WARNING] 모델 변환 실패: {e}")
            raise ModelConversionError(f"모델 변환 오류: {e}")
        except Exception as e:
            print(f"[WARNING] 예기치 않은 모델 변환 오류: {e}")
            raise ModelConversionError(f"예기치 않은 모델 변환 오류: {e}")


class LLMOutputParser:
    """
    LLM 출력을 처리하고 JSON으로 파싱하는 통합 클래스
    """
    
    def __init__(self):
        self.extractor = JSONExtractor()
        self.parser = JSONParser()
    
    def extract_content(self, result: Any) -> str:
        """LLM 결과에서 콘텐츠 추출"""
        if result is None:
            print("[WARNING] LLM 결과가 None입니다")
            raise ContentExtractionError("LLM 결과가 None입니다")
        
        # AIMessage 객체인 경우 content 필드 추출
        if hasattr(result, 'content'):
            print("[DEBUG] AIMessage 객체에서 content 추출")
            return result.content
        
        # 이미 문자열인 경우 그대로 반환
        if isinstance(result, str):
            return result
        
        # 사전 또는 목록인 경우 JSON으로 직렬화
        if isinstance(result, (dict, list)):
            try:
                return json.dumps(result)
            except Exception as e:
                print(f"[WARNING] 객체 직렬화 실패: {e}")
                raise ContentExtractionError(f"객체를 JSON으로 직렬화할 수 없습니다: {e}")
        
        # 기타 타입은 문자열로 변환 시도
        try:
            return str(result)
        except Exception as e:
            print(f"[WARNING] 결과를 문자열로 변환 실패: {e}")
            raise ContentExtractionError(f"결과를 문자열로 변환할 수 없습니다: {e}")
    
    def parse(self, result: Any, expected_type: Type = dict) -> Any:
        """
        LLM 결과를 파싱하여 지정된 타입(기본값: 딕셔너리)으로 변환
        
        Args:
            result: LLM 응답 (문자열, AIMessage 또는 다른 객체)
            expected_type: 예상되는 결과 타입 (기본값: dict)
            
        Returns:
            파싱된 결과
            
        Raises:
            ParseError: 파싱 중 오류 발생 시
        """
        # 디버그 정보
        try:
            if result is None:
                print("[DEBUG] 입력이 None입니다")
            elif hasattr(result, 'content'):
                print(f"[DEBUG] 입력이 content 속성을 가진 객체입니다: {type(result).__name__}")
            elif isinstance(result, str):
                print(f"[DEBUG] 입력이 문자열입니다. 길이: {len(result)}")
                if len(result) > 100:
                    print(f"[DEBUG] 문자열 일부: {result[:50]}...{result[-50:]}")
            elif isinstance(result, dict):
                print(f"[DEBUG] 입력이 딕셔너리입니다. 키: {list(result.keys())}")
            else:
                print(f"[DEBUG] 입력 타입: {type(result).__name__}")
        except Exception as e:
            print(f"[DEBUG] 입력 정보 출력 중 오류: {e}")
        
        # 이미 올바른 타입인 경우 바로 반환
        if isinstance(result, expected_type) and not isinstance(result, str):
            return result
        
        try:
            # 콘텐츠 추출
            content = self.extract_content(result)
            
            # 빈 문자열 체크
            if not content.strip():
                print("[WARNING] 빈 문자열 결과")
                return {} if expected_type == dict else []
            
            # 다양한 방법으로 JSON 추출 시도
            
            # 1. 마크다운 코드 블록에서 추출
            markdown_json = self.extractor.extract_from_markdown(content)
            if markdown_json:
                try:
                    parsed = self.parser.parse_json(markdown_json)
                    if isinstance(parsed, expected_type):
                        print("[DEBUG] 마크다운에서 JSON 파싱 성공")
                        return parsed
                except JSONParseError:
                    pass
            
            # 2. 기대 타입에 따라 JSON 구조 추출
            if expected_type == dict:
                json_obj = self.extractor.extract_json_object(content)
                if json_obj:
                    try:
                        parsed = self.parser.parse_json(json_obj)
                        if isinstance(parsed, dict):
                            print("[DEBUG] JSON 객체 파싱 성공")
                            return parsed
                    except JSONParseError:
                        pass
            elif expected_type == list:
                json_arr = self.extractor.extract_json_array(content)
                if json_arr:
                    try:
                        parsed = self.parser.parse_json(json_arr)
                        if isinstance(parsed, list):
                            print("[DEBUG] JSON 배열 파싱 성공")
                            return parsed
                    except JSONParseError:
                        pass
            
            # 3. JSON일 가능성이 높은 블록 추출 시도
            possible_json = self.extractor.extract_possible_json_block(content)
            if possible_json:
                try:
                    parsed = self.parser.parse_json(possible_json)
                    if isinstance(parsed, expected_type):
                        print("[DEBUG] 추출된 JSON 블록 파싱 성공")
                        return parsed
                except JSONParseError:
                    pass
            
            # 4. 전체 콘텐츠를 JSON으로 파싱 시도
            try:
                parsed = self.parser.parse_json(content)
                if isinstance(parsed, expected_type):
                    print("[DEBUG] 전체 콘텐츠를 JSON으로 파싱 성공")
                    return parsed
            except JSONParseError:
                pass
            
            # 5. 정리된 텍스트 파싱 시도
            clean_content = self.extractor.clean_text(content)
            try:
                parsed = self.parser.parse_json(clean_content)
                if isinstance(parsed, expected_type):
                    print("[DEBUG] 정리된 텍스트 파싱 성공")
                    return parsed
            except JSONParseError:
                pass
            
            # 6. 모든 잠재적 JSON 구조 시도
            potential_jsons = self.extractor.extract_all_potential_json(content)
            for json_str in potential_jsons:
                try:
                    parsed = self.parser.parse_json(json_str)
                    if isinstance(parsed, expected_type):
                        print("[DEBUG] 잠재적 JSON 구조 파싱 성공")
                        return parsed
                except JSONParseError:
                    continue
            
            # 7. 텍스트 직접 처리 시도 (사용자가 제공한 예제 형식 핸들링)
            if expected_type == dict and isinstance(content, str):
                try:
                    print("[DEBUG] 사용자 제공 예제 형식으로 파싱 시도")
                    # 범용적인 key-value 패턴 추출
                    user_format = {}
                    for line in content.split('\n'):
                        # "key": value 패턴
                        kv_match = re.search(r'"([^"]+)"\s*:\s*(.+?)(?:,\s*$|$)', line)
                        if kv_match:
                            key, value = kv_match.groups()
                            # 값 타입 변환 시도
                            try:
                                if value.startswith('"') and value.endswith('"'):
                                    user_format[key] = value[1:-1]  # 문자열
                                elif value.lower() in ('true', 'false'):
                                    user_format[key] = value.lower() == 'true'  # 불리언
                                elif '.' in value:
                                    user_format[key] = float(value)  # 실수
                                else:
                                    user_format[key] = int(value)  # 정수
                            except:
                                user_format[key] = value  # 변환 실패시 문자열로 저장
                    
                    if user_format:  # 파싱된 내용이 있으면 반환
                        print(f"[DEBUG] 사용자 형식 파싱 성공: {list(user_format.keys())}")
                        return user_format
                except Exception as e:
                    print(f"[DEBUG] 사용자 형식 파싱 실패: {e}")
            
            # 모든 시도 실패
            print("[WARNING] 모든 JSON 추출 시도 실패")
            if isinstance(content, str) and len(content) > 200:
                print(f"[DEBUG] 콘텐츠 일부: {content[:100]}...{content[-100:]}")
            return {} if expected_type == dict else []
            
        except Exception as e:
            print(f"[ERROR] 파싱 중 예기치 않은 오류: {e}")
            return {} if expected_type == dict else []
    
    def parse_to_model(self, result: Any, model_class: Type[T]) -> Union[T, Dict[str, Any]]:
        """
        LLM 결과를 파싱하고 Pydantic 모델로 변환
        
        Args:
            result: LLM 응답
            model_class: 변환할 Pydantic 모델 클래스
            
        Returns:
            파싱된 모델 객체 또는 실패 시 딕셔너리
        """
        try:
            # 기본적으로 딕셔너리로 파싱
            parsed_dict = self.parse(result, dict)
            
            # 모델로 변환
            if parsed_dict:
                try:
                    return self.parser.parse_to_model(parsed_dict, model_class)
                except ModelConversionError as e:
                    print(f"[WARNING] 모델 변환 실패, 딕셔너리 반환: {e}")
                    return parsed_dict
            
            return parsed_dict
        except Exception as e:
            print(f"[ERROR] 모델 파싱 중 예기치 않은 오류: {e}")
            return {}


# 단일 글로벌 인스턴스 생성
_parser = LLMOutputParser()

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
    try:
        return _parser.parse_to_model(content, model_class)
    except Exception as e:
        raise ValueError(f"LLM 출력 파싱 실패: {e}")

def safe_parse_llm_json_output(result: Any, expected_type: Type = dict, parser: Optional[Any] = None) -> Any:
    """
    강화된 안전한 LLM JSON 출력 파싱 함수
    
    Args:
        result: LLM 응답 (문자열, AIMessage 또는 다른 객체)
        expected_type: 예상되는 결과 타입 (기본값: dict)
        parser: 사용할 파서 (선택적, 없어도 기능에 영향 없음)
        
    Returns:
        파싱된 결과 또는 빈 객체(파싱 실패시)
    """
    try:
        # 글로벌 파서 인스턴스 사용
        return _parser.parse(result, expected_type)
    except Exception as e:
        print(f"[ERROR] 안전한 파싱 실패: {e}")
        return {} if expected_type == dict else []

def extract_markdown_from_text(text: str) -> Optional[str]:
    """
    텍스트에서 마크다운 블록 추출
    
    Args:
        text: 마크다운이 포함된 텍스트
        
    Returns:
        마크다운 텍스트 또는 None
    """
    try:
        # 마크다운 블록 패턴 (```markdown 또는 ```md로 시작하는 블록)
        markdown_pattern = r'```(?:markdown|md)?\s*([\s\S]*?)\s*```'
        markdown_match = re.search(markdown_pattern, text)
        if markdown_match:
            return markdown_match.group(1).strip()
        return None
    except Exception as e:
        print(f"[WARNING] 마크다운 추출 실패: {e}")
        return None 