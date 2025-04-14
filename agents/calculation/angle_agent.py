from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from tools.angle_tools import AngleTools
from tools.schemas.angle_schemas import AngleInput, RadiansToDegreesInput, DegreesToRadiansInput, AngleBetweenPointsInput
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models import CalculationResult
from agents.calculation.prompts.angle_prompt import ANGLE_CALCULATION_PROMPT, ANGLE_JSON_TEMPLATE

def angle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    角度计算代理
    
    执行与角度相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    if not current_task_id or not current_task_id.startswith("angle_"):
        # 작업 ID가 없거나 각도 작업이 아닌 경우
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
            name="angle_calculator",
            func=AngleTools.calculate_angle_tool,
            description="执行通用角度相关计算，包括角度大小、角平分线等",
            args_schema=AngleInput,
            handle_tool_error=True
        ),
        Tool(
            name="radians_to_degrees",
            func=AngleTools.radians_to_degrees,
            description="将弧度值转换为角度值（度）",
            args_schema=RadiansToDegreesInput,
            handle_tool_error=True
        ),
        Tool(
            name="degrees_to_radians",
            func=AngleTools.degrees_to_radians,
            description="将角度值（度）转换为弧度值",
            args_schema=DegreesToRadiansInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_angle_between_points",
            func=AngleTools.calculate_angle_three_points,
            description="计算由三个点形成的角度（第二个点为顶点）",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        Tool(
            name="calculate_angle_bisector",
            func=AngleTools.calculate_angle_bisector,
            description="计算角平分线的直线方程",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_angle_acute",
            func=AngleTools.is_angle_acute,
            description="判断给定角度是否为锐角（小于90°）",
            args_schema=RadiansToDegreesInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_angle_right",
            func=AngleTools.is_angle_right,
            description="判断给定角度是否为直角（等于90°）",
            args_schema=RadiansToDegreesInput,
            handle_tool_error=True
        ),
        Tool(
            name="is_angle_obtuse",
            func=AngleTools.is_angle_obtuse,
            description="判断给定角度是否为钝角（大于90°）",
            args_schema=RadiansToDegreesInput,
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
    prompt = ANGLE_CALCULATION_PROMPT.partial(
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
        "format_instructions": ANGLE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 계산 결과 파싱 및 저장
    try:
        parsed_result = output_parser.parse(result["output"])
        current_task.result = parsed_result.model_dump(exclude_none=True)
    except Exception as e:
        print(f"Error parsing angle calculation result: {e}")
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
        
    # 각도 결과 업데이트
    if "angles" in task.result:
        if "angles" not in state.calculation_results:
            state.calculation_results["angles"] = {}
        state.calculation_results["angles"].update(task.result["angles"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 