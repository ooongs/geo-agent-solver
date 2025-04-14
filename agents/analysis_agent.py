from typing import Dict, Any, List
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from models.state_models import CalculationQueue, CalculationTask, AnalysisResult
from utils.llm_manager import LLMManager
from utils.prompts import ANALYSIS_PROMPT



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
    
    # 프롬프트 체인 생성 및 실행
    chain = ANALYSIS_PROMPT | llm | parser
    result = chain.invoke({
        "problem": state.input_problem,
        "parsed_elements": str(state.parsed_elements)
    })
    
    # 상태 업데이트
    state.problem_analysis = {
        "problem_type": result["problem_type"],
        "approach": result["approach"],
        "calculation_types": result["calculation_types"],
        "reasoning": result["reasoning"],
        "suggested_tasks": result["suggested_tasks"],
        "suggested_tasks_reasoning": result.get("suggested_tasks_reasoning", ""),
        "direct_geogebra_commands": result.get("direct_geogebra_commands", [])
    }
    
    # 계산이 필요한지 여부 설정
    state.requires_calculation = result["requires_calculation"]
    
    # 접근 방법 설정
    state.approach = result["approach"]
    
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
            for i, task_info in enumerate(result["suggested_tasks"]):
                task_id = f"{task_info['task_type']}_{i+1}"
                
                # GeoGebra 명령어로 대체 가능성 확인
                is_geogebra_alternative = False
                geogebra_command = None
                
                # direct_geogebra_commands에서 대응하는 명령 찾기
                for geogebra_cmd in result.get("direct_geogebra_commands", []):
                    if (geogebra_cmd.get("operation_type") == task_info.get("operation_type") and
                        all(task_info["parameters"].get(k) == v for k, v in geogebra_cmd.get("parameters", {}).items())):
                        is_geogebra_alternative = True
                        geogebra_command = geogebra_cmd.get("geogebra_command")
                        break
                
                state.calculation_queue.tasks.append(
                    CalculationTask(
                        task_id=task_id,
                        task_type=task_info['task_type'],
                        operation_type=task_info.get('operation_type'),
                        parameters=task_info.get('parameters', {}),
                        dependencies=task_info.get('dependencies', []),
                        description=task_info.get('description', ''),
                        geogebra_alternatives=is_geogebra_alternative,
                        geogebra_command=geogebra_command
                    )
                )
    
    return state 