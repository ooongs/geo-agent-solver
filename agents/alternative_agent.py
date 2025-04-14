from typing import Dict, Any, List, Optional
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from utils.prompts import ALTERNATIVE_PROMPT
from utils.llm_manager import LLMManager
import json
import re

def alternative_solution_agent(state):
    """
    대체 해법 탐색 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        대체 해법이 추가된 상태 객체
    """
    # 도구 생성
    tools = get_alternative_tools()
    
    # LLM 초기화
    llm = LLMManager.get_alternative_solution_llm()
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, ALTERNATIVE_PROMPT)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 에이전트 실행
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "approach": str(state.difficulty.get("approach", "")) if state.difficulty else "{}",
        "errors": str(state.validation.get("errors", [])) if state.validation else "[]"
    })
    
    # 결과 분석
    try:
        alternative_solution = json.loads(result["output"]) if isinstance(result["output"], str) else result["output"]
    except (json.JSONDecodeError, TypeError):
        alternative_solution = _parse_alternative_solution(result["output"])
    
    # 상태 업데이트
    state.alternative_solution = alternative_solution
    state.attempt_count += 1
    
    return state

def get_alternative_tools():
    """대체 해법 탐색 에이전트용 도구 생성"""
    return [
        StructuredTool.from_function(
            name="analyze_error_causes",
            func=_analyze_error_causes_tool,
            description="分析错误原因，深入分析验证失败的根本原因"
        ),
        StructuredTool.from_function(
            name="suggest_alternative_approach",
            func=_suggest_alternative_approach_tool,
            description="提出替代解法，根据问题和错误分析提出新的解决方案"
        ),
        StructuredTool.from_function(
            name="compare_approaches",
            func=_compare_approaches_tool,
            description="比较不同解法的优缺点，评估当前方法和替代方法的差异"
        )
    ]

# === Tool 함수 구현 ===

def _analyze_error_causes_tool(input_json: str) -> str:
    """
    오류 원인 분석 도구
    
    Args:
        input_json: 입력 데이터(JSON 문자열) - errors, commands, calculations를 포함
        
    Returns:
        오류 분석 결과(JSON 문자열)
    """
    try:
        # 입력 데이터 파싱
        data = json.loads(input_json) if isinstance(input_json, str) else input_json
        errors = data.get("errors", [])
        commands = data.get("commands", [])
        calculations = data.get("calculations", {})
        
        # 오류 원인 분석
        result = _analyze_error_causes(errors, commands, calculations)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"root_causes": [str(e)], "severity": ["high"]}, ensure_ascii=False)

def _suggest_alternative_approach_tool(input_json: str) -> str:
    """
    대체 해법 제안 도구
    
    Args:
        input_json: 입력 데이터(JSON 문자열) - problem_text, parsed_elements, error_analysis를 포함
        
    Returns:
        대체 해법(JSON 문자열)
    """
    try:
        # 입력 데이터 파싱
        data = json.loads(input_json) if isinstance(input_json, str) else input_json
        problem_text = data.get("problem_text", "")
        parsed_elements = data.get("parsed_elements", {})
        error_analysis = data.get("error_analysis", {})
        
        # 대체 해법 제안
        result = _suggest_alternative_approach(problem_text, parsed_elements, error_analysis)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"approach": str(e), "steps": []}, ensure_ascii=False)

def _compare_approaches_tool(input_json: str) -> str:
    """
    해법 비교 도구
    
    Args:
        input_json: 입력 데이터(JSON 문자열) - current_approach, alternative_approach를 포함
        
    Returns:
        비교 결과(JSON 문자열)
    """
    try:
        # 입력 데이터 파싱
        data = json.loads(input_json) if isinstance(input_json, str) else input_json
        current_approach = data.get("current_approach", {})
        alternative_approach = data.get("alternative_approach", {})
        
        # 해법 비교
        result = _compare_approaches(current_approach, alternative_approach)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"comparison": [str(e)], "recommendation": "alternative"}, ensure_ascii=False)

# === 헬퍼 함수 ===

def _analyze_error_causes(errors: List[str], commands: List[str], calculations: Dict[str, Any]) -> Dict[str, Any]:
    """
    오류 원인 분석
    
    Args:
        errors: 오류 목록
        commands: 명령어 목록
        calculations: 계산 결과
        
    Returns:
        오류 분석 결과
    """
    root_causes = []
    severity = []
    
    # 오류가 없는 경우
    if not errors:
        return {"root_causes": [], "severity": []}
    
    # 오류 유형 분석
    for error in errors:
        # 구문 오류
        if "syntax" in error.lower() or "command" in error.lower():
            root_causes.append("命令语法错误")
            severity.append("high")
        # 누락된 객체
        elif "missing" in error.lower() or "not defined" in error.lower():
            root_causes.append("几何对象缺失")
            severity.append("medium")
        # 제약 조건 오류
        elif "constraint" in error.lower() or "condition" in error.lower():
            root_causes.append("约束条件不满足")
            severity.append("high")
        # 기타 오류
        else:
            root_causes.append("未知错误")
            severity.append("medium")
    
    return {
        "root_causes": root_causes,
        "severity": severity
    }

def _suggest_alternative_approach(problem_text: str, parsed_elements: Dict[str, Any], error_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    대체 해법 제안
    
    Args:
        problem_text: 문제 텍스트
        parsed_elements: 파싱된 요소
        error_analysis: 오류 분석 결과
        
    Returns:
        대체 해법
    """
    # 문제 유형 파악
    problem_type = "一般几何问题"  # 기본값
    
    # 파싱된 요소에서 문제 유형 추출
    if "triangles" in parsed_elements or "triangle" in problem_text.lower():
        problem_type = "三角形问题"
    elif "circles" in parsed_elements or "circle" in problem_text.lower():
        problem_type = "圆问题"
    elif "coordinates" in parsed_elements or "coordinate" in problem_text.lower():
        problem_type = "坐标几何问题"
    
    # 오류 유형에 따른 대체 해법
    approach = ""
    steps = []
    
    # 대체 해법 생성
    if problem_type == "三角形问题":
        approach = "解析几何法"
        steps = [
            "1. 建立坐标系",
            "2. 将三角形的顶点用坐标表示",
            "3. 利用坐标计算几何量",
            "4. 通过代数关系求解问题"
        ]
    elif problem_type == "圆问题":
        approach = "向量法"
        steps = [
            "1. 用向量表示圆心和圆上的点",
            "2. 利用向量的点积和叉积计算几何关系",
            "3. 建立向量方程求解问题"
        ]
    elif problem_type == "坐标几何问题":
        approach = "参数化方法"
        steps = [
            "1. 用参数方程表示几何对象",
            "2. 建立参数间的关系方程",
            "3. 求解参数方程得到结果"
        ]
    else:
        approach = "综合几何法"
        steps = [
            "1. 分析几何关系",
            "2. 利用几何定理建立方程",
            "3. 通过代数计算求解几何量"
        ]
    
    return {
        "approach": approach,
        "steps": steps
    }

def _compare_approaches(current_approach: Dict[str, Any], alternative_approach: Dict[str, Any]) -> Dict[str, Any]:
    """
    해법 비교
    
    Args:
        current_approach: 현재 해법
        alternative_approach: 대체 해법
        
    Returns:
        비교 결과
    """
    comparison = []
    
    # 현재 해법 장단점
    current_pros = ["容易理解", "直观"]
    current_cons = ["可能不够通用", "受特定条件限制"]
    
    # 대체 해법 장단점
    alt_pros = ["更加通用", "适用范围广"]
    alt_cons = ["计算可能复杂", "需要更多数学知识"]
    
    # 비교 결과 생성
    comparison.append(f"当前方法 ({current_approach.get('approach', '几何法')}):")
    comparison.append("  优点: " + ", ".join(current_pros))
    comparison.append("  缺点: " + ", ".join(current_cons))
    comparison.append(f"替代方法 ({alternative_approach.get('approach', '代数法')}):")
    comparison.append("  优点: " + ", ".join(alt_pros))
    comparison.append("  缺点: " + ", ".join(alt_cons))
    
    # 추천 결정
    recommendation = "alternative" if len(alt_pros) > len(current_pros) else "current"
    
    return {
        "comparison": comparison,
        "recommendation": recommendation
    }

def _parse_alternative_solution(output: str) -> Dict[str, Any]:
    """
    대체 해법 텍스트 파싱
    
    Args:
        output: 대체 해법 텍스트
        
    Returns:
        구조화된 대체 해법
    """
    alternative_solution = {
        "approach": "",
        "steps": [],
        "explanation": ""
    }
    
    # 해법 추출
    approach_match = re.search(r'方法[:：]\s*(.+?)(?=\n|$)', output)
    if approach_match:
        alternative_solution["approach"] = approach_match.group(1).strip()
    
    # 단계 추출
    steps = []
    step_pattern = r'(?:步骤|第\d+步)[.：:]\s*(.+?)(?=\n|$)'
    for match in re.finditer(step_pattern, output, re.MULTILINE):
        steps.append(match.group(1).strip())
    
    # 번호가 있는 리스트 추출
    numbered_pattern = r'(\d+)[.、)]\s*(.+?)(?=\n|$)'
    for match in re.finditer(numbered_pattern, output, re.MULTILINE):
        steps.append(match.group(2).strip())
    
    alternative_solution["steps"] = steps
    
    # 설명 추출
    explanation_match = re.search(r'说明[:：]\s*(.+?)(?=\n|$)', output)
    if explanation_match:
        alternative_solution["explanation"] = explanation_match.group(1).strip()
    else:
        # 첫 단락을 설명으로 사용
        lines = output.strip().split('\n')
        if lines:
            alternative_solution["explanation"] = lines[0].strip()
    
    return alternative_solution 