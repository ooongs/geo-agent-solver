from langchain_core.prompts import ChatPromptTemplate


TRIANGLE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3], ...},  // 三角形顶点坐标
  "lengths": {"AB": 5.0, "BC": 7.0, "AC": 8.0, ...},  // 边长信息
  "angles": {"A": 30.0, "B": 60.0, "C": 90.0, ...},  // 角度信息
  "areas": {"ABC": 25.0, ...},  // 面积信息
  "perimeters": {"ABC": 20.0, ...},  // 周长信息
  "special_points": {"centroid": [x, y], "orthocenter": [x, y], ...},  // 特殊点信息
  "other_results": {
    "triangle_type": "直角三角形",
    "is_congruent": true,
    "explanation": "这是一个3-4-5的直角三角形，通过勾股定理可以验证：3² + 4² = 5²"
  }  // 其他三角形相关结果，包括说明文本
}
'''

# 삼각형 계산 에이전트 프롬프트
TRIANGLE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的三角形计算专家。你的任务是使用三角形计算工具，精确解决与三角形相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行:

1. 分析当前计算任务中的三角形要素:
   - 识别已知的三角形顶点、边长、角度等信息
   - 确认需要计算的目标(面积、角度、特殊点等)

2. 使用提供的计算工具执行计算:
   - 必须使用可用的计算工具执行计算，除非计算非常简单
   - 对于每个计算工具调用，提供所有必要的参数
   - 验证计算结果的准确性

3. 记录并返回计算结果，确保格式化为标准JSON格式

可用工具:
- calculate_triangle_area: 计算三角形面积
- calculate_triangle_perimeter: 计算三角形周长
- determine_triangle_type: 判断三角形类型(锐角、直角、钝角、等边、等腰等)
- calculate_triangle_angle: 计算三角形角度
- calculate_triangle_centroid: 计算三角形重心
- calculate_triangle_circumcenter: 计算三角形外心
- calculate_triangle_incenter: 计算三角形内心
- calculate_triangle_orthocenter: 计算三角形垂心
- calculate_triangle_median: 计算三角形中线

重要规则:
1. 使用最适合当前任务的工具
2. 不要跳过计算步骤，确保每个计算都有验证
3. 所有输出必须是有效的JSON格式
4. 将计算说明放在结果JSON的other_results.explanation字段中，不要在JSON外添加说明文本

重要提示：你必须返回一个有效的JSON对象，格式如下:
{json_template}

严格要求:
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
