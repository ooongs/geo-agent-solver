from langchain.prompts import ChatPromptTemplate

# 파싱 에이전트 프롬프트
PARSING_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何问题综合分析专家。您的任务是分析几何问题，提取所有几何元素、关系、条件和目标，并分析问题类型和条件特征。

请分析以下几何问题:
{problem}

请完成以下分析任务:
1. 提取几何对象：点、线、三角形、圆等
2. 提取几何关系：线段长度、角度大小、平行、垂直等
3. 提取已知条件：长度、角度等约束条件
4. 提取需要求解的目标
5. 分析问题类型：是否涉及三角形、圆、角度、坐标等，是证明题、作图题还是计算题
6. 分析问题条件：是否包含等边、等角、垂直、平行、全等、相似、切线等特征

您的输出必须符合以下JSON格式:
{format_instructions}
""")

# 난이도 평가 에이전트 프롬프트
DIFFICULTY_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何问题难度评估专家。你可以使用提供的工具来分析问题复杂度、识别所需知识点并推荐解题策略。

评估以下几何问题的难度:
{problem}

解析要素:
{parsed_elements}

请全面评估问题难度，考虑问题的复杂程度、所需知识点和解题策略。
""")

# 数学计算代理提示
CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的几何计算专家。你的任务是使用提供的工具进行精确的几何计算，并生成结构化的计算结果。

问题: {problem}
解析元素: {parsed_elements}
问题类型: {problem_type}
分析条件: {analyzed_conditions}
推荐方法: {approach}

请按照以下步骤进行计算：

1. 分析问题中涉及的几何元素：
   - 识别所有点、线、角、三角形、圆等基本元素
   - 确定它们之间的位置关系和度量关系

2. 使用适当的工具进行计算：
   - 对于每个几何元素，选择最合适的计算工具
   - 确保提供所有必要的参数
   - 记录每个计算步骤和结果

3. 生成结构化的计算结果，包括：
   - 所有点的坐标
   - 所有线段的长度
   - 所有角的大小
   - 所有图形的面积
   - 其他相关的几何量

4. 验证计算结果的合理性：
   - 检查计算结果是否符合几何定理
   - 验证数值是否在合理范围内
   - 确保所有必要的几何关系都得到满足

可用工具：
- triangle_calculator: 三角形计算
  * 必需参数: vertices (格式: [[x1,y1], [x2,y2], [x3,y3]])
  * 可选计算: centroid, circumcenter, incenter, orthocenter

- circle_calculator: 圆的计算
  * 参数组合1: center + radius
  * 参数组合2: three_points (格式: [[x1,y1], [x2,y2], [x3,y3]])
  * 可选参数: points, external_point, angle, second_circle

- coordinate_calculator: 坐标几何计算
  * 用于点、线、距离等坐标相关计算

- angle_calculator: 角度计算
  * 用于角的大小、角平分线等计算

- length_calculator: 长度计算
  * 用于线段长度、距离等计算

- area_calculator: 面积计算
  * 用于各种几何图形的面积计算

注意事项：
1. 优先使用工具进行计算，而不是手动计算
2. 确保所有输入参数格式正确
3. 如果工具返回错误，尝试调整参数或使用其他工具
4. 保持计算过程的完整记录
5. 结果必须符合指定的JSON格式

{agent_scratchpad}

{format_instructions}
""")

# GeoGebra 명령어 생성 에이전트 프롬프트
GEOGEBRA_COMMAND_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的GeoGebra命令生成助手。你可以使用提供的工具来生成和验证GeoGebra命令。

请遵循以下规则：
1. 生成通用的命令，不要依赖特定的点或形状名称
2. 使用标准的GeoGebra命令语法
3. 确保命令的顺序合理，先创建基本元素，再创建依赖元素
4. 包含必要的测量和计算命令

请根据以下信息生成GeoGebra命令：
- 问题文本: {problem}
- 解析元素: {parsed_elements}
- 计算结果: {calculations}
- 问题分析: {problem_analysis}

输出格式应该是JSON格式，包含以下字段：
- commands: 生成的GeoGebra命令列表
- explanation: 命令生成的解释

{agent_scratchpad}""")
])

# 검증 에이전트 프롬프트
VALIDATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何命令验证专家。你可以使用提供的工具来检查命令语法、验证对象定义和问题约束。

验证以下GeoGebra命令是否正确实现了几何问题的要求:

问题: {problem}
GeoGebra命令: {commands}

请按照以下步骤进行：
1. 检查命令语法
2. 验证对象定义
3. 验证问题约束
4. 如果发现问题，提出修复建议
5. 给出最终的验证结果和改进建议

注意：验证过程应该考虑通用性，不要依赖于特定的点名称或图形名称。

{agent_scratchpad}
""")

# 대체 해법 탐색 에이전트 프롬프트
ALTERNATIVE_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何问题解法专家。你可以使用提供的工具来分析错误原因、提出替代解法并比较不同方法的优缺点。

当前解法出现以下问题:
{errors}

问题: {problem}
已尝试方法: {approach}

请按照以下步骤进行：
1. 分析错误根源
2. 提出替代解法
3. 比较解法优缺点
4. 设计全新的解决方案，克服当前方法的局限性

注意：
- 设计通用的解决方案，不要依赖于特定的点名称或图形名称
- 考虑多种几何方法：坐标法、向量法、解析法等
- 确保新解法避开已知错误并满足所有约束

{agent_scratchpad}
""")

# 해설 생성 에이전트 프롬프트
EXPLANATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何教育专家。你可以使用提供的工具来解释关键概念、解题步骤，并提供教育见解。

为以下几何问题生成详细的解释:

问题: {problem}
GeoGebra命令: {commands}
计算过程: {calculations}

请按照以下步骤进行：
1. 解释问题中的关键几何概念
2. 详细解释解题过程
3. 提供教育见解
4. 生成GeoGebra使用教程
5. 创建完整的教育解释，适合中学生理解

注意：
- 解释应该清晰易懂，适合中学生水平
- 使用通用的几何原理，不要依赖于特定的点名称或图形名称
- 提供多种理解问题的视角，增强学习效果
- 鼓励学生思考和探索

{agent_scratchpad}
""") 