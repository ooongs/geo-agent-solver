from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from utils.geometry_tools import GeometryTools
import math
import re

def handle_triangle_problem(calculations: Dict[str, Any], problem_type: Dict[str, Any], parsed: Dict[str, Any]) -> None:
    """
    삼각형 관련 문제 처리
    
    Args:
        calculations: 계산 결과 저장소
        problem_type: 문제 유형 정보
        parsed: 파싱된 문제 정보
    """
    # 삼각형 정보 초기화
    if "triangles" not in calculations:
        calculations["triangles"] = {}
    
    # 삼각형 식별
    triangle_name = _identify_triangle(parsed)
    if not triangle_name:
        # 기본 삼각형 ABC 가정
        triangle_name = "ABC"
    
    # 삼각형 속성 초기화
    triangle = {
        "vertices": list(triangle_name),
        "sides": [],
        "angles": {},
        "area": None,
        "perimeter": None,
        "type": "unknown",
        "properties": {}
    }
    
    # 삼각형 변 계산
    sides = []
    for i in range(3):
        side = f"{triangle_name[i]}{triangle_name[(i+1)%3]}"
        sides.append(side)
    
    triangle["sides"] = sides
    
    # 좌표가 있는 경우 삼각형 계산
    if all(v in calculations.get("coordinates", {}) for v in triangle_name):
        points = [calculations["coordinates"][v] for v in triangle_name]
        
        # 변 길이 계산
        for i, side in enumerate(sides):
            p1 = points[i]
            p2 = points[(i+1)%3]
            distance = GeometryTools.calculate_distance(p1, p2)
            calculations["distances"][side] = distance
        
        # 각도 계산
        for i in range(3):
            p1 = points[(i+2)%3]
            p2 = points[i]
            p3 = points[(i+1)%3]
            angle = GeometryTools.calculate_angle(p1, p2, p3)
            angle_name = f"{triangle_name[(i+2)%3]}{triangle_name[i]}{triangle_name[(i+1)%3]}"
            calculations["angles"][angle_name] = angle
            triangle["angles"][triangle_name[i]] = angle
        
        # 면적 계산
        area = GeometryTools.calculate_triangle_area(points)
        calculations["areas"][triangle_name] = area
        triangle["area"] = area
        
        # 둘레 계산
        perimeter = sum(calculations["distances"][side] for side in sides)
        triangle["perimeter"] = perimeter
        
        # 삼각형 유형 분류
        triangle["type"] = _classify_triangle(calculations["distances"], sides, calculations["angles"])
        
        # 삼각형 중심 계산
        centers = GeometryTools.calculate_triangle_centers(points)
        for center_name, coords in centers.items():
            center_label = {"centroid": "G", "circumcenter": "O", "incenter": "I", "orthocenter": "H"}
            if center_name in center_label:
                calculations["coordinates"][center_label[center_name]] = coords
                triangle["properties"][center_name] = center_label[center_name]
    
    # 기존 정보 활용
    else:
        # 거리 정보가 있는 경우
        if all(side in calculations.get("distances", {}) for side in sides):
            # 변 길이로 삼각형 유형 분류
            distances = {side: calculations["distances"][side] for side in sides}
            triangle["type"] = _classify_triangle_by_sides(distances)
            
            # 변 길이로 각도 계산 (코사인 법칙)
            for i in range(3):
                a = calculations["distances"][sides[(i+1)%3]]
                b = calculations["distances"][sides[(i+2)%3]]
                c = calculations["distances"][sides[i]]
                
                cos_angle = (a**2 + b**2 - c**2) / (2 * a * b)
                # 수치 오류 방지
                cos_angle = max(min(cos_angle, 1.0), -1.0)
                
                angle = math.acos(cos_angle)
                angle_name = f"{triangle_name[(i+1)%3]}{triangle_name[i]}{triangle_name[(i+2)%3]}"
                calculations["angles"][angle_name] = angle
                triangle["angles"][triangle_name[i]] = angle
            
            # 헤론 공식으로 면적 계산
            a = calculations["distances"][sides[0]]
            b = calculations["distances"][sides[1]]
            c = calculations["distances"][sides[2]]
            s = (a + b + c) / 2
            area = math.sqrt(s * (s-a) * (s-b) * (s-c))
            calculations["areas"][triangle_name] = area
            triangle["area"] = area
            
            # 둘레 계산
            perimeter = a + b + c
            triangle["perimeter"] = perimeter
        
        # 각도 정보가 있는 경우
        elif "angles" in calculations:
            angles = {}
            angle_names = []
            
            # 삼각형 각도 찾기
            for angle_name, value in calculations["angles"].items():
                if len(angle_name) == 3 and all(v in triangle_name for v in angle_name):
                    angles[angle_name] = value
                    angle_names.append(angle_name)
            
            if len(angle_names) == 3:
                # 각도로 삼각형 유형 분류
                triangle["type"] = _classify_triangle_by_angles(angles)
                
                # 각도를 삼각형 정보에 저장
                for angle_name, value in angles.items():
                    middle_vertex = angle_name[1]
                    triangle["angles"][middle_vertex] = value
    
    # 삼각형 정보 저장
    calculations["triangles"][triangle_name] = triangle
    
    # 삼각형 해결 단계 추가
    calculations["steps"].append(f"삼각형 {triangle_name}에 대한 계산을 수행했습니다.")
    calculations["steps"].append(f"삼각형 유형: {_triangle_type_to_korean(triangle['type'])}")
    
    if triangle["area"]:
        calculations["steps"].append(f"삼각형 면적: {triangle['area']:.2f}")
    
    if triangle["perimeter"]:
        calculations["steps"].append(f"삼각형 둘레: {triangle['perimeter']:.2f}")

def handle_circle_problem(calculations: Dict[str, Any], problem_type: Dict[str, Any], parsed: Dict[str, Any]) -> None:
    """
    원 관련 문제 처리
    
    Args:
        calculations: 계산 결과 저장소
        problem_type: 문제 유형 정보
        parsed: 파싱된 문제 정보
    """
    # 원 정보 초기화
    if "circles" not in calculations:
        calculations["circles"] = {}
    
    # 원 식별
    circle_name = _identify_circle(parsed)
    if not circle_name:
        # 기본 원 O 가정
        circle_name = "O"
    
    # 원 속성 초기화
    circle = {
        "center": circle_name,
        "radius": None,
        "diameter": None,
        "circumference": None,
        "area": None,
        "points": [],
        "properties": {}
    }
    
    # 좌표가 있는 경우 원 계산
    if circle_name in calculations.get("coordinates", {}):
        center = calculations["coordinates"][circle_name]
        
        # 반지름 정보가 있는 경우
        radius = None
        if "radius" in calculations.get("circle", {}):
            radius = calculations["circle"]["radius"]
        elif "r" in calculations.get("variables", {}):
            radius = calculations["variables"]["r"]
        
        if radius:
            circle["radius"] = radius
            circle["diameter"] = 2 * radius
            circle["circumference"] = 2 * math.pi * radius
            circle["area"] = math.pi * radius ** 2
            
            # 원 위의 점 생성
            for i, angle in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
                point_name = f"P{i+1}"
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                calculations["coordinates"][point_name] = (x, y)
                circle["points"].append(point_name)
    
    # 기존 정보 활용
    else:
        # 반지름 정보가 있는 경우
        if "radius" in calculations.get("circle", {}):
            radius = calculations["circle"]["radius"]
            circle["radius"] = radius
            circle["diameter"] = 2 * radius
            circle["circumference"] = 2 * math.pi * radius
            circle["area"] = math.pi * radius ** 2
        
        # 지름 정보가 있는 경우
        elif "diameter" in calculations.get("circle", {}):
            diameter = calculations["circle"]["diameter"]
            circle["diameter"] = diameter
            circle["radius"] = diameter / 2
            circle["circumference"] = math.pi * diameter
            circle["area"] = math.pi * (diameter / 2) ** 2
        
        # 원의 면적 정보가 있는 경우
        elif "area" in calculations.get("areas", {}):
            area = calculations["areas"].get(circle_name, 0)
            if area:
                circle["area"] = area
                circle["radius"] = math.sqrt(area / math.pi)
                circle["diameter"] = 2 * circle["radius"]
                circle["circumference"] = 2 * math.pi * circle["radius"]
    
    # 원 정보 저장
    calculations["circles"][circle_name] = circle
    
    # 원 속성 저장
    if circle["radius"]:
        calculations["variables"]["r"] = circle["radius"]
    
    if circle["area"]:
        calculations["areas"][circle_name] = circle["area"]
    
    # 원 해결 단계 추가
    calculations["steps"].append(f"원 {circle_name}에 대한 계산을 수행했습니다.")
    
    if circle["radius"]:
        calculations["steps"].append(f"원의 반지름: {circle['radius']:.2f}")
    
    if circle["area"]:
        calculations["steps"].append(f"원의 면적: {circle['area']:.2f}")
    
    if circle["circumference"]:
        calculations["steps"].append(f"원의 둘레: {circle['circumference']:.2f}")
    
    # 원 관련 추가 계산
    _handle_circle_special_cases(calculations, circle, parsed)

def handle_coordinate_problem(calculations: Dict[str, Any], problem_type: Dict[str, Any], parsed: Dict[str, Any]) -> None:
    """
    좌표 기하학 문제 처리
    
    Args:
        calculations: 계산 결과 저장소
        problem_type: 문제 유형 정보
        parsed: 파싱된 문제 정보
    """
    # 좌표 문제 확인
    if not problem_type.get("coordinate", False):
        return
    
    # 좌표 초기화
    if "coordinates" not in calculations:
        calculations["coordinates"] = {}
    
    # 좌표 문제 해결 단계 추가
    calculations["steps"].append("좌표 기하학 문제를 해결합니다.")
    
    # 점 좌표 추출
    points = _extract_points_from_parsed(parsed)
    
    # 파싱된 좌표 처리
    for point, coords in points.items():
        calculations["coordinates"][point] = coords
    
    # 두 점 사이의 거리 계산
    for i, point1 in enumerate(points.keys()):
        for point2 in list(points.keys())[i+1:]:
            p1 = calculations["coordinates"][point1]
            p2 = calculations["coordinates"][point2]
            distance = GeometryTools.calculate_distance(p1, p2)
            calculations["distances"][f"{point1}{point2}"] = distance
            calculations["steps"].append(f"거리 |{point1}{point2}| = {distance:.2f}")
    
    # 선분의 중점 계산
    for i, point1 in enumerate(points.keys()):
        for point2 in list(points.keys())[i+1:]:
            p1 = calculations["coordinates"][point1]
            p2 = calculations["coordinates"][point2]
            midpoint = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
            midpoint_name = f"M_{point1}{point2}"
            calculations["coordinates"][midpoint_name] = midpoint
            calculations["steps"].append(f"선분 {point1}{point2}의 중점 {midpoint_name} = ({midpoint[0]:.2f}, {midpoint[1]:.2f})")
    
    # 직선 방정식 계산
    for i, point1 in enumerate(points.keys()):
        for point2 in list(points.keys())[i+1:]:
            p1 = calculations["coordinates"][point1]
            p2 = calculations["coordinates"][point2]
            
            if p1[0] != p2[0]:  # 수직선이 아닌 경우
                slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
                intercept = p1[1] - slope * p1[0]
                
                if "lines" not in calculations:
                    calculations["lines"] = {}
                
                line_name = f"{point1}{point2}"
                calculations["lines"][line_name] = {
                    "type": "standard",
                    "a": slope,
                    "b": -1,
                    "c": intercept,
                    "slope": slope,
                    "y_intercept": intercept,
                    "equation": f"y = {slope:.2f}x + {intercept:.2f}"
                }
                
                calculations["steps"].append(f"직선 {line_name}의 방정식: {calculations['lines'][line_name]['equation']}")
            else:  # 수직선인 경우
                if "lines" not in calculations:
                    calculations["lines"] = {}
                
                line_name = f"{point1}{point2}"
                calculations["lines"][line_name] = {
                    "type": "vertical",
                    "a": 1,
                    "b": 0,
                    "c": -p1[0],
                    "x_intercept": p1[0],
                    "equation": f"x = {p1[0]:.2f}"
                }
                
                calculations["steps"].append(f"직선 {line_name}의 방정식: {calculations['lines'][line_name]['equation']}")
    
    # 다각형 면적 계산
    if len(points) >= 3:
        # 볼록 다각형 가정
        point_list = list(points.keys())
        # 시계 방향으로 정렬된 점들
        point_coords = [calculations["coordinates"][p] for p in point_list]
        area = GeometryTools.calculate_polygon_area(point_coords)
        
        polygon_name = "".join(point_list)
        calculations["areas"][polygon_name] = area
        calculations["steps"].append(f"다각형 {polygon_name}의 면적: {area:.2f}")
    
    # 좌표 특수 케이스 처리
    _handle_coordinate_special_cases(calculations, parsed)

# 헬퍼 함수들
def _identify_triangle(parsed: Dict[str, Any]) -> str:
    """파싱된 데이터에서 삼각형 식별"""
    if "triangles" in parsed:
        return next(iter(parsed["triangles"].keys()), "ABC")
    
    # 삼각형 패턴 찾기
    triangle_pattern = r'三角形([A-Z][A-Z][A-Z])'
    for text in parsed.get("text", []):
        match = re.search(triangle_pattern, text)
        if match:
            return match.group(1)
    
    # 세 점 패턴 찾기
    points = []
    for element in parsed.get("geometric_objects", {}).values():
        if element.get("type") == "point":
            points.append(element.get("name", ""))
    
    if len(points) >= 3:
        return "".join(sorted(points[:3]))
    
    return "ABC"  # 기본값

def _identify_circle(parsed: Dict[str, Any]) -> str:
    """파싱된 데이터에서 원 식별"""
    if "circles" in parsed:
        return next(iter(parsed["circles"].keys()), "O")
    
    # 원 패턴 찾기
    circle_pattern = r'([A-Z])圆'
    for text in parsed.get("text", []):
        match = re.search(circle_pattern, text)
        if match:
            return match.group(1)
    
    # 원 중심 찾기
    for element in parsed.get("geometric_objects", {}).values():
        if element.get("type") == "circle":
            return element.get("center", "O")
    
    return "O"  # 기본값

def _extract_points_from_parsed(parsed: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    """파싱된 데이터에서 좌표 추출"""
    points = {}
    
    # 기하 객체에서 점 찾기
    for name, element in parsed.get("geometric_objects", {}).items():
        if element.get("type") == "point":
            if "coordinates" in element:
                coords = element["coordinates"]
                points[name] = (coords[0], coords[1])
    
    # 좌표 패턴 찾기
    coord_pattern = r'([A-Z])\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)'
    for text in parsed.get("text", []):
        for match in re.finditer(coord_pattern, text):
            point, x, y = match.groups()
            points[point] = (float(x), float(y))
    
    return points

def _classify_triangle(distances: Dict[str, float], sides: List[str], angles: Dict[str, float]) -> str:
    """삼각형 분류"""
    # 변 길이로 분류
    side_lengths = [distances[side] for side in sides]
    
    # 각도로 분류 (라디안)
    angle_values = list(angles.values())
    
    # 직각 삼각형 (π/2 = 90도)
    if any(abs(angle - math.pi/2) < 1e-10 for angle in angle_values):
        # 등변 직각 삼각형
        if side_lengths[0] == side_lengths[1] or side_lengths[1] == side_lengths[2] or side_lengths[0] == side_lengths[2]:
            return "isosceles_right"
        return "right"
    
    # 예각 삼각형 (모든 각이 π/2 미만)
    if all(angle < math.pi/2 for angle in angle_values):
        # 정삼각형 (모든 변이 같음)
        if side_lengths[0] == side_lengths[1] == side_lengths[2]:
            return "equilateral"
        # 이등변 삼각형 (두 변이 같음)
        if side_lengths[0] == side_lengths[1] or side_lengths[1] == side_lengths[2] or side_lengths[0] == side_lengths[2]:
            return "isosceles_acute"
        return "acute"
    
    # 둔각 삼각형 (한 각이 π/2 초과)
    if any(angle > math.pi/2 for angle in angle_values):
        # 이등변 둔각 삼각형
        if side_lengths[0] == side_lengths[1] or side_lengths[1] == side_lengths[2] or side_lengths[0] == side_lengths[2]:
            return "isosceles_obtuse"
        return "obtuse"
    
    # 기본적인 삼각형
    if side_lengths[0] == side_lengths[1] == side_lengths[2]:
        return "equilateral"
    if side_lengths[0] == side_lengths[1] or side_lengths[1] == side_lengths[2] or side_lengths[0] == side_lengths[2]:
        return "isosceles"
    
    return "scalene"

def _classify_triangle_by_sides(distances: Dict[str, float]) -> str:
    """변 길이로 삼각형 분류"""
    sides = list(distances.values())
    
    # 정삼각형 (모든 변이 같음)
    if abs(sides[0] - sides[1]) < 1e-10 and abs(sides[1] - sides[2]) < 1e-10:
        return "equilateral"
    
    # 이등변 삼각형 (두 변이 같음)
    if abs(sides[0] - sides[1]) < 1e-10 or abs(sides[1] - sides[2]) < 1e-10 or abs(sides[0] - sides[2]) < 1e-10:
        # 직각 삼각형 체크 (피타고라스 정리)
        sides.sort()
        if abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-10:
            return "isosceles_right"
        
        # 둔각 삼각형 체크 (가장 긴 변의 제곱이 다른 두 변의 제곱 합보다 큼)
        if sides[2]**2 > sides[0]**2 + sides[1]**2:
            return "isosceles_obtuse"
        
        return "isosceles_acute"
    
    # 일반 삼각형
    sides.sort()
    
    # 직각 삼각형 체크
    if abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-10:
        return "right"
    
    # 둔각 삼각형 체크
    if sides[2]**2 > sides[0]**2 + sides[1]**2:
        return "obtuse"
    
    # 예각 삼각형
    return "acute"

def _classify_triangle_by_angles(angles: Dict[str, float]) -> str:
    """각도로 삼각형 분류"""
    angle_values = list(angles.values())
    
    # 직각 삼각형 (π/2 = 90도)
    if any(abs(angle - math.pi/2) < 1e-10 for angle in angle_values):
        return "right"
    
    # 예각 삼각형 (모든 각이 π/2 미만)
    if all(angle < math.pi/2 for angle in angle_values):
        # 정삼각형 (모든 각이 같음 = π/3 = 60도)
        if all(abs(angle - math.pi/3) < 1e-10 for angle in angle_values):
            return "equilateral"
        
        # 이등변 삼각형 (두 각이 같음)
        if len(set([round(angle, 10) for angle in angle_values])) < 3:
            return "isosceles_acute"
        
        return "acute"
    
    # 둔각 삼각형 (한 각이 π/2 초과)
    if any(angle > math.pi/2 for angle in angle_values):
        # 이등변 둔각 삼각형 (두 각이 같음)
        if len(set([round(angle, 10) for angle in angle_values])) < 3:
            return "isosceles_obtuse"
        
        return "obtuse"
    
    return "scalene"

def _triangle_type_to_korean(triangle_type: str) -> str:
    """삼각형 유형을 한국어로 변환"""
    types = {
        "equilateral": "정삼각형",
        "isosceles": "이등변삼각형",
        "isosceles_acute": "예각 이등변삼각형",
        "isosceles_right": "직각 이등변삼각형",
        "isosceles_obtuse": "둔각 이등변삼각형",
        "right": "직각삼각형",
        "acute": "예각삼각형",
        "obtuse": "둔각삼각형",
        "scalene": "부등변삼각형",
        "unknown": "알 수 없는 삼각형"
    }
    
    return types.get(triangle_type, "알 수 없는 삼각형")

def _handle_circle_special_cases(calculations: Dict[str, Any], circle: Dict[str, Any], parsed: Dict[str, Any]) -> None:
    """원 특수 케이스 처리"""
    # 원에 내접하는 다각형
    if "triangles" in calculations and circle.get("radius"):
        for triangle_name, triangle in calculations["triangles"].items():
            # 내접원 확인
            if "properties" in triangle and "incenter" in triangle["properties"]:
                incenter = triangle["properties"]["incenter"]
                
                if incenter == circle["center"]:
                    # 내접원 속성 설정
                    calculations["steps"].append(f"삼각형 {triangle_name}의 내접원을 발견했습니다.")
                    
                    # 내접원의 반지름 계산: r = 2 * 면적 / 둘레
                    if triangle.get("area") and triangle.get("perimeter"):
                        inradius = 2 * triangle["area"] / triangle["perimeter"]
                        calculations["steps"].append(f"내접원의 반지름: {inradius:.2f}")
    
    # 원의 접선과 할선
    if "lines" in calculations:
        center = calculations["coordinates"].get(circle["center"])
        radius = circle.get("radius")
        
        if center and radius:
            for line_name, line in calculations["lines"].items():
                if line["type"] == "standard":
                    # 직선과 원의 거리 계산
                    a, b, c = line["a"], line["b"], line["c"]
                    distance = abs(a*center[0] + b*center[1] + c) / math.sqrt(a**2 + b**2)
                    
                    # 접선인 경우
                    if abs(distance - radius) < 1e-10:
                        calculations["steps"].append(f"직선 {line_name}은 원 {circle['center']}의 접선입니다.")
                    
                    # 할선인 경우
                    elif distance < radius:
                        chord_length = 2 * math.sqrt(radius**2 - distance**2)
                        calculations["steps"].append(f"직선 {line_name}은 원 {circle['center']}을 지나며, 호의 길이는 {chord_length:.2f}입니다.")

def _handle_coordinate_special_cases(calculations: Dict[str, Any], parsed: Dict[str, Any]) -> None:
    """좌표 특수 케이스 처리"""
    # 두 직선의 교점 계산
    if "lines" in calculations and len(calculations["lines"]) >= 2:
        lines = list(calculations["lines"].items())
        
        for i, (line1_name, line1) in enumerate(lines):
            for line2_name, line2 in lines[i+1:]:
                # 두 직선의 교점 계산
                if line1["type"] == "vertical" and line2["type"] == "standard":
                    # 수직선과 일반선의 교점
                    x = line1["x_intercept"]
                    y = line2["a"] * x + line2["y_intercept"]
                    
                    intersection_point = (x, y)
                    intersection_name = f"I_{line1_name}_{line2_name}"
                    
                    calculations["coordinates"][intersection_name] = intersection_point
                    calculations["steps"].append(f"직선 {line1_name}과 {line2_name}의 교점 {intersection_name} = ({x:.2f}, {y:.2f})")
                
                elif line2["type"] == "vertical" and line1["type"] == "standard":
                    # 수직선과 일반선의 교점
                    x = line2["x_intercept"]
                    y = line1["a"] * x + line1["y_intercept"]
                    
                    intersection_point = (x, y)
                    intersection_name = f"I_{line1_name}_{line2_name}"
                    
                    calculations["coordinates"][intersection_name] = intersection_point
                    calculations["steps"].append(f"직선 {line1_name}과 {line2_name}의 교점 {intersection_name} = ({x:.2f}, {y:.2f})")
                
                elif line1["type"] == "standard" and line2["type"] == "standard":
                    # 두 일반선의 교점
                    if abs(line1["a"] - line2["a"]) < 1e-10:
                        # 평행선
                        if abs(line1["y_intercept"] - line2["y_intercept"]) < 1e-10:
                            calculations["steps"].append(f"직선 {line1_name}과 {line2_name}은 일치합니다.")
                        else:
                            calculations["steps"].append(f"직선 {line1_name}과 {line2_name}은 평행합니다.")
                    else:
                        # 교점 계산
                        x = (line2["y_intercept"] - line1["y_intercept"]) / (line1["a"] - line2["a"])
                        y = line1["a"] * x + line1["y_intercept"]
                        
                        intersection_point = (x, y)
                        intersection_name = f"I_{line1_name}_{line2_name}"
                        
                        calculations["coordinates"][intersection_name] = intersection_point
                        calculations["steps"].append(f"직선 {line1_name}과 {line2_name}의 교점 {intersection_name} = ({x:.2f}, {y:.2f})")
    
    # 점과 직선 사이의 거리 계산
    if "lines" in calculations and len(calculations["coordinates"]) > 0:
        for point_name, point in calculations["coordinates"].items():
            for line_name, line in calculations["lines"].items():
                # 점이 선분의 끝점인지 확인
                if point_name in line_name:
                    continue
                
                if line["type"] == "standard":
                    a, b, c = line["a"], -1, line["y_intercept"]
                    distance = abs(a*point[0] + b*point[1] + c) / math.sqrt(a**2 + b**2)
                    
                    distance_name = f"d_{point_name}_{line_name}"
                    calculations["distances"][distance_name] = distance
                    calculations["steps"].append(f"점 {point_name}에서 직선 {line_name}까지의 거리: {distance:.2f}")
                
                elif line["type"] == "vertical":
                    distance = abs(point[0] - line["x_intercept"])
                    
                    distance_name = f"d_{point_name}_{line_name}"
                    calculations["distances"][distance_name] = distance
                    calculations["steps"].append(f"점 {point_name}에서 직선 {line_name}까지의 거리: {distance:.2f}") 