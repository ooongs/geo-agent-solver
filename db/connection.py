"""
데이터베이스 연결 관리 모듈

이 모듈은 PostgreSQL 데이터베이스 연결을 관리합니다.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database
from db.models import Base

from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """데이터베이스 연결 관리자"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 환경 변수에서 설정값을 읽거나 기본값 사용
        self.db_host = os.environ.get("DB_HOST", "localhost")
        self.db_port = os.environ.get("DB_PORT", "5432")
        self.db_name = os.environ.get("DB_NAME", "geogebra_commands")
        self.db_user = os.environ.get("DB_USER", "postgres")
        self.db_password = os.environ.get("DB_PASSWORD", "postgres")
        
        self.engine = None
        self.session_factory = None
        self._initialized = True
    
    def get_connection_string(self):
        """데이터베이스 연결 문자열 반환"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def init_db(self, create_tables=True):
        """데이터베이스 초기화"""
        connection_string = self.get_connection_string()
        
        # 엔진 생성
        self.engine = create_engine(connection_string)
        
        # 데이터베이스가 없으면 생성
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
            print(f"데이터베이스 '{self.db_name}'을 생성했습니다.")
        
        # 테이블 생성
        if create_tables:
            Base.metadata.create_all(self.engine)
            print("테이블이 생성되었습니다.")
        
        # 세션 팩토리 생성
        self.session_factory = scoped_session(sessionmaker(bind=self.engine))
        print(f"데이터베이스 '{self.db_name}'에 연결되었습니다.")
        
        return self.engine
    
    def get_session(self):
        """세션 반환"""
        if not self.session_factory:
            self.init_db(create_tables=False)
        return self.session_factory()
    
    def close(self):
        """연결 종료"""
        if self.session_factory:
            self.session_factory.remove()
            print("세션이 종료되었습니다.")
        
    def test_connection(self):
        """연결 테스트"""
        try:
            session = self.get_session()
            session.close()
            return True
        except Exception as e:
            print(f"데이터베이스 연결 오류: {e}")
            return False 