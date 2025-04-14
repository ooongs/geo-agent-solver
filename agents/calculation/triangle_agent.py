from typing import Dict, Any, List, Optional, Union
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from tools.triangle_tools import TriangleTools
from tools.wrappers.triangle_wrappers import (
    calculate_area_wrapper,
    calculate_area_from_sides_wrapper,
    calculate_perimeter_wrapper,
    calculate_angles_wrapper,
    is_right_triangle_wrapper,
    is_isosceles_triangle_wrapper,
    is_equilateral_triangle_wrapper,
    calculate_centroid_wrapper,
    calculate_circumcenter_wrapper,
    calculate_incenter_wrapper,
    calculate_orthocenter_wrapper,
    calculate_triangle_centers_wrapper
)
from tools.schemas.triangle_schemas import TriangleInput, TriangleAreaInput, TrianglePerimeterInput, TriangleAngleInput
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models import CalculationResult
from agents.calculation.prompts.triangle_prompt import TRIANGLE_CALCULATION_PROMPT, TRIANGLE_JSON_TEMPLATE


def triangle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    三角形计算代理
    
    执行与三角形相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    if not current_task_id or not current_task_id.startswith("triangle_"):
        # 작업 ID가 없거나 삼각형 작업이 아닌 경우
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
            name="triangle_calculator",
            func=TriangleTools.calculate_triangle_tool,
            description="执行通用三角形相关计算，包括三角形的各种几何性质",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_area",
            func=calculate_area_wrapper,
            description="计算三角形的面积，需提供三个顶点坐标",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_area_from_sides",
            func=calculate_area_from_sides_wrapper,
            description="根据三边长度计算三角形的面积（使用海伦公式）",
            args_schema=TrianglePerimeterInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_perimeter",
            func=calculate_perimeter_wrapper,
            description="计算三角形的周长",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_angles",
            func=calculate_angles_wrapper,
            description="计算三角形的三个内角（弧度）",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_right_triangle",
            func=is_right_triangle_wrapper,
            description="判断三角形是否为直角三角形",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_isosceles_triangle",
            func=is_isosceles_triangle_wrapper,
            description="判断三角形是否为等腰三角形",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_equilateral_triangle",
            func=is_equilateral_triangle_wrapper,
            description="判断三角形是否为等边三角形",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_centroid",
            func=calculate_centroid_wrapper,
            description="计算三角形的重心",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circumcenter",
            func=calculate_circumcenter_wrapper,
            description="计算三角形的外心",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_incenter",
            func=calculate_incenter_wrapper,
            description="计算三角形的内心",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_orthocenter",
            func=calculate_orthocenter_wrapper,
            description="计算三角形的垂心",
            args_schema=TriangleInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_triangle_centers",
            func=calculate_triangle_centers_wrapper,
            description="计算三角形的所有中心点（重心、外心、内心、垂心）",
            args_schema=TriangleInput,
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
    prompt = TRIANGLE_CALCULATION_PROMPT.partial(
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
        "json_template": TRIANGLE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 계산 결과 파싱 및 저장
    try:
        parsed_result = output_parser.parse(result["output"])
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"Error parsing triangle calculation result: {e}")
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
    
    # 길이 결과 업데이트
    if "lengths" in task.result:
        if "lengths" not in state.calculation_results:
            state.calculation_results["lengths"] = {}
        state.calculation_results["lengths"].update(task.result["lengths"])
    
    # 각도 결과 업데이트
    if "angles" in task.result:
        if "angles" not in state.calculation_results:
            state.calculation_results["angles"] = {}
        state.calculation_results["angles"].update(task.result["angles"])
    
    # 면적 결과 업데이트
    if "areas" in task.result:
        if "areas" not in state.calculation_results:
            state.calculation_results["areas"] = {}
        state.calculation_results["areas"].update(task.result["areas"])
    
    # 둘레 결과 업데이트
    if "perimeters" in task.result:
        if "perimeters" not in state.calculation_results:
            state.calculation_results["perimeters"] = {}
        state.calculation_results["perimeters"].update(task.result["perimeters"])
    
    # 특수점 결과 업데이트
    if "special_points" in task.result:
        if "special_points" not in state.calculation_results:
            state.calculation_results["special_points"] = {}
        state.calculation_results["special_points"].update(task.result["special_points"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 