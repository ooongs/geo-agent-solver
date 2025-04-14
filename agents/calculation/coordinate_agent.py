from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from tools.coordinate_tools import CoordinateTools
from tools.wrappers.coordinate_wrappers import (
    calculate_midpoint_wrapper,
    calculate_slope_wrapper,
    calculate_line_equation_wrapper,
    are_points_collinear_wrapper,
    are_lines_parallel_wrapper
)
from tools.schemas.coordinate_schemas import (
    CoordinateInput,
    MidpointInput,
    SlopeInput,
    LineEquationInput,
    CollinearInput,
    LinesParallelInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models import CalculationResult
from agents.calculation.prompts.coordinate_prompt import COORDINATE_CALCULATION_PROMPT, COORDINATE_JSON_TEMPLATE

def coordinate_calculation_agent(state: GeometryState) -> GeometryState:
    """
    坐标计算代理
    
    执行与坐标相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    if not current_task_id or not current_task_id.startswith("coordinate_"):
        # 작업 ID가 없거나 좌표 작업이 아닌 경우
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
            name="coordinate_calculator",
            func=CoordinateTools.calculate_coordinate_tool,
            description="执行综合坐标计算，包括多个点的坐标、中点、距离等",
            args_schema=CoordinateInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_midpoint",
            func=calculate_midpoint_wrapper,
            description="计算两点的中点坐标",
            args_schema=MidpointInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_slope",
            func=calculate_slope_wrapper,
            description="计算两点连线的斜率",
            args_schema=SlopeInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_line_equation",
            func=calculate_line_equation_wrapper,
            description="计算通过两点的直线方程（ax + by + c = 0 形式）",
            args_schema=LineEquationInput,
            handle_tool_error=True
        ),
        Tool(
            name="check_points_collinear",
            func=are_points_collinear_wrapper,
            description="检查三点是否共线，如果不共线则计算三角形面积",
            args_schema=CollinearInput,
            handle_tool_error=True
        ),
        Tool(
            name="check_lines_parallel",
            func=are_lines_parallel_wrapper,
            description="检查两直线是否平行，如果不平行则计算交点",
            args_schema=LinesParallelInput,
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
    
    # 계산 결과 파싱 및 저장
    try:
        parsed_result = output_parser.parse(result["output"])
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"Error parsing coordinate calculation result: {e}")
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
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 