"""
Enhanced Calculation Manager Agent Module

This module defines an advanced calculation manager agent that builds dependency graphs,
manages task execution order, and optimizes geometric calculation processes.
"""

from typing import Dict, Any, List, Optional, Union
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from models.state_models import GeometryState, CalculationTask, DependencyGraph, DependencyNode
from geo_prompts import CALCULATION_MANAGER_PROMPT, MANAGER_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from utils.json_parser import safe_parse_llm_json_output
from agents.calculation.utils import refine_calculation_manager_input

def build_dependency_graph(tasks: List[CalculationTask]) -> DependencyGraph:
    """
    Build a dependency graph from a list of calculation tasks
    
    Args:
        tasks: List of calculation tasks
        
    Returns:
        A dependency graph object
    """
    graph = DependencyGraph(nodes={})
    
    # First pass: create nodes
    for task in tasks:
        node = DependencyNode(
            task_id=task.task_id,
            dependencies=task.dependencies,
            status="completed" if task.status == "completed" else "pending"
        )
        graph.nodes[task.task_id] = node
    
    # Second pass: determine execution order
    available_tasks = set()
    execution_order = []
    completed_tasks = set()
    
    # Initialize with tasks that have no dependencies
    for task_id, node in graph.nodes.items():
        if not node.dependencies or all(dep in completed_tasks for dep in node.dependencies):
            available_tasks.add(task_id)
    
    # Build execution order
    while available_tasks:
        # Choose a task (for now, just take any)
        task_id = next(iter(available_tasks))
        available_tasks.remove(task_id)
        
        # Add to execution order and mark as completed
        execution_order.append(task_id)
        completed_tasks.add(task_id)
        
        # Find new available tasks
        for next_id, node in graph.nodes.items():
            if next_id not in completed_tasks and next_id not in available_tasks:
                if all(dep in completed_tasks for dep in node.dependencies):
                    available_tasks.add(next_id)
    
    graph.execution_order = execution_order
    return graph

def enhance_calculation_request(task: CalculationTask, results: Dict[str, Any]) -> CalculationTask:
    """
    Enhance a calculation request with context and results from previous calculations
    
    Args:
        task: The calculation task to enhance
        results: Current calculation results
        
    Returns:
        Enhanced calculation task
    """
    enhanced_task = task.copy()
    
    # Integrate dependency results
    for dep in task.dependencies:
        if dep in results:
            # Add dependency results to task parameters
            enhanced_task.parameters[f"{dep}_result"] = results[dep]
    
    return enhanced_task

def prioritize_coordinate_tasks(tasks: List[CalculationTask]) -> List[CalculationTask]:
    """
    Prioritize coordinate calculation tasks for basic geometric elements

    Args:
        tasks: List of calculation tasks

    Returns:
        Prioritized list of calculation tasks
    """
    # Separate coordinate tasks and other tasks
    coordinate_tasks = []
    other_tasks = []
    
    for task in tasks:
        if task.task_type == "coordinate" and is_basic_geometry_task(task):
            coordinate_tasks.append(task)
        else:
            other_tasks.append(task)
    
    # Combine lists with coordinate tasks first
    return coordinate_tasks + other_tasks

def is_basic_geometry_task(task: CalculationTask) -> bool:
    """
    Check if a task is related to basic geometry element initialization

    Args:
        task: The calculation task to check

    Returns:
        True if the task is for basic geometry initialization, False otherwise
    """
    # Check for specific patterns indicating basic geometry setup
    if task.operation_type in ["point_coordinates", "initial_setup", "polygon_coordinates"]:
        return True
    
    # Check parameters for keywords indicating basic geometry
    params = task.parameters
    for key, value in params.items():
        if isinstance(value, str) and any(keyword in value.lower() 
                                         for keyword in ["initial", "basic", "setup", "reference"]):
            return True
    
    # Check description for keywords
    if task.description and any(keyword in task.description.lower() 
                              for keyword in ["initial", "setup", "reference point", "basic"]):
        return True
    
    return False

def get_available_tools_for_task(task_type: str) -> Dict[str, List[str]]:
    """
    Get available tools for a specific task type

    Args:
        task_type: Type of calculation task

    Returns:
        Dictionary of available tools categorized by tool type
    """
    # Define tools by task type
    tools_by_task = {
        "coordinate": {
            "math_tools": ["calculate_midpoint", "calculate_slope", "calculate_line_equation", "calculate_segment_division", "calculate_internal_division_point", "calculate_external_division_point", "calculate_vector", "calculate_dot_product", "calculate_cross_product", "normalize_vector", "calculate_distance_point_to_line", "calculate_line_intersection", "calculate_ray_intersection"],
            "validation_tools": ["check_collinearity", "check_parallelism", "check_perpendicularity", "check_point_on_segment", "check_point_in_triangle"],
        },
        "angle": {
            "math_tools": ["calculate_angle_three_points", "calculate_angle_with_direction", "calculate_angle_two_vectors", "calculate_angle_two_lines", "calculate_triangle_interior_angles", "calculate_triangle_exterior_angles", "calculate_inscribed_angle", "calculate_angle_bisector", "calculate_angle_trisection", "calculate_angle_complement", "calculate_angle_supplement", "normalize_angle", "calculate_rotation", "calculate_regular_polygon_angle", "radians_to_degrees", "degrees_to_radians"],
            "validation_tools": ["classify_angle", "is_angle_acute", "is_angle_right", "is_angle_obtuse", "is_angle_straight", "is_angle_reflex", "is_triangle_acute", "is_triangle_right", "is_triangle_obtuse", "is_triangle_equiangular"],
        },
        "triangle": {
            "math_tools": ["calculate_triangle_area", "calculate_triangle_area_from_sides", "calculate_triangle_perimeter", "calculate_triangle_angles", "calculate_triangle_centroid", "calculate_triangle_circumcenter", "calculate_triangle_incenter", "calculate_triangle_orthocenter", "calculate_triangle_centers", "calculate_triangle_inradius", "calculate_triangle_circumradius", "calculate_triangle_median_lengths", "calculate_triangle_altitude_lengths"],
            "validation_tools": ["is_right_triangle", "is_isosceles_triangle", "is_equilateral_triangle", "triangle_classification", "is_point_inside_triangle"],
        },
        "circle": {
            "math_tools": ["calculate_circle_area", "calculate_circle_circumference", "calculate_circle_diameter", "calculate_circle_radius", "calculate_chord_length", "calculate_sector_area", "calculate_segment_area", "calculate_circle_from_three_points", "calculate_circle_from_center_and_point", "calculate_central_angle", "calculate_inscribed_angle", "calculate_power_of_point"],
            "validation_tools": ["check_point_circle_position", "calculate_tangent_points", "calculate_circle_intersection"],
        },
        "length": {
            "math_tools": ["calculate_distance_points", "calculate_distance_point_to_line", "calculate_distance_parallel_lines", "calculate_perimeter_triangle", "calculate_perimeter_quadrilateral", "calculate_perimeter_polygon", "calculate_circumference", "calculate_chord_length", "calculate_arc_length"],
        },
        "area": {
            "math_tools": ["calculate_area_triangle", "calculate_area_triangle_from_sides", "calculate_area_triangle_from_base_height", "calculate_area_rectangle", "calculate_area_rectangle_from_points", "calculate_area_square", "calculate_area_parallelogram", "calculate_area_parallelogram_from_points", "calculate_area_rhombus", "calculate_area_rhombus_from_points", "calculate_area_trapezoid", "calculate_area_trapezoid_from_points", "calculate_area_regular_polygon", "calculate_area_polygon", "calculate_area_circle", "calculate_area_sector", "calculate_area_segment", "calculate_area_quadrilateral"],
        },
    }

    # Return tools for the specified task type or empty dictionary if not found
    return tools_by_task.get(task_type, {"math_tools": [], "validation_tools": []})

def calculation_manager_agent(state: GeometryState) -> GeometryState:
    """
    Enhanced calculation manager agent
    
    Analyzes geometry problems, creates and manages calculation tasks, 
    builds dependency relationships, and optimizes the solution process.
    
    Now modified to only run once at the beginning of the calculation process.
    
    Args:
        state: Current state object
        
    Returns:
        Updated state object
    """
    print("[DEBUG] Starting calculation_manager_agent")
    
    # 이미 초기화된 경우 바로 라우터로 넘어감
    if getattr(state, 'is_manager_initialized', False):
        print("[DEBUG] Manager already initialized. Routing to calculation_router_agent.")
        return state
    
    # 입력 데이터 정제
    refined_input = refine_calculation_manager_input(state)
    
    # 상세 입력 로깅
    print(f"[DEBUG] Refined Input: {str(refined_input)[:200]}...")
    
    # LLM 초기화
    llm = LLMManager.get_calculation_manager_llm()
    
    # 프롬프트 생성
    prompt = CALCULATION_MANAGER_PROMPT
    
    # 출력 파서 생성
    output_parser = JsonOutputParser()
    
    # 첫 실행인지 확인 - 초기 계산 작업 생성 필요
    is_first_run = (not state.calculation_queue.tasks)
    
    # 첫 실행인 경우, Planner의 청사진으로부터 작업 생성
    if is_first_run and hasattr(state, 'problem_analysis') and state.problem_analysis.get('suggested_tasks_blueprint'):
        print("[DEBUG] First run: Creating initial tasks from planner blueprint")
        
        blueprint = state.problem_analysis.get('suggested_tasks_blueprint', [])
        completed_task_ids = []
        
        # 청사진에서 작업 생성
        for i, task_info in enumerate(blueprint):
            task_id = f"{task_info['task_type']}_{i+1}"
            
            # GeoGebra 대체 가능 여부 확인
            geogebra_alternatives = task_info.get("geogebra_alternatives", False)
            geogebra_command = task_info.get("geogebra_command")
            
            # 도구 목록 가져오기
            available_tools = get_available_tools_for_task(task_info['task_type'])
            
            # 계산 작업 생성
            task = CalculationTask(
                task_id=task_id,
                task_type=task_info['task_type'],
                operation_type=task_info.get('operation_type'),
                parameters=task_info.get('parameters', {}),
                dependencies=task_info.get('dependencies', []),
                description=task_info.get('description', ''),
                status="pending",
                geogebra_alternatives=geogebra_alternatives,
                geogebra_command=geogebra_command,
                available_tools=available_tools  # 사용 가능한 도구 목록 추가
            )
            
            # GeoGebra 명령어로 대체 가능한 경우 바로 완료된 것으로 처리
            if geogebra_alternatives and geogebra_command:
                completed_task_ids.append(task_id)
                task.status = "completed"
                
                # 계산 결과에 GeoGebra 명령어 정보 추가
                if "geogebra_direct_commands" not in state.calculation_results:
                    state.calculation_results["geogebra_direct_commands"] = []
                
                state.calculation_results["geogebra_direct_commands"].append({
                    "task_id": task_id,
                    "task_type": task.task_type,
                    "parameters": task.parameters,
                    "geogebra_command": geogebra_command
                })
            
            # 작업을 큐에 추가
            state.calculation_queue.tasks.append(task)
        
        # 기본 도형 좌표 계산 작업 우선 순위 지정
        state.calculation_queue.tasks = prioritize_coordinate_tasks(state.calculation_queue.tasks)
        
        # 완료된 작업 ID를 큐에 추가
        state.calculation_queue.completed_task_ids.extend(completed_task_ids)
        
        # 기본 의존성 그래프 생성
        if state.calculation_queue.tasks:
            state.calculation_queue.dependency_graph = build_dependency_graph(state.calculation_queue.tasks)
    
    # 체인 생성
    chain = prompt | llm | output_parser
    
    # 에이전트 실행 - 정제된 입력 사용
    result = chain.invoke({
        "problem": refined_input["problem"],
        "parsed_elements": str(refined_input["parsed_elements"]),
        "problem_analysis": str(refined_input["problem_analysis"]),
        "calculation_results": str(refined_input["calculation_results"]),
        "calculation_queue": str(refined_input.get("calculation_queue", {})),
        "json_template": MANAGER_JSON_TEMPLATE,
        "format_instructions": output_parser.get_format_instructions()
    })
    
    # LLM 응답 로깅
    print(f"[DEBUG] Manager Agent Raw Response: {str(result)[:200]}...")
    
    try:
        # 결과가 이미 딕셔너리 형태인지 확인
        if isinstance(result, dict):
            print("[DEBUG] 결과가 이미 딕셔너리 형태입니다")
            parsed_result = result
        else:
            # AIMessage 객체인지 확인하고 content 추출
            if hasattr(result, 'content'):
                print("[DEBUG] AIMessage 객체에서 content 추출")
                result_content = result.content
            else:
                result_content = result
                print(f"[DEBUG] 결과를 그대로 사용합니다: {type(result_content)}")
                
            # 개선된 JSON 파싱 로직
            try:
                # 기존 출력 파서 시도
                parsed_result = output_parser.parse(result_content)
                print("[DEBUG] 기본 출력 파서로 파싱 성공")
            except Exception as parser_error:
                print(f"[WARNING] 기본 출력 파서 실패: {parser_error}")
                
                # 사용자 제공 JSON 직접 처리 시도
                if isinstance(result_content, str) and result_content.strip().startswith('{'):
                    try:
                        import json
                        parsed_result = json.loads(result_content)
                        print("[DEBUG] 직접 JSON 파싱 성공")
                    except json.JSONDecodeError as json_error:
                        print(f"[WARNING] 직접 JSON 파싱 실패: {json_error}")
                        # 안전한 파서 시도
                        parsed_result = safe_parse_llm_json_output(result_content, dict)
                else:
                    # 안전한 파서 시도
                    print("[DEBUG] 안전한 JSON 파서로 파싱 시도")
                    parsed_result = safe_parse_llm_json_output(result_content, dict)
                
                # 안전한 파서도 실패하면 결과 문자열 직접 검사
                if not parsed_result and isinstance(result_content, str):
                    print("[DEBUG] 직접 JSON 추출 시도")
                    # JSON 부분 직접 추출 시도
                    import re
                    json_pattern = r'```json\s*([\s\S]*?)\s*```'
                    json_match = re.search(json_pattern, result_content)
                    if json_match:
                        try:
                            import json
                            json_str = json_match.group(1).strip()
                            parsed_result = json.loads(json_str)
                            print("[DEBUG] 마크다운 블록에서 JSON 추출 성공")
                        except Exception as direct_error:
                            print(f"[ERROR] 마크다운 블록에서 JSON 추출 실패: {direct_error}")
                            parsed_result = {}
                    else:
                        # 전체 JSON 객체 찾기 시도
                        json_obj_pattern = r'(\{[\s\S]*\})'
                        json_obj_match = re.search(json_obj_pattern, result_content)
                        if json_obj_match:
                            try:
                                json_str = json_obj_match.group(1).strip()
                                parsed_result = json.loads(json_str)
                                print("[DEBUG] 문자열에서 JSON 객체 추출 성공")
                            except Exception as json_error:
                                print(f"[ERROR] JSON 객체 추출 실패: {json_error}")
                                parsed_result = {}
                        else:
                            print("[WARNING] 결과에서 JSON 콘텐츠를 찾을 수 없습니다")
                            parsed_result = {}
        
        if parsed_result:
            print(f"[DEBUG] 파싱 결과 키: {parsed_result.keys() if parsed_result else 'None'}")
        else:
            print("[WARNING] 파싱 결과가 비어 있습니다")
        
        # 확실한 null 체크 추가
        if parsed_result is None:
            print("[WARNING] Manager 에이전트 응답 파싱 실패")
            # fallback 로직으로 직접 이동
            raise ValueError("Manager 응답 파싱 실패")
            
        # Extract analysis information
        if "analysis" in parsed_result:
            state.geometric_constraints = parsed_result.get("geometric_constraints", {}) or {}
        
        # Process dependency graph with stronger checks
        if "dependency_graph" in parsed_result and parsed_result["dependency_graph"] is not None:
            dep_graph_data = parsed_result["dependency_graph"]
            nodes = {}
            
            # Safer iteration with explicit None checks
            if "nodes" in dep_graph_data and dep_graph_data["nodes"] is not None:
                for node_id, node_data in dep_graph_data["nodes"].items():
                    if node_data is None:
                        node_data = {}
                    nodes[node_id] = DependencyNode(
                        task_id=node_id,
                        dependencies=node_data.get("dependencies", []) or [],
                        status=node_data.get("status", "pending")
                    )
            
            # Create dependency graph
            dep_graph = DependencyGraph(
                nodes=nodes,
                execution_order=dep_graph_data.get("execution_order", [])
            )
            
            # Update state with dependency graph
            if state.calculation_queue:
                state.calculation_queue.dependency_graph = dep_graph
        
        # Process tasks
        tasks_list = parsed_result.get("tasks", [])
        completed_ids = parsed_result.get("completed_task_ids", [])
        next_calc_type = parsed_result.get("next_calculation_type")
        
        # Update existing tasks and add new ones
        for task_info in tasks_list:
            task_id = task_info.get("task_id")
            
            # Check if this task already exists
            existing_task = None  # CalculationTask
            for task in state.calculation_queue.tasks:
                if task.task_id == task_id:
                    existing_task = task
                    break
            
            if existing_task:
                # Update existing task
                existing_task.parameters.update(task_info.get("parameters", {}))
                existing_task.dependencies = list(set(existing_task.dependencies + task_info.get("dependencies", [])))
                
                # Update special fields
                if "specific_method" in task_info:
                    existing_task.specific_method = task_info["specific_method"]
                if "required_precision" in task_info:
                    existing_task.required_precision = task_info["required_precision"]
                
                # Update GeoGebra information
                if "geogebra_alternatives" in task_info:
                    existing_task.geogebra_alternatives = task_info["geogebra_alternatives"]
                if "geogebra_command" in task_info:
                    existing_task.geogebra_command = task_info["geogebra_command"]
                
                # Add available tools
                task_type = existing_task.task_type
                available_tools = get_available_tools_for_task(task_type)
                existing_task.available_tools = available_tools
                
                # Mark GeoGebra tasks as completed
                if existing_task.geogebra_alternatives and existing_task.geogebra_command:
                    if existing_task.task_id not in state.calculation_queue.completed_task_ids:
                        state.calculation_queue.completed_task_ids.append(existing_task.task_id)
                    existing_task.status = "completed"
                    
                    # Store GeoGebra command
                    if "geogebra_direct_commands" not in state.calculation_results:
                        state.calculation_results["geogebra_direct_commands"] = []
                    
                    # Check if command already exists
                    command_exists = False
                    for cmd in state.calculation_results.get("geogebra_direct_commands", []):
                        if cmd.get("task_id") == existing_task.task_id:
                            command_exists = True
                            break
                    
                    if not command_exists:
                        state.calculation_results["geogebra_direct_commands"].append({
                            "task_id": existing_task.task_id,
                            "task_type": existing_task.task_type,
                            "parameters": existing_task.parameters,
                            "geogebra_command": existing_task.geogebra_command
                        })
            else:
                # Create new task
                task_type = task_info["task_type"]
                available_tools = get_available_tools_for_task(task_type)
                
                new_task = CalculationTask(
                    task_id=task_id,
                    task_type=task_type,
                    operation_type=task_info["operation_type"],
                    specific_method=task_info.get("specific_method"),
                    required_precision=task_info.get("required_precision"),
                    parameters=task_info.get("parameters", {}),
                    dependencies=task_info.get("dependencies", []),
                    description=task_info.get("description", ""),
                    status="pending",
                    geogebra_alternatives=task_info.get("geogebra_alternatives", False),
                    geogebra_command=task_info.get("geogebra_command"),
                    available_tools=available_tools  # 사용 가능한 도구 목록 추가
                )
                
                # Mark GeoGebra tasks as completed
                if new_task.geogebra_alternatives and new_task.geogebra_command:
                    if new_task.task_id not in state.calculation_queue.completed_task_ids:
                        completed_ids.append(new_task.task_id)
                    new_task.status = "completed"
                    
                    # Store GeoGebra command
                    if "geogebra_direct_commands" not in state.calculation_results:
                        state.calculation_results["geogebra_direct_commands"] = []
                    
                    state.calculation_results["geogebra_direct_commands"].append({
                        "task_id": new_task.task_id,
                        "task_type": new_task.task_type,
                        "parameters": new_task.parameters,
                        "geogebra_command": new_task.geogebra_command
                    })
                
                state.calculation_queue.tasks.append(new_task)
        
        # 기본 도형 좌표 계산 작업 우선 순위 재지정
        state.calculation_queue.tasks = prioritize_coordinate_tasks(state.calculation_queue.tasks)
        
        # Update completed tasks
        for task_id in completed_ids:
            if task_id not in state.calculation_queue.completed_task_ids:
                state.calculation_queue.completed_task_ids.append(task_id)
                
                # Update task status
                for task in state.calculation_queue.tasks:
                    if task.task_id == task_id:
                        task.status = "completed"
                        break
        
        # Set next calculation type (라우터가 재설정할 것이므로 의미 없어짐)
        if next_calc_type:
            state.next_calculation = next_calc_type
        
        # Manager 초기화 완료 표시 - 이후부터는 라우터가 담당
        setattr(state, 'is_manager_initialized', True)
        
    except Exception as e:
        print(f"Error processing calculation manager result: {e}")
        
        # 기본 의존성 그래프 생성
        if state.calculation_queue and state.calculation_queue.tasks:
            print("[DEBUG] Creating basic dependency graph as fallback")
            state.calculation_queue.dependency_graph = build_dependency_graph(state.calculation_queue.tasks)
            
            # 기본 도형 좌표 계산 작업 우선 순위 지정 (에러 발생해도 적용)
            state.calculation_queue.tasks = prioritize_coordinate_tasks(state.calculation_queue.tasks)
            
            # 각 작업에 도구 목록 추가
            for task in state.calculation_queue.tasks:
                task.available_tools = get_available_tools_for_task(task.task_type)
        
        # Manager 초기화 완료 표시 - 에러가 있어도 라우터가 처리하도록
        setattr(state, 'is_manager_initialized', True)
    
    return state 