from typing import Dict, Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool
from agents.calculation.wrappers.area_wrappers import (
    calculate_area_triangle_wrapper,
    calculate_area_triangle_from_sides_wrapper,
    calculate_area_triangle_from_base_height_wrapper,
    calculate_area_rectangle_wrapper,
    calculate_area_rectangle_from_points_wrapper,
    calculate_area_square_wrapper,
    calculate_area_parallelogram_wrapper,
    calculate_area_parallelogram_from_points_wrapper,
    calculate_area_rhombus_wrapper,
    calculate_area_rhombus_from_points_wrapper,
    calculate_area_trapezoid_wrapper,
    calculate_area_trapezoid_from_points_wrapper,
    calculate_area_regular_polygon_wrapper,
    calculate_area_polygon_wrapper,
    calculate_area_circle_wrapper,
    calculate_area_sector_wrapper,
    calculate_area_segment_wrapper,
    calculate_area_quadrilateral_wrapper
)
from agents.calculation.schemas.area_schemas import (
    TriangleAreaFromPointsInput,
    TriangleAreaFromSidesInput,
    TriangleAreaFromBaseHeightInput,
    RectangleAreaFromPointsInput,
    RectangleAreaFromWidthHeightInput,
    SquareAreaFromSideInput,
    ParallelogramAreaFromPointsInput,
    RhombusAreaFromPointsInput,
    RhombusAreaFromDiagonalsInput,
    TrapezoidAreaFromPointsInput,
    TrapezoidAreaFromBaseHeightInput,
    RegularPolygonAreaFromSideInput,
    PolygonAreaFromPointsInput,
    CircleAreaFromRadiusInput,
    SectorAreaFromRadiusAngleInput,
    SegmentAreaFromRadiusAngleInput,
    ParallelogramAreaFromBaseHeightInput,
    QuadrilateralAreaFromPointsInput
)
from langchain_core.output_parsers import JsonOutputParser
from models.calculation_result_model import CalculationResult
from geo_prompts import AREA_CALCULATION_PROMPT, AREA_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from agents.calculation.utils.result_utils import update_calculation_results
from utils.json_parser import safe_parse_llm_json_output
def area_calculation_agent(state: GeometryState) -> GeometryState:
    """
    범용적인 면적 계산 에이전트
    
    면적 관련 기하학적 계산 수행
    """
    print("[DEBUG] Starting area_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Finding a pending area task.")
        for task in state.calculation_queue.tasks:
            if task.task_type == "area" and task.status == "pending":
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
    if not current_task or current_task.task_type != "area":
        print(f"[DEBUG] No area task found. Returning state.")
        return state
    
    
    # 도구 생성
    tools = [
        StructuredTool.from_function(
            name="calculate_area_triangle",
            func=calculate_area_triangle_wrapper,
            description="Calculate triangle area from vertices",
            args_schema=TriangleAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_triangle_from_sides",
            func=calculate_area_triangle_from_sides_wrapper,
            description="Calculate triangle area from three sides using Heron's formula",
            args_schema=TriangleAreaFromSidesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_triangle_from_base_height",
            func=calculate_area_triangle_from_base_height_wrapper,
            description="Calculate triangle area from base and height",
            args_schema=TriangleAreaFromBaseHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rectangle",
            func=calculate_area_rectangle_wrapper,
            description="Calculate rectangle area from width and height",
            args_schema=RectangleAreaFromWidthHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rectangle_from_points",
            func=calculate_area_rectangle_from_points_wrapper,
            description="Calculate rectangle area from vertices",
            args_schema=RectangleAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_square",
            func=calculate_area_square_wrapper,
            description="Calculate square area from side length",
            args_schema=SquareAreaFromSideInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_parallelogram",
            func=calculate_area_parallelogram_wrapper,
            description="Calculate parallelogram area from base and height",
            args_schema=ParallelogramAreaFromBaseHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_parallelogram_from_points",
            func=calculate_area_parallelogram_from_points_wrapper,
            description="Calculate parallelogram area from vertices",
            args_schema=ParallelogramAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rhombus",
            func=calculate_area_rhombus_wrapper,
            description="Calculate rhombus area from diagonals",
            args_schema=RhombusAreaFromDiagonalsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_rhombus_from_points",
            func=calculate_area_rhombus_from_points_wrapper,
            description="Calculate rhombus area from vertices",
            args_schema=RhombusAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_trapezoid",
            func=calculate_area_trapezoid_wrapper,
            description="Calculate trapezoid area from parallel sides and height",
            args_schema=TrapezoidAreaFromBaseHeightInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_trapezoid_from_points",
            func=calculate_area_trapezoid_from_points_wrapper,
            description="Calculate trapezoid area from vertices",
            args_schema=TrapezoidAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_regular_polygon",
            func=calculate_area_regular_polygon_wrapper,
            description="Calculate regular polygon area from side length and number of sides",
            args_schema=RegularPolygonAreaFromSideInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_polygon",
            func=calculate_area_polygon_wrapper,
            description="Calculate polygon area from vertices",
            args_schema=PolygonAreaFromPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_circle",
            func=calculate_area_circle_wrapper,
            description="Calculate circle area from radius",
            args_schema=CircleAreaFromRadiusInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_sector",
            func=calculate_area_sector_wrapper,
            description="Calculate sector area from radius and central angle",
            args_schema=SectorAreaFromRadiusAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_segment",
            func=calculate_area_segment_wrapper,
            description="Calculate segment area from radius and central angle",
            args_schema=SegmentAreaFromRadiusAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_area_quadrilateral",
            func=calculate_area_quadrilateral_wrapper,
            description="Calculate quadrilateral area from vertices",
            args_schema=QuadrilateralAreaFromPointsInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_area_calculation_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = AREA_CALCULATION_PROMPT.partial(
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
        # 특정 종속성 데이터 변환 로직 (면적 계산에 맞게 조정)
        for dep_id, dep_data in task_dependencies.items():
            # 예: 좌표 데이터를 면적 계산에 활용
            if "coordinates" in dep_data:
                enhanced_task["parameters"]["coordinates"] = dep_data["coordinates"]
            # 예: 길이 데이터를 면적 계산에 활용
            if "lengths" in dep_data:
                enhanced_task["parameters"]["lengths"] = dep_data["lengths"]
    
    # 에이전트 실행 - 종속성 데이터 전달 - 수정된 부분
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "current_task": str(enhanced_task),
        "calculation_results": str(state.calculation_results),
        "dependencies": str(task_dependencies),  # 종속성 데이터 전달 - 추가됨
        "json_template": AREA_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    
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

# 기존 _update_calculation_results 함수 제거 