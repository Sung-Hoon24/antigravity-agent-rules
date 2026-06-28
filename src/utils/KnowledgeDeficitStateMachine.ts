/**
 * [KnowledgeDeficitStateMachine] 지식 결핍 상태 관리 로직
 * 시청자에게 논리적 필연성을 주입하여 다음 행동을 유도합니다.
 */

type State = 'Initial' | 'NormalFlow' | 'GapDetected' | 'ConflictThresholdHit' | 'Resolution';

interface StateContext {
    currentIntensity: number; // 현재 지식 충돌 강도 (0.0 ~ 1.0)
    state: State;
}

/**
 * 상태 전환 로직을 관리하는 핵심 함수입니다.
 * @param context - 현재 상태 컨텍스트
 * @param newInformationRatio - 새롭게 주입되는 정보의 신뢰성 비율 (0~1)
 * @returns 새로운 StateContext와 다음 액션 타입을 포함합니다.
 */
export const updateState = (context: StateContext, newInformationRatio: number): { newState: State; nextAction: 'CONTINUE' | 'TRIGGER_VTM' | 'RESOLUTION'; contextUpdate: Partial<StateContext> } => {
    let nextState = context.state;
    let nextAction: 'CONTINUE' | 'TRIGGER_VTM' | 'RESOLUTION' = 'CONTINUE';
    const conflictIncrease = 1 - newInformationRatio; // 신뢰성 낮을수록 충돌 증가

    // 1. 현재 지식 충돌 강도 업데이트
    const newIntensity = Math.min(1.0, context.currentIntensity + (conflictIncrease * 0.3));

    let nextContextUpdate: Partial<StateContext> = { currentIntensity: newIntensity };


    // 2. 상태 머신 로직 실행
    if (newIntensity >= 0.7 && context.state !== 'ConflictThresholdHit') {
        // 임계값 도달! VTM 트리거
        nextState = 'ConflictThresholdHit';
        nextAction = 'TRIGGER_VTM';
        console.log(`[STATE MACHINE] 🚨 지식 충돌 임계값(70%) 초과 감지. VTM 발동 준비.`);
    } else if (newIntensity >= 0.4 && context.state === 'NormalFlow') {
        // Gap 발생 초기 단계
        nextState = 'GapDetected';
        nextAction = 'TRIGGER_VTM'; // 경고급 애니메이션으로 트래픽 유도
        console.log(`[STATE MACHINE] 🤔 지식적 결핍 감지. 청중 참여 유도 필요.`);
    } else if (newIntensity < 0.3) {
        // 충분한 정보 주입 또는 해소
        nextState = 'NormalFlow';
        nextAction = 'CONTINUE';
    }

    return {
        newState: nextState,
        nextAction: nextAction,
        contextUpdate: nextContextUpdate
    };
};

/**
 * 초기 상태 설정 함수 (Initial State)
 */
export const initializeState = (): StateContext => ({
    currentIntensity: 0.0,
    state: 'Initial'
});
