import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import socketio
from schemas import *
# from config import MODEL_PATH
import asyncio
import uuid
from main import solve_geometry_problem

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # DeepSeek API 키 추가

# FastAPI 앱 초기화 (한 번만 선언)
app = FastAPI(title="GeoGebra Command Generator", description="GeoGebra Command Generator Based on Multi-Agent System")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 작업 상태 저장소
tasks = {}

# Socket.IO 설정 - 수정된 버전
sio = socketio.AsyncServer(
    async_mode='asgi', 
    cors_allowed_origins='*',
    logger=True,  # 로깅 활성화
    engineio_logger=True,  # Engine.IO 로깅 활성화
    ping_timeout=120,  # 핑 타임아웃 증가
    ping_interval=25,  # 핑 간격 설정
    max_http_buffer_size=1000000,  # 버퍼 크기 증가
    allow_upgrades=True  # 업그레이드 허용
)
socket_app = socketio.ASGIApp(sio)

# Socket.IO 앱을 FastAPI에 마운트 (FastAPI 앱 유지)
app.mount('/socket.io', socket_app)  # /socket.io 경로에 마운트

# 연결 이벤트 핸들러
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# 서버 상태 확인 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": 'MODEL_PATH'}

# JSON 직렬화 가능한 객체로 변환하는 함수
def make_json_serializable(obj):
    """객체를 JSON 직렬화 가능한 형태로 변환"""
    if obj is None:
        return None
    # ConstructionPlan 클래스 직접 처리
    elif obj.__class__.__name__ == 'ConstructionPlan':
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
    # 일반적인 객체 변환 방법 적용    
    elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        return obj.to_dict()
    elif hasattr(obj, 'model_dump') and callable(getattr(obj, 'model_dump')):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    # 기본 타입이 아닌 경우 변환 시도
    elif not isinstance(obj, (str, int, float, bool)) and hasattr(obj, '__dict__'):
        return make_json_serializable(obj.__dict__)
    # 기본 타입으로 변환 시도
    else:
        try:
            # JSON으로 직렬화 가능한지 테스트
            import json
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            # 직렬화 불가능한 경우 문자열로 변환
            return str(obj)

# 비동기 작업 처리 함수
async def process_geometry_problem(task_id: str, user_query: str):
    try:
        # 작업 상태 업데이트
        tasks[task_id]["status"] = "processing"
        await sio.emit('task_update', {"task_id": task_id, "status": "processing"})
        
        # 진행 상황을 받을 콜백 함수 정의
        async def progress_callback(step: str, message: str, data: dict = None):
            # 데이터가 있으면 JSON 직렬화 가능하게 변환
            if data:
                data = make_json_serializable(data)
                
            # 에이전트 진행 상황 이벤트 발생
            await sio.emit('agent_progress', {
                "task_id": task_id,
                "step": step,
                "message": message,
                "data": data
            })
            
            # 특정 단계의 데이터 업데이트 (예: 파싱된 요소, GeoGebra 명령어, 설명 등)
            if step == "state_update" and data:
                await sio.emit('state_update', {
                    "task_id": task_id,
                    "type": "state_update",
                    "data": data
                })
            
            # 전체 상태 업데이트 이벤트 처리
            if step == "state_full_update" and data:
                await sio.emit('state_full_update', {
                    "task_id": task_id,
                    "type": "state_full_update",
                    "node": data.get("node"),
                    "data": data.get("data")
                })
            
            # 노드 완료/시작 이벤트
            if step in ["node_start", "node_complete"]:
                await sio.emit('node_update', {
                    "task_id": task_id,
                    "type": step,
                    "node": data.get("node") if data else None,
                    "message": message
                })
            
            # 에러 이벤트
            if step == "node_error":
                await sio.emit('error_update', {
                    "task_id": task_id,
                    "type": "error",
                    "message": message,
                    "error": data.get("error") if data else None
                })
                
            # LLM 호출 이벤트
            if step in ["llm_start", "llm_complete"]:
                await sio.emit('llm_update', {
                    "task_id": task_id,
                    "type": step,
                    "message": message
                })
                
            # 약간의 지연을 두어 메시지가 순서대로 전송되도록 함
            await asyncio.sleep(0.2)  # 0.1에서 0.2로 지연 시간 증가
        
        # 기하학 문제 해결 (콜백 함수 전달)
        result = await solve_geometry_problem(user_query, progress_callback)
        
        # 결과를 JSON 직렬화 가능한 형태로 변환
        serializable_result = make_json_serializable(result)
        
        # 작업 완료 및 결과 저장
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = serializable_result
        
        # Socket.IO를 통해 결과 전송
        await sio.emit('task_completed', {
            "task_id": task_id, 
            "status": "completed", 
            "result": serializable_result
        })
        
        print(f"작업 완료: {task_id}")
        
    except GeneratorExit as ge:
        # GeneratorExit 예외 처리
        print(f"GeneratorExit 예외 발생: {task_id}")
        # 작업 상태를 실패로 변경
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = "비동기 스트림이 종료되었습니다. 연결 문제가 발생했을 수 있습니다."
        
        # 오류 정보 전송
        try:
            await sio.emit('task_error', {
                "task_id": task_id, 
                "status": "failed", 
                "error": "비동기 스트림이 종료되었습니다. 연결 문제가 발생했을 수 있습니다."
            })
        except Exception:
            print(f"사용자에게 에러 메시지를 보내는데 실패했습니다: {task_id}")
            
    except Exception as e:
        # 오류 처리
        error_message = str(e)
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = error_message
        
        # 오류 정보 전송
        await sio.emit('task_error', {
            "task_id": task_id, 
            "status": "failed", 
            "error": error_message
        })
        
        print(f"작업 실패: {task_id}, 오류: {error_message}")

# 명령어 생성 API 엔드포인트 - 작업 ID 반환 및 비동기 처리
@app.post("/generate-commands", response_model=TaskResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        # 사용자 쿼리 추출
        user_query = ""
        for msg in request.messages:
            if msg.role == "user":
                user_query = msg.content
        
        # 작업 ID 생성
        task_id = str(uuid.uuid4())
        
        # 작업 상태 초기화
        tasks[task_id] = {
            "status": "pending",
            "query": user_query,
            "result": None,
            "error": None
        }
        
        # 비동기 작업 시작
        background_tasks.add_task(process_geometry_problem, task_id, user_query)
        
        # 작업 ID 반환
        return {"task_id": task_id, "status": "pending"}
            
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

# 작업 상태 확인 API
@app.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    response = {
        "task_id": task_id,
        "status": task["status"]
    }
    
    # 작업 완료 시 결과 포함
    if task["status"] == "completed" and task["result"]:
        response["result"] = task["result"]
    
    # 작업 실패 시 오류 메시지 포함
    if task["status"] == "failed" and task["error"]:
        response["error"] = task["error"]
    
    return response

# 직접 실행 시 서버 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 