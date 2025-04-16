from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from agents.calculation.wrappers.triangle_wrappers import (
    calculate_area_wrapper,
    calculate_area_from_sides_wrapper,
    calculate_perimeter_wrapper,
    is_right_triangle_wrapper,
    is_isosceles_triangle_wrapper,
    is_equilateral_triangle_wrapper,
    calculate_angles_wrapper,
    calculate_centroid_wrapper,
    calculate_circumcenter_wrapper,
    calculate_incenter_wrapper,
    calculate_orthocenter_wrapper,
    calculate_triangle_centers_wrapper,
    triangle_classification_wrapper
)
from agents.calculation.schemas.triangle_schemas import (
    TriangleSidesInput,
    TriangleVerticesInput
)
from langchain_core.output_parsers import JsonOutputParser
from agents.calculation.models.calculation_result_model import CalculationResult
from agents.calculation.prompts.triangle_prompt import TRIANGLE_CALCULATION_PROMPT, TRIANGLE_JSON_TEMPLATE
from utils.llm_manager import LLMManager


def triangle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    三角形计算代理
    
    执行与三角形相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    print("[DEBUG] Starting triangle_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Setting it to the first pending triangle task.")
        # 작업 ID가 없는 경우 첫 번째 대기 중인 삼각형 작업 설정
        for task in state.calculation_queue.tasks:
            if task.task_type == "triangle" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    if not current_task_id or not current_task_id.startswith("triangle_"):
        # 작업 ID가 없거나 삼각형 작업이 아닌 경우
        print(f"[DEBUG] Task ID not set or not a triangle task: {current_task_id}. Returning state.")
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
            name="calculate_triangle_area",
            func=calculate_area_wrapper,
            description="计算三角形的面积（使用三个顶点坐标）",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_area_from_sides",
            func=calculate_area_from_sides_wrapper,
            description="计算三角形的面积（使用三边长度，海伦公式）",
            args_schema=TriangleSidesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_perimeter",
            func=calculate_perimeter_wrapper,
            description="计算三角形的周长",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_right_triangle",
            func=is_right_triangle_wrapper,
            description="判断三角形是否为直角三角形",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_isosceles_triangle",
            func=is_isosceles_triangle_wrapper,
            description="判断三角形是否为等腰三角形",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_equilateral_triangle",
            func=is_equilateral_triangle_wrapper,
            description="判断三角形是否为等边三角形",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_angles",
            func=calculate_angles_wrapper,
            description="计算三角形的三个角",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_centroid",
            func=calculate_centroid_wrapper,
            description="计算三角形的质心（重心）",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_circumcenter",
            func=calculate_circumcenter_wrapper,
            description="计算三角形的外心",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_incenter",
            func=calculate_incenter_wrapper,
            description="计算三角形的内心",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_orthocenter",
            func=calculate_orthocenter_wrapper,
            description="计算三角形的垂心",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_centers",
            func=calculate_triangle_centers_wrapper,
            description="计算三角形的所有中心点（质心、外心、内心、垂心）",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="triangle_classification",
            func=triangle_classification_wrapper,
            description="三角形分类（直角、锐角、钝角、等腰、等边等）",
            args_schema=TriangleVerticesInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_triangle_calculation_llm()
    
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
        
    # 삼각형 결과 업데이트
    if "triangles" in task.result:
        if "triangles" not in state.calculation_results:
            state.calculation_results["triangles"] = {}
        state.calculation_results["triangles"].update(task.result["triangles"])
    
    # 기타 결과 업데이트
    if "other_results" in task.result:
        if "other_results" not in state.calculation_results:
            state.calculation_results["other_results"] = {}
        state.calculation_results["other_results"].update(task.result["other_results"]) 