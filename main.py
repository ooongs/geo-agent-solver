import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import sys

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
        # 실제 GeoGebra 명령어만 추출하여 저장
        real_commands = []
        commands_started = False
        
        for cmd in result["geogebra_commands"]:
            # 명령어 정리 (따옴표 제거)
            if cmd.startswith("\"") and cmd.endswith("\","):
                cmd = cmd[1:-2]  # 시작 따옴표와 끝의 따옴표+쉼표 제거
            elif cmd.startswith("\"") and cmd.endswith("\""):
                cmd = cmd[1:-1]  # 시작과 끝의 따옴표만 제거
            
            # commands 섹션이 시작되면 플래그 설정
            if cmd == "commands": 
                commands_started = True
                continue
            
            # 다음과 같은 경우는 스킵
            if cmd.startswith("analysis") or cmd.startswith("fixed_issues") or cmd == "]" or cmd == "[":
                continue
                
            real_commands.append(cmd)
        
        # 명령어들을 하나의 문자열로 합쳐서 저장
        f.write("\n".join(real_commands))
    
    # 해설 저장 (마크다운)
    with open(f"{output_dir}/{base_filename}.md", "w", encoding="utf-8") as f:
        f.write(result["explanation"])
    
    print(f"\nResults saved in {output_dir} directory.")

def main():
    """메인 실행 함수"""
    print("\nGeometry problem solver (GeoGebra command generation)\n")
    
    # 명령줄 인수 확인
    if len(sys.argv) > 1:
        # 명령줄에서 문제 텍스트 받기
        problem_text = sys.argv[1]
    else:
        # 문제 입력 또는 예제 선택
        use_example = input("Use example problem? (y/n): ").lower() == 'y'
        
        if use_example:
            # 예제 문제 목록
            examples = [
                "在△ABC中，∠C=90°，AB=5，BC=3，求AC的长度。",
                "已知圆O的半径为5，点P在圆上，点Q是直径OP上的中点，求PQ的长度。",
                "在坐标平面中，点A(1,2)，点B(4,6)，求线段AB的中点坐标。",
                "已知等边三角形ABC的边长为6，求三角形的高和面积。",
                "在平面直角坐标系中，点A(0,0)，点B(3,0)，点C(0,4)，证明△ABC是直角三角形，并求其面积。",
                "△ABC为正三角形，D、E为BC上的点，且有∠CAD=∠DAE=∠EAB,取AD的中点F，连接BF交AE于G"
            ]
            
            print("\nExample problem list:")
            for i, example in enumerate(examples):
                print(f"{i+1}. {example}")
            
            choice = int(input("\nSelect example number (1-6): ")) - 1
            problem_text = examples[choice]
        else:
            # 사용자 직접 입력
            problem_text = input("\nEnter Chinese geometry problem: ")
    
    # 문제 해결
    print("\nSolving problem...")
    result = solve_geometry_problem(problem_text)
    
    # 결과 출력
    display_result(result)
    
    # 결과 저장 (명령줄 인수로 넘어왔을 때는 자동 저장)
    if len(sys.argv) > 1:
        save_result(result)
        print(f"\nResults saved in output directory.")
    else:
        save = input("\nSave results? (y/n): ").lower() == 'y'
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