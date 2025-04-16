from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import socketio
from server.schemas import *
from config import MODEL_PATH
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
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
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
    return {"status": "healthy", "model": MODEL_PATH}

# 비동기 작업 처리 함수
async def process_geometry_problem(task_id: str, user_query: str):
    try:
        # 작업 상태 업데이트
        tasks[task_id]["status"] = "processing"
        await sio.emit('task_update', {"task_id": task_id, "status": "processing"})
        
        # 기하학 문제 해결
        result = await solve_geometry_problem(user_query)
        
        # 작업 완료 및 결과 저장
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
        
        # Socket.IO를 통해 결과 전송
        await sio.emit('task_completed', {
            "task_id": task_id, 
            "status": "completed", 
            "result": result
        })
        
        print(f"작업 완료: {task_id}")
        
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