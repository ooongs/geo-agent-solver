"""
GeoGebra Command Agent Module

This module provides an agent for generating GeoGebra commands from structured data.
"""

from typing import Dict, Any, List, Optional
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from geo_prompts import GEOGEBRA_COMMAND_PROMPT, COMMAND_GENERATION_TEMPLATE
from utils.llm_manager import LLMManager
from agents.tools import get_common_tools
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
    tools = get_tools()
    
    # 공통 도구 추가
    common_tools = get_common_tools()
    tools.extend(common_tools)
    
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
        "json_template": COMMAND_GENERATION_TEMPLATE,
        "retrieved_commands": json.dumps(state.retrieved_commands),
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

def get_tools():
    """
    Get the list of tools for the GeoGebra Command Agent.
    
    Returns:
        A list of StructuredTool objects.
    """
    # 기존 도구 제거, 통합 도구로 대체
    return []


        
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