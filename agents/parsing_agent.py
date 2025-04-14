from typing import Dict, Any, List, Optional, Type, TypedDict
from langchain_openai import ChatOpenAI
from utils.prompts import PARSING_PROMPT
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import re
from config import DEFAULT_MODEL
from utils.llm_manager import LLMManager

# 출력 구조 정의
class GeometricObject(BaseModel):
    type: str = Field(description="几何对象的类型 (point, line, circle, triangle 等)")
    vertices: Optional[List[str]] = Field(None, description="多边形的顶点")
    center: Optional[str] = Field(None, description="圆的中心点")
    radius: Optional[float] = Field(None, description="圆的半径")
    points: Optional[List[str]] = Field(None, description="定义对象的点")

class Relation(BaseModel):
    type: str = Field(description="关系类型 (segment, parallel, perpendicular 等)")
    elements: Optional[List[str]] = Field(None, description="相关的元素")
    length: Optional[float] = Field(None, description="线段长度")
    target: Optional[bool] = Field(None, description="是否为求解目标")

class Condition(BaseModel):
    type: str = Field(description="条件类型 (angle, equality, similarity 等)")
    measure: Optional[float] = Field(None, description="角度或测量值")
    unit: Optional[str] = Field(None, description="测量单位 (degree, radian 等)")
    elements: Optional[List[str]] = Field(None, description="相关的元素")

class Target(BaseModel):
    type: str = Field(description="目标类型 (length, angle, area 等)")
    segment: Optional[str] = Field(None, description="需要求解的线段")
    angle: Optional[str] = Field(None, description="需要求解的角度")
    description: Optional[str] = Field(None, description="目标的描述")

class ProblemType(BaseModel):
    triangle: bool = Field(False, description="问题是否与三角形相关")
    circle: bool = Field(False, description="问题是否与圆相关")
    angle: bool = Field(False, description="问题是否与角度相关")
    coordinate: bool = Field(False, description="问题是否与坐标相关")
    proof: bool = Field(False, description="问题是否为证明题")
    construction: bool = Field(False, description="问题是否为作图题")
    measurement: bool = Field(False, description="问题是否为计算题")

class AnalyzedConditions(BaseModel):
    equal_sides: bool = Field(False, description="问题是否包含等边条件")
    equal_angles: bool = Field(False, description="问题是否包含等角条件")
    perpendicular: bool = Field(False, description="问题是否包含垂直条件")
    parallel: bool = Field(False, description="问题是否包含平行条件")
    congruent: bool = Field(False, description="问题是否包含全等条件")
    similar: bool = Field(False, description="问题是否包含相似条件")
    tangent: bool = Field(False, description="问题是否包含切线条件")

class ParsedElements(BaseModel):
    geometric_objects: Dict[str, GeometricObject] = Field(
        description="问题中出现的所有几何对象 (点、线、圆、三角形等)"
    )
    relations: Dict[str, Relation] = Field(
        description="几何对象之间的关系 (线段、平行、垂直等)"
    )
    conditions: Dict[str, Condition] = Field(
        description="问题中给出的条件 (角度、长度等约束条件)"
    )
    targets: Dict[str, Target] = Field(
        description="问题中需要求解的目标"
    )
    problem_type: ProblemType = Field(
        default_factory=ProblemType,
        description="问题类型分析结果"
    )
    analyzed_conditions: AnalyzedConditions = Field(
        default_factory=AnalyzedConditions,
        description="问题条件分析结果"
    )

def parsing_agent(state):
    """
    중국어 기하학 문제에서 기하학적 요소를 추출하는 에이전트
    
    Args:
        state: 현재 상태(GeometryState 객체), input_problem 속성 포함
        
    Returns:
        parsed_elements가 추가된 상태 딕셔너리
    """
    # 출력 파서 설정
    parser = PydanticOutputParser(pydantic_object=ParsedElements)
    
    # 자동으로 형식 지침 생성
    format_instructions = parser.get_format_instructions()
    
    # LLM 설정
    llm = LLMManager.get_parsing_llm()
    
    # 프롬프트 체인 생성 및 실행
    chain = (PARSING_PROMPT.partial(format_instructions=format_instructions) | llm | parser)
    
    try:
        # 구조화된 형식으로 결과 가져오기
        parsed_elements = chain.invoke({"problem": state.input_problem})
        
        # Pydantic 모델을 딕셔너리로 변환
        parsed_elements_dict = parsed_elements.model_dump()
        
        # 추가 처리가 필요한 경우 여기서 수행
        _enhance_with_keywords(parsed_elements_dict, state.input_problem)
        
    except Exception as e:
        # 파싱 실패 시 수동 파싱 시도
        print(f"구조화된 파싱 실패, 수동 파싱 시도: {str(e)}")
        result_text = llm.invoke(PARSING_PROMPT.format(problem=state.input_problem, format_instructions=format_instructions))
        
        try:
            # JSON 형식 응답 추출 시도
            json_content = _extract_json_from_response(result_text.content)
            parsed_elements_dict = json.loads(json_content)
        except:
            # 수동 파싱으로 마지막 시도
            parsed_elements_dict = _manual_parsing(result_text.content, state.input_problem)
        
        # 구조화되지 않은 경우 빈 구조 생성
        if not isinstance(parsed_elements_dict, dict) or not parsed_elements_dict:
            parsed_elements_dict = {
                "geometric_objects": {},
                "relations": {},
                "conditions": {},
                "targets": {},
                "error": f"파싱 오류: {str(e)}"
            }
    
    # 항상 딕셔너리 형태로 반환
    return {"parsed_elements": parsed_elements_dict}

def _extract_json_from_response(response: str) -> str:
    """응답에서 JSON 부분만 추출"""
    # JSON 블록 추출 시도
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
    if json_match:
        return json_match.group(1)
    
    # JSON 객체 추출 시도
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        return json_match.group(0)
    
    # JSON 추출 실패 시 전체 응답 반환
    return response


def _manual_parsing(content: str, problem: str) -> Dict[str, Any]:
    """LLM 응답이 JSON이 아닌 경우의 수동 파싱"""
    result = {
        "geometric_objects": {},
        "relations": {},
        "conditions": {},
        "targets": {}
    }
    
    # 텍스트에서 기하학적 요소 추출 시도
    
    # 1. 점 추출 (대문자 알파벳으로 표현되는 경우가 많음)
    points = re.findall(r'\b([A-Z])\b', content + " " + problem)
    for point in set(points):
        result["geometric_objects"][point] = {"type": "point"}
    
    # 2. 삼각형 추출 (△ABC 또는 三角形ABC 형태)
    triangles = re.findall(r'△\s*([A-Z]{3})|三角形\s*([A-Z]{3})', content + " " + problem)
    for triangle in triangles:
        triangle_name = "".join(filter(None, triangle))  # 매치된 그룹 중 비어있지 않은 것
        if triangle_name:
            result["geometric_objects"][f"triangle_{triangle_name}"] = {
                "type": "triangle",
                "vertices": list(triangle_name)
            }
    
    # 3. 선분 추출 (AB 형태 또는 선분AB 형태)
    segments = re.findall(r'线段\s*([A-Z]{2})|\b([A-Z]{2})\b', content + " " + problem)
    for segment in segments:
        segment_name = "".join(filter(None, segment))
        if len(segment_name) == 2 and segment_name.isalpha():
            result["relations"][f"segment_{segment_name}"] = {
                "type": "segment",
                "elements": list(segment_name)
            }
    
    # 4. 원 추출 (O为圆心 형태)
    circles = re.findall(r'([A-Z])为圆心|圆心([A-Z])|圆\s*([A-Z])', content + " " + problem)
    for circle in circles:
        center = "".join(filter(None, circle))
        if center:
            result["geometric_objects"][f"circle_{center}"] = {
                "type": "circle",
                "center": center
            }
    
    # 5. 각도 추출 (∠ABC 형태)
    angles = re.findall(r'∠\s*([A-Z]{3})|角\s*([A-Z]{3})', content + " " + problem)
    for angle in angles:
        angle_name = "".join(filter(None, angle))
        if len(angle_name) == 3:
            result["geometric_objects"][f"angle_{angle_name}"] = {
                "type": "angle",
                "points": list(angle_name)
            }
    
    # 6. 조건 추출 (예: "AB = BC", "∠ABC = 90°" 등)
    # 이 부분은 특정 패턴을 찾기 어려워 단순화된 접근 사용
    equal_conditions = re.findall(r'([A-Z]{2,3})\s*=\s*([A-Z]{2,3})', content + " " + problem)
    for i, condition in enumerate(equal_conditions):
        result["conditions"][f"equality_{i}"] = {
            "type": "equality",
            "elements": [condition[0], condition[1]]
        }
    
    # 7. 목표 추출 (求...)
    targets = re.findall(r'求\s*([^。，,\.]+)', problem)
    for i, target in enumerate(targets):
        result["targets"][f"target_{i}"] = {
            "description": target.strip()
        }
    
    return result

def _enhance_with_keywords(parsed_elements: Dict[str, Any], problem: str) -> None:
    """키워드 기반 추가 정보 추출"""
    # 삼각형 유형 식별
    if "正三角形" in problem:
        parsed_elements["conditions"]["triangle_type"] = {"type": "triangle_type", "value": "equilateral"}
    elif "等腰三角形" in problem:
        parsed_elements["conditions"]["triangle_type"] = {"type": "triangle_type", "value": "isosceles"}
    elif "直角三角形" in problem:
        parsed_elements["conditions"]["triangle_type"] = {"type": "triangle_type", "value": "right"}
    
    # 원 관련 키워드
    if "圆" in problem:
        # 원이 이미 식별되었는지 확인
        circle_exists = False
        for obj in parsed_elements.get("geometric_objects", {}).values():
            if isinstance(obj, dict) and obj.get("type") == "circle":
                circle_exists = True
                break
        
        # 원이 없으면 기본 원 추가
        if not circle_exists:
            parsed_elements.setdefault("geometric_objects", {})["circle_O"] = {
                "type": "circle",
                "center": "O"
            }
    
    # 좌표 관련 키워드
    if "坐标" in problem or "平面直角坐标系" in problem:
        if isinstance(parsed_elements, dict):
            parsed_elements["has_coordinate_system"] = True
    
    # 문제 유형 분석 추가
    if "problem_type" not in parsed_elements:
        parsed_elements["problem_type"] = {}
    
    problem_type = parsed_elements["problem_type"]
    
    # 기하학적 요소에 따른 문제 유형 분석
    if "三角形" in problem or any("triangle" in str(obj).lower() for obj in parsed_elements.get("geometric_objects", {}).values()):
        problem_type["triangle"] = True
    
    if "圆" in problem or any("circle" in str(obj).lower() for obj in parsed_elements.get("geometric_objects", {}).values()):
        problem_type["circle"] = True
    
    if "角" in problem or "度" in problem or any("angle" in str(obj).lower() for obj in parsed_elements.get("geometric_objects", {}).values()):
        problem_type["angle"] = True
    
    if "坐标" in problem or "平面直角坐标系" in problem:
        problem_type["coordinate"] = True
    
    # 문제 목표 분석
    if "证明" in problem or "求证" in problem:
        problem_type["proof"] = True
    
    if "作" in problem or "画" in problem or "构造" in problem:
        problem_type["construction"] = True
    
    if "求" in problem or "计算" in problem:
        problem_type["measurement"] = True
    
    # 문제 조건 분석 추가
    if "analyzed_conditions" not in parsed_elements:
        parsed_elements["analyzed_conditions"] = {}
    
    conditions = parsed_elements["analyzed_conditions"]
    
    # 조건 키워드에 따른 분석
    condition_keywords = {
        "equal_sides": ["相等", "等长", "等边"],
        "equal_angles": ["等角", "相等"],
        "perpendicular": ["垂直", "正交", "直角"],
        "parallel": ["平行", "平行线"],
        "congruent": ["全等", "重合"],
        "similar": ["相似", "相似比"],
        "tangent": ["相切", "切线"]
    }
    
    for condition, keywords in condition_keywords.items():
        for keyword in keywords:
            if keyword in problem:
                conditions[condition] = True
                break 