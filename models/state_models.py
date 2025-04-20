"""
State Model Module

This module defines state model classes used in the geometry problem solver.
It also includes calculation-related models to avoid circular import problems.
"""

from typing import Dict, List, Any, Optional, Literal, Union
from pydantic import BaseModel, Field


class DependencyNode(BaseModel):
    task_id: str
    dependencies: List[str] = []
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None

class DependencyGraph(BaseModel):
    nodes: Dict[str, DependencyNode] = {}
    execution_order: List[str] = []

# Calculation task class definition
class CalculationTask(BaseModel):
    task_id: str = Field(description="Unique identifier for the calculation task")
    task_type: str = Field(description="Calculation task type, such as 'triangle', 'circle', 'angle', etc.")
    operation_type: Optional[str] = Field(
        description="Specific operation type, such as 'midpoint', 'intersect', 'perpendicular', etc.",
        default=None
    )
    specific_method: Optional[str] = Field(description="Specific method", default=None)
    required_precision: Optional[str] = Field(description="Required precision", default=None)
    parameters: Dict[str, Any] = Field(description="Parameters for the calculation task")
    dependencies: List[str] = Field(description="IDs of other tasks this task depends on", default_factory=list)
    description: str = Field(description="Task description and analysis")
    result: Optional[Dict[str, Any]] = Field(description="Calculation result", default=None)
    status: Literal["pending", "running", "completed", "failed"] = Field(
        description="Task status", default="pending"
    )
    geogebra_alternatives: bool = Field(
        description="Whether it can be directly implemented using GeoGebra commands without calculation",
        default=False
    )
    geogebra_command: Optional[str] = Field(
        description="GeoGebra command that can replace the calculation",
        default=None
    )
    available_tools: Dict[str, List[str]] = Field(default_factory=dict)

    def copy(self) -> "CalculationTask":
        return CalculationTask(
            task_id=self.task_id,
            task_type=self.task_type,
            operation_type=self.operation_type,
            parameters=self.parameters.copy(),
            dependencies=self.dependencies.copy(),
            description=self.description,
            status=self.status,
            specific_method=self.specific_method,
            required_precision=self.required_precision,
            geogebra_alternatives=self.geogebra_alternatives,
            geogebra_command=self.geogebra_command,
            available_tools=self.available_tools.copy()
        )

# Calculation queue class definition
class CalculationQueue(BaseModel):
    tasks: List[CalculationTask] = Field(description="List of all calculation tasks", default_factory=list)
    current_task_id: Optional[str] = Field(description="ID of the currently executing task", default=None)
    completed_task_ids: List[str] = Field(description="List of completed task IDs", default_factory=list)
    dependency_graph: Optional[DependencyGraph] = Field(description="Dependency graph for calculation tasks", default=None)
    
    def get_next_task(self) -> Optional[CalculationTask]:
        """Get the next executable task"""
        for task in self.tasks:
            if task.status == "pending" and all(dep in self.completed_task_ids for dep in task.dependencies):
                return task
        return None

# Calculation task creation model
class CalculationTaskCreation(BaseModel):
    """Calculation task creation model"""
    tasks: List[Dict[str, Any]] = Field(description="List of calculation tasks to create")
    next_calculation_type: Optional[str] = Field(description="Type of the next calculation to execute", default=None)
    completed_task_ids: List[str] = Field(description="List of completed task IDs", default_factory=list)

class ConstructionStep(BaseModel):
    """Construction step model"""
    step_id: str = Field(description="Unique step identifier")
    description: str = Field(description="Step description")
    task_type: str = Field(description="Step type, such as 'point construction', 'line construction', etc.")
    operation_type: Optional[str] = Field(description="Specific operation type", default=None)
    geometric_elements: List[str] = Field(description="Geometric elements involved in this step", default_factory=list)
    command_type: Optional[str] = Field(description="Suggested GeoGebra command type", default=None)
    parameters: Dict[str, Any] = Field(description="Step parameters", default_factory=dict)
    dependencies: List[str] = Field(description="IDs of steps this step depends on", default_factory=list)
    geogebra_command: Optional[str] = Field(description="Directly usable GeoGebra command", default=None)
    selected_command: Optional[Dict[str, Any]] = Field(description="Selected best command", default=None)

class ConstructionPlan(BaseModel):
    """Construction plan model"""
    title: str = Field(description="Construction plan title")
    description: str = Field(description="Overall description of the construction plan")
    steps: List[ConstructionStep] = Field(description="List of construction steps", default_factory=list)
    final_result: str = Field(description="Expected final result")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ConstructionPlan instance to a dictionary for JSON serialization"""
        steps_list = []
        for step in self.steps:
            step_dict = {
                "step_id": step.step_id,
                "description": step.description,
                "task_type": step.task_type,
                "operation_type": step.operation_type,
                "geometric_elements": step.geometric_elements,
                "command_type": step.command_type,
                "parameters": step.parameters,
                "dependencies": step.dependencies,
                "geogebra_command": step.geogebra_command
            }
            
            # Handle selected_command which might contain complex objects
            if step.selected_command:
                step_dict["selected_command"] = {k: v for k, v in step.selected_command.items() 
                                              if not isinstance(v, (BaseModel, type))}
            else:
                step_dict["selected_command"] = None
                
            steps_list.append(step_dict)
            
        return {
            "title": self.title,
            "description": self.description,
            "steps": steps_list,
            "final_result": self.final_result
        }


class CalculationTypes(BaseModel):
    """Calculation type information"""
    triangle: bool = False
    circle: bool = False
    angle: bool = False
    length: bool = False
    area: bool = False
    coordinate: bool = False


class SuggestedTask(BaseModel):
    """Suggested task information"""
    task_type: str
    operation_type: Optional[str] = None
    parameters: Dict[str, Any] = {}
    dependencies: List[str] = []
    description: str = ""
    geogebra_alternatives: bool = False
    geogebra_command: Optional[str] = None


class PlannerResult(BaseModel):
    """Analysis result model"""

    requires_calculation: bool = Field(description="Whether complex calculations are required")
    reasoning: str = Field(description="Analysis reasoning")
    suggested_tasks: Optional[List[Dict[str, Any]]] = Field(description="Suggested calculation tasks", default_factory=list)
    suggested_tasks_reasoning: Optional[str] = Field(description="Reasoning for suggested calculation tasks", default="")
    # Add construction plan field
    construction_plan: Optional[ConstructionPlan] = Field(
        description="Geometric construction plan for simple problems", 
        default=None
    )


# Geometry state model
class GeometryState(BaseModel):
    input_problem: Optional[str] = Field(description="Input geometry problem", default=None)
    parsed_elements: Dict[str, Any] = Field(description="Parsed geometric elements and conditions", default_factory=dict)
    problem_analysis: Dict[str, Any] = Field(description="Problem analysis results", default_factory=dict)
    approach: Optional[str] = Field(description="Method for solving the problem", default=None)
    calculations: Dict[str, Any] = Field(description="Merged calculation results", default_factory=dict)

    # Calculation-related fields
    calculation_queue: Optional[CalculationQueue] = Field(description="Calculation task queue", default=None)
    calculation_results: Dict[str, Any] = Field(description="Intermediate calculation results", default_factory=dict)
    next_calculation: Optional[str] = Field(description="Type of the next calculation to execute", default=None)
    requires_calculation: bool = Field(default=True, description="Whether calculations are required")
    is_manager_initialized: bool = Field(default=False, description="Whether the Manager agent has been initialized")
    
    # GeoGebra and validation-related fields
    geogebra_commands: Optional[List[str]] = Field(default=None, description="Generated GeoGebra commands")
    validation: Optional[Dict[str, Any]] = Field(default=None, description="Validation results") 
    explanation: Optional[str] = Field(default=None, description="Explanation")
    errors: Optional[List[str]] = Field(default=None, description="Errors that occurred")
    is_valid: bool = Field(default=False, description="Solution validity")
    retrieved_commands: Optional[List[Dict[str, Any]]] = Field(default=None, description="Retrieved GeoGebra commands")

    # Add construction plan field
    construction_plan: Optional[ConstructionPlan] = Field(default=None, description="Geometric construction plan")
    
    # Add command regeneration-related fields
    regenerated_commands: Optional[List[str]] = Field(default=None, description="Regenerated GeoGebra commands")
    command_regeneration_attempts: int = Field(default=0, description="Number of attempts to regenerate GeoGebra commands")

    # Add geometric constraints
    geometric_constraints: Optional[Dict[str, Any]] = Field(description="Geometric constraints", default=None)

    # Add intermediate construction information
    intermediate_constructions: Optional[Dict[str, Any]] = Field(description="Intermediate construction information", default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the GeometryState instance to a dictionary for JSON serialization"""
        result = {
            "input_problem": self.input_problem,
            "parsed_elements": self.parsed_elements,
            "problem_analysis": self.problem_analysis,
            "approach": self.approach,
            "calculations": self.calculations,
            "calculation_results": self.calculation_results,
            "next_calculation": self.next_calculation,
            "requires_calculation": self.requires_calculation,
            "is_manager_initialized": self.is_manager_initialized,
            "geogebra_commands": self.geogebra_commands,
            "validation": self.validation,
            "explanation": self.explanation,
            "errors": self.errors,
            "is_valid": self.is_valid,
            "retrieved_commands": self.retrieved_commands,
            "regenerated_commands": self.regenerated_commands,
            "command_regeneration_attempts": self.command_regeneration_attempts,
            "geometric_constraints": self.geometric_constraints,
            "intermediate_constructions": self.intermediate_constructions
        }
        
        # Handle construction_plan
        if self.construction_plan:
            result["construction_plan"] = self.construction_plan.to_dict()
        else:
            result["construction_plan"] = None
            
        # Handle calculation_queue
        if self.calculation_queue:
            result["calculation_queue"] = {
                "completed_task_ids": self.calculation_queue.completed_task_ids,
                "current_task_id": self.calculation_queue.current_task_id,
                "tasks_count": len(self.calculation_queue.tasks) if self.calculation_queue.tasks else 0
            }
        else:
            result["calculation_queue"] = None
            
        return result

