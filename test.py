# 각 삼등분 문제 테스트

from models.state_models import GeometryState

# 테스트용 기하학적 문제
test_problem = "△ABC为正三角形，D、E为BC上的点，且有∠CAD=∠DAE=∠EAB,取AD的中点F，连接BF交AE于G"

# 초기 상태 생성
state = GeometryState(
    input_problem=test_problem,
    requires_calculation=True,
    parsed_elements={
        "problem_type": "angle_trisection_and_intersection",
        "geometric_objects": ["triangle ABC", "points D, E, F, G"],
        "geometric_relationships": ["D, E on BC", "∠CAD=∠DAE=∠EAB", "F is midpoint of AD", "G is intersection of BF and AE"],
        "analyzed_conditions": {
            "regular_polygon": True,
            "angle_trisection": True
        }
    },
    problem_analysis={
        "problem_type": "angle_trisection_and_intersection",
        "reasoning": "This problem involves an equilateral triangle with angle trisection.",
        "suggested_tasks": [
            {
                "task_type": "angle",
                "operation_type": "angleTrisection",
                "parameters": {
                    "point1": "C",
                    "point2": "A",
                    "point3": "B"
                },
                "dependencies": [],
                "description": "Trisect angle CAB"
            }
            # Other tasks as in the planner output
        ]
    }
)

# 계산 관리자 에이전트 실행
from agents.calculation.manager_agent import calculation_manager_agent
updated_state = calculation_manager_agent(state)

# 결과 확인
print(f"Dependency graph built: {updated_state.calculation_queue.dependency_graph}")
print(f"Next calculation: {updated_state.next_calculation}")
print(f"Current task: {updated_state.calculation_queue.current_task_id}")