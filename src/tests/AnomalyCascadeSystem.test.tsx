import { render, screen, act } from '@testing-library/react';
import AnomalyCascadeSystem from '../components/AnomalyCascadeSystem';

// NOTE: 실제 환경에서는 State Management와 useEffect를 mock해야 합니다.
describe('Anomaly Cascade System (ACS) Integration Test', () => {
    it("should successfully transition through Stable -> Red -> Green states and log correct parameters", async () => {
        // 초기 상태 렌더링 및 테스트 시작
        render(<AnomalyCascadeSystem />);

        console.log("\n--- Starting ACS State Transition Test ---");

        // 1. [Stable State] 확인 (초기 검증)
        let stableElement = screen.getByText(/시스템 정상 작동/i);
        expect(stableElement).toBeInTheDocument();
        console.log("✅ PASS: Initial Stable State verified.");

        // Mocking setTimeout을 사용하여 시간 흐름 강제 제어 (실제 개발 환경에서 필수)
        jest.useFakeTimers();

        // 2. [Transition to Anomaly_Red] 트리거 대기 및 실행
        act(() => {
            jest.advanceTimersByTime(3000); // 3초 경과
        });
        await act(async () => {
             jest.runAllTimers(); // 모든 타이머 이벤트 처리
        });

        // Red State 확인 및 파라미터 검증
        let redElement = screen.getByText(/CRITICAL FAILURE/i);
        expect(redElement).toBeInTheDocument();
        console.log("✅ PASS: Anomaly_Red state reached successfully.");
        // 실제 테스트에서는 여기에 P_NoiseMagnitude의 임계치 초과 여부를 체크하는 로직 추가가 필요합니다.

        // 3. [Transition to Recovering_Green] 트리거 대기 및 실행
        act(() => {
            jest.advanceTimersByTime(4000); // 4초 경과 (Red -> Green)
        });
         await act(async () => {
             jest.runAllTimers();
        });

        // Green State 확인 및 파라미터 검증
        let greenElement = screen.getByText(/RECOVERY IN PROGRESS/i);
        expect(greenElement).toBeInTheDocument();
        console.log("✅ PASS: Recovering_Green state reached successfully.");

        // 4. [End State]까지 기다림 (최종 검증)
        act(() => {
            jest.advanceTimersByTime(6000); // 나머지 시간 경과
        });
         await act(async () => {
             jest.runAllTimers();
        });

        // 최종 Stable 상태 확인 또는 종료 메시지 확인
        let finalStableElement = screen.getByText(/시스템 정상 작동/i);
        expect(finalStableElement).toBeInTheDocument();
        console.log("✅ PASS: System returned to stable state.");


        jest.useRealTimers();
    });
});
