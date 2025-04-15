from typing import Dict, Any, List
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from models.state_models import CalculationQueue, CalculationTask, AnalysisResult, ConstructionPlan
from utils.llm_manager import LLMManager
from utils.prompts import ANALYSIS_PROMPT, ANALYSIS_JSON_TEMPLATE
from utils.construction_util import build_construction_plan



def analysis_agent(state):
    """
    기하학 문제 분석 에이전트
    
    Args:
        state: 현재 상태(GeometryState 객체), input_problem, parsed_elements 속성 포함
        
    Returns:
        분석 정보가 추가된 상태 딕셔너리
    """
    # LLM 설정
    llm = LLMManager.get_analysis_agent_llm()
    
    # JSON 출력 파서 생성
    parser = JsonOutputParser(pydantic_object=AnalysisResult)
    
    # 파싱 에이전트에서 이미 처리한 정보 활용
    existing_problem_type = state.parsed_elements.get("problem_type", {})
    existing_approach = state.parsed_elements.get("approach", "GeoGebra作图")
    
    # 프롬프트 체인 생성 및 실행
    chain = ANALYSIS_PROMPT | llm | parser
    result = chain.invoke({
        "problem": state.input_problem,
        "parsed_elements": str(state.parsed_elements),
        "json_template": ANALYSIS_JSON_TEMPLATE
    })
    
    # 상태 업데이트 - 파싱 에이전트에서 이미 분석한 problem_type과 approach 사용
    state.problem_analysis = {
        "problem_type": existing_problem_type,
        "approach": existing_approach,
        "calculation_types": result["calculation_types"],
        "reasoning": result["reasoning"],
        "suggested_tasks": result["suggested_tasks"],
        "suggested_tasks_reasoning": result.get("suggested_tasks_reasoning", "")
    }
    
    # 계산이 필요한지 여부 설정
    state.requires_calculation = result["requires_calculation"]
    
    # 계산이 필요 없는 경우 construction_plan 생성
    if not result["requires_calculation"]:
        # 직접 생성된 construction_plan 사용 또는 유틸리티로 생성
        if result.get("construction_plan"):
            state.construction_plan = result["construction_plan"]
        else:
            # 유틸리티로 계획 생성
            state.construction_plan = build_construction_plan(
                state.input_problem,
                state.parsed_elements
            )
    
    # 계산 관련 로직 초기화
    if state.requires_calculation:
        # 계산 큐 초기화
        state.calculation_queue = CalculationQueue(
            tasks=[],
            current_task_id=None,
            completed_task_ids=[]
        )
        
        # 초기 계산 유형 설정 (우선순위에 따라)
        for calc_type, needed in result["calculation_types"].items():
            if needed:
                state.next_calculation = calc_type
                break
        
        # 초기 계산 작업 추가 (제안된 작업이 있는 경우)
        if result["suggested_tasks"]:
            completed_task_ids = []
            
            for i, task_info in enumerate(result["suggested_tasks"]):
                task_id = f"{task_info['task_type']}_{i+1}"
                
                # GeoGebra 대체 가능 여부 확인
                geogebra_alternatives = task_info.get("geogebra_alternatives", False)
                geogebra_command = task_info.get("geogebra_command")
                
                # 계산 작업 생성
                task = CalculationTask(
                    task_id=task_id,
                    task_type=task_info['task_type'],
                    operation_type=task_info.get('operation_type'),
                    parameters=task_info.get('parameters', {}),
                    dependencies=task_info.get('dependencies', []),
                    description=task_info.get('description', ''),
                    geogebra_alternatives=geogebra_alternatives,
                    geogebra_command=geogebra_command
                )
                
                # GeoGebra 명령어로 대체 가능한 경우 바로 완료된 것으로 처리
                if geogebra_alternatives and geogebra_command:
                    completed_task_ids.append(task_id)
                    task.status = "completed"
                    
                    # 계산 결과에 GeoGebra 명령어 정보 추가
                    if "geogebra_direct_commands" not in state.calculation_results:
                        state.calculation_results["geogebra_direct_commands"] = []
                    
                    state.calculation_results["geogebra_direct_commands"].append({
                        "task_id": task_id,
                        "task_type": task.task_type,
                        "parameters": task.parameters,
                        "geogebra_command": geogebra_command
                    })
                
                # 작업을 큐에 추가
                state.calculation_queue.tasks.append(task)
            
            # 완료된 작업 ID를 큐에 추가
            state.calculation_queue.completed_task_ids.extend(completed_task_ids)
    
    return state 