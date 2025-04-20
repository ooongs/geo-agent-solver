import os
import json
from typing import Dict, Any, Optional, Callable, Awaitable
from dotenv import load_dotenv
import sys
import asyncio
from datetime import datetime
from graph import create_geometry_solver_graph
from models import GeometryState


# 환경 변수 로드
load_dotenv()

async def solve_geometry_problem(
    problem_text: str, 
    progress_callback: Optional[Callable[[str, str, Optional[Dict[str, Any]]], Awaitable[None]]] = None,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    기하학 문제를 해결하고 GeoGebra 명령어와 해설을 제공하는 메인 함수
    
    Args:
        problem_text: 중국어 기하학 문제 텍스트
        progress_callback: 진행 상황을 받을 콜백 함수
        output_file: 결과를 저장할 파일 경로 (선택 사항)
        
    Returns:
        해결 결과 딕셔너리 (GeoGebra 명령어, 해설 등 포함)
    """
    # 그래프 생성
    solver_graph = create_geometry_solver_graph()
    
    # 초기 상태 설정
    initial_state = GeometryState(input_problem=problem_text)
    
    # 스트리밍 결과 기록 변수
    streaming_results = []
    
    # 최종 상태를 추적할 변수
    final_state = None
    
    # 디버그 모드로 그래프 실행 (스트리밍)
    if progress_callback:
        await progress_callback("system", "그래프 실행 시작", {"status": "starting"})
        
        try:
            # 마지막 상태 업데이트를 추적하기 위한 변수들
            last_node = None
            node_results = {}
            
            async for chunk in solver_graph.astream(
                initial_state,
                stream_mode=["debug", "updates", "values"],
                config={
                    "recursion_limit": 30
                }
            ):
                stream_mode, data = chunk
                streaming_results.append(data)
                
                if stream_mode == "debug":
                    # 디버그 이벤트 처리
                    if data["type"] == "task":
                        node_name = data["payload"]["name"]
                        last_node = node_name
                        await progress_callback(
                            "node_start", 
                            f"{node_name} 작업 시작", 
                            {"node": node_name, "payload": data["payload"]}
                        )
                    
                    elif data["type"] == "task_result":
                        node_name = data["payload"]["name"]
                        error = data["payload"]["error"]
                        result = data["payload"]["result"]
                        
                        # 노드 결과 저장
                        if result:
                            node_results[node_name] = result
                        
                        if error:
                            await progress_callback(
                                "node_error", 
                                f"{node_name} 실행 중 오류 발생", 
                                {"node": node_name, "error": error}
                            )
                        else:
                            await progress_callback(
                                "node_complete", 
                                f"{node_name} 작업 완료", 
                                {"node": node_name, "result": result}
                            )
                
                elif stream_mode == "updates":
                    # 상태 업데이트 처리
                    node_name = list(data.keys())[0]
                    update_data = data[node_name]
                    await progress_callback(
                        "state_update", 
                        f"{node_name}에서 상태 업데이트", 
                        {"node": node_name, "data": update_data}
                    )
                
                elif stream_mode == "values":
                    # 전체 상태 값 추적
                    final_state = data
                    
                    # 프론트엔드에 전체 상태 업데이트 전송
                    if progress_callback and last_node:
                        try:
                            # GeometryState 객체를 직접 전달하여 JSON 직렬화 오류가 발생할 수 있으므로
                            # final_state가 GeometryState 객체라면 to_dict() 메서드를 사용해 변환
                            # 서버의 make_json_serializable 함수가 이를 처리하므로 여기서는 객체를 그대로 전달
                            
                            # ConstructionPlan 객체가 있는 경우 먼저 변환
                            if hasattr(final_state, 'construction_plan') and final_state.construction_plan:
                                try:
                                    if hasattr(final_state.construction_plan, 'to_dict'):
                                        # 직접 변환을 시도합니다
                                        final_state.construction_plan = final_state.construction_plan.to_dict()
                                except Exception as cp_error:
                                    print(f"ConstructionPlan 변환 실패: {str(cp_error)}")
                                    # 실패하면 None으로 설정
                                    final_state.construction_plan = None
                            
                            await progress_callback(
                                "state_full_update", 
                                f"전체 상태 업데이트", 
                                {"node": last_node, "data": final_state}
                            )
                        except Exception as e:
                            print(f"상태 업데이트 중 오류 발생: {str(e)}")
                            # 오류가 발생해도 계속 진행
            
            # 마지막 상태가 없는 경우를 대비해 기본 실행 결과 사용
            if not final_state:
                print("스트리밍에서 최종 상태를 얻지 못했습니다. 기본 실행 결과를 사용합니다.")
                result = await solver_graph.ainvoke(
                    initial_state,
                    config={
                        "recursion_limit": 30
                    }
                )
                final_state = dict(result)
        
        except GeneratorExit:
            print("GeneratorExit: 스트림이 비정상적으로 종료되었습니다. 이는 클라이언트 연결 문제 또는 소켓 타임아웃 때문일 수 있습니다.")
            if not final_state:
                print("스트림이 종료되어 결과를 가져오는 다른 방법을 시도합니다.")
                try:
                    # 스트림이 중단되었으므로 대체 방법으로 결과 가져오기
                    result = await solver_graph.ainvoke(
                        initial_state,
                        config={
                            "recursion_limit": 30
                        }
                    )
                    final_state = dict(result)
                    
                    # 복구 성공 알림
                    await progress_callback("system", "스트림이 종료되어 대체 방법으로 결과를 가져왔습니다.", {"status": "recovered"})
                    
                except Exception as recovery_error:
                    print(f"결과 복구 실패: {str(recovery_error)}")
                    await progress_callback("system_error", f"결과 복구 실패: {str(recovery_error)}", {"error": str(recovery_error)})
                    raise recovery_error
            else:
                # 일부 결과는 이미 있으므로 현재 상태로 계속 진행
                await progress_callback("system", "스트림이 일부 종료되었지만 일부 결과는 유효합니다.", {"status": "partial_results"})
            
        except Exception as e:
            await progress_callback("system_error", f"그래프 실행 오류: {str(e)}", {"error": str(e)})
            raise e
            
        await progress_callback("system", "그래프 실행 완료", {"status": "completed"})
    else:
        # 기존 로직: 스트리밍 없이 최종 결과만 반환
        result = await solver_graph.ainvoke(
            initial_state,
            config={
                "recursion_limit": 30
            }
        )
        final_state = dict(result)
    
    # GeometryState 객체를 직접 반환하면 JSON 직렬화 오류가 발생할 수 있으므로
    # 딕셔너리로 변환하여 반환
    if isinstance(final_state, GeometryState):
        # 더 확실하게 모든 필드를 직접 추출합니다
        result_dict = {
            "problem": problem_text,
            "geogebra_commands": final_state.geogebra_commands if final_state.geogebra_commands else [],
            "explanation": final_state.explanation if final_state.explanation else "",
            "parsed_elements": final_state.parsed_elements,
            "error": final_state.errors,
            "streaming_results": streaming_results if progress_callback else None,
            # 아래 필드 추가
            "is_valid": final_state.is_valid,
            "problem_analysis": final_state.problem_analysis,
            "calculation_results": final_state.calculation_results
        }
    else:
        # 이미 딕셔너리 형태라면 더 많은 필드를 포함시킵니다
        result_dict = {
            "problem": problem_text,
            "geogebra_commands": final_state.get("geogebra_commands", []),
            "explanation": final_state.get("explanation", ""),
            "parsed_elements": final_state.get("parsed_elements", {}),
            "error": final_state.get("errors"),
            "streaming_results": streaming_results if progress_callback else None,
            # 아래 필드 추가
            "is_valid": final_state.get("is_valid", False),
            "problem_analysis": final_state.get("problem_analysis", {}),
            "calculation_results": final_state.get("calculation_results", {})
        }
    
    # 디버그 정보 출력
    if final_state.geogebra_commands:
        print(f"\n디버그: geogebra_commands 타입: {type(final_state.geogebra_commands)}")
        print(f"디버그: geogebra_commands 길이: {len(final_state.geogebra_commands) if final_state.geogebra_commands else 0}")
        print(f"디버그: geogebra_commands 내용: {final_state.geogebra_commands[:3] if final_state.geogebra_commands else '없음'}")
    
    return result_dict

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
    base_filename = f"{problem_short}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_commands"
    
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

async def main_async():
    """비동기 메인 실행 함수"""
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
    result = await solve_geometry_problem(problem_text)
    
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


def main():
    """메인 함수 - 비동기 함수 호출을 위한 래퍼"""
    asyncio.run(main_async())


if __name__ == "__main__":
    # 메인 함수 실행
    main()
    
    # 테스트 실행 (주석 처리)