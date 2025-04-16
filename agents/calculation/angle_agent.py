from typing import Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool
from agents.calculation.tools.angle_tools import AngleTools
from agents.calculation.wrappers.angle_wrappers import (
    calculate_angle_three_points_wrapper,
    calculate_angle_two_lines_wrapper,
    calculate_angle_two_vectors_wrapper,
    calculate_interior_angles_triangle_wrapper,
    calculate_exterior_angles_triangle_wrapper,
    calculate_inscribed_angle_wrapper,
    calculate_angle_bisector_wrapper,
    calculate_angle_trisection_wrapper,
    angle_classification_wrapper
)
from agents.calculation.schemas.angle_schemas import (
    RadiansToDegreesInput, 
    DegreesToRadiansInput, 
    AngleBetweenPointsInput, 
    AngleBetweenLinesInput, 
    AngleBetweenVectorsInput,
    AngleTriangleInput,
    InscribedAngleInput,
    AngleClassificationInput
)
from langchain_core.output_parsers import JsonOutputParser
from models.calculation_result_model import CalculationResult
from geo_prompts import ANGLE_CALCULATION_PROMPT, ANGLE_JSON_TEMPLATE
from utils.llm_manager import LLMManager

def angle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    角度计算代理
    
    执行与角度相关的几何计算
    
    Args:
        state: 当前状态对象
        
    Returns:
        更新后的状态对象
    """
    print("[DEBUG] Starting angle_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Setting it to the first pending angle task.")
        # 작업 ID가 없는 경우 첫 번째 대기 중인 각도 작업 설정
        for task in state.calculation_queue.tasks:
            if task.task_type == "angle" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    if not current_task_id or not current_task_id.startswith("angle_"):
        # 작업 ID가 없거나 각도 작업이 아닌 경우
        print(f"[DEBUG] Task ID not set or not a angle task: {current_task_id}. Returning state.")
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
            name="calculate_angle_points",
            func=calculate_angle_three_points_wrapper,
            description="计算三点形成的角度",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_vectors",
            func=calculate_angle_two_vectors_wrapper,
            description="计算两个向量之间的角度",
            args_schema=AngleBetweenVectorsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_lines",
            func=calculate_angle_two_lines_wrapper,
            description="计算两条直线之间的角度",
            args_schema=AngleBetweenLinesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_angles",
            func=calculate_interior_angles_triangle_wrapper,
            description="计算三角形的三个内角",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_exterior_angles",
            func=calculate_exterior_angles_triangle_wrapper,
            description="计算三角形的外角",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_bisector",
            func=calculate_angle_bisector_wrapper,
            description="计算角平分线",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_trisection",
            func=calculate_angle_trisection_wrapper,
            description="计算角的三等分线",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_angle_type",
            func=angle_classification_wrapper,
            description="判断角的类型（锐角、直角、钝角）",
            args_schema=AngleClassificationInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="radians_to_degrees",
            func=AngleTools.radians_to_degrees,
            description="将弧度值转换为角度值（度）",
            args_schema=RadiansToDegreesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_inscribed_angle",
            func=calculate_inscribed_angle_wrapper,
            description="计算圆内接角",
            args_schema=InscribedAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="degrees_to_radians",
            func=AngleTools.degrees_to_radians,
            description="将角度值（度）转换为弧度值",
            args_schema=DegreesToRadiansInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_angle_calculation_llm()
    
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
        "json_template": ANGLE_JSON_TEMPLATE,
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