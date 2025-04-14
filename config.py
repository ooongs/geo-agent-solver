from langchain_openai import ChatOpenAI

# LLM 설정
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.1

ADVANCED_MODEL = "gpt-4o"
ADVANCED_TEMPERATURE = 0.1

# 시스템 설정
MAX_ATTEMPTS = 3
DEFAULT_LANGUAGE = "chinese"

# LLM 초기화 함수
def get_llm(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, system_message=None):
    """LLM 인스턴스 생성"""
    default_system_message = "您是一个专业的几何问题解析系统，精通中文几何术语和概念，能准确理解并分析各类几何问题。"
    
    if system_message:
        system_prompt = system_message
    else:
        system_prompt = default_system_message
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        messages=[{"role": "system", "content": system_prompt}]
    ) 