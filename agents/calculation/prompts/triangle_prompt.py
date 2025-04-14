from langchain_core.prompts import ChatPromptTemplate


TRIANGLE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3]},  // 三角形顶点坐标
  "lengths": {"AB": 5.0, "BC": 7.0, "CA": 6.0},  // 三角形边长
  "angles": {"A": 60.0, "B": 70.0, "C": 50.0},  // 三角形内角
  "areas": {"triangle": 15.0},  // 三角形面积
  "perimeters": {"triangle": 18.0},  // 三角形周长
  "special_points": {"centroid": [x, y], "circumcenter": [x, y], "orthocenter": [x, y], "incenter": [x, y]},  // 特殊点
  "circle_properties": {"circumradius": 3.5, "inradius": 1.5},  // 圆的性质
  "other_results": {"triangle_type": "scalene", "is_right": false}  // 其他三角形相关结果
}
'''

# 삼각형 계산 에이전트 프롬프트
TRIANGLE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的三角形计算专家。你的任务是使用三角形计算工具，精确解决与三角形相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行：

1. 分析当前计算任务中的三角形要素：
   - 识别已知的三角形信息
   - 确认需要计算的目标属性

2. 使用三角形计算工具执行计算：
   - 提供所有必要的参数，如点的坐标、边长等
   - 指定需要计算的三角形属性

3. 记录并返回计算结果，确保结果的精确性和完整性。

可用的三角形计算工具参数：
- points: 点的坐标列表，格式为 [[x1,y1], [x2,y2], ...]
- sides: 边长列表，格式为 [a, b, c, ...]
- angles: 角度列表，格式为 [θ1, θ2, θ3, ...]
- triangle_type: 三角形类型，如 "equilateral", "isosceles", "right" 等

注意：
1. 输入参数必须组成有效的三角形
2. 角度使用度数表示，而非弧度
3. 坐标可以是整数或小数

返回数据必须是一个符合以下JSON结构的对象：
{json_template}

{format_instructions}

{agent_scratchpad}
""")
