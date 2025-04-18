"""
GeoGebra 명령어 검색 모듈

이 모듈은 pgvector를 사용한 GeoGebra 명령어 검색 기능을 제공합니다.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sqlalchemy import text, select, func, case, or_, and_
from sqlalchemy.sql.expression import literal_column
from pgvector.sqlalchemy import Vector

from db.connection import DatabaseManager
from db.models import GeogebraCommand

class CommandRetrieval:
    """GeoGebra 명령어 검색 클래스"""
    
    # 클래스 변수로 모델과 데이터베이스 매니저를 저장
    _embedding_model = None
    _db_manager = None
    _embedding_model_name = "BAAI/bge-m3"
    
    @classmethod
    def _get_embedding_model(cls) -> SentenceTransformer:
        """
        임베딩 모델을 가져오거나 초기화합니다.
        
        Returns:
            SentenceTransformer 모델
        """
        if cls._embedding_model is None:
            cls._embedding_model = SentenceTransformer(cls._embedding_model_name)
        return cls._embedding_model
    
    @classmethod
    def _get_db_manager(cls) -> DatabaseManager:
        """
        데이터베이스 매니저를 가져오거나 초기화합니다.
        
        Returns:
            DatabaseManager 인스턴스
        """
        if cls._db_manager is None:
            cls._db_manager = DatabaseManager()
        return cls._db_manager
    
    @classmethod
    def generate_embedding(cls, text: str) -> np.ndarray:
        """
        텍스트 임베딩 생성
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        model = cls._get_embedding_model()
        return model.encode(text)
    
    @classmethod
    def search_commands_by_command(cls, command: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        특정 명령어로 검색하고 description 유사도로 정렬
        
        Args:
            command: 검색할 명령어
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록
        """
        # 세션 생성
        db_manager = cls._get_db_manager()
        session = db_manager.get_session()
        
        try:
            # 명령어 임베딩 생성 (설명 유사도 검색용)
            command_embedding = cls.generate_embedding(command)
            
            # ORM 쿼리 생성
            distance = GeogebraCommand.embedding.cosine_distance(command_embedding)
            score = func.power(1.0 + distance, -1)
            
            query = (
                select(
                    GeogebraCommand.id,
                    GeogebraCommand.command,
                    GeogebraCommand.syntax,
                    GeogebraCommand.description,
                    GeogebraCommand.category,
                    GeogebraCommand.examples,
                    GeogebraCommand.note,
                    GeogebraCommand.related,
                    distance.label('distance'),
                    score.label('score')
                )
                .where(func.lower(GeogebraCommand.command) == func.lower(command))
                .order_by(distance)
                .limit(top_k)
            )
            
            result = session.execute(query)
            
            commands = []
            for row in result:
                commands.append({
                    "command_id": row.id,
                    "command": row.command,
                    "syntax": row.syntax,
                    "description": row.description,
                    "category": row.category,
                    "examples": row.examples,
                    "note": row.note,
                    "related": row.related,
                    "source": "direct_command",
                    "score": float(row.score)
                })
            
            return commands
        
        except Exception as e:
            print(f"명령어 검색 오류: {e}")
            return []
        finally:
            session.close()
        
    @classmethod
    def cosine_search(cls, 
                     query: str, 
                     top_k: int = 5) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 (키워드 + 벡터 검색)
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            category: 카테고리 필터
            
        Returns:
            검색 결과 목록
        """
        # 세션 생성
        db_manager = cls._get_db_manager()
        session = db_manager.get_session()
        
        try:
            # 쿼리 임베딩 생성
            query_embedding = cls.generate_embedding(query)
            
            # 벡터 거리 계산 (코사인 거리)
            vector_distance = GeogebraCommand.embedding.cosine_distance(query_embedding)
            
            # 코사인 유사도 점수 계산 (거리의 역수)
            similarity_score = func.power(1.0 + vector_distance, -1)
            
            # 기본 쿼리 구성
            query = (
                select(
                    GeogebraCommand.id,
                    GeogebraCommand.command,
                    GeogebraCommand.syntax,
                    GeogebraCommand.description,
                    GeogebraCommand.category,
                    GeogebraCommand.examples,
                    GeogebraCommand.note,
                    GeogebraCommand.related,
                    vector_distance.label('vector_distance'),
                    similarity_score.label('similarity_score')
                )
            )
            
                
            # 정렬 및 결과 제한
            query = query.order_by(similarity_score.desc()).limit(top_k)
            
            # 쿼리 실행
            result = session.execute(query)
            
            # 결과 포맷팅
            commands = []
            for row in result:
                commands.append({
                    "command_id": row.id,
                    "command": row.command,
                    "syntax": row.syntax,
                    "description": row.description,
                    "category": row.category,
                    "examples": row.examples,
                    "note": row.note,
                    "related": row.related,
                    "score": float(row.similarity_score),
                    "source": "vector_search"
                })
                
            return commands[:top_k]
        
            
        except Exception as e:
            print(f"하이브리드 검색 오류: {e}")
            return []
        finally:
            session.close()
  