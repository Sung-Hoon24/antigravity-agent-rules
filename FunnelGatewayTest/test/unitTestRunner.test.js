/**
 * Unit Test Runner: Funnel Gateway의 상태 전이 로직(State Transition Logic) 및 시간적 무결성을 테스트합니다.
 * @jest-environment jsdom
 */
describe('🚨 FunnelGateway State Machine Integrity Check', () => {
    // Mocking the state machine dependency for isolation
    const mockStateMachine = {
        transition: (newState, targetTimeMs) => { /* ... logic simulation ... */ },
        getCurrentState: () => 'IDLE'
    };

    test('✅ Initial State Check: 시스템은 항상 IDLE 상태에서 시작해야 합니다.', () => {
        expect(mockStateMachine.getCurrentState()).toBe('IDLE');
    });

    test('🚀 Hook-to-Gateway Transition (T+320ms): 시간적 결핍 유도 로직이 정확히 작동하는지 검증합니다.', () => {
        // 시나리오: 300ms 지점에서 강제로 T+320ms 상태로 진입해야 함.
        mockStateMachine.transition('GAP_INIT', 320);
        expect(mockStateMachine.getCurrentState()).toBe('GAP_INIT');
    });

    test('🔥 Critical Zone Test (T+320ms ~ T+510ms): 시간 흐름과 오류 결합 상태 전이 로직의 무결성을 검증합니다.', () => {
        // 1. 테스트 시작점 설정: T=320ms에서 시스템적 불안정성(Glitch) 발생 시뮬레이션
        mockStateMachine.transition('GLITCH_TRANSITION', 320);
        expect(mockStateMachine.getCurrentState()).toBe('GLITCH_TRANSITION');

        // 2. 중간 지점 검증: T=450ms (가장 불안정한 지점)에서 로직이 정상적으로 오류를 감지하고 재전이를 시도하는지 확인
        mockStateMachine.transition('GLITCH_TRANSITION', 450);
        // 이 테스트는 실제로 모션 엔진과의 API 통신을 통해 '오류 발생'이라는 데이터를 받는지 검증해야 합니다.
        expect(typeof mockStateMachine.getErrorCode()).toBe('number'); // 오류 코드가 숫자여야 함

        // 3. 종료 지점 확인: T=510ms를 넘어서면 반드시 다음 상태로의 전이가 준비되어 있어야 합니다.
        mockStateMachine.transition('GAP_INIT', 510);
        expect(mockStateMachine.getCurrentState()).not.toBe('GLITCH_TRANSITION'); // GLITCH에서 벗어나야 함
    });

    test('✅ Resolution State: Funnel Gateway 탈출 후 다음 콘텐츠로의 부드러운 연결이 보장되어야 합니다.', () => {
        mockStateMachine.transition('RESOLUTION', 600);
        expect(mockStateMachine.getCurrentState()).toBe('RESOLUTION');
    });
});
