"""
계산 관리자 유틸리티 모듈

이 모듈은 계산 관리자 에이전트에서 사용하는 유틸리티 함수들을 정의합니다.
"""

import re
import uuid
from typing import Dict, Any, List, Optional

from models.state_models import GeometryState, CalculationTask, CalculationQueue, CalculationTaskCreation

def process_calculation_tasks(state: GeometryState, result: CalculationTaskCreation) -> None:
    """
    구조화된 계산 작업 처리
    
    Args:
        state: 현재 상태 객체
        result: 파싱된 결과 (CalculationTaskCreation 객체 또는 딕셔너리)
    """
    queue = state.calculation_queue
    
    # 딕셔너리 또는 객체 처리를 위한 속성 접근
    if isinstance(result, dict):
        tasks = result.get("tasks", [])
        completed_task_ids = result.get("completed_task_ids", [])
        next_calculation_type = result.get("next_calculation_type")
    else:
        tasks = result.tasks
        completed_task_ids = result.completed_task_ids
        next_calculation_type = result.next_calculation_type
    
    # 완료된 작업 처리
    if completed_task_ids:
        for task_id in completed_task_ids:
            for task in queue.tasks:
                if task.task_id == task_id:
                    task.status = "completed"
                    if task_id not in queue.completed_task_ids:
                        queue.completed_task_ids.append(task_id)
                    queue.tasks.remove(task)
                    break
    
    # 새 작업 추가
    for task_data in tasks:
        task_type = task_data.get("task_type")
        parameters = task_data.get("parameters", {})
        dependencies = task_data.get("dependencies", [])
        
        if task_type:
            # 작업 ID 생성
            task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
            
            # 중복 작업 확인
            is_duplicate = False
            for existing_task in queue.tasks:
                if existing_task.task_type == task_type and existing_task.parameters == parameters:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                # 작업 생성 및 큐에 추가
                task = CalculationTask(
                    task_id=task_id,
                    task_type=task_type,
                    parameters=parameters,
                    dependencies=dependencies,
                    description=task_data.get("description", ""),
                    status="pending"
                )
                queue.tasks.append(task)
    
    # 다음 계산 유형 설정
    if next_calculation_type:
        # 해당 유형의 첫 번째 대기 중인 작업 찾기
        for task in queue.tasks:
            if task.task_type == next_calculation_type and task.status == "pending":
                queue.current_task_id = task.task_id
                task.status = "running"
                state.next_calculation = next_calculation_type
                break
    else:
        # 실행 가능한 작업 찾기
        determine_next_calculation(state)

def update_calculation_queue(state: GeometryState, agent_output: str) -> None:
    """
    에이전트 출력을 기반으로 계산 큐 업데이트
    
    Args:
        state: 현재 상태 객체
        agent_output: 에이전트 출력 문자열 (JSON 형식 기대)
    """
    # 이미 실행 중인 작업이 있는 경우 완료 처리
    queue = state.calculation_queue
    if queue.current_task_id:
        for task in queue.tasks:
            if task.task_id == queue.current_task_id and task.status == "running":
                task.status = "completed"
                if task.task_id not in queue.completed_task_ids:
                    queue.completed_task_ids.append(task.task_id)
                queue.tasks.remove(task)
                queue.current_task_id = None
                break
    
    # JSON 추출을 위한 패턴 (출력에서 JSON 부분만 추출)
    json_pattern = r'```(?:json)?\s*({.*?})\s*```|({.*})'
    
    # 출력에서 JSON 찾기
    json_match = re.search(json_pattern, agent_output, re.DOTALL)
    
    if json_match:
        # 첫 번째 또는 두 번째 그룹에서 JSON 문자열 추출
        json_str = json_match.group(1) if json_match.group(1) else json_match.group(2)
        
        try:
            import json
            # JSON 문자열을 파싱
            calculation_data = json.loads(json_str)
            
            # JSON 구조에서 작업 추출
            if "tasks" in calculation_data and isinstance(calculation_data["tasks"], list):
                for task_data in calculation_data["tasks"]:
                    # 필수 필드 확인
                    if "task_type" in task_data:
                        task_type = task_data["task_type"]
                        parameters = task_data.get("parameters", {})
                        dependencies = task_data.get("dependencies", [])
                        
                        # 작업 ID 생성 또는 재사용
                        task_id = task_data.get("task_id", f"{task_type}_{uuid.uuid4().hex[:8]}")
                        
                        # 중복 작업 확인
                        is_duplicate = False
                        for existing_task in queue.tasks:
                            if existing_task.task_id == task_id or (existing_task.task_type == task_type and existing_task.parameters == parameters):
                                is_duplicate = True
                                break
                                
                        if not is_duplicate:
                            # 작업 생성 및 큐에 추가
                            task = CalculationTask(
                                task_id=task_id,
                                task_type=task_type,
                                parameters=parameters,
                                dependencies=dependencies,
                                description=task_data.get("description", ""),
                                status="pending"
                            )
                            queue.tasks.append(task)
            
            # 완료된 작업 ID 업데이트
            if "completed_task_ids" in calculation_data and isinstance(calculation_data["completed_task_ids"], list):
                for task_id in calculation_data["completed_task_ids"]:
                    if task_id not in queue.completed_task_ids:
                        queue.completed_task_ids.append(task_id)
            
            # 다음 계산 유형 설정
            if "next_calculation_type" in calculation_data:
                # 지정된 유형의 첫 번째 대기 중인 작업 찾기
                next_type = calculation_data["next_calculation_type"]
                for task in queue.tasks:
                    if task.task_type == next_type and task.status == "pending":
                        queue.current_task_id = task.task_id
                        task.status = "running"
                        state.next_calculation = next_type
                        break
            
            return
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            # JSON 파싱 실패 시, 기존 정규 표현식 방식으로 폴백
    
    # 기존 정규 표현식 방식 (폴백)
    print("Warning: Falling back to regex pattern matching for calculation tasks")
    
    # 삼각형 계산 작업 추출
    triangle_tasks = re.findall(r'三角形计算[任务]*[：:]\s*{([^}]+)}', agent_output)
    for task_str in triangle_tasks:
        create_calculation_task(state, "triangle", task_str)
    
    # 원 계산 작업 추출
    circle_tasks = re.findall(r'圆[形]*计算[任务]*[：:]\s*{([^}]+)}', agent_output)
    for task_str in circle_tasks:
        create_calculation_task(state, "circle", task_str)
    
    # 각도 계산 작업 추출
    angle_tasks = re.findall(r'角度计算[任务]*[：:]\s*{([^}]+)}', agent_output)
    for task_str in angle_tasks:
        create_calculation_task(state, "angle", task_str)
    
    # 길이 계산 작업 추출
    length_tasks = re.findall(r'长度计算[任务]*[：:]\s*{([^}]+)}', agent_output)
    for task_str in length_tasks:
        create_calculation_task(state, "length", task_str)
    
    # 면적 계산 작업 추출
    area_tasks = re.findall(r'面积计算[任务]*[：:]\s*{([^}]+)}', agent_output)
    for task_str in area_tasks:
        create_calculation_task(state, "area", task_str)
    
    # 좌표 계산 작업 추출
    coordinate_tasks = re.findall(r'坐标计算[任务]*[：:]\s*{([^}]+)}', agent_output)
    for task_str in coordinate_tasks:
        create_calculation_task(state, "coordinate", task_str)

def create_calculation_task(state: GeometryState, task_type: str, task_str: str) -> None:
    """
    계산 작업 생성 및 큐에 추가
    
    Args:
        state: 현재 상태 객체
        task_type: 작업 유형 (triangle, circle 등)
        task_str: 작업 문자열
    """
    # 기본 파라미터 딕셔너리
    parameters = {}
    
    # 좌표 추출 (좌표는 일반적으로 "점A(1,2)" 형식)
    coordinates = re.findall(r'点\s*(\w+)\s*\(\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)', task_str)
    for point, x, y in coordinates:
        parameters[f"point_{point}"] = [float(x), float(y)]
    
    # 길이 추출 (길이는 일반적으로 "길이AB=5" 형식)
    lengths = re.findall(r'(长度|距离|边长)\s*(\w+)\s*[=:]\s*([+-]?\d+(?:\.\d+)?)', task_str)
    for _, name, value in lengths:
        parameters[f"length_{name}"] = float(value)
    
    # 각도 추출 (각도는 일반적으로 "각도ABC=60" 형식)
    angles = re.findall(r'(角度|角)\s*(\w+)\s*[=:]\s*([+-]?\d+(?:\.\d+)?)', task_str)
    for _, name, value in angles:
        parameters[f"angle_{name}"] = float(value)
    
    # 반지름 추출 (반지름은 일반적으로 "반지름=5" 형식)
    radius = re.findall(r'(半径)\s*[=:]\s*([+-]?\d+(?:\.\d+)?)', task_str)
    if radius:
        parameters["radius"] = float(radius[0][1])
    
    # 의존성 추출 (의존성은 일반적으로 "의존성: 작업1, 작업2" 형식)
    dependencies = []
    deps = re.findall(r'(依赖|依赖于|依赖任务)[：:]\s*([^,}\n]+(?:,\s*[^,}\n]+)*)', task_str)
    if deps:
        dep_list = deps[0][1].split(',')
        for dep in dep_list:
            dep_id = dep.strip()
            if dep_id:
                dependencies.append(dep_id)
    
    # 작업 ID 생성
    task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
    
    # 작업 생성 및 큐에 추가
    task = CalculationTask(
        task_id=task_id,
        task_type=task_type,
        parameters=parameters,
        dependencies=dependencies,
        description=task_str,
        status="pending"
    )
    
    # 중복 작업 확인
    for existing_task in state.calculation_queue.tasks:
        if existing_task.task_type == task.task_type and existing_task.parameters == task.parameters:
            return  # 중복 작업은 추가하지 않음
    
    # 큐에 작업 추가
    state.calculation_queue.tasks.append(task)

def determine_next_calculation(state: GeometryState) -> None:
    """
    다음에 실행할 계산 유형 결정
    
    Args:
        state: 현재 상태 객체
    """
    print(f"[DEBUG] Determining next calculation. Current queue: {state.calculation_queue}")
    queue = state.calculation_queue
    
    # 이미 실행 중인 작업이 있는지 확인
    for task in queue.tasks:
        if task.status == "running":
            print(f"[DEBUG] Found running task {task.task_id} of type {task.task_type}")
            queue.current_task_id = task.task_id
            state.next_calculation = task.task_type
            return
    
    # 실행 가능한 작업 찾기 (의존성이 없거나 모든 의존성이 완료된 작업)
    executable_tasks = []
    for task in queue.tasks:
        if task.status == "pending":
            # 의존성 확인
            dependencies_met = True
            for dep_id in task.dependencies:
                dependency_completed = False
                # 완료된 작업 ID 목록에서 확인
                if dep_id in queue.completed_task_ids:
                    dependency_completed = True
                # 아직 큐에 있는 작업 중 완료된 작업 확인
                for dep_task in queue.tasks:
                    if dep_task.task_id == dep_id and dep_task.status == "completed":
                        dependency_completed = True
                        break
                if not dependency_completed:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                executable_tasks.append(task)
    
    if executable_tasks:
        # 실행 가능한 작업 중 첫 번째 작업 선택
        task = executable_tasks[0]
        print(f"[DEBUG] Selected next task {task.task_id} of type {task.task_type}")
        queue.current_task_id = task.task_id
        task.status = "running"
        state.next_calculation = task.task_type
    else:
        # 의존성을 만족하는 작업이 없는 경우 의존성이 없는 대기 중인 작업 찾기
        for task in queue.tasks:
            if task.status == "pending" and not task.dependencies:
                print(f"[DEBUG] Found task with no dependencies: {task.task_id} of type {task.task_type}")
                queue.current_task_id = task.task_id
                task.status = "running"
                state.next_calculation = task.task_type
                return
        
        # 아직도 작업을 찾지 못한 경우 대기 중인 작업 중 첫 번째 작업 선택
        for task in queue.tasks:
            if task.status == "pending":
                print(f"[DEBUG] Selected first pending task: {task.task_id} of type {task.task_type}")
                queue.current_task_id = task.task_id
                task.status = "running"
                state.next_calculation = task.task_type
                return
        
        # 완료된 작업 큐에서 제거
        tasks_to_remove = []
        for task in queue.tasks[:]:
            if task.status == "completed" or task.task_id in queue.completed_task_ids:
                tasks_to_remove.append(task)
        
        for task in tasks_to_remove:
            if task in queue.tasks:
                queue.tasks.remove(task)
                print(f"[DEBUG] Removed completed task {task.task_id} from queue")
                
        # 작업이 없는 경우 계산 병합기로 진행
        print("[DEBUG] No pending tasks found. Setting next_calculation to None")
        state.next_calculation = None
        return 