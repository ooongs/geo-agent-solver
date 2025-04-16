from typing import Dict, List, Any, Optional
from geo_prompts import VALIDATION_PROMPT, VALIDATION_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from utils.json_parser import parse_llm_json_output, safe_parse_llm_json_output
from models.validation_models import ValidationResult
import json
import re

def validation_agent(state):
    """
    GeoGebra 명령어 검증 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        검증 결과가 추가된 상태 객체
    """
    # LLM 초기화
    llm = LLMManager.get_validation_llm()
    
    # 입력 데이터 준비
    chain = VALIDATION_PROMPT | llm
    print(f"[DEBUG] Validation agent start")
    result = chain.invoke({
        "problem": state.input_problem,
        "commands": str(state.geogebra_commands),
        "construction_plan": str(state.construction_plan),
        # "retrieved_commands": json.dumps(state.retrieved_commands),
        "json_template": VALIDATION_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    print(f"[DEBUG] Validation agent end")
    # 결과 분석
    output = result.content if hasattr(result, 'content') else result["output"]
    
    try:
        # 결과 파싱 시도 (Pydantic 모델 사용)
        validation_result = safe_parse_llm_json_output(output, ValidationResult)
        
        if validation_result is None:
            # JSON 형식으로 직접 파싱 시도
            validation_dict = json.loads(output) if isinstance(output, str) else output
            validation_result = ValidationResult(**validation_dict)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        # 텍스트인 경우 구조화된 결과로 파싱
        print(f"[WARNING] JSON 파싱 실패: {str(e)}")
        validation_dict = _parse_validation_result(output)
        validation_result = ValidationResult(**validation_dict)
    
    # 검증 성공 여부 결정
    is_valid = validation_result.is_valid
    
    # 상태 업데이트
    state.validation = validation_result.dict()
    state.is_valid = is_valid
    
    # 디버그 정보
    print(f"[DEBUG] Validation result: {is_valid}")
    if not is_valid and validation_result.errors:
        print(f"[DEBUG] Validation errors: {validation_result.errors}")
    
    return state

def _parse_validation_result(output: str) -> Dict[str, Any]:
    """
    검증 결과 텍스트 파싱 (fallback 메서드)
    
    Args:
        output: 검증 결과 텍스트
        
    Returns:
        구조화된 검증 결과
    """
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "analysis": "从验证结果中提取的分析信息"
    }
    
    # 먼저 명시적인 is_valid 표시 찾기
    valid_match = re.search(r'is_valid["\s]*[:=]["\s]*(true|false)', output, re.IGNORECASE)
    if valid_match:
        is_valid_str = valid_match.group(1).lower()
        validation_result["is_valid"] = (is_valid_str == "true")
    
    # 오류 및 경고 추출
    error_pattern = r"(错误|error).*?[:：](.*)"
    warning_pattern = r"(警告|warning).*?[:：](.*)"
    suggestion_pattern = r"(建议|suggestion).*?[:：](.*)"
    
    # 오류 찾기
    for line in output.strip().split("\n"):
        line = line.strip()
        
        # 오류 검색
        error_match = re.search(error_pattern, line, re.IGNORECASE)
        if error_match:
            validation_result["is_valid"] = False
            validation_result["errors"].append(error_match.group(2).strip())
            continue
        
        # 경고 검색
        warning_match = re.search(warning_pattern, line, re.IGNORECASE)
        if warning_match:
            validation_result["warnings"].append(warning_match.group(2).strip())
            continue
        
        # 제안 검색
        suggestion_match = re.search(suggestion_pattern, line, re.IGNORECASE)
        if suggestion_match:
            validation_result["suggestions"].append(suggestion_match.group(2).strip())
            continue
        
        # 그 외 오류 관련 문구 검색
        if "错误" in line or "error" in line.lower() or "invalid" in line.lower() or "fail" in line.lower():
            validation_result["is_valid"] = False
            validation_result["errors"].append(line)
    
    # 오류가 있는데 구체적인 내용이 없을 경우
    if not validation_result["is_valid"] and not validation_result["errors"]:
        validation_result["errors"].append("验证中出现错误，但无法提取具体内容。")
    
    return validation_result 