"""
작도 계획 유틸리티 모듈

이 모듈은 작도 계획 생성 및 관리를 위한 유틸리티 함수를 제공합니다.
"""

from typing import Dict, Any, List, Optional
from models.state_models import ConstructionPlan, ConstructionStep

def build_construction_plan(
    problem: str,
    parsed_elements: Dict[str, Any],
    calculations: Optional[Dict[str, Any]] = None,
    direct_commands: Optional[List[Dict[str, Any]]] = None,
    suggested_tasks: Optional[List[Dict[str, Any]]] = None
) -> ConstructionPlan:
    """
    작도 계획 생성
    
    Args:
        problem: 문제 텍스트
        parsed_elements: 파싱된 기하학 요소
        calculations: 계산 결과 (선택 사항)
        direct_commands: 직접 GeoGebra 명령어 (선택 사항)
        suggested_tasks: 제안된 계산 작업 (선택 사항)
        
    Returns:
        ConstructionPlan 객체
    """
    # 기본 계획 생성
    plan = ConstructionPlan(
        title=f"「{problem[:30]}...」作图计划",
        description=f"针对问题「{problem}」的几何作图计划",
        steps=[],
        final_result="完成几何作图"
    )
    
    # 단계 추가 시작
    step_counter = 1
    
    # 1. 기본 기하 요소 (점, 선 등) 추가
    if "geometric_objects" in parsed_elements:
        for obj_name, obj in parsed_elements["geometric_objects"].items():
            obj_type = obj.get("type", "").lower()
            
            if obj_type == "point":
                plan.steps.append(ConstructionStep(
                    step_id=f"step_{step_counter}",
                    description=f"绘制点 {obj_name}",
                    task_type="point_construction",
                    geometric_elements=[obj_name],
                    command_type="Point",
                    parameters={"coordinates": obj.get("coordinates", [0, 0])}
                ))
                step_counter += 1
            
            elif obj_type in ["line", "segment", "ray"]:
                if "points" in obj and len(obj["points"]) >= 2:
                    command_type = "Line" if obj_type == "line" else "Segment" if obj_type == "segment" else "Ray"
                    plan.steps.append(ConstructionStep(
                        step_id=f"step_{step_counter}",
                        description=f"绘制{obj_type} {obj_name}，通过点 {' 和 '.join(obj['points'])}",
                        task_type=f"{obj_type}_construction",
                        geometric_elements=[obj_name] + obj["points"],
                        command_type=command_type,
                        parameters={"points": obj["points"]}
                    ))
                    step_counter += 1
    
    # 2. 직접 명령어가 있는 경우 추가
    if direct_commands:
        for i, cmd in enumerate(direct_commands):
            plan.steps.append(ConstructionStep(
                step_id=f"step_{step_counter}",
                description=cmd.get("description", f"执行GeoGebra命令 {i+1}"),
                task_type=cmd.get("task_type", "direct_command"),
                operation_type=cmd.get("operation_type"),
                geometric_elements=cmd.get("elements", []),
                command_type=cmd.get("command_type"),
                parameters=cmd.get("parameters", {}),
                geogebra_command=cmd.get("geogebra_command")
            ))
            step_counter += 1
    
    # 3. 제안된 작업이 있는 경우 추가
    if suggested_tasks:
        for task in suggested_tasks:
            plan.steps.append(ConstructionStep(
                step_id=f"step_{step_counter}",
                description=task.get("description", "计算步骤"),
                task_type=task.get("task_type", "calculation"),
                operation_type=task.get("operation_type"),
                geometric_elements=task.get("elements", []),
                parameters=task.get("parameters", {}),
                dependencies=task.get("dependencies", [])
            ))
            step_counter += 1
    
    # 4. 계산 결과가 있는 경우 최종 결과 업데이트
    if calculations and "conclusion" in calculations:
        plan.final_result = calculations["conclusion"]
    
    return plan
