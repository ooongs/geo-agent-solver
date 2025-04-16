"""
계산 관리자 에이전트 모듈

이 모듈은 계산 관리자 에이전트를 정의합니다.
이 에이전트는 기하학 문제를 분석하고 계산 작업을 생성 및 관리합니다.
"""

from typing import Dict, Any, List, Optional, Union
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from models.state_models import GeometryState, CalculationQueue, CalculationTask, CalculationTaskCreation
from geo_prompts import CALCULATION_MANAGER_PROMPT, MANAGER_JSON_TEMPLATE
from agents.calculation.utils.calculation_utils import (
    update_calculation_queue,
    determine_next_calculation
)
from utils.llm_manager import LLMManager
from utils.json_parser import safe_parse_llm_json_output

def calculation_manager_agent(state: GeometryState) -> GeometryState:
    """
    计算任务管理代理
    
    分析几何问题，确定需要执行的计算任务，并创建和管理计算任务队列
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    print("[DEBUG] Starting calculation_manager_agent")

    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationTaskCreation)
    
    # LLM 초기화
    llm = LLMManager.get_calculation_manager_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = CALCULATION_MANAGER_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # 에이전트 생성 대신 체인 사용
    chain = prompt | llm
    
    # 계산 큐 확인 및 초기화 (없는 경우)
    if state.calculation_queue is None:
        state.calculation_queue = CalculationQueue(
            tasks=[],
            current_task_id=None,
            completed_task_ids=[]
        )
    
    # 계산 결과 초기화 (없는 경우)
    if state.calculation_results is None:
        state.calculation_results = {}
    
    # 현재 큐 상태 및 결과 추출
    calculation_queue = state.calculation_queue
    calculation_results = state.calculation_results
    
    # 파싱된 문제 유형과 분석 결과 추출
    parsed_elements = state.parsed_elements
    problem_analysis = state.problem_analysis if hasattr(state, "problem_analysis") else {}
    problem_type = problem_analysis.get("problem_type", {}) if problem_analysis else parsed_elements.get("problem_type", {})
    analyzed_conditions = parsed_elements.get("analyzed_conditions", {}) if parsed_elements else {}
    
    # 접근 방법 설정
    approach = state.approach or problem_analysis.get("approach", "") if problem_analysis else ""
    
    # 에이전트 실행
    result = chain.invoke({
        "problem": state.input_problem,
        "parsed_elements": str(parsed_elements),
        "problem_type": str(problem_type),
        "analyzed_conditions": str(analyzed_conditions),
        "approach": str(approach),
        "problem_analysis": str(problem_analysis),
        "calculation_queue": str(calculation_queue),
        "calculation_results": str(calculation_results),
        "json_template": MANAGER_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 에이전트 응답 분석하여 작업 큐 업데이트
    try:
        # 유틸리티 함수를 사용하여 JSON 출력 파싱
        parsed_result = safe_parse_llm_json_output(result, CalculationTaskCreation, output_parser)
        
        # 파싱된 결과가 딕셔너리인지 확인하고 작업 병합
        if isinstance(parsed_result, dict):
            tasks_list = parsed_result.get("tasks", [])
            completed_ids = parsed_result.get("completed_task_ids", [])
            next_calc_type = parsed_result.get("next_calculation_type")
        else:
            # Pydantic 모델 객체인 경우
            tasks_list = parsed_result.tasks
            completed_ids = parsed_result.completed_task_ids
            next_calc_type = parsed_result.next_calculation_type
        
        # 기존 큐에 새로운 작업 병합
        for task_info in tasks_list:
            # 작업 ID 생성 또는 재사용
            task_id = task_info.get("task_id", f"{task_info['task_type']}_{len(state.calculation_queue.tasks) + 1}")
            
            # 이미 존재하는 작업인지 확인
            existing_task = None
            for task in state.calculation_queue.tasks:
                if task.task_id == task_id:
                    existing_task = task
                    break
            
            if existing_task:
                # 기존 작업 업데이트
                existing_task.parameters.update(task_info.get("parameters", {}))
                existing_task.dependencies = list(set(existing_task.dependencies + task_info.get("dependencies", [])))
                
                # GeoGebra 대체 정보 업데이트
                if "geogebra_alternatives" in task_info:
                    existing_task.geogebra_alternatives = task_info["geogebra_alternatives"]
                if "geogebra_command" in task_info:
                    existing_task.geogebra_command = task_info["geogebra_command"]
                
                # GeoGebra 대체 가능 작업은 완료된 것으로 처리
                if existing_task.geogebra_alternatives and existing_task.geogebra_command:
                    if existing_task.task_id not in state.calculation_queue.completed_task_ids:
                        state.calculation_queue.completed_task_ids.append(existing_task.task_id)
                    existing_task.status = "completed"
                    
                    # 결과 정보에 GeoGebra 명령어 저장
                    if "geogebra_direct_commands" not in state.calculation_results:
                        state.calculation_results["geogebra_direct_commands"] = []
                    
                    # 이미 저장된 명령어인지 확인
                    command_exists = False
                    for cmd in state.calculation_results.get("geogebra_direct_commands", []):
                        if cmd.get("task_id") == existing_task.task_id:
                            command_exists = True
                            break
                    
                    if not command_exists:
                        state.calculation_results["geogebra_direct_commands"].append({
                            "task_id": existing_task.task_id,
                            "task_type": existing_task.task_type,
                            "parameters": existing_task.parameters,
                            "geogebra_command": existing_task.geogebra_command
                        })
            else:
                # 새 작업 추가
                new_task = CalculationTask(
                    task_id=task_id,
                    task_type=task_info["task_type"],
                    parameters=task_info.get("parameters", {}),
                    dependencies=task_info.get("dependencies", []),
                    description=task_info.get("description", ""),
                    status="pending",
                    geogebra_alternatives=task_info.get("geogebra_alternatives", False),
                    geogebra_command=task_info.get("geogebra_command")
                )
                
                # GeoGebra 대체 가능 작업은 바로 완료된 것으로 처리
                if new_task.geogebra_alternatives and new_task.geogebra_command:
                    if new_task.task_id not in state.calculation_queue.completed_task_ids:
                        completed_ids.append(new_task.task_id)
                    new_task.status = "completed"
                    
                    # 결과 정보에 GeoGebra 명령어 저장
                    if "geogebra_direct_commands" not in state.calculation_results:
                        state.calculation_results["geogebra_direct_commands"] = []
                    
                    state.calculation_results["geogebra_direct_commands"].append({
                        "task_id": new_task.task_id,
                        "task_type": new_task.task_type,
                        "parameters": new_task.parameters,
                        "geogebra_command": new_task.geogebra_command
                    })
                
                state.calculation_queue.tasks.append(new_task)
        
        # 완료된 작업 ID 업데이트
        for task_id in completed_ids:
            if task_id not in state.calculation_queue.completed_task_ids:
                state.calculation_queue.completed_task_ids.append(task_id)
                
                # 해당 작업의 상태도 completed로 변경
                for task in state.calculation_queue.tasks:
                    if task.task_id == task_id:
                        task.status = "completed"
                        break
        
        # 다음 계산 유형 설정 및 현재 작업 설정
        if next_calc_type:
            state.next_calculation = next_calc_type
            
            # 완료되지 않은 해당 유형의 첫 번째 대기 중인 작업 찾기
            for task in state.calculation_queue.tasks:
                if (task.task_type == next_calc_type and 
                    task.status == "pending" and 
                    task.task_id not in state.calculation_queue.completed_task_ids):
                    state.calculation_queue.current_task_id = task.task_id
                    task.status = "running"
                    print(f"[DEBUG] Setting current_task_id to {task.task_id} and status to running")
                    break
        else:
            # next_calculation_type이 null이면 모든 작업이 완료된 것으로 간주
            print("[DEBUG] No more calculation tasks to process. Setting next_calculation to None for merger.")
            state.next_calculation = None
        
    except Exception as e:
        print(f"Error parsing calculation manager result as structured JSON: {e}")
        # JSON 파싱 실패 시 텍스트 기반 방식으로 처리
        update_calculation_queue(state, result.content)
        
    # 다음 계산 유형이 설정되지 않은 경우 결정
    if not state.next_calculation:
        determine_next_calculation(state)
    
    return state 