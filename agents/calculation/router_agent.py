"""
계산 라우터 에이전트 모듈

이 모듈은 계산 태스크 간의 라우팅을 관리하고 흐름을 제어하는 에이전트를 구현합니다.
Manager 에이전트에 의해 구축된 의존성 그래프를 바탕으로 다음에 실행할 계산 에이전트를 결정합니다.
"""

from typing import Dict, Any, List, Optional
from models.state_models import GeometryState, CalculationTask


def calculation_router_agent(state: GeometryState) -> GeometryState:
    """
    계산 라우터 에이전트
    
    계산 큐의 상태를 확인하고 다음 실행해야 할 계산 에이전트를 결정합니다.
    의존성이 충족된 작업을 찾아 실행 대기열에 추가합니다.
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        업데이트된 상태 객체
    """
    print("[DEBUG] Starting calculation_router_agent")
    
    # 현재 실행 중인 작업이 있고 완료되었으면 처리
    if state.calculation_queue.current_task_id:
        # 현재 작업 완료 처리
        for task in state.calculation_queue.tasks:
            if task.task_id == state.calculation_queue.current_task_id:
                task.status = "completed"
                if task.task_id not in state.calculation_queue.completed_task_ids:
                    state.calculation_queue.completed_task_ids.append(task.task_id)
                print(f"[DEBUG] Marked task {task.task_id} as completed")
                break
        
        # 현재 작업 ID 초기화
        state.calculation_queue.current_task_id = None
    
    # 모든 작업이 완료되었는지 확인
    all_completed = True
    for task in state.calculation_queue.tasks:
        if task.status != "completed" and task.task_id not in state.calculation_queue.completed_task_ids:
            all_completed = False
            break
    
    if all_completed:
        print("[DEBUG] All calculations completed. Setting next_calculation to None for merger.")
        state.next_calculation = None
        return state
    
    # 의존성 그래프를 사용하여 다음 실행 가능한 작업 찾기
    if state.calculation_queue.dependency_graph and state.calculation_queue.dependency_graph.execution_order:
        for task_id in state.calculation_queue.dependency_graph.execution_order:
            node = state.calculation_queue.dependency_graph.nodes.get(task_id)
            if node and node.status != "completed":
                # 이 작업이 이미 완료되었는지 확인
                if task_id in state.calculation_queue.completed_task_ids:
                    node.status = "completed"
                    continue
                
                # 의존성이 충족되었는지 확인
                deps_satisfied = True
                for dep in node.dependencies:
                    dep_satisfied = False
                    for comp_id in state.calculation_queue.completed_task_ids:
                        if dep == comp_id:
                            dep_satisfied = True
                            break
                    
                    if not dep_satisfied:
                        deps_satisfied = False
                        break
                
                if deps_satisfied:
                    # 작업 찾기
                    for task in state.calculation_queue.tasks:
                        if task.task_id == task_id:
                            # 작업 설정
                            state.calculation_queue.current_task_id = task.task_id
                            state.next_calculation = task.task_type
                            task.status = "running"
                            
                            # 이전 계산 결과로 파라미터 향상
                            enhance_task_with_results(task, state.calculation_results)
                            
                            print(f"[DEBUG] Selected task {task.task_id} of type {task.task_type} for execution")
                            return state
    
    # 의존성 그래프가 없거나 사용할 수 없을 경우 fallback 메커니즘
    print("[DEBUG] Using fallback mechanism to find next task")
    next_task = find_next_task_fallback(state.calculation_queue.tasks, state.calculation_queue.completed_task_ids)
    
    if next_task:
        state.calculation_queue.current_task_id = next_task.task_id
        state.next_calculation = next_task.task_type
        next_task.status = "running"
        
        # 이전 계산 결과로 파라미터 향상
        enhance_task_with_results(next_task, state.calculation_results)
        
        print(f"[DEBUG] Fallback: Selected task {next_task.task_id} of type {next_task.task_type}")
    else:
        print("[DEBUG] No more executable tasks. Setting next_calculation to None for merger.")
        state.next_calculation = None
    
    return state


def find_next_task_fallback(tasks: List[CalculationTask], completed_task_ids: List[str]) -> Optional[CalculationTask]:
    """
    의존성 그래프가 없을 때 다음 실행 가능한 작업을 찾는 fallback 함수
    
    Args:
        tasks: 모든 계산 작업 목록
        completed_task_ids: 완료된 작업 ID 목록
        
    Returns:
        다음 실행할 작업 또는 None
    """
    for task in tasks:
        if task.status == "pending" and task.task_id not in completed_task_ids:
            # 모든 의존성이 충족되었는지 확인
            deps_satisfied = True
            for dep in task.dependencies:
                if dep not in completed_task_ids:
                    deps_satisfied = False
                    break
            
            if deps_satisfied:
                return task
    
    return None


def enhance_task_with_results(task: CalculationTask, calculation_results: Dict[str, Any]) -> None:
    """
    작업을 이전 계산 결과로 향상시킵니다.
    
    Args:
        task: 향상시킬 계산 작업
        calculation_results: 현재까지의 계산 결과
    """
    # 의존성 작업의 결과를 매개변수에 추가
    for dep in task.dependencies:
        if dep in calculation_results:
            # 의존성 결과를 작업 매개변수에 추가
            task.parameters[f"{dep}_result"] = calculation_results[dep] 