/**
 * 코다리 스크립트: Funnel Gateway MVP State Machine Logic
 * 목표: Hook -> Gap (Deficiency) -> Resolution의 시간 흐름과 상태 전환을 시뮬레이션합니다.
 */

// 🛠️ Global State Management 및 DOM 요소 참조
const container = document.getElementById('container');
const statusDisplay = document.getElementById('status-bar');
const sections = {
    hook: document.getElementById('hook-phase'),
    gap: document.getElementById('gap-phase'),
    resolution: document.getElementById('resolution-phase')
};

// 📐 타이밍 정의 (V9.0 스토리보드 기반, 시간 흐름을 코드로 구현)
const TIMING = {
    HOOK_DURATION_MS: 4000,   // 4초 동안 Hook 유지
    GAP_DURATION_MS: 5000,    // 5초 동안 Gateway 결핍 유도
    TOTAL_MVP_TIME_MS: 12000 // 총 예상 시간 (클릭 제외)
};

/**
 * 상태 업데이트 함수: UI와 Status Bar를 동기화합니다.
 * @param {string} stateName - 현재 상태 ('HOOK', 'GAP', 'RESOLUTION')
 */
function updateState(stateName, duration = null) {
    Object.values(sections).forEach(el => el.classList.add('hidden'));

    let activeSection;
    switch (stateName) {
        case 'HOOK':
            activeSection = sections.hook;
            break;
        case 'GAP':
            activeSection = sections.gap;
            break;
        case 'RESOLUTION':
            activeSection = sections.resolution;
            break;
    }

    if (activeSection) {
        activeSection.classList.remove('hidden');
    }

    let statusMessage = `현재 상태: ${stateName} (${duration ? `${Math.round(duration / 1000)}초 남음` : '진입'})`;
    statusDisplay.textContent = statusMessage;
    console.log(`[STATE CHANGE] -> ${stateName}`);
}

/**
 * Funnel Gateway의 핵심 로직을 시뮬레이션합니다.
 */
function runFunnelGatewaySequence() {
    // 1. 초기 상태 설정 및 Hook 시작 (T=0ms)
    updateState('HOOK');
    console.log("--- [MVP Start] Funnel Gateway Sequence Initiated ---");

    // 2. Hook 단계 진행 (4초)
    setTimeout(() => {
        console.log("[Transition] HOOK -> GAP: 지식 결핍 유도 시작.");
        updateState('GAP');
    }, TIMING.HOOK_DURATION_MS);

    // 3. Gap/Gateway 단계 진행 (5초) - 가장 중요한 기술적 충격 구간
    setTimeout(() => {
        console.log("[Transition] GAP -> RESOLUTION: 간극을 해소할 다음 단계를 제시합니다.");
        updateState('RESOLUTION');
    }, TIMING.HOOK_DURATION_MS + TIMING.GAP_DURATION_MS);


    // 4. Resolution 단계 완료 및 CTA 활성화 (T=9초)
    const ctaButton = document.getElementById('cta-button');
    ctaButton.addEventListener('click', () => {
        console.log("✅ API CALL TRIGGERED: 사용자가 다음 단계를 능동적으로 탐색함.");
        statusDisplay.textContent = "테스트 통과 확인했어요! (API 호출 성공)";
        alert("SUCCESS! Funnel Gateway의 목표(다음 행동 유도)를 달성했습니다. 실제 데이터 수집 로직을 여기에 구현하세요!");
    });

}

// 🚀 전체 시퀀스 실행 시작
document.addEventListener('DOMContentLoaded', runFunnelGatewaySequence);
