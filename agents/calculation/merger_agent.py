"""
결과 병합 에이전트 모듈

이 모듈은 결과 병합 에이전트를 정의합니다.
이 에이전트는 기하학 계산 결과를 분석하고 통합합니다.
"""

from typing import Dict, Any
import re
import json
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

from models.state_models import GeometryState
from agents.calculation.prompts.merger_prompt import RESULT_MERGER_PROMPT, MERGER_JSON_TEMPLATE
from utils.llm_manager import LLMManager

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
    
    # JSON 결과 추출
    json_pattern = r'```json\n(.*?)\n```'
    json_matches = re.findall(json_pattern, result.content, re.DOTALL)
    
    if json_matches:
        try:
            # JSON 파싱
            final_results = json.loads(json_matches[0])
            
            # construction_plan 분리
            construction_plan = final_results.pop("construction_plan", {})
            
            # 상태 업데이트
            state.calculations = final_results
            state.construction_plan = construction_plan
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기존 결과 유지
            pass
    
    return state 