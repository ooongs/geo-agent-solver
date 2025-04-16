"""
상태 모델 모듈

이 모듈은 기하학 문제 해결기에서 사용되는 상태 모델 클래스를 정의합니다.
또한 계산 관련 모델도 포함하여 원형 가져오기(circular import) 문제를 해결합니다.
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field

# 계산 작업 클래스 정의
class CalculationTask(BaseModel):
    task_id: str = Field(description="计算任务的唯一标识符")
    task_type: str = Field(description="计算任务类型，如'triangle', 'circle', 'angle'等")
    operation_type: Optional[str] = Field(
        description="具体操作类型，如'midpoint', 'intersect', 'perpendicular'等",
        default=None
    )
    parameters: Dict[str, Any] = Field(description="计算任务的参数")
    dependencies: List[str] = Field(description="此任务依赖的其他任务ID", default_factory=list)
    description: str = Field(description="任务描述以及分析")
    result: Optional[Dict[str, Any]] = Field(description="计算结果", default=None)
    status: Literal["pending", "running", "completed", "failed"] = Field(
        description="任务状态", default="pending"
    )
    geogebra_alternatives: bool = Field(
        description="是否可以直接使用GeoGebra命令实现，不需要计算",
        default=False
    )
    geogebra_command: Optional[str] = Field(
        description="可以替代计算的GeoGebra命令",
        default=None
    )

# 계산 큐 클래스 정의
class CalculationQueue(BaseModel):
    tasks: List[CalculationTask] = Field(description="所有计算任务列表", default_factory=list)
    current_task_id: Optional[str] = Field(description="当前正在执行的任务ID", default=None)
    completed_task_ids: List[str] = Field(description="已完成的任务ID列表", default_factory=list)
    
    def get_next_task(self) -> Optional[CalculationTask]:
        """다음 실행 가능한 작업 가져오기"""
        for task in self.tasks:
            if task.status == "pending" and all(dep in self.completed_task_ids for dep in task.dependencies):
                return task
        return None

# 계산 작업 생성 모델
class CalculationTaskCreation(BaseModel):
    """计算任务创建模型"""
    tasks: List[Dict[str, Any]] = Field(description="需要创建的计算任务列表")
    next_calculation_type: Optional[str] = Field(description="下一个要执行的计算类型", default=None)
    completed_task_ids: List[str] = Field(description="已完成的任务ID列表", default_factory=list)

class ConstructionStep(BaseModel):
    """작도 단계 모델"""
    step_id: str = Field(description="步骤唯一标识符")
    description: str = Field(description="步骤描述")
    task_type: str = Field(description="步骤类型，如'点作图'，'线作图'等")
    operation_type: Optional[str] = Field(description="具体操作类型", default=None)
    geometric_elements: List[str] = Field(description="此步骤涉及的几何元素", default_factory=list)
    command_type: Optional[str] = Field(description="建议GeoGebra命令类型", default=None)
    parameters: Dict[str, Any] = Field(description="步骤参数", default_factory=dict)
    dependencies: List[str] = Field(description="依赖的步骤ID", default_factory=list)
    geogebra_command: Optional[str] = Field(description="直接可用的GeoGebra命令", default=None)
    selected_command: Optional[Dict[str, Any]] = Field(description="选择的最佳命令", default=None)

class ConstructionPlan(BaseModel):
    """작도 계획 모델"""
    title: str = Field(description="作图计划标题")
    description: str = Field(description="作图计划整体描述")
    steps: List[ConstructionStep] = Field(description="作图步骤列表", default_factory=list)
    final_result: str = Field(description="预期最终结果")


class CalculationTypes(BaseModel):
    """계산 유형 정보"""
    triangle: bool = False
    circle: bool = False
    angle: bool = False
    length: bool = False
    area: bool = False
    coordinate: bool = False


class SuggestedTask(BaseModel):
    """제안된 작업 정보"""
    task_type: str
    operation_type: Optional[str] = None
    parameters: Dict[str, Any] = {}
    dependencies: List[str] = []
    description: str = ""
    geogebra_alternatives: bool = False
    geogebra_command: Optional[str] = None


class PlannerResult(BaseModel):
    """분석 결과 모델"""

    requires_calculation: bool = Field(description="是否需要复杂计算")
    reasoning: str = Field(description="分析理由")
    suggested_tasks: Optional[List[Dict[str, Any]]] = Field(description="建议的计算任务", default_factory=list)
    suggested_tasks_reasoning: Optional[str] = Field(description="建议的计算任务理由", default="")
    # 작도 계획 필드 추가
    construction_plan: Optional[ConstructionPlan] = Field(
        description="简单问题的几何作图计划", 
        default=None
    )


# 기하학 상태 모델
class GeometryState(BaseModel):
    input_problem: Optional[str] = Field(description="输入的几何问题", default=None)
    parsed_elements: Dict[str, Any] = Field(description="解析后的几何元素和条件", default_factory=dict)
    problem_analysis: Dict[str, Any] = Field(description="问题分析结果", default_factory=dict)
    approach: Optional[str] = Field(description="解决问题的方法", default=None)
    calculations: Dict[str, Any] = Field(description="合并后的计算结果", default_factory=dict)

    # 계산 관련 필드
    calculation_queue: Optional[CalculationQueue] = Field(description="计算任务队列", default=None)
    calculation_results: Optional[Dict[str, Any]] = Field(description="计算中间结果", default=None)
    next_calculation: Optional[str] = Field(description="下一个要执行的计算类型", default=None)
    requires_calculation: bool = Field(default=True, description="是否需要进行计算")
    
    # GeoGebra 및 검증 관련 필드
    geogebra_commands: Optional[List[str]] = Field(default=None, description="生成的GeoGebra命令")
    validation: Optional[Dict[str, Any]] = Field(default=None, description="验证结果") 
    explanation: Optional[str] = Field(default=None, description="中文解释")
    errors: Optional[List[str]] = Field(default=None, description="出现的错误")
    is_valid: bool = Field(default=False, description="解决方案有效性")
    retrieved_commands: Optional[List[Dict[str, Any]]] = Field(default=None, description="检索到的GeoGebra命令")

    # 작도 계획 필드 추가
    construction_plan: Optional[ConstructionPlan] = Field(default=None, description="几何作图计划")
    
    # 명령어 재생성 관련 필드 추가
    regenerated_commands: Optional[List[str]] = Field(default=None, description="重新生成的GeoGebra命令")
    command_regeneration_attempts: int = Field(default=0, description="重新生成GeoGebra命令的尝试次数")
