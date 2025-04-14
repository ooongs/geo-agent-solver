"""
계산 관리자 에이전트 모듈

이 모듈은 계산 관리자 에이전트를 정의합니다.
이 에이전트는 기하학 문제를 분석하고 계산 작업을 생성 및 관리합니다.
"""

from typing import Dict, Any, List, Optional, Union
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from models.state_models import GeometryState, CalculationQueue, CalculationTaskCreation
from agents.calculation.prompts.manager_prompt import CALCULATION_MANAGER_PROMPT, MANAGER_JSON_TEMPLATE
from agents.calculation.utils.calculation_utils import (
    process_calculation_tasks,
    update_calculation_queue,
    determine_next_calculation
)

def calculation_manager_agent(state: GeometryState) -> GeometryState:
    """
    计算任务管理代理
    
    分析几何问题，确定需要执行的计算任务，并创建和管理计算任务队列
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationTaskCreation)
    
    # LLM 초기화
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4"
    )
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = CALCULATION_MANAGER_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # 에이전트 생성 대신 체인 사용
    chain = prompt | llm
    
    # 계산 큐 초기화 (없는 경우)
    if state.calculation_queue is None:
        state.calculation_queue = CalculationQueue(
            tasks=[],
            completed_tasks=[],
            current_task_id=None
        )
    
    # 계산 결과 초기화 (없는 경우)
    if state.calculation_results is None:
        state.calculation_results = {}
    
    # 현재 큐 상태 및 결과 추출
    calculation_queue = state.calculation_queue
    calculation_results = state.calculation_results
    
    # 파싱된 문제 유형과 조건 추출
    parsed_elements = state.parsed_elements
    problem_type = parsed_elements.get("problem_type", {}) if parsed_elements else {}
    analyzed_conditions = parsed_elements.get("analyzed_conditions", {}) if parsed_elements else {}
    
    # 에이전트 실행
    result = chain.invoke({
        "problem": state.input_problem,
        "parsed_elements": str(parsed_elements),
        "problem_type": str(problem_type),
        "analyzed_conditions": str(analyzed_conditions),
        "approach": str(state.difficulty.get("approach", "")) if state.difficulty else "{}",
        "calculation_queue": str(calculation_queue),
        "calculation_results": str(calculation_results),
        "json_template": MANAGER_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 에이전트 응답 분석하여 작업 큐 업데이트
    try:
        # AIMessage 객체에서 content 속성 사용
        # JSON 파서를 이용한 파싱 시도
        parsed_result = output_parser.parse(result.content)
        # 파싱 성공 시 구조화된 방식으로 처리
        process_calculation_tasks(state, parsed_result)
    except Exception as e:
        print(f"Error parsing calculation manager result as structured JSON: {e}")
        # JSON 파싱 실패 시 텍스트 기반 방식으로 처리
        # AIMessage 객체에서 content 속성 사용
        update_calculation_queue(state, result.content)
        
        # 다음 계산 유형이 설정되지 않은 경우에만 결정
        if not state.next_calculation:
            determine_next_calculation(state)
    
    return state 