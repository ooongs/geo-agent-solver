from typing import Dict, Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool, Tool
from agents.calculation.wrappers import (
    calculate_distance_points_wrapper,
    calculate_distance_point_to_line_wrapper,
    calculate_distance_parallel_lines_wrapper,
    calculate_perimeter_triangle_wrapper,
    calculate_perimeter_quadrilateral_wrapper,
    calculate_perimeter_polygon_wrapper,
    calculate_circumference_wrapper,
    calculate_chord_length_wrapper,
    calculate_arc_length_wrapper
)
from agents.calculation.schemas.length_schemas import (
    DistanceBetweenPointsInput,
    DistancePointToLineInput,
    DistanceParallelLinesInput,
    PerimeterTriangleInput,
    PerimeterQuadrilateralInput,
    PerimeterPolygonInput,
    CircumferenceInput,
    ChordLengthInput,
    ArcLengthInput
)
from langchain_core.output_parsers import JsonOutputParser
from models.calculation_result_model import CalculationResult
from geo_prompts import LENGTH_CALCULATION_PROMPT, LENGTH_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from agents.calculation.utils.result_utils import update_calculation_results
import json
import re
from utils.json_parser import safe_parse_llm_json_output

def length_calculation_agent(state: GeometryState) -> GeometryState:
    """
    범용적인 길이 계산 에이전트
    
    길이 관련 기하학적 계산 수행
    """
    print("[DEBUG] Starting length_calculation_agent")
    
    # 현재 작업 ID 가져오기
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Finding a pending length task.")
        for task in state.calculation_queue.tasks:
            if task.task_type == "length" and task.status == "pending":
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
    if not current_task or current_task.task_type != "length":
        print(f"[DEBUG] No length task found. Returning state.")
        return state
    
    
    # 도구 생성
    tools = [
        StructuredTool.from_function(
            name="calculate_distance_points",
            func=calculate_distance_points_wrapper,
            description="Calculate the distance between two points",
            args_schema=DistanceBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_distance_point_to_line",
            func=calculate_distance_point_to_line_wrapper,
            description="Calculate the distance from a point to a line",
            args_schema=DistancePointToLineInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_distance_parallel_lines",
            func=calculate_distance_parallel_lines_wrapper,
            description="Calculate the distance between two parallel lines",
            args_schema=DistanceParallelLinesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_perimeter_triangle",
            func=calculate_perimeter_triangle_wrapper,
            description="Calculate the perimeter of a triangle",
            args_schema=PerimeterTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_perimeter_quadrilateral",
            func=calculate_perimeter_quadrilateral_wrapper,
            description="Calculate the perimeter of a quadrilateral",
            args_schema=PerimeterQuadrilateralInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_perimeter_polygon",
            func=calculate_perimeter_polygon_wrapper,
            description="Calculate the perimeter of a polygon",
            args_schema=PerimeterPolygonInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_circumference",
            func=calculate_circumference_wrapper,
            description="Calculate the circumference of a circle",
            args_schema=CircumferenceInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_chord_length",
            func=calculate_chord_length_wrapper,
            description="Calculate the length of a chord in a circle",
            args_schema=ChordLengthInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_arc_length",
            func=calculate_arc_length_wrapper,
            description="Calculate the length of an arc in a circle",
            args_schema=ArcLengthInput,
            handle_tool_error=True
        )
    ]
    
    # 출력 파서 생성
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # LLM 초기화
    llm = LLMManager.get_length_calculation_llm()
    
    # 프롬프트 생성 (파서 지침 포함)
    prompt = LENGTH_CALCULATION_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 종속성 데이터 준비
    task_dependencies = {}
    if current_task.dependencies:
        for dep_id in current_task.dependencies:
            if dep_id in state.calculation_results:
                task_dependencies[dep_id] = state.calculation_results[dep_id]
    
    # 종속성 데이터 처리
    enhanced_task = current_task.model_dump()
    if current_task.parameters and task_dependencies:
        for dep_id, dep_data in task_dependencies.items():
            if "coordinates" in dep_data:
                enhanced_task["parameters"]["coordinates"] = dep_data["coordinates"]
    
    # 에이전트 실행
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "current_task": str(enhanced_task),
        "calculation_results": str(state.calculation_results),
        "dependencies": str(task_dependencies),
        "json_template": LENGTH_JSON_TEMPLATE,
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
    
    # 전체 계산 결과에 추가
    update_calculation_results(state, current_task)
    
    return state 