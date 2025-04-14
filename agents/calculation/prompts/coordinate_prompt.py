from langchain_core.prompts import ChatPromptTemplate

COORDINATE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // 各点的坐标
  "other_results": {"coordinate_type": "midpoint", "is_valid": true}  // 其他坐标相关结果
}
'''

# 좌표 계산 에이전트 프롬프트
COORDINATE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的坐标计算专家。你的任务是使用坐标计算工具，精确解决与坐标相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析当前计算任务中的坐标要素：
   - 识别已知的坐标信息
   - 确认需要计算的目标坐标

2. 使用坐标计算工具执行计算：
   - 提供所有必要的参数，如点的坐标、距离等
   - 指定需要计算的坐标类型

3. 记录并返回计算结果，确保结果的精确性和完整性。

可用的坐标计算工具参数：
- points: 已知点的坐标列表，格式为 [[x1,y1], [x2,y2], ...]
- distances: 距离列表，格式为 [d1, d2, ...]
- angles: 角度列表，格式为 [θ1, θ2, ...]
- coordinate_type: 坐标类型，如 "midpoint", "intersection", "reflection" 等

注意：
1. 输入参数必须组成有效的坐标计算
2. 坐标单位保持一致
3. 坐标可以是整数或小数

返回数据必须是一个符合以下JSON结构的对象：
{json_template}

{format_instructions}

{agent_scratchpad}
""")