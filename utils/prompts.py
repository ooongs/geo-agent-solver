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
7. 确定问题适合的作图方法：尺规作图、GeoGebra作图、坐标几何作图、解析几何作图等

您的输出必须符合以下JSON格式:
{format_instructions}
""")

ANALYSIS_JSON_TEMPLATE = '''
{
  "requires_calculation": boolean,
  "calculation_types": {
    "triangle": boolean,
    "circle": boolean,
    "angle": boolean,
    "length": boolean,
    "area": boolean,
    "coordinate": boolean
  },
  "reasoning": "分析理由",
  "suggested_tasks_reasoning": "作图计划的详细推理过程",
  "suggested_tasks": [
    {
      "task_type": "triangle/circle/angle/length/area/coordinate",
      "operation_type": "midpoint/intersect/perpendicular/parallel/angleBisector/etc",
      "parameters": {
        "param1": "value1",
        "param2": "value2"
      },
      "dependencies": [],
      "description": "作图步骤描述",
      "geogebra_alternatives": boolean,
      "geogebra_command": "对应的GeoGebra命令（如果可替代）"
    }
  ],
  "construction_plan": {
    "title": "作图计划标题",
    "description": "作图计划整体描述",
    "steps": [
      {
        "step_id": "step_1",
        "description": "步骤描述",
        "task_type": "point_construction/line_construction/etc",
        "geometric_elements": ["A", "B", "Line_AB"],
        "command_type": "Point/Line/Segment/etc",
        "parameters": {
          "param1": "value1"
        }
      }
    ],
    "final_result": "预期最终结果"
  }
}
'''


# 분석 에이전트 프롬프트
ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何问题作图分析专家。你的任务是分析几何问题的特点，确定解决问题的最佳作图方法。
注意：解析元素中已包含problem_type和approach的分析结果，请优先考虑这些已有的分析结果。

请分析以下几何问题:
{problem}

解析要素:
{parsed_elements}

请完成以下分析任务:
1. 判断问题的作图类型：
   - 基本作图：基本的点、线、圆等几何元素的作图
   - 特殊作图：特定条件下的几何图形作图
   - 构造作图：根据给定条件构造复杂几何图形
2. 提出作图任务建议，包括：
   - 任务类型（triangle/circle/angle/length/area/coordinate 等）
   - 所需参数
   - 作图步骤之间的依赖关系
3. 判断哪些操作可以直接使用GeoGebra命令完成而无需计算:
   - 两点中点的计算 (可用 Midpoint 命令)
   - 线的交点计算 (可用 Intersect 命令)
   - 角平分线 (可用 AngleBisector 命令)
   - 垂直线/平行线 (可用 Perpendicular/Parallel 命令)
   - 圆的内切/外接 (可用相应的 Circle 命令)
   - 将可以直接用GeoGebra命令替代的任务添加geogebra_alternatives=true标记和geogebra_command属性
4. 判断是否需要使用计算工具并在 reasoning 中详细说明:
   - 如果问题需要以下计算工具处理，则 requires_calculation 为 True，需要提供suggested_tasks，不提供 construction_plan:
     * triangle_calculation_agent: 复杂三角形关系计算
     * circle_calculation_agent: 复杂圆相关计算
     * angle_calculation_agent: 复杂角度关系计算
     * length_calculation_agent: 复杂长度和距离计算
     * area_calculation_agent: 复杂面积计算
     * coordinate_calculation_agent: 复杂坐标转换和计算
   - 如果问题需要计算工具处理，则确定需要的计算类型 task_type：
     * triangle: 三角形相关计算
     * circle: 圆相关计算
     * angle: 角度相关计算
     * length: 长度相关计算
     * area: 面积相关计算
     * coordinate: 坐标几何计算 
   - 如果所有操作都可以通过GeoGebra命令直接完成，则 requires_calculation 为 False， 需要提供 construction_plan，不需要提供 suggested_tasks

                                                   
注意: 对于每个suggested_task，请根据具体操作特性设置合适的operation_type，确保如下:
- task_type表示计算步骤的大类别(三角形/圆/角度/长度/面积/坐标)
- operation_type表示具体执行的操作类型(例如midpoint, intersect)
- 当任务可以通过GeoGebra命令直接实现时，应当设置geogebra_alternatives=true并提供geogebra_command
- 同一个task_type可以有不同的operation_type，取决于具体操作

常见operation_type参考(但不限于):
- midpoint: 中点计算
- intersect: 交点计算
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
{json_template}

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
- 问题分析: {problem_analysis}
- 作图计划: {construction_plan}
- 计算结果: {calculations}

分析输入数据，注意以下几点：
1. 如果提供了具体的坐标和度量值，请使用这些精确值
2. 如果只有问题分析但没有计算结果，需要通过几何关系推断合理的值
3. 如果有计算结果但没有问题分析，请从计算结果中推断问题类型
4. 确保生成的命令是完整的，能够准确表达问题的几何关系
5. 对于不确定的值，使用合理的默认值（如默认半径、默认角度等）
6. 作图计划中会包含每个步骤可用的命令和其语法、示例等信息，请严格使用作图计划中的命令生成GeoGebra命令
7. 请确保生成的命令严格遵守指令的依赖关系，在某一步骤指令中使用其他步骤的命令时，请确保其他步骤的命令已经生成
8. 指令的正确用法为 <Object Name> : <CommandName> (<Parameter1>, <Parameter2>, ...) 或者 <Object Name> = <CommandName> [<Parameter1>, <Parameter2>, ...]，例如，a:Segment(B,C)、a=Segment(B,C)、a:Segment[B,C]、a=Segment[B,C]都是合法的
9. 定义一个点时，点的对象名为大写字母，并用括号括起来，例如，A=(1,2)，B=(3,4)，C=(5,6)等
10. 定义一个向量时，向量的对象名为小写字母，并用括号括起来，例如，v=(1,2)，u=(3,4)，w=(5,6)等
11. 如果作图计划中要求生成一个点或向量并提供可参考的指令，而其值已经确定，请直接定义该点或向量，不要使用 Point 或 Vector 命令
12. 如果需要定义一个对象上的点，且还没有确定其坐标，请使用 <Object Name> = Point(<Object>) 命令生成动态点。如果最后能够预测或确定其坐标，则最后使用 SetCoords(<Object>, <x>, <y>) 命令确定其坐标，并保证定义的动态点和 SetCoords 命令的参数对象是同一个对象

     
你的输出必须符合以下JSON格式:
{{
  "commands": [ "GeoGebra命令1", "GeoGebra命令2", ... ],
  "explanation": "命令生成的解释（1.第一个命令的解释，\n 2.第二个命令的解释，\n ...）"
}}
仅返回JSON格式的响应，不要添加其他说明或注释。

{agent_scratchpad}""")
])

# 검증 에이전트 프롬프트
VALIDATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何命令验证专家。你可以使用提供的工具来检查命令语法、验证对象定义和问题约束。

验证以下GeoGebra命令是否正确实现了几何问题的要求:

问题: {problem}
作图计划: {construction_plan}
GeoGebra命令: {commands}

请按照以下步骤进行：
1. 检查命令语法（如果使用了作图计划中提供的 retrieved_commands 的命令，需要考虑是否满足作图计划中提供的 retrieved_commands 的约束）
2. 验证对象定义（Point、Line、Segment、Angle、Circle、Polygon等对象的定义是否正确）
3. 验证命令依赖关系（保证命令的变量已经定义，例如，使用 Polygon(A,B,C) 命令生成三角形 ABC，需要保证此命令前A、B、C三个点已经定义）
4. 验证问题约束
5. 如果发现问题，提出修复建议
6. 给出最终的验证结果和改进建议

若生成的命令无误，则is_valid为True，否则为False

注意：验证过程应该考虑通用性，不要依赖于特定的点名称或图形名称。
                                                     

请以以下JSON格式输出：
{{
  "analysis": "对验证结果的分析（用 Markdown 格式，详细分析）",
  "is_valid": boolean,
  "errors": ["错误1", "错误2", ...] // 从验证结果中提取的错误信息
  "warnings": ["警告1", "警告2", ...] // 从验证结果中提取的警告信息
  "suggestions": ["建议1", "建议2", ...] // 从验证结果中提取的建议信息
}}
{agent_scratchpad}
""")

# GeoGebra 명령어 재생성 에이전트 프롬프트 추가
COMMAND_REGENERATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个GeoGebra命令重新生成专家。你的任务是根据验证失败的原因，重新生成正确的GeoGebra命令。

问题: {problem}
作图计划: {construction_plan}
原始GeoGebra命令: {original_commands}
验证结果: {validation_result}
当前重新生成尝试次数: {attempt_count}

请按照以下步骤进行：
1. 分析验证失败的具体原因
2. 识别需要修正的命令
3. 保留正确的命令，修正或重新生成有问题的命令
4. 确保命令的顺序逻辑正确，依赖关系明确
5. 检查生成的命令是否解决了验证中指出的所有问题

注意：
- 保持命令简洁明了
- 确保命令间的依赖关系正确
- 避免之前命令中出现的错误
- 必须生成完整的命令列表，而不仅是修改部分
- 适当调整命令顺序，确保前面的命令不依赖后面尚未定义的对象

请以以下JSON格式输出：
{{
  "analysis": "对验证失败原因的分析（用 Markdown 格式，详细分析）",
  "fixed_issues": ["修复的问题1", "修复的问题2", ...],
  "commands": ["GeoGebra命令1", "GeoGebra命令2", ...]
}}

{agent_scratchpad}
""")

# 해설 생성 에이전트 프롬프트
EXPLANATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何教育专家，需要生成详细的解题解释。请使用以下信息创建一个结构化的教学说明：

问题: {problem}
几何元素: {parsed_elements}
问题分析: {problem_analysis}
解题方法: {approach}
计算过程: {calculations}
GeoGebra命令: {geogebra_commands}
验证结果: {validation}

请按照以下Markdown格式生成一个全面且教育性强的解释：

### 1. 解释问题中的关键几何概念
(解释问题涉及的主要几何概念，如三角形、圆、角度等，结合问题特点进行针对性解释)

### 2. 详细解释解题过程
(按照逻辑顺序解释解题步骤，从已知条件到求解目标，展示思维过程)

### 3. 提供教育见解
(分析此类问题的学习价值，提供学习建议和思维方法)

### 4. 生成GeoGebra使用教程
(解释如何使用GeoGebra工具验证或探索此问题)

### 5. 完整教育解释（适合中学生）
(整合以上内容，提供一个完整、易懂的解释，适合中学生学习理解)

注意：
- 解释应该清晰易懂，适合中学生水平
- 使用适当的数学术语和精确表达
- 鼓励学生思考和探索
- 必须使用Markdown格式组织内容，确保层次分明
- 根据问题难度调整解释的深度和广度
- 必要时引用问题分析和计算过程中的关键信息
""") 

# 명령어 선택 에이전트 프롬프트
COMMAND_SELECTION_PROMPT = ChatPromptTemplate.from_template("""
请为以下几何作图步骤选择最合适的GeoGebra命令。
{reranker_agent_input}

请分析每个命令的语法、描述和示例，选择最适合该作图步骤的命令。请考虑：
1. 命令的功能是否与作图步骤的要求一致
2. 命令的几何元素是否与步骤中的几何元素匹配
3. 命令的复杂度和易用性
4. 命令的评分（越高越好）

请以以下格式输出您的选择：
{{
  "selected_commands": [
    {{"step_id": <步骤ID>, "command_id": <命令ID>, "reason": "<选择理由>", "command_syntax": "<命令语法>"}},
    {{"step_id": <步骤ID>, "command_id": <命令ID>, "reason": "<选择理由>", "command_syntax": "<命令语法>"}},
    ...
  ]
}}
仅返回JSON格式的响应，不要添加其他说明或注释。
""")