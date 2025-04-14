"""
상태 모델 모듈

이 모듈은 기하학 문제 해결기에서 사용되는 상태 모델 클래스를 정의합니다.
또한 계산 관련 모델도 포함하여 원형 가져오기(circular import) 문제를 해결합니다.
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

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
    skip_calculations: List[str] = Field(description="可以跳过的计算任务ID列表", default_factory=list)

# 에이전트 상태 열거형
class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# 기하학 상태 모델
class GeometryState(BaseModel):
    input_problem: Optional[str] = Field(description="输入的几何问题", default=None)
    parsed_elements: Dict[str, Any] = Field(description="解析后的几何元素和条件", default_factory=dict)
    problem_analysis: Dict[str, Any] = Field(description="问题分析结果", default_factory=dict)
    difficulty: Optional[Dict[str, Any]] = Field(description="问题难度评估结果", default=None)
    approach: Optional[str] = Field(description="解决问题的方法", default=None)
    agent_status: Dict[str, AgentStatus] = Field(description="各代理的状态", default_factory=dict)
    intermediate_results: Dict[str, Any] = Field(description="中间计算结果", default_factory=dict)
    calculations: Dict[str, Any] = Field(description="计算过程和结果", default_factory=dict)
    solution: Optional[Dict[str, Any]] = Field(description="最终解决方案", default=None)
    chinese_solution: Optional[str] = Field(description="中文解决方案", default=None)
    current_agent: Optional[str] = Field(description="当前正在运行的代理", default=None)
    
    # 계산 관련 필드
    calculation_queue: Optional[CalculationQueue] = Field(description="计算任务队列", default=None)
    calculation_results: Optional[Dict[str, Any]] = Field(description="合并后的计算结果", default=None)
    next_calculation: Optional[str] = Field(description="下一个要执行的计算类型", default=None)
    requires_calculation: bool = Field(default=True, description="是否需要进行计算")
    
    # GeoGebra 및 검증 관련 필드
    geogebra_commands: Optional[List[str]] = Field(default=None, description="生成的GeoGebra命令")
    validation: Optional[Dict[str, Any]] = Field(default=None, description="验证结果") 
    alternative_solution: Optional[Dict[str, Any]] = Field(default=None, description="替代解法")
    explanation: Optional[str] = Field(default=None, description="中文解释")
    attempt_count: int = Field(default=0, description="尝试次数")
    errors: Optional[List[str]] = Field(default=None, description="出现的错误")
    is_valid: bool = Field(default=False, description="解决方案有效性")

class AnalysisResult(BaseModel):
    """분석 결과 모델"""
    problem_type: Dict[str, bool] = Field(description="问题类型分析")
    approach: str = Field(description="推荐的解题方法")
    requires_calculation: bool = Field(description="是否需要复杂计算")
    calculation_types: Dict[str, bool] = Field(description="需要的计算类型")
    reasoning: str = Field(description="分析理由")
    suggested_tasks: List[Dict[str, Any]] = Field(description="建议的计算任务", default_factory=list)
    suggested_tasks_reasoning: str = Field(description="建议的计算任务理由", default="")
    direct_geogebra_commands: List[Dict[str, Any]] = Field(
        description="可以直接使用GeoGebra命令实现的操作，不需要计算", 
        default_factory=list
    )
