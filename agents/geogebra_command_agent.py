from typing import Dict, Any, List, Optional
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from utils.prompts import GEOGEBRA_COMMAND_PROMPT
from utils.llm_manager import LLMManager
import re
import json
import numpy as np

def geogebra_command_agent(state):
    """
    GeoGebra 명령어 생성 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        GeoGebra 명령어가 추가된 상태 객체
    """
    # 도구 생성
    tools = get_geogebra_command_tools()
    
    # LLM 초기화
    llm = LLMManager.get_geogebra_command_llm()
    
    # 입력 데이터 준비
    # 계산 결과가 없는 경우 빈 딕셔너리로 초기화
    calculations = getattr(state, "calculations", {})
    if not calculations and hasattr(state, "calculation_results"):
        calculations = state.calculation_results
    
    # 문제 분석 정보가 없는 경우 계산 결과에서 문제 유형 정보 추출
    problem_analysis = {}
    if hasattr(state, "problem_analysis"):
        problem_analysis = state.problem_analysis
    elif "problem_type" in calculations:
        problem_analysis = {"problem_type": calculations["problem_type"]}

    construction_plan = getattr(state, "construction_plan", {})
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, GEOGEBRA_COMMAND_PROMPT)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 에이전트 실행
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "problem_analysis": str(problem_analysis),
        "construction_plan": str(construction_plan),
        "calculations": str(calculations),
        "agent_scratchpad": ""
    })
    
    # 결과에서 명령어 추출
    try:
        # JSON 형식인 경우 파싱
        commands_data = json.loads(result["output"]) if isinstance(result["output"], str) else result["output"]
        if isinstance(commands_data, dict) and "commands" in commands_data:
            commands = commands_data["commands"]
        elif isinstance(commands_data, list):
            commands = commands_data
        else:
            # 텍스트에서 명령어 추출
            commands = _extract_commands_from_text(result["output"])
    except (json.JSONDecodeError, TypeError):
        # 텍스트에서 명령어 추출
        commands = _extract_commands_from_text(result["output"])
    
    # 상태 업데이트
    state.geogebra_commands = commands
    
    # GeoGebra 직접 명령어 추가 (계산 없이 생성 가능한 명령어)
    if hasattr(state, "calculation_results") and state.calculation_results:
        direct_commands = _extract_direct_commands_from_calculations(state.calculation_results)
        if direct_commands:
            # 명령어 순서를 조정하여 기본 점/선 명령어가 먼저 오도록 함
            reorganized_commands = []
            
            # 1. 점 정의 명령어 추가
            point_commands = [cmd for cmd in commands if "=" in cmd and cmd.split("=")[0].strip() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
            reorganized_commands.extend(point_commands)
            
            # 2. 직접 명령어 추가 (중점, 교점 등)
            reorganized_commands.extend(direct_commands)
            
            # 3. 나머지 명령어 추가
            for cmd in commands:
                if cmd not in reorganized_commands:
                    reorganized_commands.append(cmd)
            
            state.geogebra_commands = reorganized_commands
            print(f"[DEBUG] Added {len(direct_commands)} direct GeoGebra commands")
    
    return state

def get_geogebra_command_tools():
    """GeoGebra 명령어 생성 에이전트용 도구 생성"""
    return [
        StructuredTool.from_function(
            name="generate_point_commands",
            func=_generate_point_commands_tool,
            description="根据解析元素和计算结果生成点的GeoGebra命令"
        ),
        StructuredTool.from_function(
            name="generate_line_commands",
            func=_generate_line_commands_tool,
            description="根据解析元素和计算结果生成线和线段的GeoGebra命令"
        ),
        StructuredTool.from_function(
            name="generate_circle_commands",
            func=_generate_circle_commands_tool,
            description="根据解析元素和计算结果生成圆的GeoGebra命令"
        ),
        StructuredTool.from_function(
            name="generate_angle_commands",
            func=_generate_angle_commands_tool,
            description="根据解析元素和计算结果生成角的GeoGebra命令"
        ),
        StructuredTool.from_function(
            name="generate_measurement_commands",
            func=_generate_measurement_commands_tool,
            description="根据解析元素和计算结果生成测量的GeoGebra命令"
        ),
        StructuredTool.from_function(
            name="validate_geogebra_syntax",
            func=_validate_geogebra_syntax_tool,
            description="验证GeoGebra命令的语法"
        )
    ]

# === Tool 함수 구현 ===

def _generate_point_commands_tool(input_json: str) -> str:
    """
    점 명령어 생성 도구
    
    Args:
        input_json: 파싱된 요소와 계산 결과를 포함한 JSON 문자열
        
    Returns:
        점 명령어 목록(JSON 문자열)
    """
    try:
        # 입력이 JSON 문자열인 경우 파싱
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            data = json.loads(input_json)
            parsed_elements = data.get("parsed_elements", {})
            calculations = data.get("calculations", {})
        else:
            # 일반 텍스트인 경우 기본값 설정
            parsed_elements = {}
            calculations = {}
        
        commands = []
        
        # 좌표 정보에서 점 명령어 생성
        if "coordinates" in calculations:
            for point_name, coord in calculations["coordinates"].items():
                if isinstance(coord, (list, tuple)) and len(coord) == 2:
                    commands.append(f"{point_name} = ({coord[0]}, {coord[1]})")
        
        # 기하학적 요소에서 점 추가 정보 확인
        if "geometric_objects" in parsed_elements:
            for obj_name, obj in parsed_elements["geometric_objects"].items():
                if obj.get("type", "").lower() == "point" and obj_name not in calculations.get("coordinates", {}):
                    # 임의의 좌표 할당 (기본값)
                    x = np.random.uniform(-5, 5)
                    y = np.random.uniform(-5, 5)
                    commands.append(f"{obj_name} = ({x}, {y})")
        
        return json.dumps({"commands": commands}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def _generate_line_commands_tool(input_json: str) -> str:
    """
    선 명령어 생성 도구
    
    Args:
        input_json: 파싱된 요소와 계산 결과를 포함한 JSON 문자열
        
    Returns:
        선 명령어 목록(JSON 문자열)
    """
    try:
        # 입력이 JSON 문자열인 경우 파싱
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            data = json.loads(input_json)
            parsed_elements = data.get("parsed_elements", {})
            calculations = data.get("calculations", {})
        else:
            # 일반 텍스트인 경우 기본값 설정
            parsed_elements = {}
            calculations = {}
        
        commands = []
        
        # 계산 결과에서 선분 정보 확인
        if "distances" in calculations:
            for segment_name, distance in calculations["distances"].items():
                if len(segment_name) == 2 and segment_name.isalpha():
                    # 두 점 사이의 선분 생성
                    commands.append(f"Segment({segment_name[0]}, {segment_name[1]})")
        
        # 기하학적 요소에서 선 정보 확인
        if "geometric_objects" in parsed_elements:
            for obj_name, obj in parsed_elements["geometric_objects"].items():
                if obj.get("type", "").lower() in ["line", "segment", "ray"]:
                    if "points" in obj and len(obj["points"]) >= 2:
                        p1, p2 = obj["points"][0], obj["points"][1]
                        if obj.get("type", "").lower() == "line":
                            commands.append(f"{obj_name} = Line({p1}, {p2})")
                        elif obj.get("type", "").lower() == "segment":
                            commands.append(f"{obj_name} = Segment({p1}, {p2})")
                        elif obj.get("type", "").lower() == "ray":
                            commands.append(f"{obj_name} = Ray({p1}, {p2})")
        
        # 관계에 따른 선 생성
        if "relationships" in parsed_elements:
            for rel_name, rel in parsed_elements["relationships"].items():
                rel_type = rel.get("type", "").lower()
                elements = rel.get("elements", [])
                
                if rel_type == "parallel" and len(elements) >= 2:
                    # 평행선 생성
                    line1, line2 = elements[0], elements[1]
                    if line1 in parsed_elements.get("geometric_objects", {}) and line2 not in [cmd.split("=")[0].strip() for cmd in commands]:
                        points = parsed_elements["geometric_objects"][line1].get("points", [])
                        if len(points) >= 2 and "point" in elements:
                            commands.append(f"{line2} = Line({elements['point']}, Vector({points[0]}, {points[1]}))")
                
                elif rel_type == "perpendicular" and len(elements) >= 2:
                    # 수직선 생성
                    line1, line2 = elements[0], elements[1]
                    if line1 in parsed_elements.get("geometric_objects", {}) and line2 not in [cmd.split("=")[0].strip() for cmd in commands]:
                        points = parsed_elements["geometric_objects"][line1].get("points", [])
                        if len(points) >= 2 and "point" in elements:
                            commands.append(f"{line2} = Perpendicular({line1}, {elements['point']})")
        
        # 직선 방정식이 있는 경우
        if "lines" in calculations:
            for line_name, line_info in calculations["lines"].items():
                if "equation" in line_info and line_name not in [cmd.split("=")[0].strip() for cmd in commands]:
                    eq = line_info["equation"]
                    commands.append(f"{line_name}: {eq}")
        
        return json.dumps({"commands": commands}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def _generate_circle_commands_tool(input_json: str) -> str:
    """
    원 명령어 생성 도구
    
    Args:
        input_json: 파싱된 요소와 계산 결과를 포함한 JSON 문자열
        
    Returns:
        원 명령어 목록(JSON 문자열)
    """
    try:
        # 입력이 JSON 문자열인 경우 파싱
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            data = json.loads(input_json)
            parsed_elements = data.get("parsed_elements", {})
            calculations = data.get("calculations", {})
        else:
            # 일반 텍스트인 경우 기본값 설정
            parsed_elements = {}
            calculations = {}
        
        commands = []
        
        # 원 정보가 있는 경우
        if "circle" in calculations:
            circle_info = calculations["circle"]
            
            if isinstance(circle_info, dict):
                # 원 중심과 반지름으로 정의
                if "center" in circle_info and "radius" in circle_info:
                    center = circle_info["center"]
                    radius = circle_info["radius"]
                    
                    if "center_coords" in circle_info:
                        # 방정식 형태
                        x, y = float(circle_info["center_coords"][0]), float(circle_info["center_coords"][1])
                        commands.append(f"c: (x - {x})^2 + (y - {y})^2 = {radius}^2")
                    
                    # 중심과 반지름 형태
                    commands.append(f"Circle({center}, {radius})")
                
                # 외접원 정보가 있는 경우
                if "circumcircle" in circle_info:
                    circle = circle_info["circumcircle"]
                    center = circle.get("center", "O")  # 기본값 O
                    radius = circle.get("radius", 1)    # 기본값 1
                    commands.append(f"Circumcircle = Circle({center}, {radius})")
        
        # 기하학적 요소에서 원 정보 확인
        if "geometric_objects" in parsed_elements:
            for obj_name, obj in parsed_elements["geometric_objects"].items():
                if obj.get("type", "").lower() == "circle":
                    if "center" in obj and "radius" in obj:
                        # 중심과 반지름으로 정의된 원
                        commands.append(f"{obj_name} = Circle({obj['center']}, {obj['radius']})")
                    elif "center" in obj and "point" in obj:
                        # 중심과 한 점으로 정의된 원
                        commands.append(f"{obj_name} = Circle({obj['center']}, {obj['point']})")
                    elif "points" in obj and len(obj["points"]) >= 3:
                        # 세 점으로 정의된 원
                        p1, p2, p3 = obj["points"][0], obj["points"][1], obj["points"][2]
                        commands.append(f"{obj_name} = Circle({p1}, {p2}, {p3})")
        
        return json.dumps({"commands": commands}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def _generate_angle_commands_tool(input_json: str) -> str:
    """
    각도 명령어 생성 도구
    
    Args:
        input_json: 파싱된 요소와 계산 결과를 포함한 JSON 문자열
        
    Returns:
        각도 명령어 목록(JSON 문자열)
    """
    try:
        # 입력이 JSON 문자열인 경우 파싱
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            data = json.loads(input_json)
            parsed_elements = data.get("parsed_elements", {})
            calculations = data.get("calculations", {})
        else:
            # 일반 텍스트인 경우 기본값 설정
            parsed_elements = {}
            calculations = {}
        
        commands = []
        
        # 각도 정보가 있는 경우
        if "angles" in calculations:
            for angle_name, angle_value in calculations["angles"].items():
                if len(angle_name) == 3 and angle_name.isalpha():
                    # 세 점으로 정의된 각
                    commands.append(f"Angle({angle_name[0]}, {angle_name[1]}, {angle_name[2]})")
                    
                    # 특별한 각도는 표시
                    if isinstance(angle_value, (int, float)):
                        if abs(angle_value - 90) < 0.1:  # 직각
                            commands.append(f"SetRightAngle({angle_name[0]}, {angle_name[1]}, {angle_name[2]}, true)")
        
        # 기하학적 요소에서 각도 정보 확인
        if "geometric_objects" in parsed_elements:
            for obj_name, obj in parsed_elements["geometric_objects"].items():
                if obj.get("type", "").lower() == "angle":
                    if "points" in obj and len(obj["points"]) >= 3:
                        p1, p2, p3 = obj["points"][0], obj["points"][1], obj["points"][2]
                        commands.append(f"{obj_name} = Angle({p1}, {p2}, {p3})")
                    elif "rays" in obj and len(obj["rays"]) >= 2:
                        ray1, ray2 = obj["rays"][0], obj["rays"][1]
                        commands.append(f"{obj_name} = Angle({ray1}, {ray2})")
        
        # 특정 값을 가진 각도 표시
        if "angle_constraints" in calculations:
            for angle_name, angle_value in calculations["angle_constraints"].items():
                if len(angle_name) == 3 and angle_name.isalpha():
                    commands.append(f"Angle({angle_name[0]}, {angle_name[1]}, {angle_name[2]}) = {angle_value}")
        
        return json.dumps({"commands": commands}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def _generate_measurement_commands_tool(input_json: str) -> str:
    """
    측정 명령어 생성 도구
    
    Args:
        input_json: 파싱된 요소, 계산 결과, 문제 유형을 포함한 JSON 문자열
        
    Returns:
        측정 명령어 목록(JSON 문자열)
    """
    try:
        # 입력이 JSON 문자열인 경우 파싱
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            data = json.loads(input_json)
            parsed_elements = data.get("parsed_elements", {})
            calculations = data.get("calculations", {})
            problem_type = data.get("problem_type", {})
        else:
            # 일반 텍스트인 경우 기본값 설정
            parsed_elements = {}
            calculations = {}
            problem_type = {}
        
        commands = []
        
        # 거리 측정
        if "distances" in calculations:
            for segment_name, distance in calculations["distances"].items():
                if len(segment_name) == 2 and segment_name.isalpha():
                    commands.append(f"Distance({segment_name[0]}, {segment_name[1]})")
        
        # 각도 측정
        if "angles" in calculations:
            for angle_name, angle_value in calculations["angles"].items():
                if len(angle_name) == 3 and angle_name.isalpha():
                    commands.append(f"AngleText = Text(\"{angle_name} = {angle_value}°\", {angle_name[1]})")
        
        # 면적 측정
        if "areas" in calculations:
            for shape_name, area in calculations["areas"].items():
                # 다각형 면적
                if "polygon" in shape_name.lower() and "coordinates" in calculations:
                    vertices = []
                    for point_name in parsed_elements.get("geometric_objects", {}).get(shape_name, {}).get("points", []):
                        if point_name in calculations["coordinates"]:
                            vertices.append(point_name)
                    
                    if len(vertices) >= 3:
                        polygon_str = ", ".join(vertices)
                        commands.append(f"Area(Polygon({polygon_str}))")
                        commands.append(f"AreaText = Text(\"Area = {area}\", Centroid(Polygon({polygon_str})))")
        
        # 문제 유형에 따른 추가 측정
        if isinstance(problem_type, dict):
            if problem_type.get("measurement", False):
                # 측정 문제인 경우 관련 값 표시
                if "target_value" in calculations:
                    target = calculations["target_value"]
                    if isinstance(target, dict):
                        for name, value in target.items():
                            commands.append(f"TargetText = Text(\"{name} = {value}\", (0, 0))")
            
            if problem_type.get("triangle", False):
                # 삼각형 정보 표시
                triangle_points = []
                for obj_name, obj in parsed_elements.get("geometric_objects", {}).items():
                    if obj.get("type", "").lower() == "polygon" and len(obj.get("points", [])) == 3:
                        triangle_points = obj["points"]
                        break
                
                if triangle_points and len(triangle_points) == 3:
                    p1, p2, p3 = triangle_points
                    commands.append(f"Triangle = Polygon({p1}, {p2}, {p3})")
                    commands.append(f"Perimeter(Triangle)")
                    commands.append(f"Area(Triangle)")
        
        return json.dumps({"commands": commands}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def _validate_geogebra_syntax_tool(input_json: str) -> str:
    """
    GeoGebra 명령어 구문 검증 도구
    
    Args:
        input_json: 명령어 목록을 포함한 JSON 문자열
        
    Returns:
        검증 결과(JSON 문자열)
    """
    try:
        # 입력이 JSON 문자열인 경우 파싱
        if isinstance(input_json, str) and input_json.strip().startswith('{'):
            data = json.loads(input_json)
            commands = data.get("commands", [])
        else:
            # 일반 텍스트인 경우 줄바꿈으로 분리
            commands = [line.strip() for line in input_json.strip().split("\n") if line.strip()]
        
        result = validate_geogebra_syntax(commands)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"is_valid": False, "errors": [str(e)]}, ensure_ascii=False)

# === 헬퍼 함수 ===

def _extract_commands_from_text(text: str) -> List[str]:
    """
    텍스트에서 GeoGebra 명령어 추출
    
    Args:
        text: 명령어가 포함된 텍스트
        
    Returns:
        명령어 목록
    """
    # 줄바꿈으로 구분된 텍스트인 경우
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    
    # 명령어로 보이는 라인만 필터링
    commands = []
    for line in lines:
        # 숫자 접두사 또는 마크다운 코드 블록 표시 제거
        line = re.sub(r'^(\d+[\.\)]\s*|```\w*|`)', '', line)
        line = line.strip()
        
        # 빈 라인 또는 명령어로 보이지 않는 라인 제외
        if not line or line.startswith('#') or line.startswith('//'):
            continue
            
        # = 또는 : 이 포함된 라인만 명령어로 간주
        if '=' in line or ':' in line or '(' in line:
            commands.append(line)
    
    return commands

def _extract_direct_commands_from_calculations(calculations: Dict[str, Any]) -> List[str]:
    """
    계산 결과에서 GeoGebra 직접 명령어 추출
    
    Args:
        calculations: 계산 결과 딕셔너리
        
    Returns:
        GeoGebra 직접 명령어 목록
    """
    direct_commands = []
    
    # geogebra_direct_commands 필드가 있는지 확인
    if "geogebra_direct_commands" in calculations:
        for cmd_info in calculations["geogebra_direct_commands"]:
            if "geogebra_command" in cmd_info and cmd_info["geogebra_command"]:
                direct_commands.append(cmd_info["geogebra_command"])
    
    return direct_commands 