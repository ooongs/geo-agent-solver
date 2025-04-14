from typing import List, Dict, Any, Optional
import re

class GeoGebraValidator:
    """GeoGebra 명령어 검증을 위한 클래스"""
    
    # GeoGebra 명령어 정규식 패턴
    POINT_PATTERN = r"^[A-Z]\s*=\s*\(\s*[-+]?\d*\.?\d+\s*,\s*[-+]?\d*\.?\d+\s*\)$"
    LINE_PATTERN = r"^[a-z]\s*:\s*(y|x)\s*=\s*[-+]?\d*\.?\d*((\s*[+-]\s*[-+]?\d*\.?\d*\s*\*\s*[xy])|)$"
    CIRCLE_PATTERN = r"^[a-z]\s*:\s*\(\s*x\s*[-+]\s*[-+]?\d*\.?\d+\s*\)\s*\^\s*2\s*\+\s*\(\s*y\s*[-+]\s*[-+]?\d*\.?\d+\s*\)\s*\^\s*2\s*=\s*[-+]?\d*\.?\d+\s*\^\s*2$"
    SEGMENT_PATTERN = r"^Segment\s*\(\s*[A-Z]\s*,\s*[A-Z]\s*\)$"
    ANGLE_PATTERN = r"^Angle\s*\(\s*[A-Z]\s*,\s*[A-Z]\s*,\s*[A-Z]\s*\)$"
    # 추가 패턴
    PARALLEL_PATTERN = r"^Parallel\s*\(\s*[a-z]\s*,\s*[A-Z]\s*\)$"
    PERPENDICULAR_PATTERN = r"^Perpendicular\s*\(\s*[a-z]\s*,\s*[A-Z]\s*\)$"
    POLYGON_PATTERN = r"^Polygon\s*\(\s*[A-Z](\s*,\s*[A-Z])+\s*\)$"
    MIDPOINT_PATTERN = r"^Midpoint\s*\(\s*[A-Z]\s*,\s*[A-Z]\s*\)$"
    BISECTOR_PATTERN = r"^AngleBisector\s*\(\s*[A-Z]\s*,\s*[A-Z]\s*,\s*[A-Z]\s*\)$"
    INTERSECTION_PATTERN = r"^Intersect\s*\(\s*[a-zA-Z]\s*,\s*[a-zA-Z]\s*\)$"
    CIRCLE_CENTER_POINT_PATTERN = r"^Circle\s*\(\s*[A-Z]\s*,\s*[A-Z]\s*\)$"
    CIRCLE_CENTER_RADIUS_PATTERN = r"^Circle\s*\(\s*[A-Z]\s*,\s*[-+]?\d*\.?\d+\s*\)$"
    REFLECTION_PATTERN = r"^Reflect\s*\(\s*[A-Z]\s*,\s*[a-z]\s*\)$"
    ROTATION_PATTERN = r"^Rotate\s*\(\s*[A-Z]\s*,\s*[-+]?\d*\.?\d+\s*,\s*[A-Z]\s*\)$"
    
    @staticmethod
    def validate_syntax(commands: List[str]) -> Dict[str, Any]:
        """GeoGebra 명령어의 문법 검증"""
        errors = []
        
        for i, cmd in enumerate(commands):
            cmd = cmd.strip()
            valid = False
            
            # 각 명령어 유형별 정규식 검사
            if re.match(GeoGebraValidator.POINT_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.LINE_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.CIRCLE_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.SEGMENT_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.ANGLE_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.PARALLEL_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.PERPENDICULAR_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.POLYGON_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.MIDPOINT_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.BISECTOR_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.INTERSECTION_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.CIRCLE_CENTER_POINT_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.CIRCLE_CENTER_RADIUS_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.REFLECTION_PATTERN, cmd):
                valid = True
            elif re.match(GeoGebraValidator.ROTATION_PATTERN, cmd):
                valid = True
            elif cmd.startswith("SetAxesVisible") or cmd.startswith("SetGridVisible"):
                valid = True
            # 추가 패턴은 필요에 따라 확장
            
            if not valid:
                errors.append({
                    "line": i+1,
                    "command": cmd,
                    "message": "Invalid command syntax"
                })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_geometric_consistency(commands: List[str], elements: Dict[str, Any]) -> Dict[str, Any]:
        """기하학적 일관성 검증"""
        errors = []
        defined_objects = set()
        
        for i, cmd in enumerate(commands):
            # 점 정의 확인
            if "=" in cmd and cmd.split("=")[0].strip() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                obj_name = cmd.split("=")[0].strip()
                defined_objects.add(obj_name)
            
            # 기하학적 요소 사용 검증 (예: 정의되지 않은 점 사용 확인)
            if "Segment" in cmd or "Angle" in cmd:
                match = re.findall(r'[A-Z]', cmd)
                for point in match:
                    if point not in defined_objects:
                        errors.append({
                            "line": i+1,
                            "command": cmd,
                            "message": f"Point {point} used before definition"
                        })
        
        # 필요한 기하학적 요소가 모두 정의되었는지 확인
        required_objects = set(elements.get("geometric_objects", {}).keys())
        missing_objects = required_objects - defined_objects
        
        if missing_objects:
            errors.append({
                "message": f"Missing geometric objects: {', '.join(missing_objects)}"
            })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_command_relations(commands: List[str]) -> Dict[str, Any]:
        """GeoGebra 명령어 간의 관계 검증"""
        errors = []
        defined_objects = {}
        required_objects = {}
        
        # 첫 번째 패스: 정의된 객체 추출
        for i, cmd in enumerate(commands):
            cmd = cmd.strip()
            
            # 점 정의
            if "=" in cmd and cmd.split("=")[0].strip() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                obj_name = cmd.split("=")[0].strip()
                defined_objects[obj_name] = {"type": "point", "line": i+1}
            
            # 선 정의
            elif ":" in cmd and cmd.split(":")[0].strip() in "abcdefghijklmnopqrstuvwxyz":
                obj_name = cmd.split(":")[0].strip()
                defined_objects[obj_name] = {"type": "line", "line": i+1}
            
            # 원 정의 (Circle 명령)
            elif cmd.startswith("Circle"):
                match = re.search(r'Circle\s*\(\s*([A-Z])\s*,', cmd)
                if match:
                    center = match.group(1)
                    obj_name = f"c_{center}"  # 원 이름 생성
                    defined_objects[obj_name] = {"type": "circle", "line": i+1}
        
        # 두 번째 패스: 필요한 객체와 의존성 검사
        for i, cmd in enumerate(commands):
            cmd = cmd.strip()
            
            # Segment, Angle 등의 명령에서 사용되는 점 추출
            if "(" in cmd and ")" in cmd:
                used_objects = re.findall(r'[A-Za-z]', cmd[cmd.index("("):cmd.index(")")+1])
                for obj in used_objects:
                    if obj.isupper() and obj not in defined_objects:  # 대문자는 점
                        required_objects[obj] = {"type": "point", "line": i+1}
                    elif obj.islower() and obj not in defined_objects:  # 소문자는 선 또는 원
                        required_objects[obj] = {"type": "line/circle", "line": i+1}
        
        # 정의되지 않았지만 사용된 객체 찾기
        for obj, info in required_objects.items():
            if obj not in defined_objects:
                errors.append({
                    "line": info["line"],
                    "object": obj,
                    "message": f"Object '{obj}' used but not defined"
                })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def validate(commands: List[str], elements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """종합적인 검증 수행"""
        syntax_result = GeoGebraValidator.validate_syntax(commands)
        
        if not syntax_result["is_valid"]:
            return syntax_result
        
        # 명령어 간의 관계 검증
        relation_result = GeoGebraValidator.validate_command_relations(commands)
        if not relation_result["is_valid"]:
            return relation_result
        
        # 기하학적 요소가 제공된 경우 일관성 검증
        if elements:
            consistency_result = GeoGebraValidator.validate_geometric_consistency(commands, elements)
            if not consistency_result["is_valid"]:
                return consistency_result
        
        return {
            "is_valid": True,
            "message": "All commands validated successfully"
        }

def validate_geogebra_syntax(commands: List[str]) -> Dict[str, Any]:
    """GeoGebra 명령어의 문법을 검증하는 함수"""
    return GeoGebraValidator.validate_syntax(commands) 