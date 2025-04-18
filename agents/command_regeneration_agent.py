from typing import List
from geo_prompts import COMMAND_REGENERATION_PROMPT, COMMAND_REGENERATION_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from utils.json_parser import safe_parse_llm_json_output
from models.validation_models import RegenerationResult
from agents.tools import get_common_tools
from langchain.agents import AgentExecutor, create_openai_functions_agent
import json
import re
from config import MAX_ATTEMPTS

def command_regeneration_agent(state):
    """
    GeoGebra 명령어 재생성 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        재생성된 명령어가 추가된 상태 객체
    """
    # 시도 횟수 증가
    state.command_regeneration_attempts += 1
    
    # 최대 시도 횟수 초과 시 중단
    if state.command_regeneration_attempts > MAX_ATTEMPTS:
        print(f"[WARNING] 최대 명령어 재생성 시도 횟수({MAX_ATTEMPTS})를 초과했습니다.")
        return state
    
    # LLM 초기화
    llm = LLMManager.get_geogebra_command_llm(temperature=0.2)  # 약간의 창의성 허용
    
    # 공통 도구 가져오기
    tools = get_common_tools()
    
    # 원본 명령어 저장
    original_commands = state.geogebra_commands
    
    # 에이전트 생성
    agent = create_openai_functions_agent(llm, tools, COMMAND_REGENERATION_PROMPT)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 에이전트 실행
    try:
        result = agent_executor.invoke({
            "problem": state.input_problem,
            "original_commands": str(original_commands),
            "validation_result": str(state.validation),
            "attempt_count": state.command_regeneration_attempts,
            "json_template": COMMAND_REGENERATION_JSON_TEMPLATE,
            "agent_scratchpad": ""
        })
        
        # 결과 분석
        output = result["output"] if "output" in result else result.get("content", "")
        
        try:
            # Pydantic 모델을 사용하여 파싱 시도
            parsed_result = safe_parse_llm_json_output(output, dict)
            
            if not parsed_result:
                # JSON 파싱 실패시 백업 파싱
                print(f"[WARNING] safe_parse_llm_json_output 반환 값이 비어 있습니다")
                regenerated_commands = _extract_commands_from_text(output)
                analysis = "재생성 결과를 JSON 형식으로 파싱할 수 없어 텍스트에서 명령어를 추출했습니다."
                fixed_issues = []
            else:
                # 성공적으로 파싱된 딕셔너리 사용
                try:
                    # commands 필드가 리스트인 경우 처리
                    if 'commands' in parsed_result and isinstance(parsed_result['commands'], list):
                        # 이미 리스트 형태이므로 그대로 사용, RegenerationResult 모델의 commands 필드는 List[str]임
                        pass
                        
                    regeneration_result = RegenerationResult(**parsed_result)
                    regenerated_commands = regeneration_result.commands
                    analysis = regeneration_result.analysis
                    fixed_issues = regeneration_result.fixed_issues
                except Exception as e:
                    print(f"[WARNING] 파싱된 결과를 RegenerationResult로 변환 실패: {str(e)}")
                    # commands가 직접 리스트로 전달될 수 있음
                    if isinstance(parsed_result.get('commands'), list):
                        regenerated_commands = parsed_result.get('commands')
                        analysis = parsed_result.get('analysis', "Analysis not available")
                        fixed_issues = parsed_result.get('fixed_issues', [])
                    else:
                        regenerated_commands = _extract_commands_from_text(output)
                        analysis = "재생성 결과에서 명령어를 추출할 수 없어 텍스트에서 명령어를 추출했습니다."
                        fixed_issues = []
        except Exception as e:
            # 파싱 실패 시 텍스트에서 명령어 추출
            print(f"[WARNING] JSON 파싱 실패: {str(e)}")
            regenerated_commands = _extract_commands_from_text(output)
            analysis = "재생성 결과를 JSON 형식으로 파싱할 수 없어 텍스트에서 명령어를 추출했습니다."
            fixed_issues = []
        
        # 명령어가 추출되지 않았다면 원본 명령어 유지
        if not regenerated_commands:
            print("[WARNING] 재생성된 명령어가 없어 원본 명령어를 유지합니다.")
            regenerated_commands = original_commands
            
    except Exception as e:
        print(f"[ERROR] 명령어 재생성 에이전트 실행 오류: {str(e)}")
        regenerated_commands = original_commands
        analysis = f"에이전트 실행 오류: {str(e)}"
        fixed_issues = []
    
    # 상태 업데이트
    state.regenerated_commands = regenerated_commands
    state.geogebra_commands = regenerated_commands  # 검증을 위해 기존 명령어 교체
    
    # 디버그 정보
    print(f"[DEBUG] Command regeneration attempt {state.command_regeneration_attempts}/{MAX_ATTEMPTS}")
    print(f"[DEBUG] Analysis: {analysis}")
    if fixed_issues:
        print(f"[DEBUG] Fixed issues: {fixed_issues}")
    
    return state

def _extract_commands_from_text(text: str) -> List[str]:
    """
    텍스트에서 GeoGebra 명령어 추출
    
    Args:
        text: 명령어가 포함된 텍스트
        
    Returns:
        명령어 목록
    """
    # 명령어 블록 패턴
    command_block_pattern = r'```(?:geogebra)?\s*([\s\S]*?)\s*```'
    command_block_match = re.search(command_block_pattern, text)
    
    if command_block_match:
        # 코드 블록에서 명령어 추출
        commands_text = command_block_match.group(1)
        lines = [line.strip() for line in commands_text.strip().split("\n") if line.strip()]
    else:
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
        if '=' in line or ':' in line or '(' in line or '[' in line:
            commands.append(line)
    
    return commands 