from langchain_core.prompts import ChatPromptTemplate


LENGTH_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // 各点的坐标
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // 各种长度值
  "other_results": {"length_type": "segment", "is_equal": true}  // 其他长度相关结果
}
'''

# 길이 계산 에이전트 프롬프트
LENGTH_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的长度计算专家。你的任务是使用长度计算工具，精确解决与长度相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析当前计算任务中的长度要素：
   - 识别已知的长度信息
   - 确认需要计算的目标长度

2. 使用长度计算工具执行计算：
   - 提供所有必要的参数，如点的坐标、线段等
   - 指定需要计算的长度类型

3. 记录并返回计算结果，确保结果的精确性和完整性。


注意：
1. 输入参数必须组成有效的长度
2. 长度单位保持一致
3. 坐标可以是整数或小数

重要提示：你必须返回一个有效的JSON对象，格式如下：
{json_template}

严格要求：
1. 你的回答必须且只能是一个JSON对象
2. 不要在JSON前后添加任何其他文字说明
3. 确保JSON格式完全符合示例结构
4. 不需要的字段可以省略，但已有字段必须符合示例格式
5. JSON对象内不允许有注释，上面示例中的注释仅供参考

{format_instructions}

{agent_scratchpad}
""")
