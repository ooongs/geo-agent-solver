from typing import List, Dict, Any, Optional, Union
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
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 2048

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
    problem: str
    geogebra_commands: List[str]
    explanation: Optional[str] = None
    parsed_elements: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# WebSocket 메시지 모델
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]

# 작업 관련 스키마 추가
class TaskResponse(BaseModel):
    """비동기 작업 생성 응답"""
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    """작업 상태 응답"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TaskCompletedResponse(BaseModel):
    """작업 완료 응답"""
    task_id: str
    status: str
    result: Dict[str, Any]

# 스트리밍 관련 스키마 추가
class NodeStartEvent(BaseModel):
    """노드 시작 이벤트"""
    task_id: str
    type: str = "node_start"
    node: str
    message: str
    payload: Optional[Dict[str, Any]] = None

class NodeCompleteEvent(BaseModel):
    """노드 완료 이벤트"""
    task_id: str
    type: str = "node_complete"
    node: str
    message: str
    result: Optional[List[Any]] = None

class NodeErrorEvent(BaseModel):
    """노드 오류 이벤트"""
    task_id: str
    type: str = "node_error"
    node: str
    message: str
    error: Optional[str] = None

class StateUpdateEvent(BaseModel):
    """상태 업데이트 이벤트"""
    task_id: str
    type: str = "state_update"
    node: str
    data: Dict[str, Any]

class StateFullUpdateEvent(BaseModel):
    """전체 상태 업데이트 이벤트"""
    task_id: str
    type: str = "state_full_update"
    node: str
    data: Dict[str, Any]

class SystemEvent(BaseModel):
    """시스템 이벤트"""
    task_id: str
    type: str = "system"
    message: str
    status: Optional[str] = None

class SystemErrorEvent(BaseModel):
    """시스템 오류 이벤트"""
    task_id: str
    type: str = "system_error"
    message: str
    error: Optional[str] = None

# 모든 이벤트 타입을 포함하는 유니온 타입
StreamEvent = Union[
    NodeStartEvent, 
    NodeCompleteEvent, 
    NodeErrorEvent, 
    StateUpdateEvent, 
    StateFullUpdateEvent,
    SystemEvent,
    SystemErrorEvent
]