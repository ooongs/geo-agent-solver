from langchain_core.prompts import ChatPromptTemplate


LENGTH_JSON_TEMPLATE = '''
{
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // 各种长度值
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // 点的坐标（可选）
  "other_results": {
    "length_type": "segment",
    "is_equal": true,
    "explanation": "通过勾股定理计算得到 AC = sqrt(AB^2 + BC^2) = sqrt(9 + 16) = sqrt(25) = 5"
  }  // 其他长度相关结果，包括说明文本
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

2. 使用提供的计算工具执行计算：
   - 必须使用可用的计算工具执行计算，除非计算非常简单
   - 对于每个计算工具调用，提供所有必要的参数
   - 验证计算结果的准确性

3. 记录并返回计算结果，确保格式化为标准JSON格式

可用工具：
- calculate_distance_points：计算两点之间的距离
- calculate_distance_point_to_line：计算点到直线的距离
- calculate_distance_parallel_lines：计算两条平行线之间的距离
- calculate_perimeter_triangle：计算三角形的周长
- calculate_perimeter_quadrilateral：计算四边形的周长
- calculate_perimeter_polygon：计算多边形的周长
- calculate_circumference：计算圆的周长
- calculate_chord_length：计算圆的弦长
- calculate_arc_length：计算圆的弧长

重要规则：
1. 使用最适合当前任务的工具
2. 不要跳过计算步骤，确保每个计算都有验证
3. 所有输出必须是有效的JSON格式
4. 将计算说明放在结果JSON的other_results.explanation字段中，不要在JSON外添加说明文本

重要提示：你必须返回一个有效的JSON对象，格式如下：
{json_template}

严格要求：
1. 你的回答必须且只能是一个JSON对象
2. 不要在JSON前后添加任何其他文字说明
3. 确保JSON格式完全符合示例结构
4. 不需要的字段可以省略，但已有字段必须符合示例格式
5. JSON对象内不允许有注释，上面示例中的注释仅供参考
6. 对于简单计算，也要验证结果的正确性
7. 将所有解释和说明文本放在other_results.explanation字段中

{format_instructions}

{agent_scratchpad}
""")
