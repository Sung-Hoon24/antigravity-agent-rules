/**
 * VTM Test Harness (MVP Prototype)
 * 목적: Designer가 정의한 Void Transition Module의 입력 파라미터와 흐름 제어를 테스트한다.
 * 실제 렌더링 없이, 시스템이 요구하는 '파라미터 스펙'을 검증하는 데 초점을 맞춘다.
 */

// -------------------------
// 1. Input Structure Definition (API Spec 준수)
// -------------------------

/**
 * @typedef {Object} VTMInput
 * @property {string} sourceMedia - 현재 미디어 스트림 유형 (e.g., 'video', 'text_overlay').
 * @property {number} timeMarkerStart - 전환 시작 시간 (초).
 * @property {number} timeMarkerEnd - 전환 종료 시간 (초).
 * @property {number} triggerIntensity - 정보 충돌 임계값 점수 (0.0 ~ 1.0).
 */

/**
 * VTM 테스트를 실행하는 메인 함수.
 * @param {VTMInput} inputData - 테스트에 사용할 입력 파라미터.
 */
function runVTMTestHarness(inputData) {
    console.log("=====================================================");
    console.log(`[TEST START] VTM Prototype 실행 (Intensity: ${inputData.triggerIntensity.toFixed(2)})`);
    console.log("=====================================================");

    // 1단계 유효성 검사
    if (inputData.triggerIntensity < 0 || inputData.triggerIntensity > 1) {
        throw new Error("🚨 [ERROR] Trigger Intensity는 반드시 0.0 ~ 1.0 사이여야 합니다.");
    }

    console.log(`✅ Input Validation Passed: Media=${inputData.sourceMedia}, Time=[${inputData.timeMarkerStart}s - ${inputData.timeMarkerEnd}s]`);


    // 2단계: Phase 1 시뮬레이션 (Glitch Initialization)
    simulatePhase1(inputData);

    // 3단계: Phase 2 시뮬레이션 (Information Overload/Void Transition)
    simulatePhase2(inputData);

    console.log("\n=====================================================");
    console.log("✨ VTM Test Harness 실행 완료. 모든 파라미터가 성공적으로 처리됨.");
    console.log("=====================================================");
}


/**
 * Phase 1: Glitch Initialization 시뮬레이션
 * @param {VTMInput} inputData - 테스트 입력 데이터.
 */
function simulatePhase1(inputData) {
    const intensity = inputData.triggerIntensity;

    console.log("\n[PHASE 1] Glitch Initialization (정보 노이즈 주입)...");

    // [Color_Channel_Offset] 시뮬레이션 로직: 강도가 높을수록 오프셋 범위가 넓어져야 함
    const maxOffset = Math.min(0.07, intensity * 0.8);
    console.log(`  - Color Offset Range Simulation: R:[-${maxOffset.toFixed(2)}], G:[${maxOffset.toFixed(2)}], B:[${maxOffset.toFixed(2)}]`);

    // 트랜지션 횟수 결정 (강도가 높으면 더 자주 발생)
    const glitchCount = Math.ceil(1 + intensity * 5);
    console.log(`  - Expected Glitch Cycles: ${glitchCount}회 반복 예상.`);
}


/**
 * Phase 2: Void Transition 시뮬레이션
 * @param {VTMInput} inputData - 테스트 입력 데이터.
 */
function simulatePhase2(inputData) {
    const intensity = inputData.triggerIntensity;

    console.log("\n[PHASE 2] Information Overload / Void Transition...");

    // 정보 과부하에 따른 시각적 왜곡 파라미터 계산 (예: 글리치 노이즈의 주파수)
    const distortionFrequency = intensity * 5 + 1; // 최소 1Hz 유지
    console.log(`  - Distortion Frequency Calculated: ${distortionFrequency.toFixed(2)} Hz.`);

    // Void 발생 정도 (강도가 높으면 'Void' 시간이 길어지고 파라미터가 극단적임)
    const voidDuration = Math.max(0.5, intensity * 1.5);
    console.log(`  - Calculated Void Duration: ${voidDuration.toFixed(2)}초 (최대 논리 단절).`);

    // API 호출 가상화: 다음 컴포넌트가 받을 데이터 구조 정의
    const nextComponentPayload = {
        type: "Data_Packet",
        duration: voidDuration,
        params: {
            focus: "Cognitive Gap Visualization",
            entropyLevel: intensity * 100 // 백분율로 측정하여 전달
        }
    };

    console.log(`  - 💾 다음 모듈 (예: [ERROR_LAYER_2]) 호출 준비 완료.`);
    // console.log(JSON.stringify(nextComponentPayload, null, 2)); // 실제 디버깅 시 주석 해제 예정
}


// ====================================================
// 🚀 테스트 케이스 실행 (Simulation)
// ====================================================

console.log("-----------------------------------------------------");
console.log("     ✅ [TEST CASE 1] Normal Transition (Intensity: 0.4)");
console.log("-----------------------------------------------------");
try {
    runVTMTestHarness({ sourceMedia: 'video', timeMarkerStart: 2.3, timeMarkerEnd: 2.8, triggerIntensity: 0.4 });
} catch (e) {
    console.error(e.message);
}

console.log("\n\n-----------------------------------------------------");
console.log("     ✅ [TEST CASE 2] Critical Void Transition (Intensity: 0.9)");
console.log("-----------------------------------------------------");
try {
    runVTMTestHarness({ sourceMedia: 'text_overlay', timeMarkerStart: 4.5, timeMarkerEnd: 6.0, triggerIntensity: 0.9 });
} catch (e) {
    console.error(e.message);
}

console.log("\n\n-----------------------------------------------------");
console.log("     ❌ [TEST CASE 3] Failure Case Test (Invalid Intensity)");
console.log("-----------------------------------------------------");
try {
    runVTMTestHarness({ sourceMedia: 'video', timeMarkerStart: 0, timeMarkerEnd: 1, triggerIntensity: 1.5 });
} catch (e) {
    // 에러 처리가 정상 작동하는지 검증
    console.error(`\n[PASS] 예상 오류 발생 확인: ${e.message}`);
}
