import json

def refine_calculation_manager_input(state):
    """
    계산 관리자 에이전트에 전달할 입력 데이터를 정제합니다.
    중복 정보를 제거하고 핵심 정보만 추출하여 토큰 사용량을 줄입니다.
    
    Args:
        state: 현재 기하학 상태
        
    Returns:
        정제된 입력 데이터 딕셔너리
    """
    # 기본 문제 정보
    refined_input = {
        "problem": state.input_problem,
        "parsed_elements": extract_key_elements(state.parsed_elements),
        "problem_analysis": extract_key_analysis(state.problem_analysis),
    }
    
    # 계산 결과 정제
    refined_input["calculation_results"] = extract_key_results(state.calculation_results)
    
    # 계산 큐 정제
    if state.calculation_queue:
        refined_input["calculation_queue"] = refine_calculation_queue(state.calculation_queue)
        
    return refined_input

def extract_key_elements(parsed_elements):
    """핵심 기하 요소만 추출"""
    if not parsed_elements:
        return {}
    
    # 핵심 정보만 추출
    key_elements = {
        "geometric_objects": {},
        "problem_type": parsed_elements.get("problem_type", {}),
        "analyzed_conditions": parsed_elements.get("analyzed_conditions", {}),
        "approach": parsed_elements.get("approach", "")
    }
    
    # 일부 중요한 기하 객체만 포함
    if "geometric_objects" in parsed_elements:
        for obj_name, obj_data in parsed_elements["geometric_objects"].items():
            # 주요 점, 선, 삼각형만 포함
            if obj_data.get("type") in ["point", "triangle"]:
                key_elements["geometric_objects"][obj_name] = obj_data
    
    return key_elements

def extract_key_analysis(problem_analysis):
    """문제 분석에서 핵심 정보만 추출"""
    if not problem_analysis:
        return {}
    
    return {
        "problem_type": problem_analysis.get("problem_type", {}),
        "approach": problem_analysis.get("approach", ""),
        "reasoning": problem_analysis.get("reasoning", ""),
        "suggested_tasks_reasoning": problem_analysis.get("suggested_tasks_reasoning", "")
    }

def extract_key_results(calculation_results):
    """계산 결과에서 핵심 정보만 추출하고 원시 JSON 파싱"""
    if not calculation_results:
        return {}
    
    refined_results = {}
    
    for task_id, result in calculation_results.items():
        # geogebra_direct_commands는 간소화하지 않고 그대로 전달
        if task_id == "geogebra_direct_commands":
            refined_results[task_id] = result
            continue
            
        # 원시 JSON 문자열 파싱
        if isinstance(result, dict) and "raw_output" in result:
            try:
                # JSON 블록 추출 패턴 - ```json\n...\n``` 형식 처리
                json_str = result["raw_output"]
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1]
                    if "```" in json_str:
                        json_str = json_str.split("```")[0]
                
                parsed = json.loads(json_str.strip())
                
                # 필요한 핵심 필드만 추출
                refined_result = {
                    "task_id": parsed.get("task_id", task_id),
                    "success": parsed.get("success", True)
                }
                
                # 기본 기하학적 데이터 추출
                for field in ["coordinates", "lengths", "angles", "areas"]:
                    if field in parsed and parsed[field]:
                        refined_result[field] = parsed[field]
                
                # 특수 필드 추출
                if "geometric_elements" in parsed and parsed["geometric_elements"]:
                    refined_result["geometric_elements"] = parsed["geometric_elements"]
                
                if "derived_data" in parsed and parsed["derived_data"]:
                    refined_result["derived_data"] = parsed["derived_data"]
                
                refined_results[task_id] = refined_result
            except Exception as e:
                # 파싱 실패 시 최소한의 정보만 포함
                refined_results[task_id] = {
                    "task_id": task_id,
                    "success": False,
                    "error": str(e)
                }
        else:
            # 이미 처리된 결과는 그대로 사용
            refined_results[task_id] = result
    
    return refined_results

def refine_calculation_queue(calculation_queue):
    """계산 큐에서 필요한 정보만 추출"""
    refined_queue = {
        "completed_task_ids": calculation_queue.completed_task_ids,
        "current_task_id": calculation_queue.current_task_id
    }
    
    # 대기 작업 정제
    pending_tasks = []
    for task in calculation_queue.tasks:
        if task.status == "pending":
            pending_tasks.append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "operation_type": task.operation_type,
                "dependencies": task.dependencies,
                "parameters": task.parameters,
                "description": task.description
            })
    
    refined_queue["tasks"] = pending_tasks
    
    # 의존성 그래프 정제
    if calculation_queue.dependency_graph:
        refined_queue["dependency_graph"] = {
            "execution_order": calculation_queue.dependency_graph.execution_order
        }
        
        # 노드 상태만 간결하게 포함
        nodes = {}
        for node_id, node in calculation_queue.dependency_graph.nodes.items():
            nodes[node_id] = {
                "dependencies": node.dependencies,
                "status": node.status
            }
        
        refined_queue["dependency_graph"]["nodes"] = nodes
    
    return refined_queue
