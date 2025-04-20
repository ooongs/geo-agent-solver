// Socket.IO를 사용한 기하학 문제 해결 클라이언트 예제
// import { io } from 'socket.io-client'; <- 이 줄을 제거하고 HTML에서 로드된 io 객체 사용

class GeometryProblemSolver {
  constructor(serverUrl = 'http://localhost:8000') {
    this.serverUrl = serverUrl;
    this.socket = null;
    this.taskId = null;
    this.callbacks = {
      onProcessing: null,
      onCompleted: null,
      onError: null,
      onUpdate: null,
      onAgentProgress: null,
      onStateUpdate: null,
      onStateFullUpdate: null,
      onNodeUpdate: null,
      onLlmUpdate: null
    };
  }

  // Socket.IO 연결 초기화
  connect() {
    // Socket.IO 연결 옵션 설정
    const options = {
      transports: ['websocket', 'polling'],  // 웹소켓을 우선 시도하고, 실패 시 폴링으로 대체
      reconnection: true,                    // 재연결 활성화
      reconnectionAttempts: 5,               // 최대 5번 재시도
      reconnectionDelay: 1000,               // 재연결 지연 시간(ms)
      timeout: 20000,                        // 연결 타임아웃
      autoConnect: true,                    // 자동 연결
      path: '/socket.io/'                    // 소켓 경로 명시
    };

    console.log('서버에 연결 시도:', this.serverUrl);
    this.socket = io(this.serverUrl, options);

    // 소켓 이벤트 핸들러 등록
    this.socket.on('connect', () => {
      console.log('서버에 연결되었습니다. ID: ' + this.socket.id);
      document.getElementById('status-text').textContent = '서버에 연결되었습니다.';
    });

    this.socket.on('disconnect', () => {
      console.log('서버와 연결이 끊어졌습니다.');
      document.getElementById('status-text').textContent = '서버와 연결이 끊어졌습니다. 페이지를 새로고침하세요.';
    });

    // 연결 재시도 이벤트
    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log(`연결 재시도 중... (${attemptNumber}번째 시도)`);
      document.getElementById('status-text').textContent = `서버에 재연결 시도 중... (${attemptNumber}/5)`;
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`재연결 성공! (${attemptNumber}번째 시도)`);
      document.getElementById('status-text').textContent = '서버에 다시 연결되었습니다.';
      
      // 재연결 후 작업 ID가 있으면 상태 확인
      if (this.taskId) {
        this.checkTaskStatus(this.taskId)
          .then(response => {
            console.log('작업 상태 확인:', response);
            if (response.status === 'completed' && response.result) {
              if (this.callbacks.onCompleted) {
                this.callbacks.onCompleted(response.result);
              }
            }
          })
          .catch(error => console.error('작업 상태 확인 실패:', error));
      }
    });

    // 연결 오류 이벤트
    this.socket.on('connect_error', (error) => {
      console.error('연결 오류:', error);
      const errorMsg = `서버 연결 오류: ${error.message || JSON.stringify(error)}`;
      document.getElementById('status-text').textContent = errorMsg;
      
      // XHR 방식으로 서버 상태 확인
      fetch(`${this.serverUrl}/health`)
        .then(response => response.json())
        .then(data => {
          console.log('서버 상태 확인 성공:', data);
          document.getElementById('status-text').textContent = 
            `서버는 활성화되어 있으나 Socket.IO 연결에 문제가 있습니다. 새로고침을 시도하세요.`;
        })
        .catch(err => {
          console.error('서버 상태 확인 실패:', err);
          document.getElementById('status-text').textContent = 
            '서버가 응답하지 않습니다. 서버가 실행 중인지 확인하세요.';
        });
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

    // 에이전트 진행 상황 이벤트 처리
    this.socket.on('agent_progress', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('에이전트 진행 상황:', data);
        if (this.callbacks.onAgentProgress) {
          this.callbacks.onAgentProgress(data);
        }
      }
    });

    // 상태 업데이트 이벤트 처리
    this.socket.on('state_update', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('상태 업데이트:', data);
        if (this.callbacks.onStateUpdate) {
          this.callbacks.onStateUpdate(data);
        }
      }
    });

    // 노드 업데이트 이벤트 처리
    this.socket.on('node_update', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('노드 업데이트:', data);
        this._handleNodeUpdate(data);
      }
    });

    // LLM 업데이트 이벤트 처리
    this.socket.on('llm_update', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('LLM 업데이트:', data);
        if (this.callbacks.onLlmUpdate) {
          this.callbacks.onLlmUpdate(data);
        }
      }
    });

    // 에러 업데이트 이벤트 처리
    this.socket.on('error_update', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.error('에러 업데이트:', data);
        
        // 에이전트 시각화 업데이트
        if (window.agentFlowVisualizer && data.node) {
          window.agentFlowVisualizer.updateNodeStatus(data.node, 'error', data.message || '오류 발생');
        }
        
        // 그래프 시각화 업데이트
        if (window.graphViz && data.node) {
          window.graphViz.updateNodeStatus(data.node, 'error', data.message || '오류 발생');
        }
        
        if (this.callbacks.onError) {
          this.callbacks.onError(data.error || data.message);
        }
      }
    });

    // 작업 완료 처리
    this.socket.on('task_completed', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('작업이 완료되었습니다.');
        console.log('==== 최종 결과 데이터 ====');
        console.log('geogebra_commands:', data.result.geogebra_commands);
        console.log('explanation:', data.result.explanation);
        console.log('is_valid:', data.result.is_valid);
        console.log('=========================');
        
        if (this.callbacks.onCompleted) {
          this.callbacks.onCompleted(data.result);
        }
        
        // 결과 시각화 업데이트
        if (window.resultVisualizer) {
          if (data.result.parsed_elements) {
            window.resultVisualizer.updateParsedElements(data.result.parsed_elements);
          }
          if (data.result.geogebra_commands) {
            window.resultVisualizer.updateCommands(data.result.geogebra_commands);
          }
          if (data.result.explanation) {
            window.resultVisualizer.updateExplanation(data.result.explanation);
          }
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

    // 전체 상태 업데이트 이벤트 처리
    this.socket.on('state_full_update', (data) => {
      if (this.taskId && data.task_id === this.taskId) {
        console.log('전체 상태 업데이트:', data);
        if (this.callbacks.onStateFullUpdate) {
          this.callbacks.onStateFullUpdate(data);
        }
        
        // 결과 시각화 업데이트
        if (window.resultVisualizer) {
          if (data.data.parsed_elements) {
            window.resultVisualizer.updateParsedElements(data.data.parsed_elements);
          }
          if (data.data.geogebra_commands) {
            window.resultVisualizer.updateCommands(data.data.geogebra_commands);
          }
          if (data.data.explanation) {
            window.resultVisualizer.updateExplanation(data.data.explanation);
          }
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

  // Socket.IO 이벤트 이름과 내부 콜백 이름 매핑 확인
  mapSocketEventToCallback(eventName) {
    // 소켓 이벤트 이름을 내부 콜백 이름으로 변환
    const eventMap = {
      'node_update': 'onNodeUpdate',
      'state_update': 'onStateUpdate', 
      'state_full_update': 'onStateFullUpdate',
      'agent_progress': 'onAgentProgress',
      'llm_update': 'onLlmUpdate',
      'error_update': 'onError',
      'task_update': 'onUpdate',
      'task_completed': 'onCompleted',
      'task_error': 'onError'
    };
    
    return eventMap[eventName] || eventName;
  }

  // 노드 업데이트 이벤트 처리
  _handleNodeUpdate(data) {
    if (!this.taskId || data.task_id !== this.taskId) return;
    
    console.log('노드 업데이트 처리:', data);
    const callback = this.callbacks.onNodeUpdate;
    
    if (callback) {
      callback(data);
    }
    
    // 에이전트 흐름 시각화 직접 업데이트
    if (window.agentFlowVisualizer) {
      console.log('AgentFlowVisualizer로 노드 업데이트 중...');
      
      if (data.type === 'node_start') {
        window.agentFlowVisualizer.updateNodeStatus(data.node, 'running', data.message || '작업 시작');
      } else if (data.type === 'node_complete') {
        window.agentFlowVisualizer.updateNodeStatus(data.node, 'completed', data.message || '작업 완료');
      }
    } else {
      console.warn('AgentFlowVisualizer가 초기화되지 않았습니다.');
    }
    
    // 그래프 시각화 업데이트
    if (window.graphViz) {
      console.log('GraphVisualization으로 노드 업데이트 중...');
      
      if (data.type === 'node_start') {
        window.graphViz.updateNodeStatus(data.node, 'active', data.message || '작업 시작');
      } else if (data.type === 'node_complete') {
        window.graphViz.updateNodeStatus(data.node, 'completed', data.message || '작업 완료');
      }
    }
  }

  // 문제 제출
  async submitProblem(problemText) {
    try {
      // 로딩 상태 표시
      this.updateUI('pending', '작업을 제출 중입니다...');
      console.log('문제 제출 중:', problemText);

      // API URL 로그
      const apiUrl = `${this.serverUrl}/generate-commands`;
      console.log('API 요청 URL:', apiUrl);

      // 요청 본문
      const requestBody = {
        messages: [
          {
            role: 'user',
            content: problemText
          }
        ]
      };
      console.log('요청 본문:', JSON.stringify(requestBody));

      // 서버에 작업 제출
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestBody),
      });

      console.log('응답 상태:', response.status, response.statusText);
      
      // 응답 본문이 JSON이 아닌 경우 처리
      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
        console.log('응답 데이터:', data);
      } else {
        const textResponse = await response.text();
        console.error('JSON이 아닌 응답 받음:', textResponse);
        throw new Error('서버가 유효한 JSON을 반환하지 않았습니다.');
      }
      
      if (response.ok) {
        this.taskId = data.task_id;
        this.updateUI('submitted', `작업이 제출되었습니다. 작업 ID: ${this.taskId}`);
        console.log('작업 ID 할당됨:', this.taskId);
        return this.taskId;
      } else {
        const errorMsg = `작업 제출 실패: ${data.detail || '알 수 없는 오류'}`;
        this.updateUI('error', errorMsg);
        console.error(errorMsg);
        throw new Error(data.detail || '작업 제출에 실패했습니다.');
      }
    } catch (error) {
      const errorMsg = `오류 발생: ${error.message || error}`;
      this.updateUI('error', errorMsg);
      console.error('문제 제출 중 예외 발생:', error);
      
      // 서버 상태 확인 시도
      try {
        const healthResponse = await fetch(`${this.serverUrl}/health`);
        const healthData = await healthResponse.json();
        console.log('서버 상태 확인:', healthData);
      } catch (healthError) {
        console.error('서버 상태 확인 실패:', healthError);
      }
      
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

// 에이전트 실행 흐름을 시각화하는 컴포넌트
class AgentFlowVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.error(`Container with id ${containerId} not found`);
      return;
    }
    
    this.agentNodes = [
      { id: 'parsing_agent', name: '문제 해석', status: 'pending' },
      { id: 'planner_agent', name: '해결 계획 수립', status: 'pending' },
      { id: 'calculation_manager_agent', name: '계산 관리', status: 'pending' },
      { id: 'calculation_router_agent', name: '계산 라우팅', status: 'pending' },
      { id: 'triangle_calculation_agent', name: '삼각형 계산', status: 'pending' },
      { id: 'circle_calculation_agent', name: '원 계산', status: 'pending' },
      { id: 'angle_calculation_agent', name: '각도 계산', status: 'pending' },
      { id: 'length_calculation_agent', name: '길이 계산', status: 'pending' },
      { id: 'area_calculation_agent', name: '넓이 계산', status: 'pending' },
      { id: 'coordinate_calculation_agent', name: '좌표 계산', status: 'pending' },
      { id: 'calculation_result_merger_agent', name: '계산 결과 병합', status: 'pending' },
      { id: 'command_retrieval_agent', name: 'GeoGebra 명령어 검색', status: 'pending' },
      { id: 'command_generation_agent', name: 'GeoGebra 명령어 생성', status: 'pending' },
      { id: 'validation_agent', name: '명령어 검증', status: 'pending' },
      { id: 'command_regeneration_agent', name: '명령어 재생성', status: 'pending' },
      { id: 'explanation_agent', name: '해설 생성', status: 'pending' }
    ];
    
    this.activeNode = null;
    this.renderFlow();
  }
  
  // 에이전트 그래프 렌더링
  renderFlow() {
    console.log('AgentFlowVisualizer.renderFlow 호출됨');
    
    if (!this.container) {
      console.error('컨테이너가 없습니다.');
      return;
    }
    
    // 컨테이너 초기화
    this.container.innerHTML = '';
    this.container.className = 'agent-flow-container';
    
    // 그래프 컨테이너 생성
    const graphContainer = document.createElement('div');
    graphContainer.className = 'agent-graph';
    
    // 각 에이전트 노드 생성
    this.agentNodes.forEach(node => {
      const nodeElement = document.createElement('div');
      // 중요: nodeId를 그대로 사용 (node-를 앞에 붙이지 않음)
      nodeElement.id = node.id;
      nodeElement.className = `agent-node status-${node.status}`;
      if (this.activeNode === node.id) {
        nodeElement.classList.add('active');
      }
      
      // 상태 아이콘
      const statusIcon = document.createElement('div');
      statusIcon.className = 'status-icon';
      
      // 노드 이름
      const nameElement = document.createElement('div');
      nameElement.className = 'node-name';
      nameElement.textContent = node.name;
      
      nodeElement.appendChild(statusIcon);
      nodeElement.appendChild(nameElement);
      graphContainer.appendChild(nodeElement);
      
      console.log(`노드 생성: ID=${node.id}, 이름=${node.name}, 상태=${node.status}`);
    });
    
    this.container.appendChild(graphContainer);
    
    // 활성 노드 로그 섹션
    const logSection = document.createElement('div');
    logSection.className = 'agent-log-section';
    
    const logTitle = document.createElement('h3');
    logTitle.textContent = '에이전트 활동 로그';
    
    const logContent = document.createElement('div');
    logContent.id = 'agent-log-content';
    logContent.className = 'agent-log-content';
    
    logSection.appendChild(logTitle);
    logSection.appendChild(logContent);
    this.container.appendChild(logSection);
    
    console.log('AgentFlowVisualizer 렌더링 완료');
  }
  
  // 노드 상태 업데이트
  updateNodeStatus(nodeId, status, message = '') {
    console.log(`AgentFlowVisualizer.updateNodeStatus 호출: ${nodeId}, 상태: ${status}, 메시지: ${message}`);
    
    const nodeIndex = this.agentNodes.findIndex(node => node.id === nodeId);
    if (nodeIndex === -1) {
      console.warn(`노드 ID '${nodeId}'를 찾을 수 없습니다.`);
      return;
    }
    
    // 노드 상태 업데이트
    this.agentNodes[nodeIndex].status = status;
    console.log(`노드 '${nodeId}' 상태를 '${status}'로 업데이트`);
    
    // UI 요소 찾기 - ID에 접두사 없이 그대로 사용
    const nodeElement = document.getElementById(nodeId);
    if (!nodeElement) {
      console.warn(`노드 UI 요소 '${nodeId}'를 찾을 수 없습니다. 그래프를 다시 렌더링합니다.`);
      this.renderFlow();  // 그래프 다시 그리기
      return;
    }
    
    // 클래스 업데이트
    nodeElement.className = `agent-node status-${status}`;
    
    // 활성 노드 설정
    if (status === 'running') {
      this.activeNode = nodeId;
      nodeElement.classList.add('active');
      
      // 로그에 메시지 추가
      this.addLogMessage(this.agentNodes[nodeIndex].name, message);
    } else if (status === 'completed' && this.activeNode === nodeId) {
      nodeElement.classList.remove('active');
      this.activeNode = null;
      
      // 완료 메시지 추가
      this.addLogMessage(this.agentNodes[nodeIndex].name, `완료: ${message}`);
    }
    
    // 다른 노드의 active 클래스 제거
    if (status === 'running') {
      this.agentNodes.forEach(node => {
        if (node.id !== nodeId) {
          const otherElement = document.getElementById(node.id);
          if (otherElement) otherElement.classList.remove('active');
        }
      });
    }
  }
  
  // 로그 메시지 추가
  addLogMessage(agentName, message) {
    const logContent = document.getElementById('agent-log-content');
    if (!logContent) return;
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    
    const timestamp = new Date().toLocaleTimeString();
    const agentLabel = document.createElement('span');
    agentLabel.className = 'agent-label';
    agentLabel.textContent = agentName;
    
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span> `;
    logEntry.appendChild(agentLabel);
    logEntry.innerHTML += `: ${message}`;
    
    logContent.appendChild(logEntry);
    logContent.scrollTop = logContent.scrollHeight;
  }
  
  // 모든 노드 초기화
  resetNodes() {
    this.agentNodes.forEach(node => {
      node.status = 'pending';
    });
    this.activeNode = null;
    this.renderFlow();
    
    const logContent = document.getElementById('agent-log-content');
    if (logContent) logContent.innerHTML = '';
  }
}

// GeoGebra 명령어 및 결과 시각화 컴포넌트
class ResultVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.error(`Container with id ${containerId} not found`);
      return;
    }
    
    // 탭 구조 생성
    this.createTabs();
  }
  
  // 탭 UI 생성
  createTabs() {
    if (!this.container) return;
    
    // 컨테이너 초기화
    this.container.innerHTML = '';
    this.container.className = 'result-container';
    
    // 탭 헤더
    const tabHeader = document.createElement('div');
    tabHeader.className = 'tab-header';
    
    const tabs = [
      { id: 'parsed-tab', name: '문제 해석' },
      { id: 'commands-tab', name: 'GeoGebra 명령어' },
      { id: 'explanation-tab', name: '해설' }
    ];
    
    // 탭 버튼 생성
    tabs.forEach(tab => {
      const tabButton = document.createElement('button');
      tabButton.id = `${tab.id}-btn`;
      tabButton.className = 'tab-button';
      tabButton.textContent = tab.name;
      tabButton.onclick = () => this.showTab(tab.id);
      
      tabHeader.appendChild(tabButton);
    });
    
    // 탭 컨텐츠 영역
    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content';
    
    // 각 탭의 컨텐츠 영역 생성
    tabs.forEach(tab => {
      const tabPane = document.createElement('div');
      tabPane.id = tab.id;
      tabPane.className = 'tab-pane';
      
      tabContent.appendChild(tabPane);
    });
    
    this.container.appendChild(tabHeader);
    this.container.appendChild(tabContent);
    
    // 기본 탭 표시
    this.showTab('parsed-tab');
    
    console.log('탭 생성 완료:', tabs.map(t => t.id));
  }
  
  // 탭 표시
  showTab(tabId) {
    // 모든 탭 컨텐츠 숨기기
    const tabPanes = this.container.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => {
      pane.style.display = 'none';
    });
    
    // 모든 탭 버튼 비활성화
    const tabButtons = this.container.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
      button.classList.remove('active');
    });
    
    // 선택한 탭 컨텐츠 표시
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
      selectedTab.style.display = 'block';
    }
    
    // 선택한 탭 버튼 활성화
    const selectedButton = document.getElementById(`${tabId}-btn`);
    if (selectedButton) {
      selectedButton.classList.add('active');
    }
  }
  
  // 파싱된 요소 업데이트
  updateParsedElements(parsedElements) {
    const tabPane = document.getElementById('parsed-tab');
    if (!tabPane) return;
    
    if (!parsedElements || Object.keys(parsedElements).length === 0) {
      tabPane.innerHTML = '<div class="empty-message">아직 문제 해석이 완료되지 않았습니다.</div>';
      return;
    }
    
    tabPane.innerHTML = '<div class="parsed-elements-container"></div>';
    const container = tabPane.querySelector('.parsed-elements-container');
    
    // 파싱된 요소 표시
    Object.entries(parsedElements).forEach(([key, value]) => {
      const elementDiv = document.createElement('div');
      elementDiv.className = 'parsed-element';
      
      const titleEl = document.createElement('h4');
      titleEl.textContent = this.humanizeKeyName(key);
      
      const valueEl = document.createElement('div');
      valueEl.className = 'element-value';
      valueEl.innerHTML = this.formatValue(value);
      
      elementDiv.appendChild(titleEl);
      elementDiv.appendChild(valueEl);
      container.appendChild(elementDiv);
    });
  }
  
  // GeoGebra 명령어 업데이트
  updateCommands(commands) {
    console.log('ResultVisualizer.updateCommands 호출됨:', commands);
    
    if (!commands || commands.length === 0) {
      console.warn('비어있는 명령어 리스트가 전달되었습니다.');
      const commandsTab = document.getElementById('commands-tab');
      if (commandsTab) {
        commandsTab.innerHTML = '<p class="no-results">아직 생성된 명령어가 없습니다.</p>';
      }
      return;
    }
    
    const commandsTab = document.getElementById('commands-tab');
    if (!commandsTab) {
      console.error('commands-tab 요소를 찾을 수 없습니다.');
      return;
    }
    
    // 명령어 출력을 위한 HTML 생성
    const filteredCommands = this.filterGeoGebraCommands(commands);
    
    // 필터링된 명령어가 없으면 안내 메시지 표시
    if (filteredCommands.length === 0) {
      commandsTab.innerHTML = '<p class="no-results">유효한 GeoGebra 명령어가 없습니다.</p>';
      console.warn('필터링 후 유효한 명령어가 없습니다.');
      return;
    }
    
    console.log('필터링된 명령어:', filteredCommands);
    
    // 명령어 복사 버튼 만들기
    let commandsHtml = `
      <div class="commands-actions">
        <button id="copy-commands" class="copy-btn">모든 명령어 복사</button>
        <button id="open-geogebra" class="open-btn">GeoGebra에서 열기</button>
      </div>
      <div class="commands-list">
    `;
    
    // 각 명령어를 개별적으로 출력
    filteredCommands.forEach((cmd, index) => {
      commandsHtml += `
        <div class="command-item">
          <div class="command-number">${index + 1}</div>
          <div class="command-text">${cmd}</div>
          <button class="copy-single-btn" data-cmd="${this.escapeHtml(cmd)}">복사</button>
        </div>
      `;
    });
    
    commandsHtml += '</div>';
    commandsTab.innerHTML = commandsHtml;
    
    // 명령어 복사 버튼 이벤트 리스너 추가
    const copyCommandsBtn = document.getElementById('copy-commands');
    if (copyCommandsBtn) {
      copyCommandsBtn.addEventListener('click', () => {
        const commandsText = filteredCommands.join('\n');
        this.copyToClipboard(commandsText);
        alert('모든 명령어가 클립보드에 복사되었습니다!');
      });
    }
    
    // GeoGebra 열기 버튼 이벤트 리스너 추가
    const openGeogebraBtn = document.getElementById('open-geogebra');
    if (openGeogebraBtn) {
      openGeogebraBtn.addEventListener('click', () => {
        const commandsText = encodeURIComponent(filteredCommands.join('\n'));
        window.open(`https://www.geogebra.org/classic?command=${commandsText}`, '_blank');
      });
    }
    
    // 개별 명령어 복사 버튼 이벤트 리스너 추가
    const copySingleBtns = document.querySelectorAll('.copy-single-btn');
    copySingleBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const cmd = e.target.getAttribute('data-cmd');
        this.copyToClipboard(cmd);
        
        // 복사 확인 표시
        const originalText = e.target.textContent;
        e.target.textContent = '복사됨';
        e.target.classList.add('copied');
        
        setTimeout(() => {
          e.target.textContent = originalText;
          e.target.classList.remove('copied');
        }, 1000);
      });
    });
  }
  
  // GeoGebra 명령어 필터링 (실제 명령어만 추출)
  filterGeoGebraCommands(commands) {
    if (!Array.isArray(commands)) {
      console.error('commands가 배열이 아닙니다:', commands);
      return [];
    }
    
    // 첫 번째로 명령어 문자열 정리 (따옴표, 쉼표 제거)
    const cleanedCommands = commands.map(cmd => {
      if (typeof cmd !== 'string') {
        console.warn('명령어가 문자열이 아닙니다:', cmd);
        return String(cmd);
      }
      
      // 따옴표와 쉼표 제거
      let cleaned = cmd;
      if (cleaned.startsWith('"') && cleaned.endsWith('",')) {
        cleaned = cleaned.slice(1, -2);
      } else if (cleaned.startsWith('"') && cleaned.endsWith('"')) {
        cleaned = cleaned.slice(1, -1);
      } else if (cleaned.endsWith(',')) {
        cleaned = cleaned.slice(0, -1);
      }
      
      return cleaned;
    });
    
    // 실제 명령어만 필터링 (메타 데이터 제외)
    return cleanedCommands.filter(cmd => {
      // 불필요한 항목 건너뛰기
      return cmd !== 'commands' && 
             !cmd.startsWith('analysis') && 
             !cmd.startsWith('fixed_issues') &&
             cmd !== '[' && 
             cmd !== ']' &&
             cmd.trim() !== ''; // 빈 문자열 제외
    });
  }
  
  // HTML 이스케이프
  escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
  
  // 클립보드에 복사
  copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }
  
  // 해설 업데이트
  updateExplanation(explanation) {
    const tabPane = document.getElementById('explanation-tab');
    if (!tabPane) return;
    
    if (!explanation) {
      tabPane.innerHTML = '<div class="empty-message">아직 해설이 생성되지 않았습니다.</div>';
      return;
    }
    
    // 마크다운 렌더러가 있다면 사용할 수 있음
    // 여기서는 간단하게 텍스트로 표시
    const explanationContainer = document.createElement('div');
    explanationContainer.className = 'explanation-container';
    explanationContainer.innerHTML = `<pre>${explanation}</pre>`;
    
    tabPane.innerHTML = '';
    tabPane.appendChild(explanationContainer);
  }
  
  // 키 이름 사람이 읽기 쉬운 형태로 변환
  humanizeKeyName(key) {
    const nameMap = {
      'points': '점',
      'lines': '직선',
      'circles': '원',
      'triangles': '삼각형',
      'angles': '각도',
      'lengths': '길이',
      'areas': '넓이',
      'known_facts': '알려진 사실',
      'goal': '목표',
      'constraints': '제약 조건'
    };
    
    return nameMap[key] || key;
  }
  
  // 값 형식화
  formatValue(value) {
    if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value)) {
        return value.map(item => `<div>${this.formatValue(item)}</div>`).join('');
      } else {
        return Object.entries(value).map(([k, v]) => 
          `<div><strong>${k}:</strong> ${this.formatValue(v)}</div>`
        ).join('');
      }
    }
    return String(value);
  }
  
  // 모든 결과 초기화
  resetResults() {
    ['parsed-tab', 'commands-tab', 'explanation-tab'].forEach(tabId => {
      const tab = document.getElementById(tabId);
      if (tab) {
        tab.innerHTML = '<div class="empty-message">결과를 기다리는 중입니다...</div>';
      }
    });
  }
}

// 그래프 시각화를 위한 컴포넌트
class GraphVisualization {
    constructor(container) {
        this.container = container;
        this.nodes = new Map();
        this.activeNodes = new Set();
        this.completedNodes = new Set();
        this.errorNodes = new Set();
        this.connections = [
            { from: 'parsing_agent', to: 'planner_agent' },
            { from: 'planner_agent', to: 'calculation_manager_agent' },
            { from: 'planner_agent', to: 'command_retrieval_agent' },
            { from: 'calculation_manager_agent', to: 'calculation_router_agent' },
            { from: 'calculation_router_agent', to: 'triangle_calculation_agent' },
            { from: 'calculation_router_agent', to: 'circle_calculation_agent' },
            { from: 'calculation_router_agent', to: 'angle_calculation_agent' },
            { from: 'calculation_router_agent', to: 'length_calculation_agent' },
            { from: 'calculation_router_agent', to: 'area_calculation_agent' },
            { from: 'calculation_router_agent', to: 'coordinate_calculation_agent' },
            { from: 'calculation_router_agent', to: 'calculation_result_merger_agent' },
            { from: 'triangle_calculation_agent', to: 'calculation_router_agent' },
            { from: 'circle_calculation_agent', to: 'calculation_router_agent' },
            { from: 'angle_calculation_agent', to: 'calculation_router_agent' },
            { from: 'length_calculation_agent', to: 'calculation_router_agent' },
            { from: 'area_calculation_agent', to: 'calculation_router_agent' },
            { from: 'coordinate_calculation_agent', to: 'calculation_router_agent' },
            { from: 'calculation_result_merger_agent', to: 'command_retrieval_agent' },
            { from: 'command_retrieval_agent', to: 'command_generation_agent' },
            { from: 'command_generation_agent', to: 'validation_agent' },
            { from: 'validation_agent', to: 'explanation_agent' },
            { from: 'validation_agent', to: 'command_regeneration_agent' },
            { from: 'command_regeneration_agent', to: 'explanation_agent' },
            { from: 'command_regeneration_agent', to: 'validation_agent' }
        ];
        
        this.init();
    }
    
    init() {
        // 컨테이너 비우기
        this.container.innerHTML = '';
        this.container.classList.add('graph-visualization');
        
        // SVG 생성
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '400px');
        this.container.appendChild(svg);
        this.svg = svg;
        
        // 노드 컨테이너 생성
        const nodesContainer = document.createElement('div');
        nodesContainer.classList.add('nodes-container');
        this.container.appendChild(nodesContainer);
        this.nodesContainer = nodesContainer;
        
        // 노드 로깅 컨테이너 생성
        const logContainer = document.createElement('div');
        logContainer.classList.add('log-container');
        this.container.appendChild(logContainer);
        this.logContainer = logContainer;
        
        // 노드 정의 및 배치
        this.createNodes();
        this.drawConnections();
    }
    
    createNodes() {
        const nodeGroups = {
            'parsing': ['parsing_agent'],
            'planning': ['planner_agent'],
            'calculation': [
                'calculation_manager_agent', 
                'calculation_router_agent',
                'triangle_calculation_agent',
                'circle_calculation_agent',
                'angle_calculation_agent',
                'length_calculation_agent',
                'area_calculation_agent',
                'coordinate_calculation_agent',
                'calculation_result_merger_agent'
            ],
            'generation': [
                'command_retrieval_agent',
                'command_generation_agent',
                'validation_agent',
                'command_regeneration_agent'
            ],
            'explanation': ['explanation_agent']
        };
        
        let groupIndex = 0;
        
        for (const [groupName, groupNodes] of Object.entries(nodeGroups)) {
            const groupContainer = document.createElement('div');
            groupContainer.classList.add('node-group');
            groupContainer.innerHTML = `<h3>${groupName}</h3>`;
            this.nodesContainer.appendChild(groupContainer);
            
            groupNodes.forEach((nodeName, nodeIndex) => {
                const node = document.createElement('div');
                node.classList.add('node');
                node.setAttribute('data-node', nodeName);
                node.innerHTML = `<span>${nodeName}</span>`;
                
                // 노드에 위치 데이터 저장
                node.dataset.x = 100 + groupIndex * 200;
                node.dataset.y = 50 + nodeIndex * 60;
                
                // 노드 맵에 추가
                this.nodes.set(nodeName, node);
                
                groupContainer.appendChild(node);
            });
            
            groupIndex++;
        }
    }
    
    drawConnections() {
        // SVG 연결선 그리기
        this.connections.forEach(conn => {
            const fromNode = this.nodes.get(conn.from);
            const toNode = this.nodes.get(conn.to);
            
            if (fromNode && toNode) {
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.classList.add('connection');
                path.setAttribute('data-from', conn.from);
                path.setAttribute('data-to', conn.to);
                
                // 선 좌표 계산
                const x1 = fromNode.dataset.x;
                const y1 = fromNode.dataset.y;
                const x2 = toNode.dataset.x;
                const y2 = toNode.dataset.y;
                
                // 곡선으로 그리기
                path.setAttribute('d', `M ${x1} ${y1} C ${(parseInt(x1) + parseInt(x2)) / 2} ${y1}, ${(parseInt(x1) + parseInt(x2)) / 2} ${y2}, ${x2} ${y2}`);
                path.setAttribute('fill', 'none');
                path.setAttribute('stroke', '#aaa');
                path.setAttribute('stroke-width', '2');
                
                this.svg.appendChild(path);
            }
        });
    }
    
    updateNodeStatus(nodeName, status, message) {
        const node = this.nodes.get(nodeName);
        if (!node) return;
        
        // 모든 상태 클래스 제거
        node.classList.remove('active', 'completed', 'error');
        
        // 현재 상태 집합에서 제거
        this.activeNodes.delete(nodeName);
        this.completedNodes.delete(nodeName);
        this.errorNodes.delete(nodeName);
        
        // 새 상태 적용
        switch(status) {
            case 'active':
                node.classList.add('active');
                this.activeNodes.add(nodeName);
                this.addLogMessage(`🟢 ${nodeName} 시작: ${message}`);
                break;
            case 'completed':
                node.classList.add('completed');
                this.completedNodes.add(nodeName);
                this.addLogMessage(`✅ ${nodeName} 완료: ${message}`);
                break;
            case 'error':
                node.classList.add('error');
                this.errorNodes.add(nodeName);
                this.addLogMessage(`❌ ${nodeName} 오류: ${message}`);
                break;
        }
        
        // 연결 업데이트
        this.updateConnections();
    }
    
    updateConnections() {
        // 모든 연결선 업데이트
        const connections = this.svg.querySelectorAll('.connection');
        connections.forEach(conn => {
            const fromNode = conn.getAttribute('data-from');
            const toNode = conn.getAttribute('data-to');
            
            // 기본 스타일
            conn.setAttribute('stroke', '#aaa');
            conn.setAttribute('stroke-width', '2');
            conn.setAttribute('stroke-dasharray', '');
            
            // 활성 노드에서 활성 노드로의 연결
            if (this.activeNodes.has(fromNode) && this.activeNodes.has(toNode)) {
                conn.setAttribute('stroke', '#4CAF50');
                conn.setAttribute('stroke-width', '3');
            }
            // 완료된 노드에서 활성 노드로의 연결
            else if (this.completedNodes.has(fromNode) && this.activeNodes.has(toNode)) {
                conn.setAttribute('stroke', '#2196F3');
                conn.setAttribute('stroke-width', '3');
            }
            // 완료된 노드에서 완료된 노드로의 연결
            else if (this.completedNodes.has(fromNode) && this.completedNodes.has(toNode)) {
                conn.setAttribute('stroke', '#2196F3');
                conn.setAttribute('stroke-width', '2');
            }
            // 오류 노드와 관련된 연결
            else if (this.errorNodes.has(fromNode) || this.errorNodes.has(toNode)) {
                conn.setAttribute('stroke', '#F44336');
                conn.setAttribute('stroke-width', '2');
                conn.setAttribute('stroke-dasharray', '5,5');
            }
        });
    }
    
    addLogMessage(message) {
        const logEntry = document.createElement('div');
        logEntry.classList.add('log-entry');
        logEntry.textContent = message;
        this.logContainer.appendChild(logEntry);
        
        // 스크롤을 아래로 이동
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
        
        // 로그 항목 제한 (최대 50개)
        if (this.logContainer.children.length > 50) {
            this.logContainer.removeChild(this.logContainer.children[0]);
        }
    }
    
    reset() {
        this.activeNodes.clear();
        this.completedNodes.clear();
        this.errorNodes.clear();
        
        // 모든 노드 상태 초기화
        this.nodes.forEach(node => {
            node.classList.remove('active', 'completed', 'error');
        });
        
        // 모든 연결 초기화
        const connections = this.svg.querySelectorAll('.connection');
        connections.forEach(conn => {
            conn.setAttribute('stroke', '#aaa');
            conn.setAttribute('stroke-width', '2');
            conn.setAttribute('stroke-dasharray', '');
        });
        
        // 로그 초기화
        this.logContainer.innerHTML = '';
    }
}

// Socket.IO 이벤트 핸들러 확장
function setupGraphVisualizations() {
    // 그래프 시각화 컨테이너 생성
    const graphContainer = document.createElement('div');
    graphContainer.id = 'graph-visualization';
    
    // solution-container가 없으면 생성
    let solutionContainer = document.querySelector('#solution-container');
    if (!solutionContainer) {
      solutionContainer = document.createElement('div');
      solutionContainer.id = 'solution-container';
      solutionContainer.className = 'container mt-5';
      document.body.appendChild(solutionContainer);
    }
    
    // 컨테이너 표시
    solutionContainer.style.display = 'block';
    solutionContainer.prepend(graphContainer);
    
    // 그래프 시각화 스타일 추가
    const style = document.createElement('style');
    style.textContent = `
        .graph-visualization {
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: #f9f9f9;
        }
        
        .nodes-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            overflow-x: auto;
            padding: 10px 0;
        }
        
        .node-group {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0 10px;
            min-width: 200px;
        }
        
        .node-group h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #555;
        }
        
        .node {
            padding: 8px 12px;
            margin: 4px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #fff;
            font-size: 12px;
            text-align: center;
            width: 180px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            transition: all 0.3s ease;
        }
        
        .node.active {
            background-color: #E3F2FD;
            border-color: #2196F3;
            box-shadow: 0 0 5px rgba(33, 150, 243, 0.5);
        }
        
        .node.completed {
            background-color: #E8F5E9;
            border-color: #4CAF50;
        }
        
        .node.error {
            background-color: #FFEBEE;
            border-color: #F44336;
        }
        
        .status-pending {
            border-left-color: #ccc;
            opacity: 0.7;
        }
        
        .status-running {
            border-left-color: #0078ff;
            background-color: #e6f2ff;
        }
        
        .status-completed {
            border-left-color: #00c853;
            background-color: #e6fff0;
        }
        
        .status-error {
            border-left-color: #ff3d00;
            background-color: #ffedeb;
        }
        
        .status-icon {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ccc;
        }
        
        .status-running .status-icon {
            background-color: #0078ff;
            animation: pulse 1.5s infinite;
        }
        
        .status-completed .status-icon {
            background-color: #00c853;
        }
        
        .status-error .status-icon {
            background-color: #ff3d00;
        }
        
        .node-name {
            font-size: 14px;
            font-weight: 500;
        }
        
        .agent-log-section {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .agent-log-section h3 {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 16px;
            color: #333;
        }
        
        .agent-log-content {
            font-family: monospace;
            font-size: 13px;
            line-height: 1.5;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-bottom: 1px solid #eee;
        }
        
        .timestamp {
            color: #666;
        }
        
        .agent-label {
            color: #0078ff;
            font-weight: bold;
        }
        
        /* 결과 시각화 스타일 */
        .result-container {
            margin-top: 30px;
        }
        
        .tab-header {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 15px;
        }
        
        .tab-button {
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab-button.active {
            color: #0078ff;
            border-bottom-color: #0078ff;
        }
        
        .tab-pane {
            display: none;
            padding: 15px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .empty-message {
            color: #888;
            font-style: italic;
            text-align: center;
            padding: 30px;
        }
        
        .parsed-elements-container, .commands-container, .explanation-container {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .parsed-element {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .parsed-element h4 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #333;
        }
        
        .element-value {
            font-size: 14px;
            color: #555;
        }
        
        .command-item {
            padding: 8px;
            margin-bottom: 5px;
            border-radius: 4px;
            background-color: #f5f7fa;
            font-family: monospace;
            display: flex;
        }
        
        .command-number {
            color: #0078ff;
            margin-right: 10px;
            font-weight: bold;
            min-width: 25px;
        }
        
        .copy-button {
            margin-bottom: 15px;
            padding: 8px 16px;
            background-color: #0078ff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .copy-button:hover {
            background-color: #0056b3;
        }
        
        .explanation-container pre {
            white-space: pre-wrap;
            font-family: sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // 그래프 시각화 인스턴스 생성
    const graphViz = new GraphVisualization(graphContainer);
    
    // 소켓 이벤트 리스너 등록
    socket.on('agent_progress', function(data) {
        console.log('에이전트 진행 상황:', data);
    });
    
    socket.on('node_update', function(data) {
        console.log('노드 업데이트:', data);
        
        if (data.type === 'node_start') {
            graphViz.updateNodeStatus(data.node, 'active', data.message || '작업 시작');
            
            // 그래프 상태 표시 업데이트
            const statusEl = document.querySelector('#graph-status');
            if (statusEl) {
                const indicator = statusEl.querySelector('.progress-indicator');
                const statusText = statusEl.querySelector('.status-text');
                
                if (indicator) {
                    indicator.className = 'progress-indicator running';
                }
                
                if (statusText) {
                    statusText.textContent = `진행 중: ${data.node}`;
                }
            }
            
        } else if (data.type === 'node_complete') {
            graphViz.updateNodeStatus(data.node, 'completed', data.message || '작업 완료');
            
            // 그래프 상태 표시 업데이트
            const statusEl = document.querySelector('#graph-status');
            if (statusEl) {
                const statusText = statusEl.querySelector('.status-text');
                
                if (statusText) {
                    statusText.textContent = `완료된 노드: ${data.node}`;
                }
            }
        }
    });
    
    socket.on('error_update', function(data) {
        console.log('오류 업데이트:', data);
        
        if (data.type === 'error') {
            graphViz.updateNodeStatus(data.node, 'error', data.message);
        }
    });
    
    socket.on('task_update', function(data) {
        if (data.status === 'processing') {
            // 작업 시작 시 그래프 초기화
            graphViz.reset();
        }
    });
    
    // 전체 상태 업데이트 이벤트 리스너 추가
    socket.on('state_full_update', function(data) {
        console.log('전체 상태 업데이트:', data);
        
        // 상태 데이터가 있으면 결과 시각화 업데이트
        if (data.data) {
            // 결과 시각화 컴포넌트 접근
            if (window.resultVisualizer) {
                if (data.data.parsed_elements) {
                    window.resultVisualizer.updateParsedElements(data.data.parsed_elements);
                }
                if (data.data.geogebra_commands) {
                    window.resultVisualizer.updateCommands(data.data.geogebra_commands);
                }
                if (data.data.explanation) {
                    window.resultVisualizer.updateExplanation(data.data.explanation);
                }
            } else {
                // 결과 시각화 컴포넌트가 없으면 생성
                setTimeout(() => {
                    window.resultVisualizer = new ResultVisualizer('result-visualizer');
                    
                    // 데이터로 업데이트
                    if (data.data.parsed_elements) {
                        window.resultVisualizer.updateParsedElements(data.data.parsed_elements);
                    }
                    if (data.data.geogebra_commands) {
                        window.resultVisualizer.updateCommands(data.data.geogebra_commands);
                    }
                    if (data.data.explanation) {
                        window.resultVisualizer.updateExplanation(data.data.explanation);
                    }
                }, 100);
            }
        }
    });
    
    // 작업 완료 이벤트 리스너
    socket.on('task_completed', function(data) {
        console.log('작업 완료:', data);
        
        // 그래프 상태 표시 업데이트
        const statusEl = document.querySelector('#graph-status');
        if (statusEl) {
            const indicator = statusEl.querySelector('.progress-indicator');
            const statusText = statusEl.querySelector('.status-text');
            
            if (indicator) {
                indicator.className = 'progress-indicator completed';
            }
            
            if (statusText) {
                statusText.textContent = '모든 작업이 완료되었습니다.';
            }
        }
    });
    
    // 에러 이벤트 리스너
    socket.on('task_error', function(data) {
        console.error('작업 오류:', data);
        
        // 그래프 상태 표시 업데이트
        const statusEl = document.querySelector('#graph-status');
        if (statusEl) {
            const indicator = statusEl.querySelector('.progress-indicator');
            const statusText = statusEl.querySelector('.status-text');
            
            if (indicator) {
                indicator.className = 'progress-indicator failed';
            }
            
            if (statusText) {
                statusText.textContent = `오류 발생: ${data.error || '알 수 없는 오류'}`;
            }
        }
    });
    
    // 전역 변수로 저장 (다른 함수에서 접근 가능하도록)
    window.graphViz = graphViz;
}

// DOM이 로드되면 그래프 시각화 설정
document.addEventListener('DOMContentLoaded', function() {
    if (typeof socket !== 'undefined') {
        setupGraphVisualizations();
    }
});

// 사용 예제
function initializeUI() {
  console.log('initializeUI 함수 실행 시작');
  
  // 스타일시트 추가
  addStylesheet();
  
  // UI 컴포넌트 초기화
  const agentFlow = new AgentFlowVisualizer('agent-flow');
  const resultVisualizer = new ResultVisualizer('result-visualizer');
  
  // 기하학 문제 솔버 초기화
  console.log('GeometryProblemSolver 초기화 중...');
  const solver = new GeometryProblemSolver()
    .connect()
    .on('processing', (data) => {
      // 처리 중 상태 업데이트
      updateProgressBar(30);
      updateStatusText('문제를 분석 중입니다...');
    })
    .on('nodeUpdate', (data) => {
      // 노드 업데이트 표시
      console.log('노드 업데이트 콜백:', data);
      
      if (data.type === 'node_start') {
        agentFlow.updateNodeStatus(data.node, 'running', data.message || '작업 시작');
        updateProgressBar(50);
      } else if (data.type === 'node_complete') {
        agentFlow.updateNodeStatus(data.node, 'completed', data.message || '작업 완료');
        updateProgressBar(70);
      }
      
      // 그래프 시각화 업데이트
      if (window.graphViz) {
        if (data.type === 'node_start') {
          window.graphViz.updateNodeStatus(data.node, 'active', data.message || '작업 시작');
        } else if (data.type === 'node_complete') {
          window.graphViz.updateNodeStatus(data.node, 'completed', data.message || '작업 완료');
        }
      }
    })
    .on('stateUpdate', (data) => {
      // 상태 업데이트 처리
      if (data.data.parsed_elements) {
        resultVisualizer.updateParsedElements(data.data.parsed_elements);
      }
      if (data.data.geogebra_commands) {
        resultVisualizer.updateCommands(data.data.geogebra_commands);
      }
      if (data.data.explanation) {
        resultVisualizer.updateExplanation(data.data.explanation);
      }
    })
    .on('completed', (result) => {
      // 결과 표시
      updateProgressBar(100);
      updateStatusText('완료!');
      resultVisualizer.updateParsedElements(result.parsed_elements);
      resultVisualizer.updateCommands(result.geogebra_commands);
      resultVisualizer.updateExplanation(result.explanation);
      
      // 완료 표시
      document.getElementById('submit-button').disabled = false;
      document.getElementById('submit-button').textContent = '새 문제 제출';
    })
    .on('error', (error) => {
      // 오류 표시
      updateProgressBar(0);
      updateStatusText(`오류: ${error}`);
      document.getElementById('submit-button').disabled = false;
    });
  
  console.log('이벤트 핸들러 등록 완료');
  
  // 제출 버튼 이벤트 핸들러
  const submitButton = document.getElementById('submit-button');
  console.log('제출 버튼 요소:', submitButton ? '찾음' : '찾지 못함');
  
  if (submitButton) {
    console.log('제출 버튼에 이벤트 리스너 등록');
    
    // 기존 이벤트 리스너 제거 (중복 방지)
    const newButton = submitButton.cloneNode(true);
    submitButton.parentNode.replaceChild(newButton, submitButton);
    
    // 새 이벤트 리스너 등록
    newButton.addEventListener('click', async function() {
      console.log('제출 버튼 클릭됨');
      
      // 문제 입력 가져오기
      const problemInput = document.getElementById('problem-input');
      if (!problemInput || !problemInput.value.trim()) {
        alert('문제를 입력해주세요.');
        console.error('문제 입력이 비어있습니다.');
        return;
      }
      
      const problemText = problemInput.value.trim();
      console.log('입력된 문제:', problemText);
      
      // UI 초기화
      agentFlow.resetNodes();
      resultVisualizer.resetResults();
      updateProgressBar(10);
      updateStatusText('문제를 제출 중입니다...');
      
      // 버튼 비활성화
      newButton.disabled = true;
      newButton.textContent = '처리 중...';
      
      try {
        // 문제 제출
        console.log('solver.submitProblem 호출');
        await solver.submitProblem(problemText);
      } catch (error) {
        console.error('문제 제출 오류:', error);
        newButton.disabled = false;
        newButton.textContent = '문제 제출';
        updateStatusText(`오류: ${error.message || '알 수 없는 오류'}`);
      }
    });
    
    console.log('제출 버튼 이벤트 리스너 등록 완료');
  } else {
    console.error('제출 버튼을 찾을 수 없습니다.');
  }
  
  // 전역 변수에 저장
  window.geometrySolver = solver;
  window.agentFlowVisualizer = agentFlow;
  window.resultVisualizer = resultVisualizer;
  
  console.log('initializeUI 함수 실행 완료');
  
  return {
    solver,
    agentFlow,
    resultVisualizer
  };
}

// UI 업데이트 함수
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

// 스타일시트 추가 함수
function addStylesheet() {
  const style = document.createElement('style');
  style.textContent = `
    .agent-flow-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .agent-graph {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 20px;
    }
    
    .agent-node {
      padding: 15px;
      border-radius: 8px;
      background-color: #f5f5f5;
      border-left: 5px solid #ddd;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.3s ease;
    }
    
    .agent-node.active {
      box-shadow: 0 0 15px rgba(0, 120, 255, 0.5);
      transform: translateY(-5px);
    }
    
    .status-pending {
      border-left-color: #ccc;
      opacity: 0.7;
    }
    
    .status-running {
      border-left-color: #0078ff;
      background-color: #e6f2ff;
    }
    
    .status-completed {
      border-left-color: #00c853;
      background-color: #e6fff0;
    }
    
    .status-error {
      border-left-color: #ff3d00;
      background-color: #ffedeb;
    }
    
    .status-icon {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background-color: #ccc;
    }
    
    .status-running .status-icon {
      background-color: #0078ff;
      animation: pulse 1.5s infinite;
    }
    
    .status-completed .status-icon {
      background-color: #00c853;
    }
    
    .status-error .status-icon {
      background-color: #ff3d00;
    }
    
    .node-name {
      font-size: 14px;
      font-weight: 500;
    }
    
    .agent-log-section {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 15px;
      max-height: 200px;
      overflow-y: auto;
    }
    
    .agent-log-section h3 {
      margin-top: 0;
      margin-bottom: 10px;
      font-size: 16px;
      color: #333;
    }
    
    .agent-log-content {
      font-family: monospace;
      font-size: 13px;
      line-height: 1.5;
    }
    
    .log-entry {
      margin-bottom: 5px;
      padding: 5px;
      border-bottom: 1px solid #eee;
    }
    
    .timestamp {
      color: #666;
    }
    
    .agent-label {
      color: #0078ff;
      font-weight: bold;
    }
    
    /* 결과 시각화 스타일 */
    .result-container {
      margin-top: 30px;
    }
    
    .tab-header {
      display: flex;
      border-bottom: 1px solid #ddd;
      margin-bottom: 15px;
    }
    
    .tab-button {
      padding: 10px 20px;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      color: #666;
      border-bottom: 3px solid transparent;
      transition: all 0.3s;
    }
    
    .tab-button.active {
      color: #0078ff;
      border-bottom-color: #0078ff;
    }
    
    .tab-pane {
      display: none;
      padding: 15px;
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .empty-message {
      color: #888;
      font-style: italic;
      text-align: center;
      padding: 30px;
    }
    
    .parsed-elements-container, .commands-container, .explanation-container {
      max-height: 400px;
      overflow-y: auto;
    }
    
    .parsed-element {
      margin-bottom: 15px;
      padding-bottom: 15px;
      border-bottom: 1px solid #eee;
    }
    
    .parsed-element h4 {
      margin-top: 0;
      margin-bottom: 10px;
      color: #333;
    }
    
    .element-value {
      font-size: 14px;
      color: #555;
    }
    
    .command-item {
      padding: 8px;
      margin-bottom: 5px;
      border-radius: 4px;
      background-color: #f5f7fa;
      font-family: monospace;
      display: flex;
    }
    
    .command-number {
      color: #0078ff;
      margin-right: 10px;
      font-weight: bold;
      min-width: 25px;
    }
    
    .copy-button {
      margin-bottom: 15px;
      padding: 8px 16px;
      background-color: #0078ff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s;
    }
    
    .copy-button:hover {
      background-color: #0056b3;
    }
    
    .explanation-container pre {
      white-space: pre-wrap;
      font-family: sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
    }
    
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.4; }
      100% { opacity: 1; }
    }
  `;
  
  document.head.appendChild(style);
}

// 문서 로드 완료 시 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', () => {
  // UI 초기화
  initializeUI();
});
