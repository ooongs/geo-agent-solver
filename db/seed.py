"""
데이터베이스 시드 모듈

이 모듈은 GeoGebra 명령어 JSON 파일을 읽어 데이터베이스에 저장합니다.
"""

import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from db.connection import DatabaseManager
from db.models import GeogebraCommand

class CommandSeeder:
    """GeoGebra 명령어 시드 클래스"""
    
    def __init__(self, embedding_model_name: str = "BAAI/bge-m3"):
        """
        초기화
        
        Args:
            embedding_model_name: SentenceBERT 모델 이름
        """
        self.db_manager = DatabaseManager()
        self.embedding_model = SentenceTransformer(embedding_model_name)
        print(f"임베딩 모델 '{embedding_model_name}' 로드 완료. 차원: {self.embedding_model.get_sentence_embedding_dimension()}")
        
    def load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        JSON 파일 로드
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            명령어 목록
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        텍스트 임베딩 생성
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        return self.embedding_model.encode(text)
    
    def clear_commands_table(self) -> None:
        """
        GeogebraCommand 테이블의 모든 데이터 삭제 및 ID 시퀀스 초기화
        
        Returns:
            None
        """
        session = self.db_manager.get_session()
        try:
            # 테이블의 모든 데이터 삭제
            deleted_count = session.query(GeogebraCommand).delete()
            
            # ID 시퀀스 초기화 (PostgreSQL)
            session.execute(text("ALTER SEQUENCE geogebra_commands_id_seq RESTART WITH 1"))
            
            session.commit()
            print(f"GeogebraCommand 테이블에서 {deleted_count}개 명령어 삭제됨 및 ID 시퀀스 초기화됨")
        except Exception as e:
            session.rollback()
            print(f"테이블 삭제 오류: {e}")
        finally:
            session.close()
    
    def seed_commands(self, file_path: str) -> int:
        """
        명령어 데이터 시드
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            저장된 명령어 수
        """
        commands = self.load_json_file(file_path)
        session = self.db_manager.get_session()
        count = 0
        
        try:
            for cmd in commands:
                command_name = cmd.get('command', '')
                
                # 각 사용법에 대해 별도의 레코드 생성
                for usage in cmd.get('usage', []):
                    syntax = usage.get('syntax', '')
                    description = usage.get('description', '')
                    
                    # 예제 배열 그대로 저장
                    examples = usage.get('example', [])
                    
                    # 노트가 있으면 추가
                    note = usage.get('note', None)
                    
                    # 관련 명령어
                    related = usage.get('related', [])
                    
                    # 설명 텍스트에서 임베딩 생성
                    embedding_text = f"{command_name}: {description}"
                    embedding = self.generate_embedding(embedding_text)
                    
                    # 데이터베이스에 저장
                    command = GeogebraCommand(
                        command=command_name,
                        syntax=syntax,
                        description=description,
                        category=cmd.get('category', 'Unknown'),
                        examples=examples,
                        note=note,
                        related=related,
                        embedding=embedding.tolist()  # Numpy 배열을 리스트로 변환
                    )
                    
                    # 데이터베이스에 추가
                    try:
                        session.add(command)
                        session.commit()
                        count += 1
                    except IntegrityError:
                        # 이미 존재하는 명령어는 건너뜀
                        session.rollback()
                        print(f"중복 명령어 건너뜀: {command_name} - {syntax}")
                    
        except Exception as e:
            session.rollback()
            print(f"시드 오류: {e}")
        finally:
            session.close()
            
        return count
        
    def seed_from_directory(self, dir_path: str) -> Dict[str, int]:
        """
        디렉토리의 모든 JSON 파일 시드
        
        Args:
            dir_path: JSON 파일이 있는 디렉토리 경로
            
        Returns:
            파일별 저장된 명령어 수
        """
        results = {}
        
        # 디렉토리의 모든 JSON 파일 처리
        for filename in os.listdir(dir_path):
            if filename.endswith(".json"):
                file_path = os.path.join(dir_path, filename)
                count = self.seed_commands(file_path)
                results[filename] = count
                print(f"{filename}: {count}개 명령어 저장됨")
                
        return results

def main():
    """메인 함수"""
    # 데이터베이스 초기화
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    # 시더 생성 및 실행
    seeder = CommandSeeder()
    
    # GeogebraCommand 테이블의 모든 데이터 삭제
    seeder.clear_commands_table()
    
    # JSON 파일이 있는 기본 디렉토리
    data_dir = "data"
    
    # 개별 파일 시드
    object_commands_file = os.path.join(data_dir, "geogebra_object_commands.json")
    value_commands_file = os.path.join(data_dir, "geogebra_value_commands.json")
    
    # 파일이 존재하는지 확인
    if os.path.exists(object_commands_file):
        count = seeder.seed_commands(object_commands_file)
        print(f"geogebra_object_commands.json: {count}개 명령어 저장됨")
    
    if os.path.exists(value_commands_file):
        count = seeder.seed_commands(value_commands_file)
        print(f"geogebra_value_commands.json: {count}개 명령어 저장됨")
    
    # 또는 디렉토리의 모든 JSON 파일 시드
    # if os.path.isdir(data_dir):
    #     results = seeder.seed_from_directory(data_dir)
    #     print(f"총 {sum(results.values())}개 명령어 저장됨")
    
    # 데이터베이스 연결 종료
    db_manager.close()

if __name__ == "__main__":
    main() 