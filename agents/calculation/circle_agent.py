from typing import Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool
from agents.calculation.wrappers.circle_wrappers import (
    calculate_circle_area_wrapper,
    calculate_circle_circumference_wrapper,
    calculate_circle_diameter_wrapper,
    calculate_circle_radius_wrapper,
    calculate_chord_length_wrapper,
    calculate_sector_area_wrapper,
    calculate_segment_area_wrapper,
    check_point_circle_position_wrapper,
    calculate_tangent_points_wrapper,
    calculate_circle_intersection_wrapper,
    calculate_circle_from_three_points_wrapper,
    calculate_circle_from_center_and_point_wrapper,
    calculate_central_angle_wrapper,
    calculate_inscribed_angle_wrapper,
    calculate_power_of_point_wrapper
)
from agents.calculation.schemas.circle_schemas import (
    CircleRadiusInput,
    CircleDiameterInput,
    CircleChordLengthInput,
    CircleSectorAreaInput,
    CircleSegmentAreaInput,
    PointCirclePositionInput,
    CircleTangentPointsInput,
    CircleIntersectionInput,
    CircleFromThreePointsInput,
    CircleFromCenterPointInput,
    CentralAngleInput,
    InscribedAngleInput,
    PowerOfPointInput
)
from langchain_core.output_parsers import JsonOutputParser
from models.calculation_result_model import CalculationResult
from geo_prompts import CIRCLE_CALCULATION_PROMPT, CIRCLE_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from agents.calculation.utils.result_utils import update_calculation_results
from utils.json_parser import safe_parse_llm_json_output

def circle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    범용적인 원 계산 에이전트
    
    원 관련 기하학적 계산 수행
    """
    print("[DEBUG] Starting circle_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Finding a pending circle task.")
        for task in state.calculation_queue.tasks:
            if task.task_type == "circle" and task.status == "pending":
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
    if not current_task or current_task.task_type != "circle":
        print(f"[DEBUG] No circle task found. Returning state.")
        return state
    
    # 도구 생성
    tools = [
        StructuredTool.from_function(
            name="calculate_circle_area",
            func=calculate_circle_area_wrapper,
            description="Calculate the area of a circle given its radius",
            args_schema=CircleRadiusInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circle_circumference",
            func=calculate_circle_circumference_wrapper,
            description="Calculate the circumference of a circle given its radius",
            args_schema=CircleRadiusInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circle_diameter",
            func=calculate_circle_diameter_wrapper,
            description="Calculate the diameter of a circle given its radius",
            args_schema=CircleRadiusInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circle_radius",
            func=calculate_circle_radius_wrapper,
            description="Calculate the radius of a circle given its diameter",
            args_schema=CircleDiameterInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_chord_length",
            func=calculate_chord_length_wrapper,
            description="Calculate the length of a chord in a circle given radius and central angle",
            args_schema=CircleChordLengthInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_sector_area",
            func=calculate_sector_area_wrapper,
            description="Calculate the area of a sector in a circle given radius and central angle",
            args_schema=CircleSectorAreaInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_segment_area",
            func=calculate_segment_area_wrapper,
            description="Calculate the area of a segment in a circle given radius and central angle",
            args_schema=CircleSegmentAreaInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="check_point_circle_position",
            func=check_point_circle_position_wrapper,
            description="Check the position of a point relative to a circle (inside, on, or outside)",
            args_schema=PointCirclePositionInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_tangent_points",
            func=calculate_tangent_points_wrapper,
            description="Calculate tangent points from an external point to a circle",
            args_schema=CircleTangentPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circle_intersection",
            func=calculate_circle_intersection_wrapper,
            description="Calculate intersection points of two circles given their centers and radii",
            args_schema=CircleIntersectionInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circle_from_three_points",
            func=calculate_circle_from_three_points_wrapper,
            description="Calculate a circle passing through three given points",
            args_schema=CircleFromThreePointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circle_from_center_and_point",
            func=calculate_circle_from_center_and_point_wrapper,
            description="Calculate a circle given its center and a point on the circle",
            args_schema=CircleFromCenterPointInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_central_angle",
            func=calculate_central_angle_wrapper,
            description="Calculate the central angle formed by two points on a circle",
            args_schema=CentralAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_inscribed_angle",
            func=calculate_inscribed_angle_wrapper,
            description="Calculate the inscribed angle in a circle formed by three points",
            args_schema=InscribedAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_power_of_point",
            func=calculate_power_of_point_wrapper,
            description="Calculate the power of a point with respect to a circle",
            args_schema=PowerOfPointInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_circle_calculation_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = CIRCLE_CALCULATION_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 종속성 데이터 준비 - 추가된 부분
    task_dependencies = {}
    if current_task.dependencies:
        for dep_id in current_task.dependencies:
            if dep_id in state.calculation_results:
                task_dependencies[dep_id] = state.calculation_results[dep_id]
    
    # 종속성 데이터 처리 - 작업 파라미터에 필요한 데이터 추가 - 추가된 부분
    enhanced_task = current_task.model_dump()
    if current_task.parameters and task_dependencies:
        # 특정 종속성 데이터 변환 로직 (원 계산에 맞게 조정)
        for dep_id, dep_data in task_dependencies.items():
            # 예: 좌표 데이터를 원 계산에 활용
            if "coordinates" in dep_data:
                enhanced_task["parameters"]["coordinates"] = dep_data["coordinates"]
    
    # 에이전트 실행 - 종속성 데이터 전달 - 수정된 부분
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "current_task": str(enhanced_task),
        "calculation_results": str(state.calculation_results),
        "dependencies": str(task_dependencies),  # 종속성 데이터 전달 - 추가됨
        "json_template": CIRCLE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # 계산 결과 파싱 및 저장
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
    
    # 전체 계산 결과에 추가 - 공통 함수 사용으로 변경
    update_calculation_results(state, current_task)
    
    return state 