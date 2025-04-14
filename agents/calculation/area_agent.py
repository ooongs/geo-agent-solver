from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from tools.area_tools import AreaTools
from tools.wrappers.area_wrappers import (
    calculate_area_triangle_wrapper,
    calculate_area_triangle_from_sides_wrapper,
    calculate_area_triangle_from_base_height_wrapper,
    calculate_area_rectangle_wrapper,
    calculate_area_square_wrapper,
    calculate_area_parallelogram_wrapper,
    calculate_area_rhombus_wrapper,
    calculate_area_trapezoid_wrapper,
    calculate_area_regular_polygon_wrapper,
    calculate_area_polygon_wrapper,
    calculate_area_circle_wrapper,
    calculate_area_sector_wrapper,
    calculate_area_segment_wrapper
)
from tools.schemas.area_schemas import AreaInput, RectangleAreaInput, CircleAreaInput, TriangleAreaInput, PolygonAreaInput
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models import CalculationResult
from agents.calculation.prompts.area_prompt import AREA_CALCULATION_PROMPT, AREA_JSON_TEMPLATE

def area_calculation_agent(state: GeometryState) -> GeometryState:
    """
    面积计算代理
    
    执行与面积相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    if not current_task_id or not current_task_id.startswith("area_"):
        # 작업 ID가 없거나 면적 작업이 아닌 경우
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
            name="area_calculator",
            func=AreaTools.calculate_area_tool,
            description="执行通用面积相关计算，支持各种几何图形的面积计算",
            args_schema=AreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_triangle_area",
            func=calculate_area_triangle_wrapper,
            description="计算三角形的面积（使用三个顶点坐标）",
            args_schema=PolygonAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_triangle_area_from_sides",
            func=calculate_area_triangle_from_sides_wrapper,
            description="计算三角形的面积（使用三边长度，海伦公式）",
            args_schema=TriangleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_triangle_area_from_base_height",
            func=calculate_area_triangle_from_base_height_wrapper,
            description="计算三角形的面积（使用底和高）",
            args_schema=TriangleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_rectangle_area",
            func=calculate_area_rectangle_wrapper,
            description="计算矩形的面积（使用宽和高）",
            args_schema=RectangleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_square_area",
            func=calculate_area_square_wrapper,
            description="计算正方形的面积（使用边长）",
            args_schema=RectangleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_parallelogram_area",
            func=calculate_area_parallelogram_wrapper,
            description="计算平行四边形的面积（使用底和高）",
            args_schema=RectangleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_rhombus_area",
            func=calculate_area_rhombus_wrapper,
            description="计算菱形的面积（使用两条对角线）",
            args_schema=RectangleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_trapezoid_area",
            func=calculate_area_trapezoid_wrapper,
            description="计算梯形的面积（使用上底、下底和高）",
            args_schema=AreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_regular_polygon_area",
            func=calculate_area_regular_polygon_wrapper,
            description="计算正多边形的面积（使用边长和边数）",
            args_schema=AreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_polygon_area",
            func=calculate_area_polygon_wrapper,
            description="计算任意多边形的面积（使用顶点坐标）",
            args_schema=PolygonAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_circle_area",
            func=calculate_area_circle_wrapper,
            description="计算圆的面积（使用半径）",
            args_schema=CircleAreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_sector_area",
            func=calculate_area_sector_wrapper,
            description="计算扇形的面积（使用半径和角度）",
            args_schema=AreaInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_segment_area",
            func=calculate_area_segment_wrapper,
            description="计算弓形的面积（使用半径和角度）",
            args_schema=AreaInput,
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