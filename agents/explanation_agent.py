from typing import Dict, List, Any, Optional
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from utils.prompts import EXPLANATION_PROMPT
from utils.llm_manager import LLMManager
import json
import re

def explanation_agent(state):
    """
    해설 생성 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        해설이 추가된 상태 객체
    """
    # 도구 생성
    tools = get_explanation_tools()
    
    # LLM 초기화
    llm = LLMManager.get_explanation_llm()
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, EXPLANATION_PROMPT)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 에이전트 실행
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "commands": str(state.geogebra_commands),
        "calculations": str(state.calculations)
    })
    
    # 결과 처리
    explanation = result["output"]
    
    # 상태 업데이트
    state.explanation = explanation
    
    return state

def get_explanation_tools():
    """해설 생성 에이전트용 도구 생성"""
    return [
        StructuredTool.from_function(
            name="explain_key_concepts",
            func=_explain_key_concepts_tool,
            description="解释关键几何概念，提供与问题相关的核心几何概念解释"
        ),
        StructuredTool.from_function(
            name="explain_solution_steps",
            func=_explain_solution_steps_tool,
            description="解释解题步骤，详细解释从问题到解答的每个步骤"
        ),
        StructuredTool.from_function(
            name="provide_educational_insights",
            func=_provide_educational_insights_tool,
            description="提供教育见解，提供学习建议和知识拓展"
        ),
        StructuredTool.from_function(
            name="generate_geogebra_tutorial",
            func=_generate_geogebra_tutorial_tool,
            description="生成GeoGebra使用教程，提供如何在GeoGebra中实现解决方案的指导"
        )
    ]

# === Tool 함수 구현 ===

def _explain_key_concepts_tool(problem_type_json: str, knowledge_points_json: str) -> str:
    """
    핵심 개념 설명 도구
    
    Args:
        problem_type_json: 문제 유형(JSON 문자열)
        knowledge_points_json: 지식 요점(JSON 문자열)
        
    Returns:
        개념 설명(JSON 문자열)
    """
    try:
        problem_type = json.loads(problem_type_json) if isinstance(problem_type_json, str) else problem_type_json
        knowledge_points = json.loads(knowledge_points_json) if isinstance(knowledge_points_json, str) else knowledge_points_json
        
        # 핵심 개념 설명
        result = _explain_key_concepts(problem_type, knowledge_points)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"concepts": {"error": str(e)}, "illustrations": []}, ensure_ascii=False)

def _explain_solution_steps_tool(problem_text: str, commands_json: str, calculations_json: str) -> str:
    """
    해결 단계 설명 도구
    
    Args:
        problem_text: 문제 텍스트
        commands_json: 명령어 목록(JSON 문자열)
        calculations_json: 계산 결과(JSON 문자열)
        
    Returns:
        해결 단계 설명(JSON 문자열)
    """
    try:
        commands = json.loads(commands_json) if isinstance(commands_json, str) else commands_json
        calculations = json.loads(calculations_json) if isinstance(calculations_json, str) else calculations_json
        
        # 해결 단계 설명
        result = _explain_solution_steps(problem_text, commands, calculations)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"steps": [str(e)], "reasoning": []}, ensure_ascii=False)

def _provide_educational_insights_tool(problem_difficulty_json: str, approach_json: str) -> str:
    """
    교육적 인사이트 제공 도구
    
    Args:
        problem_difficulty_json: 문제 난이도(JSON 문자열)
        approach_json: 접근 방법(JSON 문자열)
        
    Returns:
        교육적 인사이트(JSON 문자열)
    """
    try:
        problem_difficulty = json.loads(problem_difficulty_json) if isinstance(problem_difficulty_json, str) else problem_difficulty_json
        approach = json.loads(approach_json) if isinstance(approach_json, str) else approach_json
        
        # 교육적 인사이트 제공
        result = _provide_educational_insights(problem_difficulty, approach)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"insights": [str(e)], "extensions": []}, ensure_ascii=False)

def _generate_geogebra_tutorial_tool(commands_json: str) -> str:
    """
    GeoGebra 튜토리얼 생성 도구
    
    Args:
        commands_json: 명령어 목록(JSON 문자열)
        
    Returns:
        GeoGebra 튜토리얼(JSON 문자열)
    """
    try:
        commands = json.loads(commands_json) if isinstance(commands_json, str) else commands_json
        
        # GeoGebra 튜토리얼 생성
        result = _generate_geogebra_tutorial(commands)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"tutorial_steps": [str(e)], "tips": []}, ensure_ascii=False)

# === 헬퍼 함수 ===

def _explain_key_concepts(problem_type: Dict[str, Any], knowledge_points: List[str]) -> Dict[str, Any]:
    """
    핵심 개념 설명
    
    Args:
        problem_type: 문제 유형
        knowledge_points: 지식 요점
        
    Returns:
        개념 설명
    """
    concepts = {}
    illustrations = []
    
    # 문제 유형에 따른 핵심 개념
    if "triangle" in problem_type:
        concepts["三角形"] = "三角形是由三条线段连接三个点而形成的平面图形。"
        concepts["勾股定理"] = "直角三角形中，两直角边的平方和等于斜边的平方。"
        illustrations.append("三角形内角和为180度")
    
    if "circle" in problem_type:
        concepts["圆"] = "圆是平面上与某定点（圆心）距离相等的所有点的集合。"
        concepts["圆周角"] = "圆周角是由圆上两点与圆上任意第三点所形成的角。"
        illustrations.append("同弧圆周角相等")
    
    if "coordinate" in problem_type:
        concepts["坐标系"] = "坐标系是确定平面或空间中点的位置的参照系。"
        concepts["距离公式"] = "两点间距离公式：d = √[(x₂-x₁)² + (y₂-y₁)²]。"
        illustrations.append("点到直线的距离公式")
    
    # 지식 요점에 따른 추가 개념
    for point in knowledge_points:
        if "相似" in point:
            concepts["相似三角形"] = "相似三角形是对应角相等且对应边成比例的三角形。"
        if "全等" in point:
            concepts["全等三角形"] = "全等三角形是对应角相等且对应边相等的三角形。"
    
    return {
        "concepts": concepts,
        "illustrations": illustrations
    }

def _explain_solution_steps(problem_text: str, commands: List[str], calculations: Dict[str, Any]) -> Dict[str, Any]:
    """
    해결 단계 설명
    
    Args:
        problem_text: 문제 텍스트
        commands: GeoGebra 명령어 목록
        calculations: 계산 결과
        
    Returns:
        해결 단계 설명
    """
    steps = []
    reasoning = []
    
    # 문제 이해
    steps.append("首先，我们需要理解问题的要求和已知条件。")
    if "求" in problem_text:
        target_match = re.search(r'求([^。]+)', problem_text)
        if target_match:
            target = target_match.group(1)
            steps.append(f"问题要求我们求{target}。")
    
    # 계산 단계 추출
    if "steps" in calculations:
        for i, step in enumerate(calculations["steps"], 1):
            steps.append(f"步骤{i}：{step}")
    
    # 명령어 기반 단계 설명
    point_cmds = [cmd for cmd in commands if "Point" in cmd or "=" in cmd and "(" in cmd and "," in cmd]
    if point_cmds:
        steps.append("我们首先在坐标系中确定关键点的位置。")
        
    line_cmds = [cmd for cmd in commands if "Line" in cmd or "Segment" in cmd or "Ray" in cmd]
    if line_cmds:
        steps.append("然后，我们连接相关点构建几何图形。")
        
    circle_cmds = [cmd for cmd in commands if "Circle" in cmd]
    if circle_cmds:
        steps.append("接着，我们构造必要的圆。")
        
    measure_cmds = [cmd for cmd in commands if "Angle" in cmd or "Distance" in cmd or "Area" in cmd]
    if measure_cmds:
        steps.append("最后，我们计算需要的测量值。")
    
    # 추론 설명
    if "三角形" in problem_text:
        reasoning.append("本题涉及三角形的性质。")
        if "直角" in problem_text:
            reasoning.append("利用勾股定理求解直角三角形的边长。")
        elif "等边" in problem_text or "等腰" in problem_text:
            reasoning.append("利用等边/等腰三角形的特殊性质。")
    elif "圆" in problem_text:
        reasoning.append("本题涉及圆的性质。")
        if "切线" in problem_text:
            reasoning.append("利用圆的切线与半径垂直的性质。")
        elif "弧" in problem_text or "弦" in problem_text:
            reasoning.append("利用圆周角和圆心角的关系。")
    elif "坐标" in problem_text:
        reasoning.append("本题涉及坐标几何。")
        reasoning.append("利用坐标公式计算距离和面积。")
    
    return {
        "steps": steps,
        "reasoning": reasoning
    }

def _provide_educational_insights(problem_difficulty: Dict[str, Any], approach: Dict[str, Any]) -> Dict[str, Any]:
    """
    교육적 인사이트 제공
    
    Args:
        problem_difficulty: 문제 난이도
        approach: 접근 방법
        
    Returns:
        교육적 인사이트
    """
    insights = []
    extensions = []
    
    # 난이도에 따른 인사이트
    difficulty_level = problem_difficulty.get("level", "medium")
    if difficulty_level == "easy":
        insights.append("这是一个基础几何问题，适合巩固基本概念。")
    elif difficulty_level == "medium":
        insights.append("这个问题需要综合应用几何知识，适合提升解题能力。")
    else:  # hard
        insights.append("这是一个较为复杂的几何问题，解题需要创造性思维。")
    
    # 접근 방법에 따른 인사이트
    approach_type = approach.get("type", "")
    if "synthetic" in approach_type.lower():
        insights.append("綜合幾何方法培養直觀思維和空間想象能力。")
        extensions.append("嘗試使用坐標方法解決同樣的問題。")
    elif "coordinate" in approach_type.lower():
        insights.append("坐標幾何方法培養數學建模和代數運算能力。")
        extensions.append("嘗試使用綜合幾何方法解決同樣的問題。")
    elif "vector" in approach_type.lower():
        insights.append("向量方法培養抽象思維和代數運算能力。")
        extensions.append("嘗試將問題推廣到三維空間。")
    
    # 일반적인 교육적 인사이트
    insights.append("解决几何问题的关键是理解图形之间的关系。")
    insights.append("多角度思考问题有助于培养数学思维的灵活性。")
    
    # 확장 학습 제안
    extensions.append("尝试改变题目条件，探索解的变化。")
    extensions.append("探索更一般的情况，寻找规律。")
    
    return {
        "insights": insights,
        "extensions": extensions
    }

def _generate_geogebra_tutorial(commands: List[str]) -> Dict[str, Any]:
    """
    GeoGebra 튜토리얼 생성
    
    Args:
        commands: GeoGebra 명령어 목록
        
    Returns:
        GeoGebra 튜토리얼
    """
    tutorial_steps = []
    tips = []
    
    # 기본 안내
    tutorial_steps.append("打开GeoGebra软件，确保显示代数视图和图形视图。")
    tutorial_steps.append("在GeoGebra中，我们可以通过输入栏输入命令，或使用工具栏中的工具。")
    
    # 명령어 그룹화 및 단계별 설명
    point_cmds = [cmd for cmd in commands if "Point" in cmd or "=" in cmd and "(" in cmd and "," in cmd]
    if point_cmds:
        tutorial_steps.append("首先，创建所需的点：")
        for cmd in point_cmds:
            tutorial_steps.append(f"  - 在输入栏中输入：{cmd}")
    
    line_cmds = [cmd for cmd in commands if "Line" in cmd or "Segment" in cmd or "Ray" in cmd]
    if line_cmds:
        tutorial_steps.append("接下来，创建线段或直线：")
        for cmd in line_cmds:
            tutorial_steps.append(f"  - 在输入栏中输入：{cmd}")
    
    circle_cmds = [cmd for cmd in commands if "Circle" in cmd]
    if circle_cmds:
        tutorial_steps.append("然后，创建圆：")
        for cmd in circle_cmds:
            tutorial_steps.append(f"  - 在输入栏中输入：{cmd}")
    
    measure_cmds = [cmd for cmd in commands if "Angle" in cmd or "Distance" in cmd or "Area" in cmd]
    if measure_cmds:
        tutorial_steps.append("最后，添加测量：")
        for cmd in measure_cmds:
            tutorial_steps.append(f"  - 在输入栏中输入：{cmd}")
    
    # 유용한 팁
    tips.append("可以使用鼠标右键点击对象，在上下文菜单中更改对象属性（如颜色、线型等）。")
    tips.append("使用视图菜单可以显示或隐藏坐标轴和网格。")
    tips.append("可以使用移动工具拖动点，观察图形的变化。")
    tips.append("按Ctrl+Z可以撤销操作，按Ctrl+Y可以重做操作。")
    tips.append("可以使用文件菜单保存和导出您的作品。")
    
    return {
        "tutorial_steps": tutorial_steps,
        "tips": tips
    } 