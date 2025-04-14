from langchain_core.prompts import ChatPromptTemplate


AREA_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // 各点的坐标
  "areas": {"triangle": 25.0, "rectangle": 50.0, ...},  // 各种面积值
  "other_results": {"area_type": "triangle", "is_regular": true}  // 其他面积相关结果
}
'''


# 면적 계산 에이전트 프롬프트
AREA_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的面积计算专家。你的任务是使用面积计算工具，精确解决与面积相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析当前计算任务中的面积要素：
   - 识别已知的面积信息
   - 确认需要计算的目标面积

2. 使用面积计算工具执行计算：
   - 提供所有必要的参数，如点的坐标、边长等
   - 指定需要计算的面积类型

3. 记录并返回计算结果，确保结果的精确性和完整性。

可用的面积计算工具参数：
- points: 点的坐标列表，格式为 [[x1,y1], [x2,y2], ...]
- sides: 边长列表，格式为 [a, b, c, ...]
- height: 高（如果需要）
- area_type: 面积类型，如 "triangle", "rectangle", "circle" 等

注意：
1. 输入参数必须组成有效的图形
2. 面积单位保持一致
3. 坐标可以是整数或小数

返回数据必须是一个符合以下JSON结构的对象：
{json_template}

{format_instructions}

{agent_scratchpad}
""")

