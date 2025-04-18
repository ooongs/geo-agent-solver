from typing import Any, Dict
from models.state_models import GeometryState, CalculationTask

def update_calculation_results(state: GeometryState, task: CalculationTask) -> None:
    """
    Universal function to update calculation results based on task results.
    
    Args:
        state: Current geometry state
        task: Completed calculation task
    """
    task_id = task.task_id
    
    if not task.result:
        print(f"[WARNING] No result found for task {task_id}")
        return
    
    # 기존 또는 새 결과 업데이트
    state.calculation_results[task_id] = task.result
    
    # If the task has specific fields, update them in the state's calculation_results
    if isinstance(task.result, dict):
        result_dict = task.result
    else:
        try:
            result_dict = task.result.to_dict()
        except:
            print(f"[WARNING] Could not convert result to dict for task {task_id}")
            return
    
    # Update specific fields that come from the result
    for field in ["coordinates", "lengths", "angles", "areas"]:
        if field in result_dict and result_dict[field]:
            if field not in state.calculation_results:
                state.calculation_results[field] = {}
            state.calculation_results[field].update(result_dict[field])
    
    # Update geometric_elements if present
    if "geometric_elements" in result_dict and result_dict["geometric_elements"]:
        if "geometric_elements" not in state.calculation_results:
            state.calculation_results["geometric_elements"] = {}
        
        for elem_type, elements in result_dict["geometric_elements"].items():
            if elements:
                if elem_type not in state.calculation_results["geometric_elements"]:
                    state.calculation_results["geometric_elements"][elem_type] = []
                
                if isinstance(elements, list):
                    state.calculation_results["geometric_elements"][elem_type].extend(elements)
                else:
                    state.calculation_results["geometric_elements"][elem_type] = elements
    
    # Update derived_data if present
    if "derived_data" in result_dict and result_dict["derived_data"]:
        if "derived_data" not in state.calculation_results:
            state.calculation_results["derived_data"] = {}
        
        for data_type, data in result_dict["derived_data"].items():
            if data:
                if data_type not in state.calculation_results["derived_data"]:
                    state.calculation_results["derived_data"][data_type] = {}
                
                if isinstance(data, dict):
                    state.calculation_results["derived_data"][data_type].update(data)
                else:
                    state.calculation_results["derived_data"][data_type] = data

def deep_merge_dict(target, source):
    """중첩 딕셔너리 병합 함수"""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            deep_merge_dict(target[key], value)
        else:
            target[key] = value
