"""
데이터베이스 초기화 스크립트

이 스크립트는 데이터베이스를 초기화합니다.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, drop_database, create_database

from db.connection import DatabaseManager
from db.models import Base

def reset_database():
    """데이터베이스를 리셋합니다."""
    db_manager = DatabaseManager()
    connection_string = db_manager.get_connection_string()
    
    # 엔진 생성
    engine = create_engine(connection_string)
    
    # 데이터베이스가 존재하면 삭제
    if database_exists(engine.url):
        drop_database(engine.url)
        print(f"데이터베이스 '{db_manager.db_name}'을 삭제했습니다.")
    
    # 데이터베이스 재생성
    create_database(engine.url)
    print(f"데이터베이스 '{db_manager.db_name}'을 생성했습니다.")
    
    # pgvector 확장 설치
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("pgvector 확장이 설치되었습니다.")
        except Exception as e:
            print(f"pgvector 확장 설치 오류: {e}")
            print("PostgreSQL에 pgvector 확장이 설치되어 있는지 확인하세요.")
            return None
    
    # 테이블 생성
    Base.metadata.create_all(engine)
    print("테이블이 생성되었습니다.")
    
    return engine

if __name__ == "__main__":
    reset_database() 