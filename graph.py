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
        planner_agent,
        explanation_agent,
        geogebra_command_agent,
        geogebra_command_retrieval_agent,
        validation_agent,
        command_regeneration_agent,
    )

    from agents.calculation import (
        triangle_calculation_agent,
        circle_calculation_agent,
        angle_calculation_agent,
        length_calculation_agent,
        area_calculation_agent,
        coordinate_calculation_agent,
        calculation_manager_agent,
        calculation_result_merger_agent,
        calculation_router_agent
    )

    # 그래프 초기화
    workflow = StateGraph(GeometryState)

    # 모든 노드 추가
    workflow.add_node("parsing_agent", parsing_agent)
    workflow.add_node("planner_agent", planner_agent)

    workflow.add_node("calculation_manager_agent", calculation_manager_agent)
    workflow.add_node("calculation_router_agent", calculation_router_agent)
    workflow.add_node("calculation_result_merger_agent", calculation_result_merger_agent)
    
    # 계산 노드 추가
    workflow.add_node("triangle_calculation_agent", triangle_calculation_agent)
    workflow.add_node("circle_calculation_agent", circle_calculation_agent)
    workflow.add_node("angle_calculation_agent", angle_calculation_agent)
    workflow.add_node("length_calculation_agent", length_calculation_agent)
    workflow.add_node("area_calculation_agent", area_calculation_agent)
    workflow.add_node("coordinate_calculation_agent", coordinate_calculation_agent)

    # GeoGebra 관련 노드 추가
    workflow.add_node("command_retrieval_agent", geogebra_command_retrieval_agent)
    workflow.add_node("command_generation_agent", geogebra_command_agent)
    workflow.add_node("validation_agent", validation_agent)
    workflow.add_node("command_regeneration_agent", command_regeneration_agent)
    workflow.add_node("explanation_agent", explanation_agent)
    
    # 기본 흐름 설정
    workflow.set_entry_point("parsing_agent")
    workflow.add_edge("parsing_agent", "planner_agent")
    
    # 분석 결과에 따른 라우팅 설정
    def route_after_planner(state: GeometryState):
        """Planner 에이전트 이후 라우팅"""
        if state.requires_calculation:
            # 계산 필요 시 Manager로 라우팅
            return "calculation_manager_agent"
        else:
            # 계산 불필요 시 바로 GeoGebra 명령어 검색으로
            return "command_retrieval_agent"
    
    workflow.add_conditional_edges(
        "planner_agent",
        route_after_planner,
        {
            "calculation_manager_agent": "calculation_manager_agent",
            "command_retrieval_agent": "command_retrieval_agent"
        }
    )
    
    # 매니저 에이전트에서 라우터로 항상 라우팅
    workflow.add_edge("calculation_manager_agent", "calculation_router_agent")
    
    # 라우터에서 계산 에이전트 또는 병합기로 라우팅
    def route_from_router(state: GeometryState):
        """라우터에서 다음 단계 결정"""
        if state.next_calculation is None:
            return "calculation_result_merger_agent"
        return f"{state.next_calculation}_calculation_agent"
    
    # 라우터 조건부 라우팅 설정
    workflow.add_conditional_edges(
        "calculation_router_agent",
        route_from_router,
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
    
    # 모든 계산 에이전트에서 다시 라우터로 돌아가기
    calculation_agents = [
        "triangle_calculation_agent",
        "circle_calculation_agent",
        "angle_calculation_agent",
        "length_calculation_agent",
        "area_calculation_agent",
        "coordinate_calculation_agent"
    ]
    
    for agent in calculation_agents:
        workflow.add_edge(agent, "calculation_router_agent")
    
    # 결과 병합 후 명령어 검색
    workflow.add_edge("calculation_result_merger_agent", "command_retrieval_agent")
    
    # GeoGebra 명령어 생성 관련 흐름
    workflow.add_edge("command_retrieval_agent", "command_generation_agent")
    workflow.add_edge("command_generation_agent", "validation_agent")

    # 검증 후 조건부 라우팅
    workflow.add_conditional_edges(
        "validation_agent",
        route_after_validation,
        {
            "success": "explanation_agent",
            "regenerate": "command_regeneration_agent"
        }
    )
    
    # 명령어 재생성 후 조건부 라우팅
    workflow.add_conditional_edges(
        "command_regeneration_agent",
        route_after_regeneration,
        {
            "explanation_agent": "explanation_agent",
            "validation_agent": "validation_agent"
        }
    )
    
    # 종료점 설정
    workflow.set_finish_point("explanation_agent")
    
    # 그래프 컴파일
    compiled_graph = workflow.compile()
    
    return compiled_graph

def route_after_validation(state: GeometryState) -> str:
    """검증 결과에 따른 라우팅 결정"""
    if state.is_valid:
        return "success"
    
    # 최대 재생성 시도 횟수 초과 시 그냥 설명으로 넘어감
    if state.command_regeneration_attempts >= MAX_ATTEMPTS:
        print(f"[WARNING] 최대 명령어 재생성 시도 횟수({MAX_ATTEMPTS})를 초과했습니다. 설명으로 넘어갑니다.")
        state.is_valid = True  # 강제로 유효하다고 설정
        return "success"
    
    return "regenerate"

def route_after_regeneration(state: GeometryState) -> str:
    """재생성 후 라우팅 결정"""
    # 최대 재생성 시도 횟수 초과 시 바로 설명으로 넘어감
    if state.command_regeneration_attempts >= MAX_ATTEMPTS:
        print(f"[WARNING] 최대 명령어 재생성 시도 횟수({MAX_ATTEMPTS})를 초과했습니다. 검증을 건너뛰고 설명으로 넘어갑니다.")
        state.is_valid = True  # 강제로 유효하다고 설정
        return "explanation_agent"
    
    # 그렇지 않으면 검증 단계로 이동
    return "validation_agent"
