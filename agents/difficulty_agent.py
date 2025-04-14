from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import DIFFICULTY_PROMPT
from config import DEFAULT_MODEL
def difficulty_agent(state):
    """
    기하학 문제의 난이도를 평가하는 에이전트
    
    Args:
        state: 현재 상태(GeometryState 객체), input_problem, parsed_elements 속성 포함
        
    Returns:
        difficulty 정보가 추가된 상태 딕셔너리
    """
    # LLM 설정
    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=0.1,
        messages=[{"role": "system", "content": "您是一个几何教育专家，能够根据几何问题的特点评估其难度和复杂性。"}]
    )
    
    # 프롬프트 체인 생성 및 실행
    chain = DIFFICULTY_PROMPT | llm
    result = chain.invoke({
        "problem": state.input_problem,
        "parsed_elements": str(state.parsed_elements)
    })
    
    # 결과를 구조화된 형태로 변환
    try:
        difficulty = {
            "level": result.content.get("level", 3),
            "factors": result.content.get("factors", []),
            "recommended_approach": result.content.get("approach", "coordinate_geometry")
        }
    except AttributeError:
        # 응답 형식이 예상과 다를 경우 기본값 설정
        difficulty = {
            "level": 3,
            "factors": ["형태가 복잡함"],
            "recommended_approach": "coordinate_geometry"
        }
    
    return {"difficulty": difficulty} 