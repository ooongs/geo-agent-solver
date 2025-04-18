"""
LLM 관리자 모듈

이 모듈은 LLM 인스턴스를 중앙에서 관리하는 LLMManager 클래스를 정의합니다.
"""

from langchain_core.messages import SystemMessage
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, ADVANCED_MODEL
import os
import functools
from geo_prompts import (
    CALCULATION_SYSTEM_MESSAGES, 
    SYSTEM_MESSAGES, 
    DEFAULT_SYSTEM_MESSAGE,
    get_system_message,
    get_calculation_system_message
)

class LLMManager:
    """
    LLM 인스턴스를 중앙에서 관리하는 클래스
    """
    
    # 기본 시스템 메시지


    
    # LLM 프로필 정의
    PROFILES = {
        # 기본 LLM 프로필
        "default": {
            "model": DEFAULT_MODEL,
            "temperature": DEFAULT_TEMPERATURE,
            "system_message": DEFAULT_SYSTEM_MESSAGE
        },
        # 고급 LLM 프로필
        "advanced": {
            "model": ADVANCED_MODEL,
            "temperature": DEFAULT_TEMPERATURE,
            "system_message": DEFAULT_SYSTEM_MESSAGE
        },
        # 계산 전용 LLM 프로필
        "calculation": {
            "model": DEFAULT_MODEL,
            "temperature": 0,
            "system_message": SYSTEM_MESSAGES["calculation"]
        },
        # 분석 전용 LLM 프로필
        "planner": {
            "model": ADVANCED_MODEL,
            "temperature": 0.3,
            "system_message": SYSTEM_MESSAGES["planner"]
        },
        # GeoGebra 명령 생성 프로필
        "geogebra": {
            "model": DEFAULT_MODEL,
            "temperature": 0.1,
            "system_message": SYSTEM_MESSAGES["geogebra"]
        },
        # 파싱 전용 LLM 프로필
        "parsing": {
            "model": DEFAULT_MODEL,
            "temperature": 0,
            "system_message": SYSTEM_MESSAGES["parsing"]
        },
        # 설명 전용 LLM 프로필
        "explanation": {
            "model": DEFAULT_MODEL,
            "temperature": 0.2,
            "system_message": SYSTEM_MESSAGES["explanation"]
        },
        # 검증 전용 LLM 프로필
        "validation": {
            "model": ADVANCED_MODEL,
            "temperature": 0,
            "system_message": SYSTEM_MESSAGES["validation"]
        },
        # 명령어 선택 전용 LLM 프로필
        "command_selection": {
            "model": DEFAULT_MODEL,
            "temperature": 0.2,
            "system_message": SYSTEM_MESSAGES["command_selection"]
        }
    }
    
    @classmethod
    def get_llm(cls, profile="default", **kwargs):
        """
        지정된 프로필에 따라 LLM 인스턴스 생성
        
        Args:
            profile: 사용할 LLM 프로필 이름
            **kwargs: ChatOpenAI 생성자에 전달할 추가 인자
            
        Returns:
            ChatOpenAI 인스턴스
        """
        if profile not in cls.PROFILES:
            raise ValueError(f"Unknown LLM profile: {profile}")
            
        # 프로필 설정 복사
        config = cls.PROFILES[profile].copy()
        
        # 시스템 메시지 추출
        system_message = config.pop("system_message", DEFAULT_SYSTEM_MESSAGE)
        
        # 추가 인자로 설정 덮어쓰기
        config.update(kwargs)
        
        # # OpenAI API 키 설정
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # ChatOpenAI 인스턴스 생성
        llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            **config
        )
        
        # deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")

        # llm = ChatDeepSeek(
        #     api_key=deepseek_api_key,
        #     **config
        # )
        
        # 원래 함수를 저장
        original_invoke = llm.__call__
        
        # 새로운 함수 정의
        @functools.wraps(original_invoke)
        def wrapped_invoke(messages, *args, **kwargs):
            # 시스템 메시지가 이미 있는지 확인
            has_system = any(m.get("type", "") == "system" or getattr(m, "type", "") == "system" for m in messages)
            
            if not has_system:
                # 시스템 메시지 추가
                if isinstance(messages[0], dict):
                    messages = [{"type": "system", "content": system_message}] + messages
                else:
                    messages = [SystemMessage(content=system_message)] + messages
            
            return original_invoke(messages, *args, **kwargs)
        
        # 함수 교체
        llm.__call__ = wrapped_invoke
        
        return llm
    
    # === 일반 LLM 인스턴스 ===
    @classmethod
    def get_calculation_llm(cls, calculation_type="default", **kwargs):
        """
        계산용 LLM 인스턴스 생성
        
        Args:
            calculation_type: 계산 유형(default, triangle, circle, angle, length, area, coordinate, manager, merger)
            **kwargs: 추가 설정 (model, temperature 등)
            
        Returns:
            계산 유형에 특화된 ChatOpenAI 인스턴스
        """
        # 베이스 프로필 복사
        config = cls.PROFILES["calculation"].copy()
        
        # 계산 유형별 시스템 메시지 설정
        system_message = CALCULATION_SYSTEM_MESSAGES.get(
            calculation_type, 
            CALCULATION_SYSTEM_MESSAGES["default"]
        )
        
        # 추가 인자로 설정 덮어쓰기
        config.update(kwargs)
        
        # system_message 설정에서 제외
        if "system_message" in config:
            config.pop("system_message")
        
        # OpenAI API 키 설정
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # ChatOpenAI 인스턴스 생성
        llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            **config
        )
        # deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")

        # llm = ChatDeepSeek(
        #     api_key=deepseek_api_key,
        #     **config
        # )
        
        # 원래 함수를 저장
        original_invoke = llm.__call__
        
        # 새로운 함수 정의
        @functools.wraps(original_invoke)
        def wrapped_invoke(messages, *args, **kwargs):
            # 시스템 메시지가 이미 있는지 확인
            has_system = any(m.get("type", "") == "system" or getattr(m, "type", "") == "system" for m in messages)
            
            if not has_system:
                # 시스템 메시지 추가
                if isinstance(messages[0], dict):
                    messages = [{"type": "system", "content": system_message}] + messages
                else:
                    messages = [SystemMessage(content=system_message)] + messages
            
            return original_invoke(messages, *args, **kwargs)
        
        # 함수 교체
        llm.__call__ = wrapped_invoke
        return llm
    
    @classmethod
    def get_planner_llm(cls, **kwargs):
        """분석용 LLM 인스턴스 생성"""
        return cls.get_llm("planner", **kwargs)
    
    @classmethod
    def get_geogebra_llm(cls, **kwargs):
        """GeoGebra 명령 생성용 LLM 인스턴스 생성"""
        return cls.get_llm("geogebra", **kwargs)
    
    @classmethod
    def get_advanced_llm(cls, **kwargs):
        """고급 LLM 인스턴스 생성"""
        return cls.get_llm("advanced", **kwargs)
        
    # === 에이전트별 LLM 인스턴스 ===
    @classmethod
    def get_parsing_llm(cls, **kwargs):
        """파싱 에이전트용 LLM 인스턴스 생성"""
        return cls.get_llm("parsing", **kwargs)
    
    @classmethod
    def get_explanation_llm(cls, **kwargs):
        """설명 에이전트용 LLM 인스턴스 생성"""
        return cls.get_llm("explanation", **kwargs)
    
    @classmethod
    def get_geogebra_command_llm(cls, **kwargs):
        """GeoGebra 명령 에이전트용 LLM 인스턴스 생성"""
        return cls.get_llm("geogebra", **kwargs)
    
    @classmethod
    def get_validation_llm(cls, **kwargs):
        """검증 에이전트용 LLM 인스턴스 생성"""
        return cls.get_llm("validation", **kwargs)
    
    @classmethod
    def get_command_selection_llm(cls, **kwargs):
        """명령어 선택 에이전트용 LLM 인스턴스 생성"""
        return cls.get_llm("command_selection", **kwargs)
    
    # === 계산 에이전트별 LLM 인스턴스 (하위 호환성 유지) ===
    @classmethod
    def get_triangle_calculation_llm(cls, **kwargs):
        """삼각형 계산 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("triangle", **kwargs)
    
    @classmethod
    def get_circle_calculation_llm(cls, **kwargs):
        """원 계산 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("circle", **kwargs)
    
    @classmethod
    def get_angle_calculation_llm(cls, **kwargs):
        """각도 계산 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("angle", **kwargs)
    
    @classmethod
    def get_length_calculation_llm(cls, **kwargs):
        """길이 계산 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("length", **kwargs)
    
    @classmethod
    def get_area_calculation_llm(cls, **kwargs):
        """넓이 계산 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("area", **kwargs)
    
    @classmethod
    def get_coordinate_calculation_llm(cls, **kwargs):
        """좌표 계산 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("coordinate", **kwargs)
    
    @classmethod
    def get_calculation_manager_llm(cls, **kwargs):
        """계산 관리 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("manager", **kwargs)
    
    @classmethod
    def get_calculation_merger_llm(cls, **kwargs):
        """계산 결과 병합 에이전트용 LLM 인스턴스 생성"""
        return cls.get_calculation_llm("merger", **kwargs) 