from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from tools.length_tools import LengthTools
from tools.wrappers.length_wrappers import (
    calculate_distance_points_wrapper,
    calculate_distance_point_to_line_wrapper,
    calculate_distance_parallel_lines_wrapper,
    calculate_perimeter_triangle_wrapper,
    calculate_perimeter_quadrilateral_wrapper,
    calculate_perimeter_polygon_wrapper,
    calculate_circumference_wrapper,
    calculate_chord_length_wrapper,
    calculate_arc_length_wrapper,
    calculate_midpoint_wrapper,
    calculate_segment_division_wrapper,
    calculate_internal_division_point_wrapper,
    calculate_external_division_point_wrapper,
    is_point_on_segment_wrapper
)
from tools.schemas.length_schemas import (
    LengthInput,
    DistanceBetweenPointsInput,
    DistancePointToLineInput,
    DistanceParallelLinesInput,
    PerimeterTriangleInput,
    PerimeterQuadrilateralInput,
    PerimeterPolygonInput,
    CircumferenceInput,
    ChordLengthInput,
    ArcLengthInput,
    MidpointInput,
    SegmentDivisionInput,
    InternalDivisionPointInput,
    ExternalDivisionPointInput,
    PointOnSegmentInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models import CalculationResult
from agents.calculation.prompts.length_prompt import LENGTH_CALCULATION_PROMPT, LENGTH_JSON_TEMPLATE
import json
import re

def extract_json_from_llm_output(output: str) -> str:
    """
    LLM 출력에서 JSON 부분만 추출하는 함수
    
    Args:
        output: LLM의 출력 문자열
        
    Returns:
        JSON 문자열만 추출된 결과
    """
    # JSON 전체를 찾기 위한 정규식
    json_pattern = r'({[\s\S]*})'
    json_matches = re.findall(json_pattern, output)
    
    if json_matches:
        # 가장 큰 JSON 블록을 찾음 (일반적으로 전체 응답이 JSON일 가능성이 높음)
        largest_match = max(json_matches, key=len)
        return largest_match
    
    return output  # JSON을 찾지 못한 경우 원본 반환

def length_calculation_agent(state: GeometryState) -> GeometryState:
    """
    长度计算代理
    
    执行与长度相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    if not current_task_id or not current_task_id.startswith("length_"):
        # 작업 ID가 없거나 길이 작업이 아닌 경우
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
            name="length_calculator",
            func=LengthTools.calculate_length_tool,
            description="执行综合长度相关计算，包括多个功能的组合",
            args_schema=LengthInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_distance_points",
            func=calculate_distance_points_wrapper,
            description="计算两点之间的距离",
            args_schema=DistanceBetweenPointsInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_distance_point_to_line",
            func=calculate_distance_point_to_line_wrapper,
            description="计算点到直线的距离",
            args_schema=DistancePointToLineInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_distance_parallel_lines",
            func=calculate_distance_parallel_lines_wrapper,
            description="计算两条平行线之间的距离",
            args_schema=DistanceParallelLinesInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_perimeter_triangle",
            func=calculate_perimeter_triangle_wrapper,
            description="计算三角形的周长",
            args_schema=PerimeterTriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_perimeter_quadrilateral",
            func=calculate_perimeter_quadrilateral_wrapper,
            description="计算四边形的周长",
            args_schema=PerimeterQuadrilateralInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_perimeter_polygon",
            func=calculate_perimeter_polygon_wrapper,
            description="计算多边形的周长",
            args_schema=PerimeterPolygonInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circumference",
            func=calculate_circumference_wrapper,
            description="计算圆的周长",
            args_schema=CircumferenceInput,
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
            name="calculate_arc_length",
            func=calculate_arc_length_wrapper,
            description="计算圆的弧长",
            args_schema=ArcLengthInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_midpoint",
            func=calculate_midpoint_wrapper,
            description="计算两点的中点",
            args_schema=MidpointInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_segment_division",
            func=calculate_segment_division_wrapper,
            description="按比例计算线段上的分割点",
            args_schema=SegmentDivisionInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_internal_division_point",
            func=calculate_internal_division_point_wrapper,
            description="计算线段的内分点",
            args_schema=InternalDivisionPointInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_external_division_point",
            func=calculate_external_division_point_wrapper,
            description="计算线段的外分点",
            args_schema=ExternalDivisionPointInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_point_on_segment",
            func=is_point_on_segment_wrapper,
            description="判断点是否在线段上",
            args_schema=PointOnSegmentInput,
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
        # LLM 출력에서 JSON 부분만 추출
        json_output = extract_json_from_llm_output(result["output"])
        # 파싱 시도
        parsed_result = output_parser.parse(json_output)
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"첫 번째 파싱 방법 실패: {e}")
        # 첫 번째 방법 실패 시 직접 JSON 파싱 시도
        try:
            # 출력에서 JSON 부분만 추출
            json_output = extract_json_from_llm_output(result["output"])
            # 직접 파싱
            manual_result = json.loads(json_output)
            current_task.result = manual_result
            print(f"수동 JSON 파싱 성공")
        except Exception as e2:
            print(f"모든 파싱 방법 실패: {e2}")
            # 모든 파싱 실패 시 결과 텍스트 그대로 저장
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