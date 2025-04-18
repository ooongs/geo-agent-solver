"""
결과 병합 에이전트 모듈

이 모듈은 결과 병합 에이전트를 정의합니다.
이 에이전트는 기하학 계산 결과를 분석하고 통합하며, 최종 작도 계획을 생성합니다.
"""

from models.state_models import GeometryState, ConstructionPlan, ConstructionStep
from geo_prompts import RESULT_MERGER_PROMPT, MERGER_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from langchain_core.output_parsers import JsonOutputParser
from utils.json_parser import safe_parse_llm_json_output
import re

def calculation_result_merger_agent(state: GeometryState) -> GeometryState:
    """
    Enhanced calculation result merger agent
    
    Analyzes and integrates geometric calculation results based on the dependency graph,
    ensures consistency, and generates a comprehensive construction plan.
    
    Args:
        state: Current state object
        
    Returns:
        Updated state object
    """
    print("[DEBUG] Starting calculation_result_merger_agent")
    
    # Check if calculation queue exists
    if not state.calculation_queue:
        print("[DEBUG] No calculation queue found. Returning state.")
        return state
    
    # Initialize LLM
    llm = LLMManager.get_calculation_merger_llm()
    
    # Create prompt
    prompt = RESULT_MERGER_PROMPT
    
    # Initialize output parser
    output_parser = JsonOutputParser()
    
    # Create chain
    chain = prompt | llm
    
    # Extract dependency graph for enhanced merging
    dependency_graph = None
    execution_order = []
    if state.calculation_queue.dependency_graph:
        dependency_graph = state.calculation_queue.dependency_graph
        execution_order = dependency_graph.execution_order
    
    # Prepare completed tasks information
    completed_tasks = []
    
    # Use execution order if available, otherwise use completed_task_ids
    if execution_order:
        # Use ordered tasks based on dependency graph
        for task_id in execution_order:
            for task in state.calculation_queue.tasks:
                if task.task_id == task_id and task.result:
                    completed_tasks.append(task)
    else:
        # Fallback to unordered completed tasks
        for task in state.calculation_queue.tasks:
            if task.task_id in state.calculation_queue.completed_task_ids and task.result:
                completed_tasks.append(task)
    
    # Extract GeoGebra direct commands if available
    geogebra_commands = []
    if "geogebra_direct_commands" in state.calculation_results:
        geogebra_commands = state.calculation_results["geogebra_direct_commands"]
    
    # Get problem analysis information (if available)
    problem_analysis = {}
    if hasattr(state, "problem_analysis") and state.problem_analysis:
        problem_analysis = state.problem_analysis
    
    # Extract geometric constraints for enhanced reasoning
    geometric_constraints = {}
    if state.geometric_constraints:
        geometric_constraints = state.geometric_constraints
    
    # Invoke the agent
    result = chain.invoke({
        "problem": state.input_problem,
        "completed_tasks": str([task.model_dump() for task in completed_tasks]),
        "calculation_results": str(state.calculation_results),
        "problem_analysis": str(problem_analysis),
        "dependency_graph": str(dependency_graph.model_dump() if dependency_graph else {}),
        "geometric_constraints": str(geometric_constraints),
        "geogebra_commands": str(geogebra_commands),
        "json_template": MERGER_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # Parse JSON result using safe parser
    try:
        print(f"[DEBUG] 병합 에이전트 결과 파싱을 시작합니다: 출력 타입 = {type(result)}")
        
        # 결과가 이미 딕셔너리 형태인지 확인
        if isinstance(result, dict):
            print("[DEBUG] 결과가 이미 딕셔너리 형태입니다")
            final_results = result
        else:
            # 결과 콘텐츠 추출
            result_content = None
            if hasattr(result, 'content'):
                print("[DEBUG] AIMessage 객체에서 content 추출")
                result_content = result.content
            elif hasattr(result, 'output'):
                print("[DEBUG] 객체에서 output 추출")
                result_content = result.output
            else:
                result_content = result
                print(f"[DEBUG] 결과를 그대로 사용합니다: {type(result_content)}")
                
            # JSON 파싱 로직
            try:
                # 기존 출력 파서 시도
                print("[DEBUG] 기본 출력 파서로 파싱 시도")
                final_results = output_parser.parse(result_content)
                print("[DEBUG] 기본 출력 파서로 파싱 성공")
            except Exception as parser_error:
                print(f"[WARNING] 기본 출력 파서 실패: {parser_error}")
                
                # 사용자 제공 JSON 직접 처리 시도
                if isinstance(result_content, str) and result_content.strip().startswith('{'):
                    try:
                        print("[DEBUG] 직접 JSON 파싱 시도")
                        import json
                        final_results = json.loads(result_content)
                        print("[DEBUG] 직접 JSON 파싱 성공")
                    except json.JSONDecodeError as json_error:
                        print(f"[WARNING] 직접 JSON 파싱 실패: {json_error}")
                        # 안전한 파서 시도
                        print("[DEBUG] 안전한 JSON 파서로 파싱 시도")
                        final_results = safe_parse_llm_json_output(result_content, dict)
                else:
                    # 안전한 파서 시도
                    print("[DEBUG] 안전한 JSON 파서로 파싱 시도")
                    final_results = safe_parse_llm_json_output(result_content, dict)
                
                print(f"[DEBUG] 최종 파싱 결과: {type(final_results)}")
                
                # 안전한 파서도 실패하면 결과 문자열 직접 검사
                if not final_results and isinstance(result_content, str):
                    print("[DEBUG] 직접 JSON 추출 시도")
                    # JSON 부분 직접 추출 시도
                    import re
                    json_pattern = r'```json\s*([\s\S]*?)\s*```'
                    json_match = re.search(json_pattern, result_content)
                    if json_match:
                        try:
                            json_str = json_match.group(1).strip()
                            final_results = json.loads(json_str)
                            print("[DEBUG] 마크다운 블록에서 JSON 추출 성공")
                        except Exception as direct_error:
                            print(f"[ERROR] 마크다운 블록에서 JSON 추출 실패: {direct_error}")
                            final_results = {}
                    else:
                        # 전체 JSON 객체 찾기 시도
                        json_obj_pattern = r'(\{[\s\S]*\})'
                        json_obj_match = re.search(json_obj_pattern, result_content)
                        if json_obj_match:
                            try:
                                json_str = json_obj_match.group(1).strip()
                                final_results = json.loads(json_str)
                                print("[DEBUG] 문자열에서 JSON 객체 추출 성공")
                            except Exception as json_error:
                                print(f"[ERROR] JSON 객체 추출 실패: {json_error}")
                                final_results = {}
                        else:
                            print("[WARNING] 결과에서 JSON 콘텐츠를 찾을 수 없습니다")
                            final_results = {}
        
        if final_results:
            print(f"[DEBUG] 파싱 결과 키: {list(final_results.keys()) if isinstance(final_results, dict) else '리스트'}")
            # Extract construction plan
            construction_plan_data = final_results.pop("construction_plan", {})
            
            # Create proper construction plan object
            if construction_plan_data:
                # Convert steps data to ConstructionStep objects
                steps = []
                for step_data in construction_plan_data.get("steps", []):
                    step = ConstructionStep(
                        step_id=step_data.get("step_id", ""),
                        description=step_data.get("description", ""),
                        task_type=step_data.get("task_type", ""),
                        operation_type=step_data.get("operation_type"),
                        geometric_elements=step_data.get("geometric_elements", []),
                        command_type=step_data.get("command_type"),
                        parameters=step_data.get("parameters", {}),
                        dependencies=step_data.get("dependencies", []),
                        geogebra_command=step_data.get("geogebra_command")
                    )
                    steps.append(step)
                
                # Create construction plan
                construction_plan = ConstructionPlan(
                    title=construction_plan_data.get("title", "Construction Plan"),
                    description=construction_plan_data.get("description", ""),
                    steps=steps,
                    final_result=construction_plan_data.get("final_result", "")
                )
                
                state.construction_plan = construction_plan
            
            # Process geometric_elements and derived_data fields
            if "geometric_elements" in final_results:
                if "geometric_elements" not in state.calculation_results:
                    state.calculation_results["geometric_elements"] = {}
                state.calculation_results["geometric_elements"].update(final_results.pop("geometric_elements", {}))
            
            if "derived_data" in final_results:
                if "derived_data" not in state.calculation_results:
                    state.calculation_results["derived_data"] = {}
                state.calculation_results["derived_data"].update(final_results.pop("derived_data", {}))
            
            # Update state with merged calculations
            state.calculations = final_results
            
            print("[DEBUG] Successfully merged calculation results and generated construction plan")
        else:
            print("[WARNING] Failed to parse merger agent result")
    
    except Exception as e:
        print(f"[ERROR] Error processing merger agent result: {e}")
    
    return state 