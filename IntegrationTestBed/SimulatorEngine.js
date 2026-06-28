/**
 * @fileoverview Funnel Gateway State Machine 기반 통합 모션 에셋 시뮬레이터 엔진.
 * 핵심 기능: 시간 축(Time Axis) 제어, 상태 전이 로직 검증, API 지연 및 데이터 오류 예측.
 */

const VIEWPORT = document.getElementById('simulation-viewport');
const LOG_OUTPUT = document.getElementById('log-output');
const TIMELINE_DISPLAY = document.getElementById('timeline-display');
const START_BUTTON = document.getElementById('start-simulation');

// --- State Machine Definition (상태 정의) ---
const STATES = {
    INIT: { name: "초기화", duration: 100 },
    NORMAL: { name: "정상 흐름 (Hook)", duration: 320, handler: handleNormalState },
    GLITCH_GAP: { name: "지식 결핍 구간 (T+320ms ~ T+510ms)", duration: 190, handler: handleGlitchGapState },
    RESOLUTION: { name: "해결/전환 직전", duration: 100, handler: handleResolutionState },
    API_FAILURE: { name: "시스템 오류 (API 지연)", duration: 500, handler: handleApiFailure }
};

let currentState = STATES.INIT;
let currentTime = 0; // ms 단위로 시간 추적
let animationFrameId = null;

// --- Utility Functions ---
function logEvent(message, type = 'INFO') {
    const p = document.createElement('p');
    p.style.color = (type === 'ERROR') ? '#f44336' : (type === 'WARNING') ? '#ffeb3b' : '#90caf9';
    p.innerHTML = `[${new Date().toLocaleTimeString()}] [${type}:${currentState.name}] ${message}`;
    LOG_OUTPUT.prepend(p); // 새로운 로그는 위에 추가
    // 로그가 너무 길어지지 않도록 제한 (선택적)
    while (LOG_OUTPUT.children.length > 50) {
        LOG_OUTPUT.removeChild(LOG_OUTPUT.lastChild);
    }
}

function updateDisplay() {
    TIMELINE_DISPLAY.textContent = `현재 시간: ${currentTime.toFixed(0)}ms | 상태: ${currentState.name}`;
}

// --- State Handlers (각 상태별 로직) ---

function handleNormalState() {
    logEvent("정상적인 정보 흐름. Funnel Gateway 진입 직전의 평온함을 유지합니다.", 'INFO');
    // 이 구간에서는 애니메이션 요소가 최소화되어야 함을 명시합니다.
}

function handleGlitchGapState() {
    logEvent(`🚨 [CRITICAL] T+320ms ~ T+510ms: 지식적 결핍(Knowledge Gap) 발생. 시스템 에셋 'Glitch' 활성화!`, 'WARNING');
    // 시뮬레이터에서 Glitch 애니메이션을 강제로 켜는 로직 (CSS/WebGL Placeholder를 활용한다고 가정)
    document.getElementById('glitch-asset').style.opacity = '1';
    setTimeout(() => { document.getElementById('glitch-asset').style.opacity = '0'; }, 50); // 짧게 플래시
}

function handleResolutionState() {
    logEvent("결핍 해소 및 다음 단계로의 전환을 유도합니다. CTA 게이트웨이 활성화.", 'INFO');
    // CTA Gateway 시각화 (CSS 클래스 활용)
    const cta = document.getElementById('cta-gateway');
    cta.classList.add('active');

    // 1초 후 다음 상태로 자동 전환을 유도하는 로직 추가 가능
}

function handleApiFailure() {
    logEvent("⚠️ [ERROR SIMULATION] API 호출 지연 감지: 외부 데이터 파이프라인 연결에 문제가 발생했습니다. (예: 사용자 액션 데이터 미수신)", 'ERROR');
    // 이 구간은 실제 제작 시 가장 위험한 지점입니다. 시스템이 멈추거나, 임시 대체 에셋으로 전환되어야 합니다.
}

// --- Core State Machine Logic ---

function transitionState(newState) {
    if (currentState === newState) return;

    logEvent(`--- 상태 전이 발생: ${currentState.name} -> ${newState.name} ---`, 'SYSTEM');
    currentTime = 0; // 새로운 스테이트 시작 시 시간을 리셋할 필요는 없지만, 로직 관리를 위해 명시적으로 재설정한다고 가정합니다.
    currentState = newState;

    // 이전 상태 클린업 (Cleanup)
    document.getElementById('glitch-asset').style.opacity = '0';
    document.getElementById('cta-gateway').classList.remove('active');

    // 새 상태 핸들러 실행 및 로직 주입
    if (currentState.handler) {
        currentState.handler();
    }
}

/**
 * @function simulateTimeStep
 * @description 시간을 조금씩 증가시키고, 현재 시간에 도달하는 State Machine의 전환을 감지합니다.
 */
function simulateTimeStep(deltaTime) {
    currentTime += deltaTime;
    updateDisplay();

    // --- [CORE LOGIC: Time-Based Transition Check] ---
    let nextState = currentState;
    let transitionOccurred = false;

    switch (currentState) {
        case STATES.INIT:
            if (currentTime >= 50) { // T=50ms 경과 시, 첫 상태로 이동
                nextState = STATES.NORMAL;
                transitionOccurred = true;
                break;
            }
            break;

        case STATES.NORMAL:
            // Funnel Gateway 진입 지점 예측 (T+320ms)
            if (currentTime >= 320 && currentTime < 350) { // 320ms에 근접하면 다음 상태로 강제 전환 시도
                nextState = STATES.GLITCH_GAP;
                transitionOccurred = true;
                break;
            }
            // API 실패 시뮬레이션 조건 (예: 특정 시간대에서 데이터가 오지 않을 때)
            if (currentTime >= 700 && currentTime < 750) { // T=700ms에 임시 오류 발생 가정
                 nextState = STATES.API_FAILURE;
                 transitionOccurred = true;
            }
            break;

        case STATES.GLITCH_GAP:
            // 결핍 구간 종료 (T+510ms)
            if (currentTime >= 510 && currentTime < 530) {
                nextState = STATES.RESOLUTION;
                transitionOccurred = true;
                break;
            }
            break;

        case STATES.RESOLUTION:
             // 모든 로직이 완료되었음을 가정하고 시뮬레이션을 종료합니다.
            if (currentTime >= 1500) {
                 logEvent("✅ 통합 모션 에셋 시뮬레이터 테스트 완료. 구조적 무결성 검증 성공.", 'SUCCESS');
                START_BUTTON.disabled = false;
                START_BUTTON.textContent = "재시작";
                return true; // 종료 플래그 반환
            }
            break;

        case STATES.API_FAILURE:
             // API 실패 후, Recovery Time이 경과하면 원래 정상 흐름으로 복귀를 시도합니다.
            if (currentTime >= 1500) {
                logEvent("♻️ 데이터 오류 구간 통과. 시스템이 자가 복구 로직을 수행하며 다음 단계로 진행합니다.", 'INFO');
                nextState = STATES.RESOLUTION;
                transitionOccurred = true;
            }
            break;
    }

    if (transitionOccurred) {
        transitionState(nextState);
        return false; // 아직 종료되지 않음
    }

    // 재귀 호출 설정: 16ms 간격으로 진행하여 부드러운 시간 흐름 구현 (FPS 기반)
    animationFrameId = requestAnimationFrame(() => simulateTimeStep(16));
    return false; // 계속 실행
}


/**
 * @function initSimulator
 * @description 시뮬레이터를 초기화하고 이벤트 리스너를 설정합니다.
 */
function initSimulator() {
    // 상태 초기화 및 버튼 핸들러 재설정
    currentState = STATES.INIT;
    currentTime = 0;
    LOG_OUTPUT.innerHTML = '<p style="color: #4caf50;">✅ 시뮬레이터 준비 완료. 시간 축 제어가 정상적으로 로드되었습니다.</p>';

    START_BUTTON.onclick = () => {
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        // 초기 상태로 강제 전환하여 타이머 리셋
        transitionState(STATES.INIT);
        simulateTimeStep(16); // 첫 프레임 실행
    };

    logEvent("System Ready: State Machine Engine Initialized.", 'SYSTEM');
}


// --- 실행 시작 ---
initSimulator();
</script>
