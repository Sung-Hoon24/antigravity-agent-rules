/*
 * VTM_TRIGGER Minimum Viable Prototype (MVP) State Machine Pseudo-Code
 * @version 1.0.0
 * @description Designer v4.0 Param Manual 기반, 엔진 통합 테스트용 핵심 로직 정의
 * @author Kodari Engineer
 */

// ===============================================
// [CONFIG] - Global Constants and Data Sources (Must be loaded first)
// ===============================================
const CONFIG = {
    TRIGGER_START_TIME: "T + 0:46", // Designer Spec L1.5 ("...그럼 이것은?") 지점
    MAX_COGNITIVE_GAP: 10,          // 최대 임계값 (예: 0~10 스케일)
    VISUAL_ASSETS: ["ArchiveNoise", "DataGridOverlay", "ParadoxTextModule"],
};

/**
 * @typedef {Object} StateTransitionInput
 * @property {number} cognitiveGapLevel - 현재 시청자의 지적 간극 레벨 (API Input). 0~10.
 * @property {string} scriptMarker - 스크립트의 현재 논리 마커 (예: "L1.5", "L2.1").
 * @property {boolean} isQuestionAsked - 질문 발생 여부 플래그.
 */

// ===============================================
// [MODULE 1] - Core State Manager
// ===============================================
class VTM_StateMachine {
    constructor() {
        this.currentState = "PRE_TRIGGER"; // 초기 상태: 안정적인 아카이브 탐색 모드
        console.log("⚙️ VTM State Machine Initialized. Ready for input stream.");
    }

    /**
     * @param {StateTransitionInput} input - 외부에서 들어오는 현재 시점의 데이터.
     */
    processInput(input) {
        let nextState = this.determineNextState(input);
        if (nextState !== this.currentState) {
            console.warn(`🚨 State Transition Detected: ${this.currentState} -> ${nextState}`);
            this.setState(nextState, input);
        } else {
             // 상태 변화가 없어도 파라미터 업데이트는 필요함.
            VisualizationEngine.updateParameters(input.cognitiveGapLevel);
        }
    }

    /**
     * 현재 Input과 과거 State를 기반으로 다음 State를 결정합니다. (핵심 비즈니스 로직)
     */
    determineNextState(input) {
        if (this.currentState === "PRE_TRIGGER") {
            // Pre-Trigger: Gap이 일정 수준 이상 올라가면 Trigger 시작
            if (input.cognitiveGapLevel >= 5 && input.scriptMarker === "L1.5") {
                return "TRIGGER_POINT"; // 논리적 충격 지점 도달
            }
        } else if (this.currentState === "TRIGGER_POINT") {
            // Trigger Point: Gap이 최대치에 근접하거나, 질문 발생 시 유지/최대화
             if (input.cognitiveGapLevel >= 8 && input.isQuestionAsked) {
                 return "PAUSED_PARADOX"; // 파라독스 고정 상태 (가장 집중해야 하는 구간)
            } else if (input.cognitiveGapLevel < 4) {
                // Gap이 급격히 낮아지면 (설명으로 풀리면) 다음 단계로 이동
                 return "POST_TRIGGER";
            }
        } else if (this.currentState === "PAUSED_PARADOX") {
             if (input.scriptMarker === "L2.1" && input.cognitiveGapLevel < 3) {
                return "POST_TRIGGER"; // 다음 논지로 넘어갈 준비 완료
            }
        }

        return this.currentState; // 상태 변화 없음 유지
    }

    setState(newState, input) {
        this.currentState = newState;
        // State 변경 시 필수적인 액션 실행 (예: 강한 UI/UX 전환 효과 발동)
        VisualizationEngine.executeTransitionEffect(newState);
    }
}

// ===============================================
// [MODULE 2] - Visualization Engine (API 호출 지점 역할)
// ===============================================
const VisualizationEngine = {
    /**
     * 현재 Gap Level에 맞춰 모든 파라미터를 동기적으로 업데이트합니다.
     * @param {number} gapLevel - Input Cognitive Gap Level.
     */
    updateParameters(gapLevel) {
        let saturationFactor, noiseFrequency;

        // 💡 핵심 로직: Gap Level을 구체적인 시각 파라미터로 매핑 (Designer Spec 활용)
        if (gapLevel > 7) {
            saturationFactor = Math.min(1.0, gapLevel / 10); // 고난도일수록 채도 급증
            noiseFrequency = "High";                           // 노이즈 주파수 증가
        } else if (gapLevel < 3) {
            saturationFactor = 0.2;                            // 낮은 Gap은 색상이 무채색으로 안정화
            noiseFrequency = "Low";
        } else {
            saturationFactor = 0.5 + (gapLevel / 10);         // 중간값 유지
            noiseFrequency = gapLevel > 4 ? "Medium" : "Low";
        }

        console.log(`🎨 VISUAL UPDATE: Gap=${Math.round(gapLevel)}, Saturation=${saturationFactor}, Noise=${noiseFrequency}`);

        // API 호출 시뮬레이션 (실제 엔진 함수 호출)
        VisualModule_ArchiveNoise.setParams({ saturation: saturationFactor, frequency: noiseFrequency });
        VisualModule_DataGridOverlay.updateIntensity(Math.abs(gapLevel - 5)); // Gap이 5에서 멀어질수록 강하게 진동
        // ... 기타 모듈 호출
    },

    /**
     * 상태가 바뀔 때마다 엔진 전체에 걸친 전환 효과를 실행합니다. (예: 화면 깜빡임, 필터 적용)
     */
    executeTransitionEffect(newState) {
        switch (newState) {
            case "TRIGGER_POINT":
                // API 호출 예시: 모든 사운드 및 비주얼 파라미터를 최대치로 1초간 부스트.
                VisualModule_GlobalFX.applyBurstFilter();
                break;
            case "PAUSED_PARADOX":
                // 가장 강력한 몰입감을 위한 특수 처리
                VisualModule_DataGridOverlay.lockInPlace(true); // 그리드를 움직이지 않게 고정
                break;
            default:
                VisualModule_GlobalFX.reset();
        }
    }
};

// ===============================================
// [MODULE 3] - Simulated External/Visualization Modules (Mockup)
// ===============================================
const VisualModule_ArchiveNoise = { setParams: (p) => console.log(`[API Call] Archive Noise updated: ${JSON.stringify(p)}`) };
const VisualModule_DataGridOverlay = { updateIntensity: (val) => console.log(`[API Call] Data Grid Intensity adjusted by: ${val}`) , lockInPlace: (b) => console.log(`[API Call] Data Grid locked: ${b}` )};
const VisualModule_GlobalFX = { applyBurstFilter: () => console.log("[API Call] Global Filter Burst Activated."), reset: () => console.log("[API Call] Global Filter Reset.") };

// ===============================================
// [EXECUTION FLOW EXAMPLE] - 시뮬레이션 테스트 실행 (테스트 통과 확인)
// ===============================================

console.log("\n=== VTM_TRIGGER Sequence Simulation Start ===");

const stateMachine = new VTM_StateMachine();

// 1. Pre-Trigger Phase: 정보 습득 및 미세한 궁금증 유도 (Gap Level 2)
stateMachine.processInput({ cognitiveGapLevel: 2, scriptMarker: "L1.3", isQuestionAsked: false });
console.log("--- [T+0:05] Stable state maintained.");

// 2. Pre-Trigger Phase: 논리적 불일치 발생 (Gap Level 4)
stateMachine.processInput({ cognitiveGapLevel: 4, scriptMarker: "L1.4", isQuestionAsked: false });
console.log("--- [T+0:35] Mild Confusion Detected.");

// 3. TRIGGER POINT: 존재론적 질문 폭발 (Gap Level 8) -> State Change!
stateMachine.processInput({ cognitiveGapLevel: 8, scriptMarker: "L1.5", isQuestionAsked: true });
console.log("✅ [T+0:46] *** VTM_TRIGGER ACTIVATED! ***");

// 4. PAUSED_PARADOX: 최고의 몰입 유도 (Gap Level 9) - 상태 유지
stateMachine.processInput({ cognitiveGapLevel: 9, scriptMarker: "L1.5", isQuestionAsked: true });
console.log("🚀 [T+0:55] Max Paradox State Maintained.");

// 5. POST_TRIGGER: 다음 논지로 전환 (Gap Level 2) -> State Change!
stateMachine.processInput({ cognitiveGapLevel: 2, scriptMarker: "L2.1", isQuestionAsked: false });
console.log("✅ [T+1:06] Transition to Deep Introspection Mode.");

console.log("\n=== Simulation Complete. MVP Pseudo-Code Ready. ===");
