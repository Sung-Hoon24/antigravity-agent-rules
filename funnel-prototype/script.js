// ===============================================================
// 💻 스크립트 로직 (State Machine Implementation)
// 개발자 시점의 주석을 통해 API 연동 지점을 명시합니다.
// ===============================================================

const mainContent = document.getElementById('main-content');
const ctaGateway = document.getElementById('cta-gateway');
const glitchOverlay = document.createElement('div'); // Glitch 전용 오버레이
glitchOverlay.className = 'glitch-overlay';
document.body.appendChild(glitchOverlay);

// 1. 상태 정의 (State Definition)
let currentState = 'INITIAL_HOOK';
const API_TRIGGER = 'API_CALL: CONCLUSION_VOID'; // 핵심 트리거 지점 명시

/**
 * @description 현재 시스템의 상태를 업데이트하고 DOM을 조정합니다.
 * @param {string} newState - 다음 상태 코드 (e.g., VOID, CTA_ACTIVE)
 */
function updateState(newState) {
    currentState = newState;
    console.log(`[STATE CHANGE]: Current State -> ${newState}`);

    // 1단계: 콘텐츠 영역 비활성화 및 오버레이 활성화
    mainContent.classList.add('hidden');
    ctaGateway.classList.remove('hidden'); // CTA는 미리 노출 준비
    glitchOverlay.classList.add('active');

    if (newState === 'VOID_DETECTED') {
        // 2단계: Glitch 애니메이션 발동 및 메시지 오버레이
        document.getElementById('trigger-point').innerHTML = '<div class="glitch-text">SYSTEM FAILURE</div>';
    } else if (newState === 'CTA_ACTIVE') {
        // 3단계: CTA Gate가 주도권을 잡고 사용자에게 구매를 강제하는 상태
        console.warn("⚠️ [API WARNING] Funnel State Machine 진입. 구매 유도가 최우선입니다.");
    }
}

/**
 * @description 시뮬레이션된 영상 재생 흐름 (Hook -> Void -> CTA)
 */
function startFunnelSimulation() {
    // 1. Hook 단계 (0초 ~ 30초): 정상적인 학술 정보 전달
    console.log("--- Funnel Start: Initial Hook State ---");

    setTimeout(() => {
        // 2. Void 감지 지점 (30초): 시스템 오류 발생 및 논리적 단절 유도
        updateState('VOID_DETECTED');
        alert('⚠️ [SYSTEM ALERT] 정보의 공백(Void)이 감지되었습니다.');
    }, 500); // 짧은 딜레이로 시뮬레이션

    // 3. 최종 CTA 진입 (40초): Void가 극대화되어 구매 유도가 필요해지는 상태
    setTimeout(() => {
        if (currentState === 'VOID_DETECTED') {
            updateState('CTA_ACTIVE');
            console.log(`✅ [SUCCESS] ${API_TRIGGER} 트리거 완료. CTA Gate를 활성화합니다.`);
        }
    }, 3000); // 시뮬레이션 시간을 위해 임의로 조정

}


/**
 * @description 구매 버튼 클릭 이벤트 핸들러 (시뮬레이션)
 */
function simulatePurchase() {
    // 여기서 실제 API 호출을 통해 사용자의 유료 전환 데이터를 수집해야 함.
    console.log("[EVENT LOG]: Purchase CTA Clicked by User.");
    alert("✅ [SUCCESS] Funnel 진입 성공! '지식 단절 마스터 패키지' 구매 페이지로 이동합니다.");

    // API 통신 시뮬레이션: 웹훅(Webhook) 호출을 통해 외부 CRM에 유저 ID와 이벤트 데이터를 전송하는 로직이 필요함.
}


// 🚀 실행 시작
window.onload = startFunnelSimulation;
</script>
