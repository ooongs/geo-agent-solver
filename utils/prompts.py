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


# 분석 에이전트 프롬프트
ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何问题作图分析专家。你的任务是分析几何问题的特点，确定解决问题的最佳作图方法。

请分析以下几何问题:
{problem}

解析要素:
{parsed_elements}

请完成以下分析任务:
1. 确定问题类型：三角形问题、圆问题、角度问题、坐标几何、面积计算等
2. 推荐作图方法：尺规作图、GeoGebra作图等
3. 判断问题的作图类型：
   - 基本作图：基本的点、线、圆等几何元素的作图
   - 特殊作图：特定条件下的几何图形作图
   - 构造作图：根据给定条件构造复杂几何图形
4. 确定需要的作图步骤类型：
   - triangle: 三角形的作图
   - circle: 圆的作图
   - angle: 角度的作图
   - length: 长度的作图
   - area: 面积的作图
   - coordinate: 坐标几何作图
5. 提出作图任务建议，包括：
   - 任务类型（上述六种类型之一）
   - 所需参数
   - 作图步骤之间的依赖关系
6. 判断哪些操作可以直接使用GeoGebra命令完成而无需计算:
   - 两点中点的计算 (可用 Midpoint 命令)
   - 线的交点计算 (可用 Intersect 命令)
   - 角平分线 (可用 AngleBisector 命令)
   - 垂直线/平行线 (可用 Perpendicular/Parallel 命令)
   - 圆的内切/外接 (可用相应的 Circle 命令)

注意: 对于每个suggested_task，请根据具体操作特性设置合适的operation_type，确保如下:
- task_type表示作图步骤的大类别(三角形/圆/角度/长度/面积/坐标)
- operation_type表示具体执行的操作类型(例如midpoint, intersect, angleBisector等)
- 当任务可以通过GeoGebra命令直接实现时，operation_type应与GeoGebra命令相对应
- 同一个task_type可以有不同的operation_type，取决于具体操作
- 对于每个任务，如果存在对应的GeoGebra命令，必须在direct_geogebra_commands中添加对应条目

常见operation_type参考(但不限于):
- midpoint: 中点计算
- intersect: 交点计算
- angleBisector: 角平分线
- perpendicular: 垂线
- parallel: 平行线
- circle: 圆的构造
- polygon: 多边形构造
- segment: 线段
- angle: 角度
- distance: 距离测量
- reflection: 镜像反射
- rotation: 旋转
- translation: 平移

注意: 请提供作图计划的详细推理解释，包括:
- 作图步骤的具体顺序和理由
- 每个步骤如何依赖于前面的步骤
- 为什么这种作图方法是最合适的
- 如何保证构造的正确性

你的输出必须符合以下JSON格式:
{{
  "problem_type": {{
    "triangle": boolean,
    "circle": boolean,
    "angle": boolean,
    "coordinate": boolean,
    "area": boolean,
    "measurement": boolean,
    "proof": boolean,
    "construction": boolean
  }},
  "approach": "作图方法（尺规作图/GeoGebra作图等）",
  "requires_calculation": boolean,
  "calculation_types": {{
    "triangle": boolean,
    "circle": boolean,
    "angle": boolean,
    "length": boolean,
    "area": boolean,
    "coordinate": boolean
  }},
  "reasoning": "分析理由",
  "suggested_tasks_reasoning": "作图计划的详细推理过程",
  "suggested_tasks": [
    {{
      "task_type": "triangle/circle/angle/length/area/coordinate",
      "operation_type": "midpoint/intersect/perpendicular/parallel/angleBisector/etc",
      "parameters": {{
        "param1": "value1",
        "param2": "value2"
      }},
      "dependencies": [],
      "description": "作图步骤描述"
    }}
  ],
  "direct_geogebra_commands": [
    {{
      "operation_type": "midpoint/intersect/perpendicular/parallel/angleBisector/etc",
      "parameters": {{
        "point1": "A",
        "point2": "B"
      }},
      "description": "使用GeoGebra的命令直接实现，无需计算",
      "geogebra_command": "Midpoint(A, B)"
    }}
  ]
}}

仅返回JSON格式的响应，不要添加其他说明或注释。
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

分析输入数据，注意以下几点：
1. 如果提供了具体的坐标和度量值，请使用这些精确值
2. 如果只有问题分析但没有计算结果，需要通过几何关系推断合理的值
3. 如果有计算结果但没有问题分析，请从计算结果中推断问题类型
4. 确保生成的命令是完整的，能够准确表达问题的几何关系
5. 对于不确定的值，使用合理的默认值（如默认半径、默认角度等）

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