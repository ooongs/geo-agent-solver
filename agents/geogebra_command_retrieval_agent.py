"""
GeoGebra 명령어 검색 에이전트 모듈

이 모듈은 SentenceBERT와 pgvector를 사용하여 작도 계획에 적합한 GeoGebra 명령어를 검색합니다.
"""

from typing import Dict, Any, List, Optional
from db.retrieval import CommandRetrieval
from utils.llm_manager import LLMManager
import json
from geo_prompts import COMMAND_SELECTION_PROMPT, COMMAND_SELECTION_TEMPLATE

def geogebra_command_retrieval_agent(state):
    """
    GeoGebra 명령어 검색 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        명령어가 추가된 상태 객체
    """
    print("[INFO] GeoGebra 명령어 검색 에이전트 실행 중...")
    
    # 검색 객체 초기화
    retrieval = CommandRetrieval()
    
    # 명령어 저장 리스트 초기화
    state.retrieved_commands = []
    
    # construction_plan이 없는 경우 예외 처리
    if not hasattr(state, "construction_plan") or not state.construction_plan:
        print("[WARN] 작도 계획이 없습니다. 검색을 진행할 수 없습니다.")
        return state
    
    # 작도 계획 가져오기
    plan = state.construction_plan
    reranker_agent_input = {
        "title": plan.title,
        "description": plan.description,
        "steps": [],
        "final_result": plan.final_result
    }
    
    for step in plan.steps:
        # 각 단계별 검색된 명령어 저장 리스트
        retrieved_commands = []
        
        # geogebra_command가 있는 경우 DB에서 해당 명령어 검색
        if step.geogebra_command:
            # DB에서 command 속성으로 대소문자 구분 없이 검색
            command_search_results = retrieval.search_commands_by_command(step.geogebra_command)
            if command_search_results:
                retrieved_commands.extend(command_search_results)
        
        # 검색 쿼리 생성
        query = f"{step.description} {step.task_type}"
        if step.command_type:
            query += f" {step.command_type}"
        
        # SentenceBERT로 검색 실행
        search_results = retrieval.cosine_search(
            query, top_k=5
        )
        
        if search_results:
            # 이미 command 속성으로 찾은 결과와 중복 체크하여 병합
            existing_syntaxes = {cmd["syntax"].lower() for cmd in retrieved_commands}
            
            for result in search_results:
                if result["syntax"].lower() in existing_syntaxes:
                    # 중복된 결과가 있으면 기존 결과의 점수 업데이트
                    for existing_cmd in retrieved_commands:
                        if existing_cmd["syntax"].lower() == result["syntax"].lower():
                            # score 값 병합 또는 업데이트
                            if "score" in result:
                                existing_cmd["sbert_score"] = result["score"]
                                # DB 검색 결과에 높은 가중치 부여
                                existing_cmd["score"] = result["score"] + 0.5
                else:
                    # 중복되지 않은 결과 추가
                    retrieved_commands.append(result)
        
        # 검색 결과가 있으면 점수 기준으로 정렬
        if retrieved_commands:
            sorted_commands = sorted(
                retrieved_commands,
                key=lambda x: x.get("score", 0),
                reverse=True
            )
            
            
            # 단계에 검색된 명령어 저장
            reranker_agent_input["steps"].append({
                "step_id": step.step_id,
                "description": step.description,
                "task_type": step.task_type,
                "operation_type": step.operation_type,
                "parameters": step.parameters,
                "retrieved_commands": sorted_commands
            })
    
    
    print(f"[INFO] {len(reranker_agent_input["steps"])}개 단계에 대한 명령어 검색 완료")
    
    # 명령어 선택 에이전트 호출
    state = command_selection_agent(state, reranker_agent_input)
    
    return state

def command_selection_agent(state, reranker_agent_input):
    """
    검색된 명령어 중 최적의 명령어를 선택하는 에이전트
    
    Args:
        state: 검색된 명령어가 포함된 상태 객체
        reranker_agent_input: 명령어 검색 결과가 포함된 입력 데이터
        
    Returns:
        선택된 명령어가 추가된 상태 객체
    """
    print("[INFO] 명령어 선택 에이전트 실행 중...")
    
    if not hasattr(state, "construction_plan") or not state.construction_plan:
        print("[WARN] 작도 계획이 없습니다. 명령어 선택을 진행할 수 없습니다.")
        return state
    
    # LLM 인스턴스 생성
    llm = LLMManager.get_command_selection_llm()
    
    # LLM 호출하여 명령어 선택
    chain = COMMAND_SELECTION_PROMPT | llm
    result = chain.invoke({
        "json_template": COMMAND_SELECTION_TEMPLATE,
        "reranker_agent_input": reranker_agent_input
    })
    
    # 응답 텍스트 파싱
    try:
        # JSON 형식 응답 추출
        response_text = result.content

        retrieved_commands = []
        
        # JSON 부분 추출
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            selection_result = json.loads(json_str)
            
            # selected_commands 배열 처리
            if "selected_commands" in selection_result:
                # 단계별 명령어 매핑을 위한 사전 생성
                step_commands = {}
                for step_data in reranker_agent_input["steps"]:
                    step_commands[step_data["step_id"]] = step_data["retrieved_commands"]
                
                # 각 선택된 명령어 처리
                for cmd_selection in selection_result["selected_commands"]:
                    step_id = cmd_selection.get("step_id")
                    command_id = cmd_selection.get("command_id")
                    reason = cmd_selection.get("reason", "")
                    
                    # step_id에 해당하는 ConstructionStep 찾기
                    step = next((s for s in state.construction_plan.steps if s.step_id == step_id), None)
                    if step and step_id in step_commands:
                        step_retrieved_commands = step_commands[step_id]
                        
                        # command_id에 해당하는 명령어 찾기
                        selected_cmd = next((cmd for cmd in step_retrieved_commands if cmd.get("command_id") == command_id), None)
                        
                        if selected_cmd:
                            # 선택된 명령어 정보 복사
                            selected_command = {
                                "command": selected_cmd.get("command", ""),
                                "syntax": selected_cmd.get("syntax", ""),
                                "description": selected_cmd.get("description", ""),
                                "examples": selected_cmd.get("examples", []),
                                "note": selected_cmd.get("note", ""),
                                "selection_reason": reason
                            }
                            retrieved_commands.append(selected_command)

                            # ConstructionStep의 selected_command에 저장
                            step.selected_command = selected_command
                        else:
                            # 첫 번째 명령어를 기본값으로 선택
                            if step_retrieved_commands:
                                step.selected_command = step_retrieved_commands[0]
                                retrieved_commands.append(step_retrieved_commands[0])
                    else:
                        print(f"[WARN] step_id {step_id}에 해당하는 단계를 찾을 수 없습니다.")
            else:
                print(f"[WARN] 응답에 selected_commands가 없습니다: {selection_result}")
                _select_default_commands(state, reranker_agent_input)
        else:
            print(f"[WARN] JSON 응답을 찾을 수 없습니다: {response_text}")
            # 모든 단계에 첫 번째 명령어를 기본값으로 선택
            _select_default_commands(state, reranker_agent_input)
            
        state.retrieved_commands = retrieved_commands
            
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 오류: {e}, 응답: {response_text}")
        # 모든 단계에 첫 번째 명령어를 기본값으로 선택
        _select_default_commands(state, reranker_agent_input)
        
    except Exception as e:
        print(f"[ERROR] 명령어 선택 오류: {e}")
        # 모든 단계에 첫 번째 명령어를 기본값으로 선택
        _select_default_commands(state, reranker_agent_input)
    
    print("[INFO] 모든 단계에 대한 명령어 선택 완료")
    
    return state

def _select_default_commands(state, reranker_agent_input):
    """모든 단계에 첫 번째 명령어를 기본값으로 선택"""
    # 단계별 명령어 매핑을 위한 사전 생성
    step_commands = {}
    for step_data in reranker_agent_input["steps"]:
        step_commands[step_data["step_id"]] = step_data["retrieved_commands"]
    
    # 선택된 명령어를 저장할 리스트
    retrieved_commands = []
    
    # 모든 단계에 대해 첫 번째 명령어 선택
    for step in state.construction_plan.steps:
        if step.step_id in step_commands and step_commands[step.step_id]:
            first_cmd = step_commands[step.step_id][0]
            
            # 선택된 명령어 정보 복사
            selected_command = {
                "command": first_cmd.get("command", ""),
                "syntax": first_cmd.get("syntax", ""),
                "description": first_cmd.get("description", ""),
                "examples": first_cmd.get("examples", []),
                "note": first_cmd.get("note", "")
            }
            
            # ConstructionStep의 selected_command에 저장
            step.selected_command = selected_command
            
            # retrieved_commands 리스트에 추가
            retrieved_commands.append(selected_command)
    
    # 상태 객체에 retrieved_commands 설정
    state.retrieved_commands = retrieved_commands
            