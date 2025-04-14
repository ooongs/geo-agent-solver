from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from utils.prompts import VALIDATION_PROMPT
from utils.geogebra_validator import validate_geogebra_syntax
import json

def validation_agent(state):
    """
    GeoGebra 명령어 검증 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        검증 결과가 추가된 상태 객체
    """
    # 도구 생성
    tools = get_validation_tools()
    
    # LLM 초기화
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4"
    )
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, VALIDATION_PROMPT)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 에이전트 실행
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "commands": str(state.geogebra_commands)
    })
    
    # 결과 분석
    try:
        validation_result = json.loads(result["output"]) if isinstance(result["output"], str) else result["output"]
    except (json.JSONDecodeError, TypeError):
        validation_result = _parse_validation_result(result["output"])
    
    # 검증 성공 여부 결정
    is_valid = validation_result.get("is_valid", False)
    
    # 상태 업데이트
    state.validation = validation_result
    state.is_valid = is_valid
    
    return state

def get_validation_tools():
    """검증 에이전트용 도구 생성"""
    return [
        Tool(
            name="check_syntax",
            func=_check_syntax_tool,
            description="检查GeoGebra命令语法，验证命令是否符合GeoGebra语法规则"
        ),
        Tool(
            name="verify_object_definitions",
            func=_verify_object_definitions_tool,
            description="验证几何对象定义，检查是否所有必要的几何对象都已定义"
        ),
        Tool(
            name="verify_problem_constraints",
            func=_verify_problem_constraints_tool,
            description="验证是否满足问题约束，检查命令是否实现了问题的所有要求和约束"
        ),
        Tool(
            name="suggest_fixes",
            func=_suggest_fixes_tool,
            description="提出修复建议，根据验证结果提供改进命令的具体建议"
        )
    ]

# === Tool 함수 구현 ===

def _check_syntax_tool(commands_json: str) -> str:
    """
    GeoGebra 명령어 구문 검증 도구
    
    Args:
        commands_json: 명령어 목록(JSON 문자열 또는 줄바꿈으로 구분된 텍스트)
        
    Returns:
        검증 결과(JSON 문자열)
    """
    try:
        # JSON 배열 또는 객체인 경우
        try:
            commands_data = json.loads(commands_json)
            if isinstance(commands_data, dict) and "commands" in commands_data:
                commands = commands_data["commands"]
            elif isinstance(commands_data, list):
                commands = commands_data
            else:
                commands = commands_json.strip().split("\n")
        except (json.JSONDecodeError, TypeError):
            # 줄바꿈으로 구분된 텍스트인 경우
            commands = [line.strip() for line in commands_json.strip().split("\n") if line.strip()]
        
        result = validate_geogebra_syntax(commands)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"is_valid": False, "errors": [str(e)]}, ensure_ascii=False)

def _verify_object_definitions_tool(commands_json: str, parsed_elements_json: str) -> str:
    """
    기하 객체 정의 검증 도구
    
    Args:
        commands_json: 명령어 목록(JSON 문자열)
        parsed_elements_json: 파싱된 요소(JSON 문자열)
        
    Returns:
        검증 결과(JSON 문자열)
    """
    try:
        # 명령어 목록 파싱
        try:
            commands_data = json.loads(commands_json)
            if isinstance(commands_data, dict) and "commands" in commands_data:
                commands = commands_data["commands"]
            elif isinstance(commands_data, list):
                commands = commands_data
            else:
                commands = commands_json.strip().split("\n")
        except (json.JSONDecodeError, TypeError):
            commands = commands_json.strip().split("\n")
        
        # 파싱된 요소 가져오기
        parsed_elements = json.loads(parsed_elements_json) if isinstance(parsed_elements_json, str) else parsed_elements_json
        
        # 필요한 객체 검증
        result = _verify_object_definitions(commands, parsed_elements)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"is_complete": False, "missing_objects": [str(e)]}, ensure_ascii=False)

def _verify_problem_constraints_tool(commands_json: str, parsed_elements_json: str, calculations_json: str) -> str:
    """
    문제 제약 조건 검증 도구
    
    Args:
        commands_json: 명령어 목록(JSON 문자열)
        parsed_elements_json: 파싱된 요소(JSON 문자열)
        calculations_json: 계산 결과(JSON 문자열)
        
    Returns:
        검증 결과(JSON 문자열)
    """
    try:
        # 명령어 목록 파싱
        try:
            commands_data = json.loads(commands_json)
            if isinstance(commands_data, dict) and "commands" in commands_data:
                commands = commands_data["commands"]
            elif isinstance(commands_data, list):
                commands = commands_data
            else:
                commands = commands_json.strip().split("\n")
        except (json.JSONDecodeError, TypeError):
            commands = commands_json.strip().split("\n")
        
        # 파싱된 요소 및 계산 결과 가져오기
        parsed_elements = json.loads(parsed_elements_json) if isinstance(parsed_elements_json, str) else parsed_elements_json
        calculations = json.loads(calculations_json) if isinstance(calculations_json, str) else calculations_json
        
        # 제약 조건 검증
        result = _verify_problem_constraints(commands, parsed_elements, calculations)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"constraints_met": False, "failed_constraints": [str(e)]}, ensure_ascii=False)

def _suggest_fixes_tool(validation_results_json: str) -> str:
    """
    수정 제안 도구
    
    Args:
        validation_results_json: 검증 결과(JSON 문자열)
        
    Returns:
        수정 제안(JSON 문자열)
    """
    try:
        validation_results = json.loads(validation_results_json) if isinstance(validation_results_json, str) else validation_results_json
        
        # 수정 제안 생성
        result = _suggest_fixes(validation_results)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"suggestions": [str(e)]}, ensure_ascii=False)

# === 헬퍼 함수 ===

def _verify_object_definitions(commands: List[str], parsed_elements: Dict[str, Any]) -> Dict[str, Any]:
    """
    기하 객체 정의 검증
    
    Args:
        commands: 명령어 목록
        parsed_elements: 파싱된 요소
        
    Returns:
        검증 결과
    """
    # 필요한 객체 목록 추출
    required_objects = set()
    
    # 파싱된 요소에서 필요한 객체 추출
    if "objects" in parsed_elements:
        for obj in parsed_elements["objects"]:
            if "name" in obj:
                required_objects.add(obj["name"])
    
    # 명령어에서 정의된 객체 추출
    defined_objects = set()
    for cmd in commands:
        parts = cmd.split("=", 1)
        if len(parts) == 2:
            obj_name = parts[0].strip()
            defined_objects.add(obj_name)
    
    # 누락된 객체 확인
    missing_objects = required_objects - defined_objects
    
    return {
        "is_complete": len(missing_objects) == 0,
        "missing_objects": list(missing_objects)
    }

def _verify_problem_constraints(commands: List[str], parsed_elements: Dict[str, Any], calculations: Dict[str, Any]) -> Dict[str, Any]:
    """
    문제 제약 조건 검증
    
    Args:
        commands: 명령어 목록
        parsed_elements: 파싱된 요소
        calculations: 계산 결과
        
    Returns:
        검증 결과
    """
    # 제약 조건 검증 결과
    constraints_met = True
    failed_constraints = []
    
    # 파싱된 요소에서 제약 조건 추출
    if "constraints" in parsed_elements:
        for constraint in parsed_elements["constraints"]:
            # 제약 조건 검증 로직
            # 실제 구현에서는 각 제약 조건 유형에 맞게 검증 필요
            constraint_met = True
            
            # 제약 조건 검증 결과 기록
            if not constraint_met:
                constraints_met = False
                failed_constraints.append(constraint)
    
    return {
        "constraints_met": constraints_met,
        "failed_constraints": failed_constraints
    }

def _suggest_fixes(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    수정 제안 생성
    
    Args:
        validation_results: 검증 결과
        
    Returns:
        수정 제안
    """
    suggestions = []
    
    # 구문 오류 관련 제안
    if "syntax" in validation_results and not validation_results["syntax"].get("is_valid", True):
        for error in validation_results["syntax"].get("errors", []):
            suggestions.append(f"语法错误修复: {error}")
    
    # 누락된 객체 관련 제안
    if "objects" in validation_results and not validation_results["objects"].get("is_complete", True):
        for missing in validation_results["objects"].get("missing_objects", []):
            suggestions.append(f"添加缺失对象: {missing}")
    
    # 제약 조건 관련 제안
    if "constraints" in validation_results and not validation_results["constraints"].get("constraints_met", True):
        for failed in validation_results["constraints"].get("failed_constraints", []):
            suggestions.append(f"满足约束条件: {failed}")
    
    return {"suggestions": suggestions}

def _parse_validation_result(output: str) -> Dict[str, Any]:
    """
    검증 결과 텍스트 파싱
    
    Args:
        output: 검증 결과 텍스트
        
    Returns:
        구조화된 검증 결과
    """
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    # 오류 및 경고 추출
    lines = output.strip().split("\n")
    for line in lines:
        line = line.strip()
        if "错误" in line or "error" in line.lower():
            validation_result["is_valid"] = False
            validation_result["errors"].append(line)
        elif "警告" in line or "warning" in line.lower():
            validation_result["warnings"].append(line)
        elif "建议" in line or "suggestion" in line.lower():
            validation_result["suggestions"].append(line)
    
    return validation_result 