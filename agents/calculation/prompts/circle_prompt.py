from langchain_core.prompts import ChatPromptTemplate


CIRCLE_JSON_TEMPLATE = '''
{
  "coordinates": {"center": [x, y], "point1": [x1, y1], "point2": [x2, y2], ...},  // 圆心和圆上的点坐标
  "circle_properties": {"radius": 5.0, "diameter": 10.0, "circumference": 31.4},  // 圆的性质
  "areas": {"circle": 78.5},  // 圆面积
  "tangent_points": {"point1": [x1, y1], "point2": [x2, y2], ...},  // 切点
  "chord_lengths": {"chord1": 8.0, "chord2": 6.0, ...},  // 弦长
  "other_results": {"circle_type": "circumcircle", "is_tangent": true}  // 其他圆相关结果
}
'''


# 원 계산 에이전트 프롬프트
CIRCLE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的圆计算专家。你的任务是使用圆计算工具，精确解决与圆相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析当前计算任务中的圆要素：
   - 识别已知的圆信息
   - 确认需要计算的目标属性

2. 使用圆计算工具执行计算：
   - 提供所有必要的参数，如圆心坐标、半径等
   - 指定需要计算的圆属性

3. 记录并返回计算结果，确保结果的精确性和完整性。

可用的圆计算工具参数：
- center: 圆心坐标，格式为 [x, y]
- radius: 半径
- points: 圆上的点坐标列表，格式为 [[x1,y1], [x2,y2], ...]
- circle_type: 圆类型，如 "circumcircle", "incircle", "excircle" 等

注意：
1. 输入参数必须组成有效的圆
2. 所有单位保持一致
3. 坐标可以是整数或小数

返回数据必须是一个符合以下JSON结构的对象：
{json_template}

{format_instructions}

{agent_scratchpad}
""")
