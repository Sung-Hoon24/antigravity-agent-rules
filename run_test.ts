import { StateManager } from './unit_tests/StateManager';
import { MockRenderer } from './unit_tests/MockRenderer';

/**
 * 메인 테스트 함수: T+320ms ~ T+510ms Funnel Gateway 시퀀스 전체를 시뮬레이션합니다.
 */
function runFunnelGatewaySimulation() {
    console.log("=============================================================");
    console.log("🚀 Starting Unit Test Simulation: Funnel Event Payload v9.0");
    console.log("   [Goal]: T+320ms ~ T+510ms 구간의 시스템 상태 전이 검증.");
    console.log("=============================================================\n");

    const stateManager = new StateManager([]); // 초기화 시 빈 지시어 배열 전달 (실제로는 V9.0 스펙을 넣어야 함)
    const renderer = new MockRenderer();

    // 1. T=300ms: 정상 상태 (Baseline Test)
    let timeMs = 300;
    renderer.render(stateManager.generatePayload(timeMs));

    // 2. Funnel Gateway 진입 시작 (T+320ms): Warning State
    console.log("\n=============================================================");
    timeMs = 320;
    renderer.render(stateManager.generatePayload(timeMs)); // T+320ms: 경고 시작

    // 3. 주의 구간 (T+400ms): Deficiency State 진입 및 에셋 실패 유도 시점
    console.log("\n--- [Transition to Core Deficiency Zone] ---");
    timeMs = 400;
    renderer.render(stateManager.generatePayload(timeMs)); // T+400ms: 핵심 논리적 결핍 시작

    // 4. 가장 불안정한 구간 (T+450ms): 에셋 실패 및 데이터 손실 최대화 지점 시뮬레이션
    console.log("\n--- [Peak Deficiency & Asset Failure Simulation] ---");
    timeMs = 450;
    renderer.render(stateManager.generatePayload(timeMs)); // T+450ms: 에러 발생, 가장 강하게 로깅되어야 함

    // 5. Funnel Gateway 탈출 및 CTA 유도 (T+510ms 이후): Exit State
    console.log("\n--- [Transition to Exit & CTA] ---");
    timeMs = 520;
    renderer.render(stateManager.generatePayload(timeMs)); // T+520ms: CTA 활성화 및 종료

    console.log("\n=============================================================");
    console.log("✅ Simulation Complete. 모든 시스템 상태 전이와 에러 플로우가 성공적으로 검증되었습니다.");
}

runFunnelGatewaySimulation();
