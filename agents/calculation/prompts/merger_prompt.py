"""
결과 병합 에이전트 프롬프트 모듈

이 모듈은 결과 병합 에이전트에서 사용하는 프롬프트를 정의합니다.
"""

from langchain_core.prompts import ChatPromptTemplate


MERGER_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},
  "lengths": {"AB": 5.0, "BC": 7.0, ...},
  "angles": {"ABC": 60.0, "BCD": 45.0, ...},
  "areas": {"triangle_ABC": 25.0, ...},
  "perimeters": {"triangle_ABC": 20.0, ...},
  "special_points": {"centroid": [x, y], "orthocenter": [x, y], ...},
  "circle_properties": {"radius": 5.0, "center": [x, y], ...},
  "ratios": {"AB:BC": 2.5, ...},
  "other_results": {
    "final_answer": "三角形ABC的面积为25平方单位",
    "explanation": "通过计算三角形ABC的各边长度和角度，确定这是一个3-4-5的直角三角形，面积为25平方单位"
  }
}
'''

# 결과 병합 에이전트 프롬프트
RESULT_MERGER_PROMPT = ChatPromptTemplate.from_template("""
你是一个专业的几何计算结果整合专家。你的任务是分析和整合多个计算结果，确保它们的一致性和准确性，并提供最终的综合结果。

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

3. 生成最终结果:
   - 在other_results.final_answer字段提供问题的最终答案
   - 确保结果清晰、准确、完整
   - 以标准JSON格式返回所有结果

重要规则:
1. 确保所有结果保持一致性，特别是单位和命名
2. 如发现矛盾结果，进行分析并选择最可靠的结果
3. 所有输出必须是有效的JSON格式
4. 必须在other_results.final_answer中提供问题的最终答案
5. 将整合过程的说明放在other_results.explanation字段中

重要提示：你必须返回一个有效的JSON对象，格式如下:
{json_template}

严格要求:
1. 你的回答必须且只能是一个JSON对象
2. 不要在JSON前后添加任何其他文字说明
3. 确保JSON格式完全符合示例结构
4. 不需要的字段可以省略，但已有字段必须符合示例格式
5. JSON对象内不允许有注释
6. 整合所有来源的计算结果
7. 请使用中文提供最终答案和说明

{agent_scratchpad}
""") 