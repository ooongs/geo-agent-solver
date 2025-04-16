# GeoGebra 명령어 검색 시스템

이 시스템은 PostgreSQL + pgvector 확장을 사용하여 GeoGebra 명령어를 저장하고 벡터 유사도 검색을 제공합니다.

## 주요 기능

- GeoGebra 명령어를 벡터 데이터베이스에 저장
- SentenceBERT를 사용한 의미적 검색
- 기하학 문제에 적합한 명령어 추천
- 하이브리드 검색 (의미적 유사도 + 키워드)

## 설치 방법

### 1. PostgreSQL 및 pgvector 설치

```bash
# PostgreSQL 설치 (Mac OS)
brew install postgresql

# PostgreSQL 서비스 시작
brew services start postgresql

# pgvector 확장 설치
psql -U postgres
CREATE EXTENSION vector;
```

### 2. 파이썬 패키지 설치

```bash
pip install -r db/requirements.txt
```

## 사용 방법

### 1. 데이터베이스 초기화 및 시드

```bash
python -m db.seed
```

### 2. 데이터베이스 연결 테스트

```bash
python -m db.main
```

### 3. 검색 사용 예제

```python
from db.retrieval import CommandRetrieval

# 검색 객체 생성
retrieval = CommandRetrieval()

# 기본 검색
results = retrieval.search_commands("두 점을 지나는 선", top_k=5)

# 하이브리드 검색
results = retrieval.cosine_search("원의 중심과 반지름", top_k=5)

# 문제 기반 명령어 추천
problem = "두 점 A(0,0)와 B(4,0)이 있다. 이 두 점을 지름의 양 끝점으로 하는 원을 그리시오."
commands = retrieval.suggest_commands_for_problem(problem, problem_type="circle")
```

## 시스템 구성

- **models.py**: ORM 모델 정의
- **connection.py**: 데이터베이스 연결 관리
- **seed.py**: 데이터 시드 기능
- **retrieval.py**: 명령어 검색 기능
- **main.py**: 연결 테스트 및 예제

## 환경 변수

데이터베이스 연결 설정은 다음 환경 변수로 구성할 수 있습니다:

- `DB_HOST`: 데이터베이스 호스트 (기본값: localhost)
- `DB_PORT`: 데이터베이스 포트 (기본값: 5432)
- `DB_NAME`: 데이터베이스 이름 (기본값: geogebra_commands)
- `DB_USER`: 데이터베이스 사용자 (기본값: postgres)
- `DB_PASSWORD`: 데이터베이스 비밀번호 (기본값: postgres)
