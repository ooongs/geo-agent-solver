"""
프롬프트 템플릿 기본 구조 패키지

이 패키지는 다양한 기하학 문제에 대한 기본 프롬프트 구조를 제공합니다.
"""

from .triangle import TrianglePromptTemplate
from .angle import AnglePromptTemplate

__all__ = [
    "TrianglePromptTemplate",
    "AnglePromptTemplate"
]
