// Socket.IO를 사용한 기하학 문제 해결 클라이언트 예제
import { io } from 'socket.io-client';

class GeometryProblemSolver {
  constructor(serverUrl = 'http://localhost:8000') {
    this.serverUrl = serverUrl;
    this.socket = null;
    this.taskId = null;
    this.callbacks = {
      onProcessing: null,
      onCompleted: null,
      onError: null,
      onUpdate: null
    };
  }

  // Socket.IO 연결 초기화
  connect() {
    this.socket = io(this.serverUrl);

    // 소켓 이벤트 핸들러 등록
    this.socket.on('connect', () => {
      console.log('서버에 연결되었습니다.');
    });

    this.socket.on('disconnect', () => {
      console.log('서버와 연결이 끊어졌습니다.');
    });

    // 작업 상태 업데이트 처리
    this.socket.on('task_update', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log(`작업 상태 업데이트: ${data.status}`);
        if (this.callbacks.onUpdate) {
          this.callbacks.onUpdate(data);
        }
        
        if (data.status === 'processing' && this.callbacks.onProcessing) {
          this.callbacks.onProcessing(data);
        }
      }
    });

    // 작업 완료 처리
    this.socket.on('task_completed', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('작업이 완료되었습니다.', data.result);
        if (this.callbacks.onCompleted) {
          this.callbacks.onCompleted(data.result);
        }
      }
    });

    // 오류 처리
    this.socket.on('task_error', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.error('작업 처리 중 오류가 발생했습니다:', data.error);
        if (this.callbacks.onError) {
          this.callbacks.onError(data.error);
        }
      }
    });

    return this;
  }

  // 이벤트 콜백 설정
  on(event, callback) {
    if (this.callbacks.hasOwnProperty(event)) {
      this.callbacks[event] = callback;
    }
    return this;
  }

  // 문제 제출
  async submitProblem(problemText) {
    try {
      // 로딩 상태 표시
      this.updateUI('pending', '작업을 제출 중입니다...');

      // 서버에 작업 제출
      const response = await fetch(`${this.serverUrl}/generate-commands`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [
            {
              role: 'user',
              content: problemText
            }
          ]
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        this.taskId = data.task_id;
        this.updateUI('submitted', `작업이 제출되었습니다. 작업 ID: ${this.taskId}`);
        return this.taskId;
      } else {
        this.updateUI('error', `작업 제출 실패: ${data.detail || '알 수 없는 오류'}`);
        throw new Error(data.detail || '작업 제출에 실패했습니다.');
      }
    } catch (error) {
      this.updateUI('error', `오류 발생: ${error.message}`);
      throw error;
    }
  }

  // 작업 상태 확인
  async checkTaskStatus(taskId) {
    try {
      const response = await fetch(`${this.serverUrl}/task/${taskId}`);
      return await response.json();
    } catch (error) {
      console.error('작업 상태 확인 중 오류 발생:', error);
      throw error;
    }
  }

  // UI 업데이트 (예시)
  updateUI(status, message) {
    console.log(`[${status}] ${message}`);
    // 실제 UI 업데이트 로직은 애플리케이션에 맞게 구현
  }

  // 연결 해제
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

// 사용 예제
async function exampleUsage() {
  const solver = new GeometryProblemSolver()
    .connect()
    .on('processing', (data) => {
      // 처리 중 상태 업데이트
      updateProgressBar(50);
      updateStatusText('문제를 분석 중입니다...');
    })
    .on('completed', (result) => {
      // 결과 표시
      updateProgressBar(100);
      updateStatusText('완료!');
      displayCommands(result.geogebra_commands);
      displayExplanation(result.explanation);
    })
    .on('error', (error) => {
      // 오류 표시
      updateProgressBar(0);
      updateStatusText(`오류: ${error}`);
    });

  try {
    // 사용자 입력 가져오기
    const problemText = document.getElementById('problem-input').value;
    
    // 문제 제출
    await solver.submitProblem(problemText);
  } catch (error) {
    console.error('Error:', error);
  }
}

// UI 업데이트 함수 (예시)
function updateProgressBar(percent) {
  const progressBar = document.getElementById('progress-bar');
  if (progressBar) {
    progressBar.style.width = `${percent}%`;
  }
}

function updateStatusText(text) {
  const statusElement = document.getElementById('status-text');
  if (statusElement) {
    statusElement.textContent = text;
  }
}

function displayCommands(commands) {
  const commandsContainer = document.getElementById('commands-container');
  if (commandsContainer) {
    commandsContainer.innerHTML = '';
    
    commands.forEach(cmd => {
      const cmdElement = document.createElement('div');
      cmdElement.textContent = cmd;
      cmdElement.className = 'command-item';
      commandsContainer.appendChild(cmdElement);
    });
  }
}

function displayExplanation(explanation) {
  const explanationElement = document.getElementById('explanation');
  if (explanationElement) {
    explanationElement.textContent = explanation || '설명이 제공되지 않았습니다.';
  }
}

// 문서 로드 완료 시 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', () => {
  const submitButton = document.getElementById('submit-button');
  if (submitButton) {
    submitButton.addEventListener('click', exampleUsage);
  }
});
