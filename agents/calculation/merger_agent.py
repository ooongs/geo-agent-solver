"""
결과 병합 에이전트 모듈

이 모듈은 결과 병합 에이전트를 정의합니다.
이 에이전트는 기하학 계산 결과를 분석하고 통합합니다.
"""

from typing import Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

from models.state_models import GeometryState
from agents.calculation.prompts.merger_prompt import RESULT_MERGER_PROMPT, MERGER_JSON_TEMPLATE
from utils.llm_manager import LLMManager

def parse_merger_result(output: str, existing_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    병합 결과 파싱
    
    Args:
        output: 에이전트 출력 문자열
        existing_results: 기존 계산 결과
        
    Returns:
        최종 계산 결과
    """
    import re
    import json
    
    # JSON 형식 결과가 있는지 확인
    json_pattern = r'```json\n(.*?)\n```'
    json_matches = re.findall(json_pattern, output, re.DOTALL)
    
    if json_matches:
        try:
            return json.loads(json_matches[0])
        except json.JSONDecodeError:
            pass
    
    # 기존 결과가 없으면 새로 생성
    if not existing_results:
        existing_results = {}
    
    # 결과 복사 (기존 결과를 유지하기 위해)
    final_results = {k: v for k, v in existing_results.items()}
    
    # 계산 단계 추출
    steps = []
    step_pattern = r'(?:步骤|step)\s*\d+[.:]\s*(.+?)(?=(?:步骤|step)|$)'
    step_matches = re.findall(step_pattern, output, re.DOTALL)
    if step_matches:
        steps = [step.strip() for step in step_matches]
    
    # 단계가 추출됐으면 추가
    if steps:
        if "steps" not in final_results:
            final_results["steps"] = []
        final_results["steps"].extend(steps)
    
    # 문제 유형 정보 추가
    problem_type = final_results.get("problem_type", {})
    if isinstance(problem_type, dict):
        if "triangle" in output.lower() or "三角形" in output:
            problem_type["triangle"] = True
        if "circle" in output.lower() or "圆" in output:
            problem_type["circle"] = True
        if "angle" in output.lower() or "角" in output:
            problem_type["angle"] = True
        if "coordinate" in output.lower() or "坐标" in output:
            problem_type["coordinate"] = True
        if "area" in output.lower() or "面积" in output:
            problem_type["area"] = True
        if "measurement" in output.lower() or "测量" in output:
            problem_type["measurement"] = True
    
    if problem_type:
        final_results["problem_type"] = problem_type
    
    # 종합 결론 추출
    conclusion = re.search(r'(?:结论|conclusion)[：:]\s*(.*?)(?=\n\n|\Z)', output, re.DOTALL)
    if conclusion:
        final_results["conclusion"] = conclusion.group(1).strip()
    
    return final_results

def calculation_result_merger_agent(state: GeometryState) -> GeometryState:
    """
    计算结果整合代理
    
    分析和整合各种几何计算的结果，确保它们的一致性和准确性
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 계산 큐가 없는 경우
    if not state.calculation_queue:
        return state
    
    # LLM 초기화
    llm = LLMManager.get_calculation_merger_llm()
    
    # 프롬프트 생성
    prompt = RESULT_MERGER_PROMPT
    
    # 에이전트 생성
    chain = prompt | llm
    
    # 완료된 작업 목록 생성
    completed_tasks = []
    for task in state.calculation_queue.tasks:
        if task.task_id in state.calculation_queue.completed_task_ids and task.result:
            completed_tasks.append(task)
    
    # 문제 분석 정보 가져오기 (있는 경우)
    problem_analysis = ""
    if hasattr(state, "problem_analysis"):
        problem_analysis = str(state.problem_analysis)
    
    # 에이전트 실행
    result = chain.invoke({
        "problem": state.input_problem,
        "completed_tasks": str([task.model_dump() for task in completed_tasks]),
        "calculation_results": str(state.calculation_results),
        "problem_analysis": problem_analysis,
        "json_template": MERGER_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 최종 결과 생성
    final_results = parse_merger_result(result.content, state.calculation_results)
    
    # 상태 업데이트
    state.calculations = final_results
    
    return state 