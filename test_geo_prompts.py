"""
geo_prompts 패키지 테스트 스크립트

이 스크립트는 geo_prompts 패키지의 기능을 테스트합니다.
"""

import os
from geo_prompts import config
from geo_prompts.system import get_system_message, get_calculation_system_message
from geo_prompts.base.triangle import TrianglePromptTemplate
from geo_prompts.base.angle import AnglePromptTemplate

# 영어로 설정 변경
print("===== 영어 버전 테스트 =====")
config.set_language("en")
print(f"현재 언어: {config.get_language()}")

# 시스템 메시지 테스트
print("\n시스템 메시지 테스트:")
print(f"기본 시스템 메시지: {get_system_message('default')[:50]}...")
print(f"계산 시스템 메시지: {get_calculation_system_message('triangle')[:50]}...")

# 프롬프트 템플릿 테스트
print("\n프롬프트 템플릿 테스트:")
triangle_prompt = TrianglePromptTemplate.get_triangle_calculation_prompt()
print(f"삼각형 계산 프롬프트: {str(triangle_prompt)[:50]}...")

angle_prompt = AnglePromptTemplate.get_angle_calculation_prompt()
print(f"각도 계산 프롬프트: {str(angle_prompt)[:50]}...")

# 중국어로 설정 변경
print("\n\n===== 중국어 버전 테스트 =====")
config.set_language("zh")
print(f"현재 언어: {config.get_language()}")

# 시스템 메시지 테스트
print("\n시스템 메시지 테스트:")
print(f"기본 시스템 메시지: {get_system_message('default')[:50]}...")
print(f"계산 시스템 메시지: {get_calculation_system_message('triangle')[:50]}...")

# 프롬프트 템플릿 테스트
print("\n프롬프트 템플릿 테스트:")
triangle_prompt = TrianglePromptTemplate.get_triangle_calculation_prompt()
print(f"삼각형 계산 프롬프트: {str(triangle_prompt)[:50]}...")

angle_prompt = AnglePromptTemplate.get_angle_calculation_prompt()
print(f"각도 계산 프롬프트: {str(angle_prompt)[:50]}...") 