from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from tools.circle_tools import CircleTools
from tools.wrappers.circle_wrappers import (
    calculate_circle_area_wrapper,
    calculate_circle_circumference_wrapper,
    calculate_circle_diameter_wrapper,
    calculate_circle_radius_wrapper,
    calculate_circle_wrapper,
    calculate_chord_length_wrapper,
    calculate_sector_area_wrapper,
    calculate_segment_area_wrapper,
    check_point_circle_position_wrapper,
    calculate_tangent_points_wrapper,
    calculate_circle_intersection_wrapper,
    calculate_circle_from_three_points_wrapper
)
from tools.schemas.circle_schemas import (
    CircleInput,
    CircleAreaInput,
    CircleCircumferenceInput,
    CircleDiameterInput,
    CircleRadiusInput,
    ChordLengthInput,
    SectorAreaInput,
    SegmentAreaInput,
    PointCirclePositionInput,
    TangentPointsInput,
    CircleIntersectionInput,
    CircleFromThreePointsInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models import CalculationResult
from agents.calculation.prompts.circle_prompt import CIRCLE_CALCULATION_PROMPT, CIRCLE_JSON_TEMPLATE

def circle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    圆形计算代理
    
    执行与圆相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    if not current_task_id or not current_task_id.startswith("circle_"):
        # 작업 ID가 없거나 원 작업이 아닌 경우
        return state
    
    # 현재 작업 찾기
    current_task = None
    for task in state.calculation_queue.tasks:
        if task.task_id == current_task_id:
            current_task = task
            break
            
    if not current_task:
        return state
    
    # 도구 생성
    tools = [
        Tool(
            name="circle_calculator",
            func=CircleTools.calculate_circle_tool,
            description="执行综合圆形相关计算，包括圆的各种几何性质",
            args_schema=CircleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_area",
            func=calculate_circle_area_wrapper,
            description="计算圆的面积",
            args_schema=CircleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_circumference",
            func=calculate_circle_circumference_wrapper,
            description="计算圆的周长",
            args_schema=CircleCircumferenceInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_diameter",
            func=calculate_circle_diameter_wrapper,
            description="计算圆的直径",
            args_schema=CircleDiameterInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_radius",
            func=calculate_circle_radius_wrapper,
            description="计算圆的半径",
            args_schema=CircleRadiusInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle",
            func=calculate_circle_wrapper,
            description="综合计算圆的各种属性",
            args_schema=CircleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_chord_length",
            func=calculate_chord_length_wrapper,
            description="计算圆的弦长",
            args_schema=ChordLengthInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_sector_area",
            func=calculate_sector_area_wrapper,
            description="计算圆的扇形面积",
            args_schema=SectorAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_segment_area",
            func=calculate_segment_area_wrapper,
            description="计算圆的弓形面积",
            args_schema=SegmentAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="check_point_circle_position",
            func=check_point_circle_position_wrapper,
            description="检查点与圆的位置关系",
            args_schema=PointCirclePositionInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_tangent_points",
            func=calculate_tangent_points_wrapper,
            description="计算外部点到圆的切点",
            args_schema=TangentPointsInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_intersection",
            func=calculate_circle_intersection_wrapper,
            description="计算两个圆的交点",
            args_schema=CircleIntersectionInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_from_three_points",
            func=calculate_circle_from_three_points_wrapper,
            description="通过三个点计算确定一个圆",
            args_schema=CircleFromThreePointsInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4"
    )
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = CIRCLE_CALCULATION_PROMPT.partial(
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
        "json_template": CIRCLE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 계산 결과 파싱 및 저장
    try:
        parsed_result = output_parser.parse(result["output"])
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"Error parsing circle calculation result: {e}")
        # 파싱 실패 시 결과 텍스트 그대로 저장
        current_task.result = {"raw_output": result["output"]}
    
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
    
    # 좌표 결과 업데이트
    if "coordinates" in task.result:
        if "coordinates" not in state.calculation_results:
            state.calculation_results["coordinates"] = {}
        state.calculation_results["coordinates"].update(task.result["coordinates"])
    
    # 원 속성 결과 업데이트
    if "circle_properties" in task.result:
        if "circle_properties" not in state.calculation_results:
            state.calculation_results["circle_properties"] = {}
        state.calculation_results["circle_properties"].update(task.result["circle_properties"])
    
    # 면적 결과 업데이트
    if "areas" in task.result:
        if "areas" not in state.calculation_results:
            state.calculation_results["areas"] = {}
        state.calculation_results["areas"].update(task.result["areas"])
    
    # 접점 결과 업데이트
    if "tangent_points" in task.result:
        if "tangent_points" not in state.calculation_results:
            state.calculation_results["tangent_points"] = {}
        state.calculation_results["tangent_points"].update(task.result["tangent_points"])
    
    # 현의 길이 결과 업데이트
    if "chord_lengths" in task.result:
        if "chord_lengths" not in state.calculation_results:
            state.calculation_results["chord_lengths"] = {}
        state.calculation_results["chord_lengths"].update(task.result["chord_lengths"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 