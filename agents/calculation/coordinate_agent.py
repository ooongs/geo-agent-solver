from typing import Dict, Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool
from agents.calculation.wrappers.coordinate_wrappers import (
    calculate_midpoint_wrapper,
    calculate_slope_wrapper,
    calculate_line_equation_wrapper,
    are_points_collinear_wrapper,
    are_lines_parallel_wrapper,
    calculate_segment_division_wrapper,
    calculate_internal_division_point_wrapper,
    calculate_external_division_point_wrapper,
    is_point_on_segment_wrapper,
    calculate_vector_wrapper,
    calculate_dot_product_wrapper,
    calculate_cross_product_wrapper,
    normalize_vector_wrapper,
    calculate_distance_point_to_line_wrapper,
    calculate_line_intersection_wrapper,
    calculate_ray_intersection_wrapper,
    are_lines_perpendicular_wrapper,
    is_point_inside_triangle_wrapper
)
from agents.calculation.schemas.coordinate_schemas import (
    MidpointInput,
    SlopeInput,
    LineEquationInput,
    CollinearInput,
    LinesParallelInput,
    SegmentDivisionInput,
    InternalDivisionPointInput,
    ExternalDivisionPointInput,
    PointOnSegmentInput,
    VectorInput,
    DotProductInput,
    CrossProductInput,
    NormalizeVectorInput,
    PointToLineInput,
    LineIntersectionInput,
    RayIntersectionInput,
    LinesPerpendicularInput,
    PointInTriangleInput
)
from langchain_core.output_parsers import JsonOutputParser
from models.calculation_result_model import CalculationResult
from geo_prompts import COORDINATE_CALCULATION_PROMPT, COORDINATE_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from agents.calculation.utils.result_utils import update_calculation_results
from utils.json_parser import safe_parse_llm_json_output

def coordinate_calculation_agent(state: GeometryState) -> GeometryState:
    """
    개선된 좌표 계산 에이전트
    """
    print("[DEBUG] Starting coordinate_calculation_agent")

    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    # 작업 ID 처리
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Finding a pending coordinate task.")
        for task in state.calculation_queue.tasks:
            if task.task_type == "coordinate" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    # 현재 작업 찾기
    current_task = None
    for task in state.calculation_queue.tasks:
        if task.task_id == current_task_id:
            current_task = task
            break
    
    # task_type 확인으로 변경
    if not current_task or current_task.task_type != "coordinate":
        print(f"[DEBUG] No coordinate task found. Returning state.")
        return state
    
    # 현재 작업에서 사용 가능한 도구 확인
    available_tools = current_task.available_tools if hasattr(current_task, 'available_tools') else {}
    use_math_tools = "math_tools" in available_tools
    use_validation_tools = "validation_tools" in available_tools
    
    # 数学工具
    math_tools = []
    if use_math_tools:
        math_tools = [
            StructuredTool.from_function(
                name="calculate_midpoint",
                func=calculate_midpoint_wrapper,
                description="Calculate the midpoint between two points",
                args_schema=MidpointInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_slope",
                func=calculate_slope_wrapper,
                description="Calculate the slope of a line passing through two points",
                args_schema=SlopeInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_line_equation",
                func=calculate_line_equation_wrapper,
                description="Calculate the equation of a line passing through two points",
                args_schema=LineEquationInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_segment_division",
                func=calculate_segment_division_wrapper,
                description="Calculate a point that divides a line segment in a given ratio",
                args_schema=SegmentDivisionInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_internal_division_point",
                func=calculate_internal_division_point_wrapper,
                description="Calculate the internal division point of a line segment",
                args_schema=InternalDivisionPointInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_external_division_point",
                func=calculate_external_division_point_wrapper,
                description="Calculate the external division point of a line segment",
                args_schema=ExternalDivisionPointInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_vector",
                func=calculate_vector_wrapper,
                description="Calculate a vector between two points",
                args_schema=VectorInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_dot_product",
                func=calculate_dot_product_wrapper,
                description="Calculate the dot product of two vectors",
                args_schema=DotProductInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_cross_product",
                func=calculate_cross_product_wrapper,
                description="Calculate the cross product of two vectors",
                args_schema=CrossProductInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="normalize_vector",
                func=normalize_vector_wrapper,
                description="Normalize a vector",
                args_schema=NormalizeVectorInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_distance_point_to_line",
                func=calculate_distance_point_to_line_wrapper,
                description="Calculate the distance from a point to a line",
                args_schema=PointToLineInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_line_intersection",
                func=calculate_line_intersection_wrapper,
                description="Calculate the intersection point of two lines",
                args_schema=LineIntersectionInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_ray_intersection",
                func=calculate_ray_intersection_wrapper,
                description="Calculate the intersection of a ray with a line segment",
                args_schema=RayIntersectionInput,
                handle_tool_error=True
            )
        ]
    
    # 验真工具
    validation_tools = []
    if use_validation_tools:
        validation_tools = [
            StructuredTool.from_function(
                name="check_collinearity",
                func=are_points_collinear_wrapper,
                description="Check if three points are collinear",
                args_schema=CollinearInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_parallelism",
                func=are_lines_parallel_wrapper,
                description="Check if two lines are parallel",
                args_schema=LinesParallelInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_perpendicularity",
                func=are_lines_perpendicular_wrapper,
                description="Check if two lines are perpendicular",
                args_schema=LinesPerpendicularInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_point_on_segment",
                func=is_point_on_segment_wrapper,
                description="Check if a point lies on a line segment",
                args_schema=PointOnSegmentInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_point_in_triangle",
                func=is_point_inside_triangle_wrapper,
                description="Check if a point is inside a triangle",
                args_schema=PointInTriangleInput,
                handle_tool_error=True
            )
        ]
    
    # 모든 도구 합치기
    tools = math_tools + validation_tools
    
    # 도구가 없는 경우 기본 세트 사용
    if not tools:
        print("[DEBUG] No specific tools available. Using default tools set.")
        tools = [
            StructuredTool.from_function(
                name="calculate_midpoint",
                func=calculate_midpoint_wrapper,
                description="Calculate the midpoint between two points",
                args_schema=MidpointInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_slope",
                func=calculate_slope_wrapper,
                description="Calculate the slope of a line passing through two points",
                args_schema=SlopeInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_line_equation",
                func=calculate_line_equation_wrapper,
                description="Calculate the equation of a line passing through two points",
                args_schema=LineEquationInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_collinearity",
                func=are_points_collinear_wrapper,
                description="Check if three points are collinear",
                args_schema=CollinearInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_parallelism",
                func=are_lines_parallel_wrapper,
                description="Check if two lines are parallel",
                args_schema=LinesParallelInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_segment_division",
                func=calculate_segment_division_wrapper,
                description="Calculate a point that divides a line segment in a given ratio",
                args_schema=SegmentDivisionInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_internal_division_point",
                func=calculate_internal_division_point_wrapper,
                description="Calculate the internal division point of a line segment",
                args_schema=InternalDivisionPointInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="calculate_external_division_point",
                func=calculate_external_division_point_wrapper,
                description="Calculate the external division point of a line segment",
                args_schema=ExternalDivisionPointInput,
                handle_tool_error=True
            ),
            StructuredTool.from_function(
                name="check_point_on_segment",
                func=is_point_on_segment_wrapper,
                description="Check if a point lies on a line segment",
                args_schema=PointOnSegmentInput,
                handle_tool_error=True
            )
        ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_coordinate_calculation_llm()
    
    # 프롬프트 생성
    prompt = COORDINATE_CALCULATION_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 종속성 데이터 준비 - 입력을 위한 데이터 변환 추가
    task_dependencies = {}
    if current_task.dependencies:
        for dep_id in current_task.dependencies:
            if dep_id in state.calculation_results:
                task_dependencies[dep_id] = state.calculation_results[dep_id]
    
    # 종속성 데이터 처리 - 작업 파라미터에 필요한 데이터 추가
    enhanced_task = current_task.model_dump()
    if current_task.parameters and task_dependencies:
        # 특정 종속성 데이터 변환 로직 (예: 각 삼등분 → 좌표 계산)
        for dep_id, dep_data in task_dependencies.items():
            # 각 삼등분 결과를 좌표 계산을 위한 입력으로 변환
            if dep_id.startswith("angle_") and enhanced_task.get("operation_type") == "rayIntersection":
                # 방향 벡터 정보 추출 및 파라미터에 추가
                rays = dep_data.get("geometric_elements", {}).get("rays", [])
                if rays:
                    enhanced_task["parameters"]["rays"] = rays
    
    # 에이전트 실행 - 종속성 데이터 전달
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "current_task": str(enhanced_task),
        "calculation_results": str(state.calculation_results),
        "dependencies": str(task_dependencies),  # 종속성 데이터 전달
        "json_template": COORDINATE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 결과 처리
    try:
        print(f"[DEBUG] 파싱을 시작합니다: 출력 타입 = {type(result)}")
        
        # output 필드가 있는지 확인하고 적절히 처리
        result_output = None
        if isinstance(result, dict) and "output" in result:
            result_output = result["output"]
            print(f"[DEBUG] 딕셔너리에서 output 필드를 추출했습니다: {type(result_output)}")
        elif hasattr(result, 'output'):
            result_output = result.output
            print(f"[DEBUG] 객체에서 output 속성을 추출했습니다: {type(result_output)}")
        elif hasattr(result, 'content'):
            result_output = result.content
            print(f"[DEBUG] 객체에서 content 속성을 추출했습니다: {type(result_output)}")
        else:
            result_output = result
            print(f"[DEBUG] 결과를 그대로 사용합니다: {type(result_output)}")
            
        # 사용자 제공 JSON 형식을 직접 파싱 시도
        # 만약 이것이 딕셔너리라면 그대로 사용
        if isinstance(result_output, dict):
            print("[DEBUG] 결과가 이미 딕셔너리 형태입니다")
            parsed_result = result_output
        else:
            # 안전한 파싱 함수를 사용하여 문자열에서 JSON 파싱
            print("[DEBUG] safe_parse_llm_json_output 함수로 파싱 시도")
            parsed_result = safe_parse_llm_json_output(result_output, dict)
        
        print(f"[DEBUG] 파싱 결과: {type(parsed_result)}")
        
        if parsed_result:
            # 파싱된 결과가 딕셔너리인 경우
            if isinstance(parsed_result, dict):
                print(f"[DEBUG] 파싱된 딕셔너리를 결과로 사용: {list(parsed_result.keys())[:5] if parsed_result else '빈 딕셔너리'}")
                current_task.result = parsed_result
            # 파싱된 결과가 CalculationResult 인스턴스인 경우
            else:
                print("[DEBUG] CalculationResult 객체를 딕셔너리로 변환")
                current_task.result = parsed_result.to_dict()
        else:
            print("[WARNING] 파싱 결과가 없어 원본 출력을 raw_output으로 저장")
            current_task.result = {"raw_output": str(result_output), "success": False}
    except Exception as e:
        print(f"[ERROR] 계산 결과 파싱 중 오류 발생: {e}")
        # 오류 발생 시 원본 출력 내용을 저장하고 성공 상태를 False로 설정
        if isinstance(result, dict) and "output" in result:
            raw_output = result["output"]
        else:
            raw_output = str(result)
        current_task.result = {"raw_output": raw_output, "success": False, "error": str(e)}
    
    # 작업 상태 업데이트
    current_task.status = "completed"
    
    # 완료된 작업 목록에 추가
    if current_task_id not in state.calculation_queue.completed_task_ids:
        state.calculation_queue.completed_task_ids.append(current_task_id)
    
    # 전체 계산 결과에 추가 - 범용 함수 사용
    update_calculation_results(state, current_task)
    
    return state
