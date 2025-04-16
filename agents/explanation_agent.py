from geo_prompts import EXPLANATION_PROMPT
from utils.llm_manager import LLMManager

def explanation_agent(state):
    """
    해설 생성 에이전트
    
    Args:
        state: 현재 상태 객체
        
    Returns:
        해설이 추가된 상태 객체
    """
    # LLM 초기화
    llm = LLMManager.get_explanation_llm()
    
    # 프롬프트 생성 및 LLM 호출
    prompt = EXPLANATION_PROMPT.format(
        problem=state.input_problem,
        parsed_elements=str(state.parsed_elements),
        problem_analysis=str(state.problem_analysis),
        approach=state.approach,
        calculations=str(state.calculations),
        geogebra_commands=str(state.geogebra_commands),
        validation=str(state.validation)
    )
    
    # LLM 직접 호출
    response = llm.invoke(prompt)
    
    # 결과 처리
    explanation = response.content
    
    # 상태 업데이트
    state.explanation = explanation
    
    return state 