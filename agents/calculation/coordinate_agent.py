from typing import Dict, Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from agents.calculation.wrappers.coordinate_wrappers import (
    calculate_midpoint_wrapper,
    calculate_slope_wrapper,
    calculate_line_equation_wrapper,
    are_points_collinear_wrapper,
    are_lines_parallel_wrapper,
    calculate_segment_division_wrapper,
    calculate_internal_division_point_wrapper,
    calculate_external_division_point_wrapper,
    is_point_on_segment_wrapper
)
from agents.calculation.schemas.coordinate_schemas import (
    MidpointInput,
    SlopeInput,
    LineEquationInput,
    CollinearInput,
    LinesParallelInput,
    SegmentDivisionInput,
    InternalDivisionPointInput,
    ExternalDivisionPointInput,
    PointOnSegmentInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models.calculation_result_model import CalculationResult
from agents.calculation.prompts.coordinate_prompt import COORDINATE_CALCULATION_PROMPT, COORDINATE_JSON_TEMPLATE
from utils.llm_manager import LLMManager

def coordinate_calculation_agent(state: GeometryState) -> GeometryState:
    """
    坐标几何计算代理
    
    执行与坐标几何相关的计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    print("[DEBUG] Starting coordinate_calculation_agent")
    print(f"[DEBUG] Initial state: {state}")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Setting it to the first pending coordinate task.")
        # 작업 ID가 없는 경우 첫 번째 대기 중인 좌표 작업 설정
        for task in state.calculation_queue.tasks:
            if task.task_type == "coordinate" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    if not current_task_id or not current_task_id.startswith("coordinate_"):
        # 작업 ID가 없거나 좌표 작업이 아닌 경우
        print(f"[DEBUG] Task ID not set or not a coordinate task: {current_task_id}. Returning state.")
        return state
    
    # 현재 작업 찾기
    current_task = None
    for task in state.calculation_queue.tasks:
        if task.task_id == current_task_id:
            current_task = task
            break
            
    if not current_task:
        print(f"[DEBUG] Could not find task with ID {current_task_id}. Returning state.")
        return state
    
    print(f"[DEBUG] Current task: {current_task}")
    
    # 도구 생성
    tools = [
        StructuredTool.from_function(
            name="calculate_midpoint",
            func=calculate_midpoint_wrapper,
            description="计算两点之间的中点",
            args_schema=MidpointInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_slope",
            func=calculate_slope_wrapper,
            description="计算两点确定的直线的斜率",
            args_schema=SlopeInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_line_equation",
            func=calculate_line_equation_wrapper,
            description="计算两点确定的直线方程",
            args_schema=LineEquationInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="check_collinearity",
            func=are_points_collinear_wrapper,
            description="检查三点是否共线",
            args_schema=CollinearInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="check_parallelism",
            func=are_lines_parallel_wrapper,
            description="检查两条线是否平行",
            args_schema=LinesParallelInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="divide_line_segment",
            func=calculate_segment_division_wrapper,
            description="将线段按比例分割",
            args_schema=SegmentDivisionInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="find_internal_division_point",
            func=calculate_internal_division_point_wrapper,
            description="找到线段的内分点",
            args_schema=InternalDivisionPointInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="find_external_division_point",
            func=calculate_external_division_point_wrapper,
            description="找到线段的外分点",
            args_schema=ExternalDivisionPointInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="check_point_on_line_segment",
            func=is_point_on_segment_wrapper,
            description="检查点是否在线段上",
            args_schema=PointOnSegmentInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_coordinate_calculation_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = COORDINATE_CALCULATION_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 에이전트 실행
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "current_task": str(current_task.model_dump()),
        "calculation_results": str(state.calculation_results),
        "json_template": COORDINATE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    print(f"[DEBUG] Result from agent: {result}")
    
    # 계산 결과 파싱 및 저장
    try:
        parsed_result = output_parser.parse(result["output"])
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"Error parsing coordinate calculation result: {e}")
        # 파싱 실패 시 결과 텍스트 그대로 저장
        current_task.result = {"raw_output": result["output"]}
    
    print(f"[DEBUG] Parsed result: {current_task.result}")
    
    # 작업 상태 업데이트 - 완료로 설정
    current_task.status = "completed"
    
    # 이 작업을 완료된 작업 목록에 추가하고 큐에서 제거
    if current_task_id not in state.calculation_queue.completed_task_ids:
        state.calculation_queue.completed_task_ids.append(current_task_id)
    
    # 작업을 큐에서 제거
    for i, task in enumerate(state.calculation_queue.tasks[:]):
        if task.task_id == current_task_id:
            state.calculation_queue.tasks.pop(i)
            print(f"[DEBUG] Removed completed task {current_task_id} from queue")
            break
    
    # 현재 작업 ID 지우기
    state.calculation_queue.current_task_id = None
    
    # 전체 계산 결과에 추가
    _update_calculation_results(state, current_task)
    
    print(f"[DEBUG] Updated state: {state}")
    
    return state

def _update_calculation_results(state: GeometryState, task: Any) -> None:
    """
    전체 계산 결과 업데이트
    
    Args:
        state: 현재 상태 객체
        task: 완료된 계산 작업
    """
    if not task.result:
        return
        
    # 결과가 없는 경우 초기화
    if not state.calculation_results:
        state.calculation_results = {}
        
    # 좌표 결과 업데이트
    if "coordinates" in task.result:
        if "coordinates" not in state.calculation_results:
            state.calculation_results["coordinates"] = {}
        state.calculation_results["coordinates"].update(task.result["coordinates"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 