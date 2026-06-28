/**
 * VTM_TRIGGER System Core Module
 * 이 모듈은 클라이맥스 구간의 상태 관리와 파라미터 처리를 담당합니다.
 */

class VTMTriggerSystem {
    constructor(initialParameters) {
        // 기본 상태 초기화: '지적 호기심 유도' 상태에서 시작 (Initial State)
        this.currentState = 'AWARENESS_STATE';
        this.parameters = this._initializeParams(initialParameters);
        console.log(`[System] VTM Trigger System Initialized in state: ${this.currentState}`);
    }

    /**
     * 초기 파라미터를 기반으로 시스템 설정을 로드합니다.
     * @param {Object} params - 외부에서 주입되는 모든 시각/기술 파라미터 객체.
     */
    _initializeParams(params) {
        // CGVS v1.1 Technical Manual의 핵심 파라미터들을 구조화하여 저장
        return {
            P_Indigo: params.get('PrimaryColor', '#2C3E50'),
            P_Gold: params.get('AccentColor', '#D4AF37'),
            P_JitterScale: parseFloat(params.get('JitterMagnitude', '0.8')), // 정보 붕괴 강도
            P_TransitionSpeed: parseFloat(params.get('FadeDurationMs', '500')), // 상태 전환 속도
            P_NodesCount: parseInt(params.get('NodeDensity', '120')) // 노드 밀도
        };
    }

    /**
     * 시스템의 핵심 기능: 상태 전이 함수 (State Transition Function)
     * @param {string} triggerEvent - 발생한 이벤트 ('QUESTION_ASKED', 'DATA_OVERLOAD', 'RESOLUTION').
     */
    transitionState(triggerEvent) {
        let nextState = this.currentState;
        const currentParams = this.parameters;

        // State Machine 로직 구현
        switch (this.currentState) {
            case 'AWARENESS_STATE': // 1. 지적 호기심 자극 단계
                if (triggerEvent === 'QUESTION_ASKED') {
                    nextState = 'CONFUSION_TRIGGER'; // 의문 유발로 전환
                } else if (triggerEvent === 'DATA_OVERLOAD') {
                    // 논리적으로 불가능한 데이터가 들어오면 강제 오류 상태 발생
                    nextState = 'ERROR_COLLAPSE';
                }
                break;

            case 'CONFUSION_TRIGGER': // 2. 미스터리/불안정 단계 (VTM_TRIGGER)
                if (triggerEvent === 'RESOLUTION') {
                    // 해결책 제시 시, 파라미터 기반의 급격한 변화를 유도해야 함
                    nextState = 'CLIMAX_REVELATION';
                    // 클라이맥스 전환 시 노이즈와 색상 강도를 극대화하도록 파라미터를 조정할 수 있음.
                    this.parameters.P_JitterScale *= 1.5;
                } else if (triggerEvent === 'QUESTION_ASKED') {
                     nextState = 'LOOPING_CYCLE'; // 질문이 계속되면 루프 상태 유지
                }
                break;

            case 'CLIMAX_REVELATION': // 3. 결말/깨달음 단계
                // 여기서 Funnel Gateway로 연결될 최종 CTA가 활성화됨
                nextState = 'POST_TRIGGER';
                break;

            default:
                console.error(`[System Error] Unknown state transition attempted from ${this.currentState}`);
        }

        if (nextState !== this.currentState) {
            console.log(`\n✅ [Transition Success]: ${this.currentState} -> ${nextState} triggered by ${triggerEvent}`);
            this.currentState = nextState;
            return true;
        } else {
            console.warn(`⚠️ [Warning]: No state change detected for event: ${triggerEvent}. Still in ${this.currentState}`);
            return false;
        }
    }

    /**
     * 현재 상태와 파라미터를 외부로 노출하여 렌더링 컴포넌트가 사용하게 함.
     */
    getStateAndParams() {
        return {
            state: this.currentState,
            params: JSON.parse(JSON.stringify(this.parameters)) // 복사본 반환
        };
    }

    // 상태에 따라 UI/UX의 변화를 계산하는 내부 메소드 (추가 가능)
    calculateVisualEffect(time) {
        const jitter = this.parameters.P_JitterScale * Math.sin(time * 0.01);
        return `[Visualization] Current Jitter: ${jitter.toFixed(2)}. Using color: ${this.parameters.P_Gold}`;
    }
}

module.exports = VTMTriggerSystem;
