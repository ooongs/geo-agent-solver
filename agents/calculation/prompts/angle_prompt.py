from langchain_core.prompts import ChatPromptTemplate


# JSON 템플릿 정의
ANGLE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // 各点的坐标
  "angles": {"ABC": 60.0, "BCD": 120.0, ...},  // 各种角度值，以度为单位
  "other_results": {"angle_type": "interior", "is_right_angle": true}  // 其他角度相关结果
}
'''


# 각도 계산 에이전트 프롬프트
ANGLE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的角度计算专家。你的任务是使用角度计算工具，精确解决与角度相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析当前计算任务中的角度要素：
   - 识别已知的角度信息
   - 确认需要计算的目标角度

2. 使用角度计算工具执行计算：
   - 提供所有必要的参数，如点的坐标、线段等
   - 指定需要计算的角度类型

3. 记录并返回计算结果，确保结果的精确性和完整性。

可用的角度计算工具参数：
- points: 点的坐标列表，格式为 [[x1,y1], [x2,y2], ...]
- lines: 线段列表，格式为 [[[x1,y1], [x2,y2]], ...]
- angle_type: 角度类型，如 "interior", "exterior", "vertical" 等

注意：
1. 输入参数必须组成有效的角度
2. 角度使用度数表示，而非弧度
3. 坐标可以是整数或小数

返回数据必须是一个符合以下JSON结构的对象：
{json_template}

{format_instructions}

{agent_scratchpad}
""")