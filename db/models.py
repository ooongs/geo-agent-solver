"""
GeoGebra 명령어 데이터베이스 모델

이 모듈은 PostgreSQL 및 pgvector를 사용하여 GeoGebra 명령어를 저장하기 위한 ORM 모델을 정의합니다.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, mapped_column
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class GeogebraCommand(Base):
    """GeoGebra 명령어 모델"""
    __tablename__ = 'geogebra_commands'
    
    id = Column(Integer, primary_key=True)
    command = Column(String(255), nullable=False, index=True)
    syntax = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(255), nullable=False, index=True)
    examples = Column(ARRAY(String), nullable=True)
    note = Column(Text, nullable=True)
    embedding = mapped_column(Vector(1024), nullable=True)  # 사용하는 모델에 맞춰 1024 차원으로 변경
    
    # 관련 명령어를 저장하기 위한 JSONB 필드
    related = Column(ARRAY(String), nullable=True)
    
    # 명령어 + 구문 조합은 고유해야 함
    __table_args__ = (
        UniqueConstraint('command', 'syntax', name='uix_command_syntax'),
    )
    
    def __repr__(self):
        return f"<GeogebraCommand(command='{self.command}', syntax='{self.syntax}')>"

# 명령어 사용 로그를 위한 추가 모델 (선택 사항)
class CommandUsage(Base):
    """명령어 사용 로그 모델"""
    __tablename__ = 'command_usage_logs'
    
    id = Column(Integer, primary_key=True)
    command_id = Column(Integer, ForeignKey('geogebra_commands.id'))
    problem_type = Column(String(255), nullable=True)
    frequency = Column(Integer, default=1)
    success_rate = Column(Integer, default=0)  # 0-100 범위의 성공률
    
    command = relationship("GeogebraCommand") 