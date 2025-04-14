import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from graph import create_geometry_solver_graph
from models import GeometryState

# 환경 변수 로드
load_dotenv()

def solve_geometry_problem(problem_text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    기하학 문제를 해결하고 GeoGebra 명령어와 해설을 제공하는 메인 함수
    
    Args:
        problem_text: 중국어 기하학 문제 텍스트
        output_file: 결과를 저장할 파일 경로 (선택 사항)
        
    Returns:
        해결 결과 딕셔너리 (GeoGebra 명령어, 해설 등 포함)
    """
    # 그래프 생성
    solver_graph = create_geometry_solver_graph()
    
    # 초기 상태 설정
    initial_state = GeometryState(input_problem=problem_text)
    
    # 그래프 실행
    result = solver_graph.invoke(initial_state)
    
    # 결과 반환
    # result 객체를 딕셔너리로 변환하여 접근
    result_dict = dict(result)
    return {
        "problem": problem_text,
        "geogebra_commands": result_dict.get("geogebra_commands"),
        "explanation": result_dict.get("explanation"),
        "difficulty": result_dict.get("difficulty"),
        "parsed_elements": result_dict.get("parsed_elements"),
        "error": result_dict.get("errors")
    }

def display_result(result: Dict[str, Any]):
    """결과 출력"""
    print("\n" + "=" * 80)
    print(f"문제: {result['problem']}")
    print("=" * 80)
    
    # GeoGebra 명령어 출력
    print("\nGeoGebra 명령어:")
    for cmd in result["geogebra_commands"]:
        print(f"  {cmd}")
    
    # 해설 요약 출력
    print("\n해설 요약:")
    if result["explanation"]:
        # 중국어 해설의 첫 100자만 표시 (너무 길면 생략)
        explanation_preview = result["explanation"][:100] + "..." if len(result["explanation"]) > 100 else result["explanation"]
        print(f"  {explanation_preview}")
    else:
        print("  해설이 생성되지 않았습니다.")
    
    # 오류 출력
    if result["error"]:
        print("\n오류:")
        print(f"  {result['error']}")
    
    print("\n" + "=" * 80)

def save_result(result: dict, output_dir: str = "output"):
    """결과를 JSON 및 GeoGebra 명령어 파일로 저장"""
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 문제 텍스트에서 파일명 생성
    problem_short = result["problem"][:20].replace(" ", "_").replace(".", "")
    base_filename = f"{problem_short}_{len(result['geogebra_commands'])}_commands"
    
    # JSON 결과 저장
    with open(f"{output_dir}/{base_filename}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # GeoGebra 명령어 저장
    with open(f"{output_dir}/{base_filename}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(result["geogebra_commands"]))
    
    # 해설 저장 (마크다운)
    with open(f"{output_dir}/{base_filename}.md", "w", encoding="utf-8") as f:
        f.write(result["explanation"])
    
    print(f"\n결과가 {output_dir} 디렉토리에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    print("\n기하학 문제 해결 시스템 (GeoGebra 명령어 생성)\n")
    
    # 문제 입력 또는 예제 선택
    use_example = input("예제 문제를 사용하시겠습니까? (y/n): ").lower() == 'y'
    
    if use_example:
        # 예제 문제 목록
        examples = [
            "在△ABC中，∠C=90°，AB=5，BC=3，求AC的长度。",
            "已知圆O的半径为5，点P在圆上，点Q是直径OP上的中点，求PQ的长度。",
            "在坐标平面中，点A(1,2)，点B(4,6)，求线段AB的中点坐标。",
            "已知等边三角形ABC的边长为6，求三角形的高和面积。",
            "在平面直角坐标系中，点A(0,0)，点B(3,0)，点C(0,4)，证明△ABC是直角三角形，并求其面积。"
        ]
        
        print("\n예제 문제 목록:")
        for i, example in enumerate(examples):
            print(f"{i+1}. {example}")
        
        choice = int(input("\n선택할 예제 번호 (1-5): ")) - 1
        problem_text = examples[choice]
    else:
        # 사용자 직접 입력
        problem_text = input("\n중국어 기하학 문제를 입력하세요: ")
    
    # 문제 해결
    print("\n문제 해결 중...")
    result = solve_geometry_problem(problem_text)
    
    # 결과 출력
    display_result(result)
    
    # 결과 저장
    save = input("\n결과를 저장하시겠습니까? (y/n): ").lower() == 'y'
    if save:
        save_result(result)

def test_with_examples():
    """예제 문제로 테스트 수행"""
    examples = [
        "在△ABC中，∠C=90°，AB=5，BC=3，求AC的长度。",
        "已知圆O的半径为5，点P在圆上，点Q是直径OP上的中点，求PQ的长度。"
    ]
    
    results = []
    for example in examples:
        print(f"\n테스트 중: {example}")
        result = solve_geometry_problem(example)
        results.append(result)
        display_result(result)
    
    # 결과 저장
    for result in results:
        save_result(result, "test_output")
    
    print(f"\n모든 테스트 결과가 test_output 디렉토리에 저장되었습니다.")

if __name__ == "__main__":
    # 메인 함수 실행
    main()
    
    # 테스트 실행 (주석 처리)
    # test_with_examples() 