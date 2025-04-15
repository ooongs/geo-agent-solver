from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import socketio
from server.schemas import *
from config import MODEL_PATH

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



# Socket.IO 설정 - 수정된 버전
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

# Socket.IO 앱을 FastAPI에 마운트 (FastAPI 앱 유지)
app.mount('/socket.io', socket_app)  # /socket.io 경로에 마운트

# 서버 상태 확인 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_PATH, "commands_count": len(embedding_service.commands)}


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     # WebSocketManager를 통한 연결 수립
#     connection_id = await websocket_manager.connect(websocket)
    
#     try:
#         while True:
#             # 클라이언트로부터 데이터 수신
#             data = await websocket.receive_json()
            
#             # WebSocketManager를 통한 메시지 처리
#             await websocket_manager.handle_message(connection_id, data)
                
#     except WebSocketDisconnect:
#         # WebSocketManager를 통한 연결 종료 처리
#         websocket_manager.disconnect(connection_id)
#         print("클라이언트 연결 종료")
#     except Exception as e:
#         print(f"WebSocket 오류: {str(e)}")
#         await websocket.close(code=1011)

# 명령어 생성 API 엔드포인트 - LLMService 사용하도록 변경
@app.post("/generate-commands", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:
        # 사용자 쿼리 추출
        user_query = ""
        for msg in request.messages:
            if msg.role == "user":
                user_query = msg.content
        
        # Agent 를 통한 명령어 생성
        result = await solve_geometry_problem(user_query)
        
        print(f"생성된 명령어: {result['commands']}")
        return result
            
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

# 직접 실행 시 서버 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 