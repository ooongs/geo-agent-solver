from langchain_core.output_parsers import JsonOutputParser
from models.state_models import CalculationQueue, CalculationTask, PlannerResult, ConstructionPlan, ConstructionStep
from utils.llm_manager import LLMManager
from geo_prompts import PLANNER_PROMPT, PLANNER_CALCULATION_JSON_TEMPLATE, PLANNER_NO_CALCULATION_JSON_TEMPLATE
from utils.construction_util import build_construction_plan
import yaml

def planner_agent(state):
    """
    기하학 문제 분석 에이전트
    
    Args:
        state: 현재 상태(GeometryState 객체), input_problem, parsed_elements 속성 포함
        
    Returns:
        분석 정보가 추가된 상태 딕셔너리
    """
    # LLM 설정
    llm = LLMManager.get_planner_llm()
    
    # 계산 결과 초기화
    if state.calculation_results is None:
        state.calculation_results = {}
    
    # JSON 출력 파서 생성
    parser = JsonOutputParser(pydantic_object=PlannerResult)
    
    # 파싱 에이전트에서 이미 처리한 정보 활용
    existing_problem_type = state.parsed_elements.get("problem_type", {})
    existing_approach = state.parsed_elements.get("approach", "GeoGebra作图")
    
    # 프롬프트 체인 생성 및 실행
    chain = PLANNER_PROMPT | llm | parser
    result = chain.invoke({
        "problem": state.input_problem,
        "parsed_elements": yaml.dump(state.parsed_elements, allow_unicode=True, sort_keys=False),
        "json_template1": PLANNER_CALCULATION_JSON_TEMPLATE,
        "json_template2": PLANNER_NO_CALCULATION_JSON_TEMPLATE
    })
    # state.input_problem = "△ABC为正三角形，D、E为BC上的点，且有∠CAD=∠DAE=∠EAB,取AD的中点F，连接BF交AE于G"
    # state.parsed_elements = {
    #   "geometric_objects": {
    #     "A": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "B": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "C": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "D": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "E": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "F": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "G": {
    #       "type": "point",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     },
    #     "AB": {
    #       "type": "line",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": [
    #         "A",
    #         "B"
    #       ]
    #     },
    #     "BC": {
    #       "type": "line",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": [
    #         "B",
    #         "C"
    #       ]
    #     },
    #     "CA": {
    #       "type": "line",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": [
    #         "C",
    #         "A"
    #       ]
    #     },
    #     "AD": {
    #       "type": "line",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": [
    #         "A",
    #         "D"
    #       ]
    #     },
    #     "AE": {
    #       "type": "line",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": [
    #         "A",
    #         "E"
    #       ]
    #     },
    #     "BF": {
    #       "type": "line",
    #       "vertices": None,
    #       "center": None,
    #       "radius": None,
    #       "points": [
    #         "B",
    #         "F"
    #       ]
    #     },
    #     "ABC": {
    #       "type": "triangle",
    #       "vertices": [
    #         "A",
    #         "B",
    #         "C"
    #       ],
    #       "center": None,
    #       "radius": None,
    #       "points": None
    #     }
    #   },
    #   "relations": {
    #     "AB_BC_CA_equal": {
    #       "type": "segment",
    #       "elements": [
    #         "AB",
    #         "BC",
    #         "CA"
    #       ],
    #       "length": None,
    #       "target": False
    #     },
    #     "angle_CAD_DAE_EAB": {
    #       "type": "angle",
    #       "elements": [
    #         "CAD",
    #         "DAE",
    #         "EAB"
    #       ],
    #       "length": None,
    #       "target": False
    #     },
    #     "F_AD_midpoint": {
    #       "type": "midpoint",
    #       "elements": [
    #         "F",
    #         "AD"
    #       ],
    #       "length": None,
    #       "target": False
    #     },
    #     "BF_intersect_AE_G": {
    #       "type": "intersection",
    #       "elements": [
    #         "BF",
    #         "AE"
    #       ],
    #       "length": None,
    #       "target": True
    #     }
    #   },
    #   "conditions": {
    #     "ABC_equilateral": {
    #       "type": "equality",
    #       "measure": None,
    #       "unit": None,
    #       "elements": [
    #         "AB",
    #         "BC",
    #         "CA"
    #       ]
    #     },
    #     "angle_CAD_DAE_EAB_equal": {
    #       "type": "angle",
    #       "measure": None,
    #       "unit": "degree",
    #       "elements": [
    #         "CAD",
    #         "DAE",
    #         "EAB"
    #       ]
    #     },
    #     "F_AD_midpoint": {
    #       "type": "midpoint",
    #       "measure": None,
    #       "unit": None,
    #       "elements": [
    #         "F",
    #         "AD"
    #       ]
    #     },
    #     "triangle_type": {
    #       "type": "triangle_type",
    #       "value": "equilateral"
    #     }
    #   },
    #   "targets": {
    #     "G": {
    #       "type": "point",
    #       "segment": None,
    #       "angle": None,
    #       "description": "Find the intersection point G of BF and AE"
    #     }
    #   },
    #   "problem_type": {
    #     "triangle": True,
    #     "circle": False,
    #     "angle": True,
    #     "coordinate": False,
    #     "area": False,
    #     "proof": False,
    #     "construction": False,
    #     "measurement": False
    #   },
    #   "analyzed_conditions": {
    #     "equal_sides": True,
    #     "equal_angles": True,
    #     "perpendicular": False,
    #     "parallel": False,
    #     "congruent": False,
    #     "similar": False,
    #     "tangent": False
    #   },
    #   "approach": "ruler-compass construction"
    # }

    # result = {
    # "requires_calculation": True,
    # "reasoning": "The problem involves dividing an angle into three equal parts (trisection) and finding the intersection point of lines constructed based on these angles. Angle trisection is not generally possible with just a ruler and compass, which means advanced calculations or geometric properties must be used to determine the positions of points D and E, and subsequently point G.",
    # "suggested_tasks_reasoning": "To solve this problem, we need to determine the positions of points D and E on BC such that the angles CAD, DAE, and EAB are equal. This requires angle calculations or trigonometric methods. Once D and E are determined, we can find the midpoint F of AD, draw BF, and find its intersection with AE to locate G.",
    # "suggested_tasks": [
    #     {
    #     "task_type": "angle",
    #     "operation_type": "angleTrisection",
    #     "parameters": {
    #         "point1": "C",
    #         "point2": "A",
    #         "point3": "B"
    #     },
    #     "dependencies": [],
    #     "description": "Divide angle CAB into three equal parts to locate points D and E",
    #     "geogebra_alternatives": False,
    #     },
    #     {
    #     "task_type": "length",
    #     "operation_type": "midpoint",
    #     "parameters": {
    #         "point1": "A",
    #         "point2": "D"
    #     },
    #     "dependencies": ["D"],
    #     "description": "Find the midpoint F of AD",
    #     "geogebra_alternatives": True,
    #     "geogebra_command": "Midpoint[A, D]"
    #     },
    #     {
    #     "task_type": "line",
    #     "operation_type": "intersect",
    #     "parameters": {
    #         "line1": "BF",
    #         "line2": "AE"
    #     },
    #     "dependencies": ["F", "E"],
    #     "description": "Find the intersection point G of BF and AE",
    #     "geogebra_alternatives": True,
    #     "geogebra_command": "Intersect[BF, AE]"
    #     }
    # ]
    # }
    
    # 상태 업데이트 - 파싱 에이전트에서 이미 분석한 problem_type과 approach 사용
    state.problem_analysis = {
        "problem_type": existing_problem_type,
        "approach": existing_approach,
        "reasoning": result.get("reasoning", ""),
        "suggested_tasks_blueprint": result.get("suggested_tasks", []),  # 명칭 변경: 이제 "청사진"으로 전달
        "suggested_tasks_reasoning": result.get("suggested_tasks_reasoning", "")
    }
    
    # 계산이 필요한지 여부 설정
    state.requires_calculation = result["requires_calculation"]
    
    # 계산이 필요 없는 경우 construction_plan 생성
    if not result["requires_calculation"]:
        # 직접 생성된 construction_plan 사용 또는 유틸리티로 생성
        if result.get("construction_plan"):
            # 딕셔너리를 ConstructionPlan 모델로 변환
            if isinstance(result["construction_plan"], dict):
                # 각 step을 ConstructionStep 객체로 변환
                steps = []
                if "steps" in result["construction_plan"]:
                    for step_dict in result["construction_plan"]["steps"]:
                        steps.append(ConstructionStep(**step_dict))
                
                # 전체 construction_plan을 ConstructionPlan 객체로 변환
                plan_dict = result["construction_plan"].copy()
                if steps:
                    plan_dict["steps"] = steps
                
                state.construction_plan = ConstructionPlan(**plan_dict)
            else:
                state.construction_plan = result["construction_plan"]
        else:
            # 유틸리티로 계획 생성
            state.construction_plan = build_construction_plan(
                state.input_problem,
                state.parsed_elements
            )
    
    # 계산 큐 초기화만 수행하고 Manager가 실제 작업을 생성하도록 함
    if state.requires_calculation:
        state.calculation_queue = CalculationQueue(
            tasks=[],
            current_task_id=None,
            completed_task_ids=[]
        )
        
    return state 