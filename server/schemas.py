from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# 요청 모델 정의
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    threshold: Optional[float] = 0.0

class BatchSearchRequest(BaseModel):
    queries: List[str]
    top_k: Optional[int] = 5
    threshold: Optional[float] = 0.0

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# 응답 모델 정의
class SearchResult(BaseModel):
    command: str
    link: str
    example: List[str]
    note: str
    syntax: str
    similarity: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

class ChatResponse(BaseModel):
    content: str
    model: str
    commands: List[str] = []  # 추출된 명령어 목록

# WebSocket 메시지 모델
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]