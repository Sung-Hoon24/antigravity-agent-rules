import { updateState, initializeState } from '../KnowledgeDeficitStateMachine';

// Mocking the state machine logic for testing purposes
describe('KnowledgeDeficitStateMachine', () => {
    let initialState: StateContext;

    beforeEach(() => {
        initialState = initializeState();
    });

    test('1. Initial State에서 Normal Flow를 거쳐 Gap Detected로 전환되는지 테스트 (Low Info)', () => {
        // 1단계: 초기 -> 정상 흐름 유지 (높은 정보 신뢰도)
        let context = updateState(initialState, 0.95);
        expect(context.newState).toBe('NormalFlow');
        expect(context.nextAction).toBe('CONTINUE');

        // 2단계: 정보 비율 하락 -> Gap Detected로 전환 시도 (중간 신뢰도)
        let context2 = updateState({ ...initialState, state: 'NormalFlow' }, 0.6);
        expect(context2.newState).toBe('GapDetected');
        expect(context2.nextAction).toBe('TRIGGER_VTM');

        // 3단계: Gap Detected 상태 유지 및 강한 충돌 유도 (매우 낮은 신뢰도)
        let context3 = updateState({ ...initialState, state: 'GapDetected' }, 0.1);
        expect(context3.newState).toBe('ConflictThresholdHit');
        expect(context3.nextAction).toBe('TRIGGER_VTM');

    });

    test('2. Conflict Threshold가 정확히 70%를 넘었을 때 VTM 트리거가 발생하는지 테스트 (Critical Test)', () => {
        // 강제 초기 상태 설정: 충돌 임계값 직전 (65%)
        let contextInitial = { currentIntensity: 0.65, state: 'NormalFlow' };

        // 정보 신뢰도(newInformationRatio)를 매우 낮게 주입하여 70% 초과 유도
        const result = updateState(contextInitial, 0.2); // 충돌 증가량 계산상 70% 이상으로 올라가야 함

        expect(result.newState).toBe('ConflictThresholdHit');
        expect(result.nextAction).toBe('TRIGGER_VTM');
    });
});
