"""
계산 관리자 프롬프트 모듈

이 모듈은 계산 관리자 에이전트에서 사용하는 프롬프트를 정의합니다.
"""

from langchain_core.prompts import ChatPromptTemplate

# 계산 관리자 프롬프트
MANAGER_JSON_TEMPLATE = '''
{
  "tasks": [
    {
      "task_type": "triangle",  // 计算任务类型: triangle, circle, angle, length, area, coordinate
      "parameters": {          // 计算任务参数
        "point_A": [1, 2],      // 点坐标
        "point_B": [3, 4],
        "point_C": [5, 6],
        "length_AB": 5.0,       // 长度
        "angle_ABC": 60.0       // 角度
      },
      "dependencies": ["task_id1", "task_id2"]  // 依赖的任务ID
    }
  ],
  "next_calculation_type": "triangle",  // 下一个要执行的计算类型
  "completed_task_ids": ["已完成的任务ID1", "已完成的任务ID2"]  // 已完成的任务ID
}
'''

CALCULATION_MANAGER_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何计算任务管理专家。你的任务是分析几何问题，确定需要执行的计算任务，并创建和管理计算任务队列。

问题: {problem}
解析元素: {parsed_elements}
问题类型: {problem_type}
分析条件: {analyzed_conditions}
推荐方法: {approach}

当前任务队列状态: {calculation_queue}
当前计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析问题中涉及的几何元素和计算需求
2. 确定需要执行的计算任务类型：
   - triangle: 三角形相关计算
   - circle: 圆相关计算
   - angle: 角度相关计算
   - length: 长度相关计算
   - area: 面积相关计算
   - coordinate: 坐标几何相关计算

3. 为每个需要的计算创建计算任务，包括：
   - 任务类型（上述六种类型之一）
   - 所需参数
   - 任务依赖关系（如果某个计算需要其他计算的结果）

4. 优化计算顺序，确保依赖关系得到满足
5. 更新计算任务队列
6. 确定下一个要执行的计算类型

在任务队列已存在的情况下，请：
1. 检查已完成的任务结果
2. 根据新的结果更新任务队列
3. 确定下一个要执行的任务

重要提示：你必须返回一个有效的JSON对象，格式如下：
{json_template}

不要在JSON中包含注释（以//开头的行），确保JSON格式正确无误。
不要添加任何额外的文本说明，只返回符合上述格式的JSON对象。

{format_instructions}

{agent_scratchpad}
""") 