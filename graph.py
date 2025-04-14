"""
그래프 모듈

이 모듈은 기하학 문제 해결 그래프를 정의합니다.
"""

from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from config import MAX_ATTEMPTS

# 상태 모델 임포트
from models.state_models import GeometryState

# 기하학 솔버 그래프 생성 함수
def create_geometry_solver_graph():
    """
    기하학 문제 해결기 그래프 생성
    
    Returns:
        그래프 인스턴스
    """
    from agents import (
        parsing_agent,
        analysis_agent,
        explanation_agent,
        geogebra_command_agent,
        validation_agent,
        alternative_solution_agent,
    )

    from agents.calculation import (
        triangle_calculation_agent,
        circle_calculation_agent,
        angle_calculation_agent,
        length_calculation_agent,
        area_calculation_agent,
        coordinate_calculation_agent,
        calculation_manager_agent,
        calculation_result_merger_agent
    )

    # 그래프 초기화
    workflow = StateGraph(GeometryState)

    workflow.add_node("parsing_agent", parsing_agent)
    workflow.add_node("analysis_agent", analysis_agent)

    workflow.add_node("triangle_calculation_agent", triangle_calculation_agent)
    workflow.add_node("circle_calculation_agent", circle_calculation_agent)
    workflow.add_node("angle_calculation_agent", angle_calculation_agent)
    workflow.add_node("length_calculation_agent", length_calculation_agent)
    workflow.add_node("area_calculation_agent", area_calculation_agent)
    workflow.add_node("coordinate_calculation_agent", coordinate_calculation_agent)
    workflow.add_node("calculation_manager_agent", calculation_manager_agent)
    workflow.add_node("calculation_result_merger_agent", calculation_result_merger_agent)


    workflow.add_node("geogebra_command_agent", geogebra_command_agent)
    workflow.add_node("validation_agent", validation_agent)
    workflow.add_node("alternative_agent", alternative_solution_agent)   
    workflow.add_node("explanation_agent", explanation_agent)
    
    # 에이전트 간 전환 규칙 설정
    workflow.set_entry_point("parsing_agent")
    workflow.add_edge("parsing_agent", "analysis_agent")
    
    # 분석 결과에 따른 라우팅 설정
    def route_after_analysis(state: GeometryState):
        if state.requires_calculation:
            return "calculation_manager_agent"
        else:
            return "geogebra_command_agent"
    
    workflow.add_conditional_edges(
        "analysis_agent",
        route_after_analysis,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "geogebra_command_agent": "geogebra_command_agent"
        }
    )
    
    # 계산 관리 및 실행 경로 설정
    def route_calculation(state: GeometryState):
        if state.next_calculation == "triangle":
            return "triangle_calculation_agent"
        elif state.next_calculation == "circle":
            return "circle_calculation_agent"
        elif state.next_calculation == "angle":
            return "angle_calculation_agent"
        elif state.next_calculation == "length":
            return "length_calculation_agent"
        elif state.next_calculation == "area":
            return "area_calculation_agent"
        elif state.next_calculation == "coordinate":
            return "coordinate_calculation_agent"
        else:
            return "calculation_result_merger_agent"
    
    workflow.add_conditional_edges(
        "calculation_manager_agent",
        route_calculation,
        {
            "triangle_calculation_agent": "triangle_calculation_agent",
            "circle_calculation_agent": "circle_calculation_agent",
            "angle_calculation_agent": "angle_calculation_agent",
            "length_calculation_agent": "length_calculation_agent",
            "area_calculation_agent": "area_calculation_agent",
            "coordinate_calculation_agent": "coordinate_calculation_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    # 계산 후 관리 혹은 병합으로 이동
    def after_calculation(state: GeometryState):
        if state.calculation_queue and state.calculation_queue.tasks:
            # 대기 중인 작업이 있는지 확인
            pending_tasks = [task for task in state.calculation_queue.tasks if task.status == "pending"]
            if pending_tasks:
                print(f"[DEBUG] Found {len(pending_tasks)} pending tasks. Returning to calculation_manager_agent")
                return "calculation_manager_agent"
        print("[DEBUG] No pending tasks remain. Moving to calculation_result_merger_agent")
        return "calculation_result_merger_agent"
    
    workflow.add_conditional_edges(
        "triangle_calculation_agent",
        after_calculation,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    workflow.add_conditional_edges(
        "circle_calculation_agent",
        after_calculation,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    workflow.add_conditional_edges(
        "angle_calculation_agent",
        after_calculation,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    workflow.add_conditional_edges(
        "length_calculation_agent",
        after_calculation,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    workflow.add_conditional_edges(
        "area_calculation_agent",
        after_calculation,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    workflow.add_conditional_edges(
        "coordinate_calculation_agent",
        after_calculation,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "calculation_result_merger_agent": "calculation_result_merger_agent"
        }
    )
    
    # 결과 병합 후 해결책 생성
    workflow.add_edge("calculation_result_merger_agent", "geogebra_command_agent")
    workflow.add_edge("geogebra_command_agent", "validation_agent")


    # 검증 후 조건부 엣지 추가
    workflow.add_conditional_edges(
        "validation_agent",
        route_after_validation,
        {
            "success": "explanation_agent",
            "failure": "alternative_agent"
        }
    )
    
    # 대체 해법에서 명령어 생성으로 돌아가는 조건부 엣지
    workflow.add_conditional_edges(
        "alternative_agent",
        route_after_alternative_solution,
        {
            "retry": "geogebra_command_agent",
            "give_up": "explanation_agent"
        }
    )
    
    # 시작점과 종료점 설정
    workflow.set_entry_point("parsing_agent")
    workflow.set_finish_point("explanation_agent")
    
    return workflow.compile()

def route_after_validation(state: GeometryState) -> str:
    """검증 결과에 따른 라우팅 결정"""
    return "success" if state.is_valid else "failure"

def route_after_alternative_solution(state: GeometryState) -> str:
    """대체 해법 탐색 후 라우팅 결정"""
    return "give_up" if state.attempt_count >= MAX_ATTEMPTS else "retry" 