from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from agents.calculation.wrappers.area_wrappers import (
    calculate_area_triangle_wrapper,
    calculate_area_triangle_from_sides_wrapper,
    calculate_area_triangle_from_base_height_wrapper,
    calculate_area_rectangle_wrapper,
    calculate_area_rectangle_from_points_wrapper,
    calculate_area_square_wrapper,
    calculate_area_parallelogram_wrapper,
    calculate_area_parallelogram_from_points_wrapper,
    calculate_area_rhombus_wrapper,
    calculate_area_rhombus_from_points_wrapper,
    calculate_area_trapezoid_wrapper,
    calculate_area_trapezoid_from_points_wrapper,
    calculate_area_regular_polygon_wrapper,
    calculate_area_polygon_wrapper,
    calculate_area_circle_wrapper,
    calculate_area_sector_wrapper,
    calculate_area_segment_wrapper
)
from agents.calculation.schemas.area_schemas import (
    TriangleAreaFromPointsInput,
    TriangleAreaFromSidesInput,
    TriangleAreaFromBaseHeightInput,
    RectangleAreaFromPointsInput,
    RectangleAreaFromWidthHeightInput,
    SquareAreaFromSideInput,
    ParallelogramAreaFromPointsInput,
    RhombusAreaFromPointsInput,
    RhombusAreaFromDiagonalsInput,
    TrapezoidAreaFromPointsInput,
    TrapezoidAreaFromBaseHeightInput,
    RegularPolygonAreaFromSideInput,
    PolygonAreaFromPointsInput,
    CircleAreaFromRadiusInput,
    SectorAreaFromRadiusAngleInput,
    SegmentAreaFromRadiusAngleInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models.calculation_result_model import CalculationResult
from agents.calculation.prompts.area_prompt import AREA_CALCULATION_PROMPT, AREA_JSON_TEMPLATE
from utils.llm_manager import LLMManager

def area_calculation_agent(state: GeometryState) -> GeometryState:
    """
    面积计算代理
    
    执行与面积相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    print("[DEBUG] Starting area_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Setting it to the first pending area task.")
        # 작업 ID가 없는 경우 첫 번째 대기 중인 면적 작업 설정
        for task in state.calculation_queue.tasks:
            if task.task_type == "area" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    if not current_task_id or not current_task_id.startswith("area_"):
        # 작업 ID가 없거나 면적 작업이 아닌 경우
        print(f"[DEBUG] Task ID not set or not an area task: {current_task_id}. Returning state.")
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
            name="calculate_area_triangle",
            func=calculate_area_triangle_wrapper,
            description="计算三角形面积（使用顶点坐标）",
            args_schema=TriangleAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_triangle_from_sides",
            func=calculate_area_triangle_from_sides_wrapper,
            description="计算三角形面积（使用三条边长度）",
            args_schema=TriangleAreaFromSidesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_triangle_from_base_height",
            func=calculate_area_triangle_from_base_height_wrapper,
            description="计算三角形面积（使用底边和高）",
            args_schema=TriangleAreaFromBaseHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rectangle",
            func=calculate_area_rectangle_wrapper,
            description="计算矩形面积",
            args_schema=RectangleAreaFromWidthHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rectangle_from_points",
            func=calculate_area_rectangle_from_points_wrapper,
            description="计算矩形面积（使用顶点坐标）",
            args_schema=RectangleAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_square",
            func=calculate_area_square_wrapper,
            description="计算正方形面积",
            args_schema=SquareAreaFromSideInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_parallelogram",
            func=calculate_area_parallelogram_wrapper,
            description="计算平行四边形面积",
            args_schema=ParallelogramAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_parallelogram_from_points",
            func=calculate_area_parallelogram_from_points_wrapper,
            description="计算平行四边形面积（使用顶点坐标）",
            args_schema=ParallelogramAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rhombus",
            func=calculate_area_rhombus_wrapper,
            description="计算菱形面积（使用对角线）",
            args_schema=RhombusAreaFromDiagonalsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rhombus_from_points",
            func=calculate_area_rhombus_from_points_wrapper,
            description="计算菱形面积（使用顶点坐标）",
            args_schema=RhombusAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_trapezoid",
            func=calculate_area_trapezoid_wrapper,
            description="计算梯形面积",
            args_schema=TrapezoidAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_trapezoid_from_points",
            func=calculate_area_trapezoid_from_points_wrapper,
            description="计算梯形面积（使用顶点坐标）",
            args_schema=TrapezoidAreaFromBaseHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_regular_polygon",
            func=calculate_area_regular_polygon_wrapper,
            description="计算正多边形面积",
            args_schema=RegularPolygonAreaFromSideInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_polygon",
            func=calculate_area_polygon_wrapper,
            description="计算多边形面积",
            args_schema=PolygonAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_circle",
            func=calculate_area_circle_wrapper,
            description="计算圆面积",
            args_schema=CircleAreaFromRadiusInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_sector",
            func=calculate_area_sector_wrapper,
            description="计算扇形面积",
            args_schema=SectorAreaFromRadiusAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_segment",
            func=calculate_area_segment_wrapper,
            description="计算弓形面积",
            args_schema=SegmentAreaFromRadiusAngleInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_area_calculation_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = AREA_CALCULATION_PROMPT.partial(
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
        "json_template": AREA_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    
    # 계산 결과 파싱 및 저장
    try:
        parsed_result = output_parser.parse(result["output"])
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"Error parsing area calculation result: {e}")
        # 파싱 실패 시 결과 텍스트 그대로 저장
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
        
    # 면적 결과 업데이트
    if "areas" in task.result:
        if "areas" not in state.calculation_results:
            state.calculation_results["areas"] = {}
        state.calculation_results["areas"].update(task.result["areas"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 