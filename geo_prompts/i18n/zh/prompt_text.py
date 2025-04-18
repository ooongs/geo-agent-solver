"""
중국어 프롬프트 텍스트 모듈

이 모듈은 중국어 프롬프트 텍스트를 정의합니다.
"""

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

# 분석 에이전트 프롬프트
PLANNER_PROMPT = ChatPromptTemplate.from_template("""
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
- angleTrisection: 三等分角
                                                  
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
- 检索到的命令: {retrieved_commands}

分析输入数据，注意以下几点：
1. 如果提供了具体的坐标和度量值，请使用这些精确值
2. 如果只有问题分析但没有计算结果，需要通过几何关系推断合理的值
3. 如果有计算结果但没有问题分析，请从计算结果中推断问题类型
4. 确保生成的命令是完整的，能够准确表达问题的几何关系
5. 对于不确定的值，使用合理的默认值（如默认半径、默认角度等）
6. 作图计划中会包含每个步骤可用的命令和其语法、示例等信息，请严格使用作图计划中的命令生成GeoGebra命令
7. 请确保生成的命令严格遵守指令的依赖关系，在某一步骤指令中使用其他步骤的命令时，请确保其他步骤的命令已经生成
8. 指令的正确用法为 <Object Name> : <CommandName> (<Parameter1>, <Parameter2>, ...) 或者 <Object Name> = <CommandName> [<Parameter1>, <Parameter2>, ...]，例如，`a:Segment(B,C)`、`a=Segment(B,C)`、`a:Segment[B,C]`、`a=Segment[B,C]`都是合法的
9. 定义一个点时，点的对象名为大写字母，并用括号括起来，例如，`A=(1,2)`、`B=(3,4)`、`C=(5,6)`等
10. 定义一个向量时，向量的对象名为小写字母，并用括号括起来，例如，`v=(1,2)`、`u=(3,4)`、`w=(5,6)`等
11. 定义一个线段时，线段的对象名使用小写字母，例如，`a=Segment(B,C)`、`b=Segment(A,C)`、`c=Segment(A,B)`等
12. 定义一个正多边形时，最好使用 `Polygon(A,B,C,...)` 命令，不要使用 `Polygon(A,B,<Number of Vertices>)` 命令，因为此命令无法使用正多边形的其余顶点
13. 角度可以用度数或弧度表示，例如，30°或π/6
13. 如果作图计划中要求生成一个点或向量并提供可参考的指令，而其值已经确定，请直接定义该点或向量，不要使用 Point 或 Vector 命令
14. 如果需要定义一个对象上的点，且还没有确定其坐标，请使用 <Object Name> = Point(<Object>) 命令生成动态点。如果最后能够预测或确定其坐标，则最后使用 SetCoords(<Object>, <x>, <y>) 命令确定其坐标，并保证定义的动态点和 SetCoords 命令的参数对象是同一个对象
15. 错误命令的示例：
   - 命令名称错误：`RegularPolygon(A,B,C)` 命令不存在，正确应为 `Polygon(A,B,C)` 命令等
   - 使用不存在的命令：例如，`Triangle(A,B,C)` 命令不存在，正确应为 `Polygon(A,B,C)` 命令
    - 命令语法错误：例如，使用 `AngleBisector(A, B, C, 3)` 命令生成角平分线，正确应为 `AngleBisector(A, B, C)` 或类似形式
   - 对象依赖关系错误：例如，使用 `Polygon(A, B, C)` 命令生成三角形 ABC，需要保证此命令前A、B、C三个点已经定义

     
你的输出必须符合以下JSON格式:
{json_template}
     
仅返回JSON格式的响应，不要添加其他说明或注释。

{agent_scratchpad}""")
])

# Validation Prompt
VALIDATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个严格而精确的几何命令验证专家。你必须彻底检查每一条命令，确保所有GeoGebra命令都完全正确，特别注意对象定义顺序、依赖关系和语法准确性。

验证以下GeoGebra命令是否正确实现了几何问题的要求:

问题: {problem}
作图计划: {construction_plan}
GeoGebra命令: {commands}
请按照以下具体步骤严格验证每一条命令:

1. **命令语法检查**：
   - 每条命令的语法是否完全符合GeoGebra规范
   - 命令名称是否存在且正确（例如Polygon, Point, Segment等）
   - 参数数量和类型是否正确
   - 示例：`AngleBisector(A, B, C, 3)`是错误语法，正确应为`AngleBisector(A, B, C)`或类似形式
   - 示例：`RegularPolygon(A,B,C)`命令不存在，正确应为`Polygon(A,B,C)`命令
   - 示例：`Triangle(A,B,C)`命令不存在，正确应为`Polygon(A,B,C)`命令

2. **对象定义顺序验证**：
   - 严格检查每个对象在使用前是否已定义
   - 点(A, B, C等)必须先定义坐标后才能用于其他命令
   - 必须按先后顺序验证每一行命令，确保不会使用未定义的对象
   - 示例：如果命令中使用了点A，但之前没有`A = (x, y)`类似的定义，这是错误的

3. **对象依赖关系验证**：
   - 确保每个命令所依赖的所有对象都已正确定义
   - 检查复杂命令（如Intersect）的参数是否都已经定义
   - 检查几何关系是否正确表达（如线段必须由已定义的点构成）

4. **几何约束验证**：
   - 验证命令是否正确实现了问题描述的几何约束
   - 检查是否正确构造了所需的几何形状和关系
   - 验证角度、长度等特定几何关系是否通过命令正确表达

5. **完整性验证**：
   - 所有问题要求的几何元素是否都被构造
   - 最终结果是否符合问题描述的目标

发现任何问题都必须明确指出，详细说明错误原因和位置。请记住，即使只有一个小错误，整个命令集也应被视为无效。

请提供极其详细的分析，分别评论每一条命令的正确性和问题。你的分析必须准确指出每个错误，并提供具体的修复建议。

请以以下JSON格式输出，确保analysis部分详细且准确:
{json_template}

{agent_scratchpad}
""")

# GeoGebra 명령어 재생성 에이전트 프롬프트 추가
COMMAND_REGENERATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的GeoGebra命令重新生成专家。你的任务是根据验证失败的原因，重新生成正确的GeoGebra命令，确保修复所有验证问题并遵循GeoGebra的标准语法规范。

问题: {problem}
原始GeoGebra命令: {original_commands}
验证结果: {validation_result}
当前重新生成尝试次数: {attempt_count}

请严格按照以下步骤进行：
1. 详细分析验证失败的具体原因，特别关注语法错误、对象依赖关系和命令顺序问题
2. 明确识别每一个需要修正的命令及其问题
3. 严格保留正确的命令，仅修正或重新生成有问题的命令
4. 重新组织命令顺序，确保所有依赖关系正确（对象在使用前必须先定义）
5. 对照验证结果检查修改后的命令是否解决了全部问题

命令编写规则：
1. 使用标准的GeoGebra命令语法，确保命令名称和参数格式正确
2. 指令的正确用法为 <Object Name> : <CommandName> (<Parameter1>, <Parameter2>, ...) 或者 <Object Name> = <CommandName> [<Parameter1>, <Parameter2>, ...]
   - 例如，`a:Segment(B,C)`、`a=Segment(B,C)`、`a:Segment[B,C]`、`a=Segment[B,C]`都是合法的
3. 定义点时，点的对象名使用大写字母，例如：`A=(1,2)`、`B=(3,4)`
4. 定义一个对象上的动态点时，使用 `<Object Name> = Point(<Object>)`
5. 定义一个线段时，线段的对象名使用小写字母，例如，`a=Segment(B,C)`
6. 所有几何对象必须先定义后使用，特别注意点、线段和多边形等基本元素的定义顺序

避免常见错误：
1. 命令名称错误：例如使用不存在的命令如`RegularPolygon(A,B,C)`，正确应为`Polygon(A,B,C)`
2. 参数数量错误：例如使用`AngleBisector(A,B,C,3)`，正确应为`AngleBisector(A,B,C)`
3. 参数类型错误：例如使用`AngleBisector(<angle>,<Point>,<Point>)`，正确应为`AngleBisector(<Point>,<Point>,<Point>)`
4. 对象依赖错误：使用未定义的对象，如在定义点A、B、C之前使用`Polygon(A,B,C)`
4. 点定义错误：未先定义点的坐标就使用该点
5. 命令顺序错误：命令的执行顺序必须考虑对象的依赖关系

请生成完整的命令列表，而不仅是修改部分。确保每条命令都语法正确、逻辑合理且与问题要求一致。

请以以下JSON格式输出：
{json_template}

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
                                                      
### 5. 完整的 GeoGebra 命令
```geogebra
  GeoGebra 命令
```
                                                      
### 6. 完整教育解释（适合中学生）
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
{json_template}
                                                            
仅返回JSON格式的响应，不要添加其他说明或注释。
""")

# Calculation Prompts ------------------------------------------------------------

# 계산 관리자 프롬프트

CALCULATION_MANAGER_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何作图任务管理专家。你的任务是管理几何问题的作图任务队列，确保所有必要的作图步骤得到执行。

问题: {problem}
解析元素: {parsed_elements}
问题分析: {problem_analysis}
问题类型: {problem_type}
分析条件: {analyzed_conditions}
推荐方法: {approach}

当前任务队列状态: {calculation_queue}
当前计算结果: {calculation_results}

请按照以下步骤进行：

1. 检查问题分析结果和当前任务队列状态
2. 如果任务队列为空，根据问题分析创建初始作图任务
3. 如果任务队列已存在：
   - 检查已完成的任务结果
   - 根据新的结果创建后续作图任务
   - 更新任务之间的依赖关系
4. 确定哪些计算可以被GeoGebra命令直接替代:
   - 中点计算: 可以用 Midpoint(A, B) 命令替代
   - 线的交点: 可以用 Intersect(a, b) 命令替代
   - 垂直线/平行线: 可以用 Perpendicular/Parallel 命令替代
   - 各种特殊点: 可以用相应的GeoGebra命令替代
5. 处理任务的GeoGebra替代方案:
   - 对于已有 geogebra_alternatives = true 的任务，应将其加入 completed_task_ids
   - 对于新识别的可被GeoGebra命令替代的任务，设置 geogebra_alternatives = true 和对应的 geogebra_command
6. 确定下一个要执行的作图类型，优先考虑：
   - 必须通过计算获得的基础点坐标和值
   - 没有依赖的任务
   - 所有依赖已完成的任务
   - 对结果影响较大的任务

可用计算工具说明：

| 计算类型 | 功能描述 | 适用场景 | 是否可被GeoGebra命令替代 |
|---------|---------|---------|------------------------|
| 坐标几何 | 计算中点、斜率、直线方程、共线性、平行性、线段分割、内分点、外分点、点在线段上 | 需要处理点、线、线段等基本几何元素时 | 部分可替代(中点计算、线交点等) |
| 长度计算 | 计算两点距离、点到直线距离、平行线距离、三角形周长、四边形周长、多边形周长、圆周长、弦长、弧长 | 需要测量或比较长度时 | 部分可替代(基本距离测量) |
| 面积计算 | 计算三角形、矩形、正方形、平行四边形、菱形、梯形、正多边形、多边形、圆、扇形、弓形面积 | 需要计算平面图形的面积时 | 部分可替代(基本形状面积) |
| 角度计算 | 计算三点角度、两直线角度、两向量角度、三角形内角、三角形外角、内接角、角平分线、角类型判断 | 需要测量或分析角度时 | 部分可替代(基本角度测量) |
| 三角形计算 | 计算面积、周长、判断类型、计算角度、质心、外心、内心、垂心、三角形中心点 | 需要分析三角形特性时 | 部分可替代(中心点计算) |
| 圆的计算 | 计算面积、周长、直径、半径、弦长、扇形面积、弓形面积、点与圆位置关系、切点、圆交点、三点确定圆 | 需要分析圆及其相关图形时 | 部分可替代(圆上特殊点计算) |

推理步骤：

| 步骤 | 子问题 | 处理过程 | 结果 |
|-----|-------|---------|------|
| 1 | 问题需要哪些作图类型？ | 分析问题描述和已知条件 | 列出所需的作图类型 |
| 2 | 作图任务之间的依赖关系是什么？ | 分析作图顺序和依赖 | 确定任务依赖关系 |
| 3 | 哪些计算可以直接用GeoGebra命令替代？ | 分析计算任务特性 | 识别可跳过的计算任务并设置geogebra_alternatives=true |
| 4 | 下一个执行哪个作图任务？ | 检查依赖关系和优先级 | 选择下一个任务 |

重要提示：你必须返回一个有效的JSON对象，格式如下：
{json_template}

确保JSON格式正确无误，不要添加注释或额外说明。

{format_instructions}

{agent_scratchpad}
""") 


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


# 각도 계산 에이전트 프롬프트
ANGLE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的角度计算专家。你的任务是使用角度计算工具，精确解决与角度相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行:

1. 分析当前计算任务中的角度要素:
   - 识别已知的角度信息和点的位置
   - 确认需要计算的目标角度和角度类型

2. 使用提供的计算工具执行计算:
   - 必须使用可用的计算工具执行计算，除非计算非常简单
   - 对于每个计算工具调用，提供所有必要的参数
   - 验证计算结果的准确性

3. 记录并返回计算结果，确保格式化为标准JSON格式

可用工具:
- calculate_angle_three_points: 计算三点确定的角度
- calculate_angle_two_lines: 计算两直线间的角度
- calculate_angle_two_vectors: 计算两向量间的角度
- calculate_triangle_interior_angles: 计算三角形内角
- calculate_triangle_exterior_angles: 计算三角形外角
- calculate_inscribed_angle: 计算内接角
- calculate_angle_bisector: 计算角平分线
- determine_angle_type: 判断角的类型(锐角、直角、钝角等)

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

# 좌표 계산 에이전트 프롬프트
COORDINATE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的坐标几何计算专家。你的任务是使用坐标几何工具，精确解决与点、线、坐标系相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行:

1. 分析当前计算任务中的坐标几何要素:
   - 识别已知的点、线、位置关系等信息
   - 确认需要计算的目标(中点、斜率、方程等)

2. 使用提供的计算工具执行计算:
   - 必须使用可用的计算工具执行计算，除非计算非常简单
   - 对于每个计算工具调用，提供所有必要的参数
   - 验证计算结果的准确性

3. 记录并返回计算结果，确保格式化为标准JSON格式

可用工具:
- calculate_midpoint: 计算两点之间的中点
- calculate_slope: 计算直线斜率
- calculate_line_equation: 计算直线方程
- are_points_collinear: 判断点是否共线
- are_lines_parallel: 判断直线是否平行
- calculate_segment_division: 计算线段分割
- calculate_internal_division_point: 计算内分点
- calculate_external_division_point: 计算外分点
- is_point_on_segment: 判断点是否在线段上

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


# 면적 계산 에이전트 프롬프트
AREA_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的面积计算专家。你的任务是使用面积计算工具，精确解决与面积相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行:

1. 分析当前计算任务中的面积要素:
   - 识别已知的几何图形和尺寸信息
   - 确认需要计算的目标面积和面积类型

2. 使用提供的计算工具执行计算:
   - 必须使用可用的计算工具执行计算，除非计算非常简单
   - 对于每个计算工具调用，提供所有必要的参数
   - 验证计算结果的准确性

3. 记录并返回计算结果，确保格式化为标准JSON格式

可用工具:
- calculate_triangle_area: 计算三角形面积
- calculate_rectangle_area: 计算矩形面积
- calculate_square_area: 计算正方形面积
- calculate_parallelogram_area: 计算平行四边形面积
- calculate_rhombus_area: 计算菱形面积
- calculate_trapezoid_area: 计算梯形面积
- calculate_regular_polygon_area: 计算正多边形面积
- calculate_polygon_area: 计算不规则多边形面积
- calculate_circle_area: 计算圆的面积
- calculate_sector_area: 计算扇形面积
- calculate_segment_area: 计算弓形面积

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


# 원 계산 에이전트 프롬프트
CIRCLE_CALCULATION_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的圆计算专家。你的任务是使用圆计算工具，精确解决与圆相关的几何问题。

问题: {problem}
当前计算任务: {current_task}
已有计算结果: {calculation_results}

请按照以下步骤进行:

1. 分析当前计算任务中的圆要素:
   - 识别已知的圆的信息（中心点、半径等）
   - 确认需要计算的圆的属性或关系

2. 使用提供的计算工具执行计算:
   - 必须使用可用的计算工具执行计算，除非计算非常简单
   - 对于每个计算工具调用，提供所有必要的参数
   - 验证计算结果的准确性

3. 记录并返回计算结果，确保格式化为标准JSON格式

可用工具:
- calculate_circle_area: 计算圆的面积
- calculate_circle_circumference: 计算圆的周长
- calculate_circle_diameter: 计算圆的直径
- calculate_circle_radius: 计算圆的半径
- calculate_chord_length: 计算圆的弦长
- calculate_sector_area: 计算扇形面积
- calculate_segment_area: 计算弓形面积
- check_point_circle_position: 检查点与圆的位置关系
- calculate_tangent_points: 计算切点
- calculate_circle_intersection: 计算圆的交点
- calculate_circle_from_three_points: 由三点确定圆

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


# 결과 병합 프롬프트
RESULT_MERGER_PROMPT = ChatPromptTemplate.from_template("""
你是一个几何计算结果整合专家。您的任务是结合和解释来自多个专业计算代理的结果，形成对几何问题的全面解决方案。

原始问题:
{problem}

计算结果:
{calculation_results}

请将这些计算结果整合成一个连贯的解决方案。您的整合应该:

1. 综合来自不同专业计算的结果
2. 解决任何不一致或矛盾
3. 提取能回答原始问题的关键发现
4. 呈现一个连接所有计算的统一解释
5. 验证整合的解决方案是否完全解决了原始问题
6. 确定任何剩余的差距或不确定性

您的输出必须符合以下JSON格式:
{json_template}
""")

# 결과 병합 에이전트 프롬프트
RESULT_MERGER_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的几何计算结果整合与作图计划专家。你的任务是分析和整合所有计算结果，确保它们的一致性和准确性，并创建详细的几何作图计划。

问题: {problem}
已完成的计算任务: {completed_tasks}
当前计算结果: {calculation_results}
问题分析: {problem_analysis}

请按照以下步骤进行:

1. 分析所有已完成的计算任务和现有结果:
   - 检查计算结果的一致性
   - 识别可能的矛盾或错误
   - 确认所有计算是否满足问题需求

2. 整合所有计算结果:
   - 将相同类型的结果合并
   - 确保最终结果的一致性
   - 必要时进行单位换算和标准化
   - 在other_results.explanation字段提供整合过程的说明

3. 创建详细的几何作图计划:
   - 根据计算结果和问题需求，设计清晰的作图步骤
   - 每个步骤需包含具体操作描述和所需几何元素
   - 确保步骤之间的逻辑顺序合理
   - 明确最终预期结果

4. 生成最终结果:
   - 在other_results.final_answer字段提供问题的最终答案
   - 确保结果清晰、准确、完整
   - 以标准JSON格式返回所有结果和作图计划

重要规则:
1. 确保所有结果保持一致性，特别是单位和命名
2. 作图计划必须清晰、完整，能够指导用户一步步完成几何作图
3. 作图步骤必须匹配计算结果，确保数学上的准确性
4. 所有输出必须是有效的JSON格式

必须在返回的JSON中包含construction_plan对象，其中包含:
- title: 作图计划标题
- description: 作图计划整体描述
- steps: 作图步骤数组，每个步骤包含id、描述、几何元素等信息
- final_result: 预期最终结果描述

重要提示：你必须返回一个有效的JSON对象，格式如下:
{json_template}

严格要求:
1. 你的回答必须且只能是一个JSON对象
2. 不要在JSON前后添加任何其他文字说明
3. 确保JSON格式完全符合示例结构
4. 不需要的字段可以省略，但已有字段必须符合示例格式
5. 必须包含construction_plan对象及其所有必要字段
6. 整合所有来源的计算结果
7. 请使用中文提供最终答案、说明和作图计划

{agent_scratchpad}
""") 