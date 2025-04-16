from typing import Dict, Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool, Tool
from agents.calculation.wrappers import (
    calculate_distance_points_wrapper,
    calculate_distance_point_to_line_wrapper,
    calculate_distance_parallel_lines_wrapper,
    calculate_perimeter_triangle_wrapper,
    calculate_perimeter_quadrilateral_wrapper,
    calculate_perimeter_polygon_wrapper,
    calculate_circumference_wrapper,
    calculate_chord_length_wrapper,
    calculate_arc_length_wrapper
)
from agents.calculation.schemas.length_schemas import (
    DistanceBetweenPointsInput,
    DistancePointToLineInput,
    DistanceParallelLinesInput,
    PerimeterTriangleInput,
    PerimeterQuadrilateralInput,
    PerimeterPolygonInput,
    CircumferenceInput,
    ChordLengthInput,
    ArcLengthInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models.calculation_result_model import CalculationResult
from agents.calculation.prompts.length_prompt import LENGTH_CALCULATION_PROMPT, LENGTH_JSON_TEMPLATE
from utils.llm_manager import LLMManager
import json
import re
from utils.json_parser import safe_parse_llm_json_output

def length_calculation_agent(state: GeometryState) -> GeometryState:
    """
    长度计算代理
    
    执行与长度相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    print("[DEBUG] Starting length_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Setting it to the first pending length task.")
        # 작업 ID가 없는 경우 첫 번째 대기 중인 길이 작업 설정
        for task in state.calculation_queue.tasks:
            if task.task_type == "length" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    if not current_task_id or not current_task_id.startswith("length_"):
        # 작업 ID가 없거나 길이 작업이 아닌 경우
        print(f"[DEBUG] Task ID not set or not a length task: {current_task_id}. Returning state.")
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
    
    
    # 도구 생성
    tools = [
        StructuredTool.from_function(
            name="calculate_distance_points",
            func=calculate_distance_points_wrapper,
            description="计算两点之间的距离",
            args_schema=DistanceBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_distance_point_to_line",
            func=calculate_distance_point_to_line_wrapper,
            description="计算点到直线的距离",
            args_schema=DistancePointToLineInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_distance_parallel_lines",
            func=calculate_distance_parallel_lines_wrapper,
            description="计算两条平行线之间的距离",
            args_schema=DistanceParallelLinesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_perimeter_triangle",
            func=calculate_perimeter_triangle_wrapper,
            description="计算三角形的周长",
            args_schema=PerimeterTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_perimeter_quadrilateral",
            func=calculate_perimeter_quadrilateral_wrapper,
            description="计算四边形的周长",
            args_schema=PerimeterQuadrilateralInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_perimeter_polygon",
            func=calculate_perimeter_polygon_wrapper,
            description="计算多边形的周长",
            args_schema=PerimeterPolygonInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circumference",
            func=calculate_circumference_wrapper,
            description="计算圆的周长",
            args_schema=CircumferenceInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_chord_length",
            func=calculate_chord_length_wrapper,
            description="计算圆的弦长",
            args_schema=ChordLengthInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_arc_length",
            func=calculate_arc_length_wrapper,
            description="计算圆的弧长",
            args_schema=ArcLengthInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_length_calculation_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = LENGTH_CALCULATION_PROMPT.partial(
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
        "json_template": LENGTH_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 계산 결과 파싱 및 저장
    try:
        # 새로운 유틸리티 함수 사용
        parsed_result = safe_parse_llm_json_output(result["output"], CalculationResult, output_parser)
        if parsed_result:
            if isinstance(parsed_result, dict):
                current_task.result = parsed_result
            else:
                current_task.result = parsed_result.model_dump(exclude_none=True)
        else:
            current_task.result = {"raw_output": result["output"]}
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        current_task.result = {"raw_output": result["output"]}
    
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
        
    # 길이 결과 업데이트
    if "lengths" in task.result:
        if "lengths" not in state.calculation_results:
            state.calculation_results["lengths"] = {}
        state.calculation_results["lengths"].update(task.result["lengths"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 