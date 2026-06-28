// VTM Simulator Engine Core Logic
 * VTM Trigger System E2E Simulation Core Engine (Source of Truth)
 * 역할: Asset Bible의 파라미터를 기반으로 State Transition과 시각적 효과를 제어하는 중앙 엔진입니다.
 */

// --- 1. Type Definitions (Asset Bible V2.0 준수) ---
type State = 'NORMAL' | 'INTELLECTUAL_CURIOSTIY' | 'COLLAPSE_GATE' | 'POST_TRIGGER';

interface Parameters {
    jitterMagnitude: number; // Jitter Effect P-Set
    colorShiftHex: string;   // Accent Color Shift
    dataNoiseLevel: number;  // Information Collapse Severity
}

interface SystemState {
    state: State;
    timeElapsed: number;     // t [sec]
    params: Parameters;      // Current visual parameters
    isTriggered: boolean;    // Did the collapse happen?
}

// --- 2. Engine Class Definition ---
export class VTM_SimulatorEngine {
    private currentState: SystemState;
    private readonly assetBibleParams: Parameters = {
        jitterMagnitude: 0.1, // Initial low value
        colorShiftHex: "#2C3E50", // Deep Indigo Primary
        dataNoiseLevel: 0.05   // Minimal noise at start
    };

    constructor() {
        this.currentState = {
            state: 'NORMAL',
            timeElapsed: 0,
            params: this.assetBibleParams,
            isTriggered: false
        };
        console.log("✅ VTM Simulator Engine Initialized.");
    }

    // VTM Simulator Engine Core Logic
     * 시뮬레이션 상태를 다음 단계로 진행시키고 파라미터를 업데이트합니다.
     * @param timeDelta - 경과 시간 (초)
     */
    public advanceState(timeDelta: number): SystemState {
        this.currentState.timeElapsed += timeDelta;

        // 1. State Transition Logic (핵심 State Machine)
        if (this.currentState.state === 'NORMAL' && this.currentState.timeElapsed > 30) {
            this.transitionTo('INTELLECTUAL_CURIOSTIY');
        } else if (this.currentState.state === 'COLLAPSE_GATE' && this.currentState.timeElapsed > 15) {
            this.transitionTo('POST_TRIGGER');
        }

        // 2. Parameter Update Logic (State에 따른 동적 파라미터 변화)
        let newParams: Parameters;
        switch(this.currentState.state) {
            case 'NORMAL':
                newParams = this.assetBibleParams; // 안정 상태 유지
                break;
            case 'INTELLECTUAL_CURIOSTIY':
                // 지적 호기심 유도 구간: Jitter와 데이터 노이즈가 점진적으로 증가합니다.
                this.currentState.params.jitterMagnitude = Math.min(0.8, this.currentState.params.jitterMagnitude + (timeDelta * 0.01));
                this.currentState.params.dataNoiseLevel = Math.min(0.3, this.currentState.params.dataNoiseLevel + timeDelta * 0.02);
                newParams = { ...this.currentState.params }; // 현재 값을 복사하여 사용
                break;
            case 'COLLAPSE_GATE':
                // 정보 붕괴 구간: 모든 파라미터가 최고치로 도달하며 불안정성을 최대화합니다.
                this.currentState.params.jitterMagnitude = Math.max(0.5, this.currentState.params.jitterMagnitude + (timeDelta * 0.1));
                this.currentState.params.dataNoiseLevel = Math.min(1.0, this.currentState.params.dataNoiseLevel + timeDelta * 0.2);
                newParams = { ...this.currentState.params };
                break;
            case 'POST_TRIGGER':
                 // 결론 도달 구간: 안정화되면서 CTA가 강조됩니다.
                this.currentState.params.jitterMagnitude *= Math.exp(-timeDelta * 0.1); // 감쇠 효과
                newParams = { ...this.currentState.params };
                break;
            default:
                newParams = this.assetBibleParams;
        }

        // 최종 상태 업데이트
        this.currentState.params = newParams;
        return { ...this.currentState, params: newParams };
    }

    // VTM Simulator Engine Core Logic
     * 상태 전환을 처리하고 새로운 로직을 실행합니다.
     */
    private transitionTo(newState: State): void {
        console.log(`\n[SYSTEM] Transitioning from ${this.currentState.state} -> ${newState}`);
        this.currentState.state = newState;
        this.currentState.timeElapsed = 0; // 새 상태 시작 시 카운트다운 초기화

        // 상태별 특수 로직 실행 (예: Collapse Gate 진입 시 플래시 효과 트리거)
        if (newState === 'COLLAPSE_GATE') {
            console.warn("🚨 WARNING: COLLAPSE GATE ACTIVATED! Maximum instability parameters applied.");
        }
    }

    public getCurrentState(): SystemState {
        return this.currentState;
    }
}
